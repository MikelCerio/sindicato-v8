"""
📰 SENTIMENT ANALYSIS SERVICE V8
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

import streamlit as st
from textblob import TextBlob
import plotly.graph_objects as go

from .market_data import MarketDataService

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    title: str
    link: str
    publisher: str
    timestamp: datetime
    polarity: float
    subjectivity: float
    sentiment: str
    emoji: str
    
    @property
    def css_class(self) -> str:
        return f"news-{self.sentiment}"


@dataclass
class SentimentAnalysis:
    news_items: List[NewsItem]
    average_polarity: float
    overall_sentiment: str
    overall_emoji: str
    positive_count: int
    negative_count: int
    neutral_count: int
    timeline_chart: Optional[go.Figure]
    
    @property
    def summary(self) -> str:
        return f"{self.overall_emoji} {self.overall_sentiment} | Score: {self.average_polarity:.2f}"


class SentimentAnalyzer:
    POSITIVE_THRESHOLD = 0.1
    NEGATIVE_THRESHOLD = -0.1
    BULLISH_KEYWORDS = ['upgrade', 'beats', 'strong', 'growth', 'profit', 'surge', 'rally']
    BEARISH_KEYWORDS = ['downgrade', 'miss', 'weak', 'decline', 'loss', 'crash', 'sell']
    
    def __init__(self):
        self._market_service = MarketDataService()
    
    def _analyze_text(self, text: str) -> Tuple[float, float]:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        text_lower = text.lower()
        
        bullish = sum(1 for kw in self.BULLISH_KEYWORDS if kw in text_lower)
        bearish = sum(1 for kw in self.BEARISH_KEYWORDS if kw in text_lower)
        polarity = max(-1, min(1, polarity + (bullish - bearish) * 0.1))
        
        return polarity, blob.sentiment.subjectivity
    
    def _classify_sentiment(self, polarity: float) -> Tuple[str, str]:
        if polarity > self.POSITIVE_THRESHOLD:
            return 'positive', '🟢'
        elif polarity < self.NEGATIVE_THRESHOLD:
            return 'negative', '🔴'
        return 'neutral', '⚪'
    
    def _create_timeline(self, news_items: List[NewsItem]) -> Optional[go.Figure]:
        if not news_items:
            return None
        
        dates = [n.timestamp for n in news_items]
        sentiments = [n.polarity for n in news_items]
        titles = [n.title[:50] + '...' for n in news_items]
        colors = ['#00ff00' if s > 0.1 else '#ff4444' if s < -0.1 else '#888' for s in sentiments]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=sentiments, mode='markers+lines',
            marker=dict(size=14, color=colors, line=dict(width=2, color='white')),
            line=dict(color='#444', width=1), text=titles,
            hovertemplate='<b>%{text}</b><br>Score: %{y:.3f}<extra></extra>'
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
        fig.update_layout(
            title="📰 News Sentiment Timeline", template="plotly_dark",
            height=300, showlegend=False, paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    @st.cache_data(ttl=300, show_spinner=False)
    def analyze(_self, ticker: str, limit: int = 10) -> SentimentAnalysis:
        raw_news = _self._market_service.get_news(ticker, limit)
        
        if not raw_news:
            return SentimentAnalysis([], 0, "Sin noticias", "⚪", 0, 0, 0, None)
        
        news_items = []
        total_polarity = 0
        pos, neg, neu = 0, 0, 0
        
        for news in raw_news:
            polarity, subj = _self._analyze_text(news['title'])
            sentiment, emoji = _self._classify_sentiment(polarity)
            
            news_items.append(NewsItem(
                news['title'], news['link'], news['publisher'],
                news['timestamp'], polarity, subj, sentiment, emoji
            ))
            total_polarity += polarity
            if sentiment == 'positive': pos += 1
            elif sentiment == 'negative': neg += 1
            else: neu += 1
        
        avg = total_polarity / len(news_items)
        overall = "BULLISH" if avg > 0.15 else "BEARISH" if avg < -0.15 else "NEUTRAL"
        emoji = "🟢" if avg > 0.15 else "🔴" if avg < -0.15 else "⚪"
        
        return SentimentAnalysis(news_items, avg, overall, emoji, pos, neg, neu, _self._create_timeline(news_items))
