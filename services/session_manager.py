"""
💾 SESSION MANAGER V8
Gestión de persistencia de análisis
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

from config import PATHS

logger = logging.getLogger(__name__)


class SessionManager:
    """Gestiona persistencia de análisis en Drive/disco."""
    
    def __init__(self):
        PATHS.ensure_directories()
    
    def save_debate(self, ticker: str, data: Dict) -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{ticker}_{timestamp}.json"
        filepath = os.path.join(PATHS.debates, filename)
        
        data['saved_at'] = timestamp
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Debate guardado: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error guardando debate: {e}")
            return ""
    
    def load_debates(self, ticker: Optional[str] = None, limit: int = 20) -> List[Dict]:
        try:
            files = sorted(os.listdir(PATHS.debates), reverse=True)
            
            if ticker:
                files = [f for f in files if f.startswith(ticker)]
            
            debates = []
            for filename in files[:limit]:
                try:
                    with open(os.path.join(PATHS.debates, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['_filename'] = filename
                        debates.append(data)
                except:
                    continue
            
            return debates
        except Exception as e:
            logger.error(f"Error cargando debates: {e}")
            return []
    
    def get_analyzed_tickers(self) -> List[str]:
        try:
            files = os.listdir(PATHS.debates)
            tickers = list(set([f.split('_')[0] for f in files if '_' in f]))
            return sorted(tickers)
        except:
            return []
    
    def delete_debate(self, filename: str) -> bool:
        try:
            os.remove(os.path.join(PATHS.debates, filename))
            return True
        except:
            return False
