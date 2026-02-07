"""
🚀 INDEXADOR RÁPIDO - Ejecutar desde Streamlit
Corre esto en la terminal donde ejecutas streamlit
"""

import os
import sys

# Añadir el directorio raíz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services import KnowledgeLibrary

def main():
    folder = "1_BIBLIOTECA"
    
    print(f"📁 Indexando carpeta: {folder}\n")
    
    if not os.path.exists(folder):
        print(f"❌ No existe la carpeta: {folder}")
        return
    
    lib = KnowledgeLibrary()
    
    # Extensiones soportadas
    supported = ['.pdf', '.epub', '.mobi', '.txt', '.md', '.html', '.htm']
    
    # Buscar archivos
    books = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in supported):
                books.append(os.path.join(root, file))
    
    print(f"📚 Encontrados {len(books)} archivos\n")
    
    if not books:
        print("⚠️ No se encontraron archivos")
        return
    
    # Indexar
    indexed = 0
    errors = 0
    
    for i, path in enumerate(books, 1):
        filename = os.path.basename(path)
        print(f"[{i}/{len(books)}] {filename[:60]}...")
        
        # Extraer título/autor
        name = os.path.splitext(filename)[0]
        
        # Casos especiales
        if "Carta_Buffett" in filename:
            year = filename.split("_")[-1].split(".")[0]
            author = "Warren Buffett"
            title = f"Carta a los Accionistas {year}"
            topics = ['value investing', 'buffett', 'annual letters']
        
        elif "Z-Library" in filename:
            # Formato: "Titulo (Autor_ (Z-Library).epub"
            parts = name.replace(" (Z-Library)", "").split(" (")
            title = parts[0].strip()
            author = parts[1].strip("_)") if len(parts) > 1 else "Unknown"
            topics = ['value investing', 'investment books']
        
        elif any(x in filename.lower() for x in ['tsla', 'intc', 'pypl', '10-k', 'f-2024']):
            # 10-Ks
            ticker = filename.split("-")[0].upper()
            author = f"{ticker} Inc."
            title = f"10-K Filing {ticker}"
            topics = ['sec filings', '10-k']
        
        else:
            author = "Unknown"
            title = name
            topics = ['general']
        
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
            n, msg = lib.add_book(fake, title, author, topics)
            
            if n > 0:
                print(f"   ✅ {n} chunks")
                indexed += 1
            else:
                print(f"   ⚠️ {msg}")
                errors += 1
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            errors += 1
    
    print(f"\n{'='*60}")
    print(f"🎉 Indexación completada!")
    print(f"✅ Indexados: {indexed}/{len(books)}")
    print(f"❌ Errores: {errors}")
    print(f"📊 Total en biblioteca: {lib.book_count}")
    print(f"{'='*60}\n")
    
    # Mostrar algunos libros
    print("📚 Libros en la biblioteca:")
    for book in lib.books[:10]:
        print(f"  - {book.title} ({book.author}) - {book.num_chunks} chunks")
    
    if len(lib.books) > 10:
        print(f"  ... y {len(lib.books) - 10} más")

if __name__ == "__main__":
    main()
