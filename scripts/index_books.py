"""
📚 INDEXADOR RÁPIDO DE BIBLIOTECA
Indexa todos los libros de una carpeta automáticamente
"""

import os
import sys

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import KnowledgeLibrary

def index_folder(folder_path):
    """Indexa todos los libros de una carpeta"""
    
    if not os.path.exists(folder_path):
        print(f"❌ No existe la carpeta: {folder_path}")
        return
    
    lib = KnowledgeLibrary()
    
    # Extensiones soportadas
    supported = ['.pdf', '.epub', '.mobi', '.txt', '.md', '.html']
    
    # Buscar archivos
    books = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in supported):
                books.append(os.path.join(root, file))
    
    print(f"📚 Encontrados {len(books)} libros")
    
    if not books:
        print("⚠️ No se encontraron libros")
        return
    
    # Indexar
    indexed = 0
    for i, path in enumerate(books, 1):
        filename = os.path.basename(path)
        print(f"\n[{i}/{len(books)}] {filename}")
        
        # Extraer título/autor del nombre
        name = os.path.splitext(filename)[0]
        parts = name.split(' - ')
        
        if len(parts) >= 2:
            author = parts[0].strip()
            title = ' - '.join(parts[1:]).strip()
        else:
            author = "Unknown"
            title = name
        
        # Topics automáticos
        topics = []
        lower = filename.lower()
        
        if any(w in lower for w in ['buffett', 'munger', 'graham', 'lynch', 'value']):
            topics.append('value investing')
        if any(w in lower for w in ['technical', 'chart', 'trading']):
            topics.append('technical analysis')
        if any(w in lower for w in ['macro', 'economy', 'dalio', 'gil']):
            topics.append('macroeconomics')
        if any(w in lower for w in ['psychology', 'behavioral', 'kahneman']):
            topics.append('behavioral finance')
        
        # Simular upload
        class FakeFile:
            def __init__(self, p):
                self._path = p
                self.name = os.path.basename(p)
            def read(self):
                with open(self._path, 'rb') as f:
                    return f.read()
        
        try:
            fake = FakeFile(path)
            n, msg = lib.add_book(fake, title, author, topics or ['general'])
            
            if n > 0:
                print(f"   ✅ {n} chunks")
                indexed += 1
            else:
                print(f"   ❌ {msg}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 Completado: {indexed}/{len(books)} libros indexados")
    print(f"📊 Total en biblioteca: {lib.book_count}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        # Carpeta por defecto
        folder = "biblioteca_maestra"
    
    print(f"📁 Indexando carpeta: {folder}\n")
    index_folder(folder)
