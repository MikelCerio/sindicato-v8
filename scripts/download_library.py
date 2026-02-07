"""
📚 Script para descargar y indexar biblioteca desde Google Drive
"""

import os
import sys

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def download_from_gdrive():
    """Descarga la carpeta de Google Drive usando gdown"""
    try:
        import gdown
    except ImportError:
        print("❌ gdown no instalado. Ejecuta: pip install gdown")
        return False
    
    # ID de la carpeta de Google Drive
    folder_id = "1jORbWga1qQYHcRgA9PpOiYCRW_mbY-Sb"
    output_dir = "biblioteca_maestra"
    
    print(f"📥 Descargando biblioteca desde Google Drive...")
    print(f"📁 Carpeta ID: {folder_id}")
    
    try:
        # Descargar carpeta completa
        gdown.download_folder(
            id=folder_id,
            output=output_dir,
            quiet=False,
            use_cookies=False
        )
        print(f"✅ Biblioteca descargada en: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ Error descargando: {e}")
        print("\n💡 Alternativa: Descarga manualmente desde:")
        print(f"   https://drive.google.com/drive/folders/1jORbWga1qQYHcRgA9PpOiYCRW_mbY-Sb")
        return False


def index_all_books(library_path="biblioteca_maestra"):
    """Indexa todos los libros de la carpeta"""
    from services import KnowledgeLibrary
    
    if not os.path.exists(library_path):
        print(f"❌ No se encontró la carpeta: {library_path}")
        return
    
    lib = KnowledgeLibrary()
    
    # Buscar todos los archivos soportados
    supported_extensions = ['.pdf', '.epub', '.mobi', '.txt', '.md']
    books_found = []
    
    for root, dirs, files in os.walk(library_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in supported_extensions:
                books_found.append(os.path.join(root, file))
    
    print(f"\n📚 Encontrados {len(books_found)} libros para indexar")
    
    if not books_found:
        print("⚠️ No se encontraron libros en la carpeta")
        return
    
    # Indexar cada libro
    indexed = 0
    for i, book_path in enumerate(books_found, 1):
        filename = os.path.basename(book_path)
        print(f"\n[{i}/{len(books_found)}] Indexando: {filename}")
        
        # Intentar extraer título y autor del nombre del archivo
        # Formato esperado: "Autor - Titulo.pdf"
        name_parts = os.path.splitext(filename)[0].split(' - ')
        
        if len(name_parts) >= 2:
            author = name_parts[0].strip()
            title = ' - '.join(name_parts[1:]).strip()
        else:
            author = "Unknown"
            title = os.path.splitext(filename)[0]
        
        # Determinar topics basados en el nombre
        topics = []
        filename_lower = filename.lower()
        if any(word in filename_lower for word in ['buffett', 'munger', 'graham', 'value']):
            topics.append('value investing')
        if any(word in filename_lower for word in ['technical', 'chart', 'trading']):
            topics.append('technical analysis')
        if any(word in filename_lower for word in ['macro', 'economy', 'fed']):
            topics.append('macroeconomics')
        
        # Simular file upload
        class FakeFile:
            def __init__(self, path):
                self._path = path
                self.name = os.path.basename(path)
            
            def read(self):
                with open(self._path, 'rb') as f:
                    return f.read()
        
        try:
            fake_file = FakeFile(book_path)
            n, msg = lib.add_book(fake_file, title, author, topics)
            
            if n > 0:
                print(f"   ✅ {msg}")
                indexed += 1
            else:
                print(f"   ❌ {msg}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 Indexación completada: {indexed}/{len(books_found)} libros")
    print(f"📊 Total de libros en biblioteca: {lib.book_count}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Descarga e indexa biblioteca")
    parser.add_argument('--download', action='store_true', help='Descargar desde Google Drive')
    parser.add_argument('--index', action='store_true', help='Indexar libros locales')
    parser.add_argument('--path', default='biblioteca_maestra', help='Ruta de la biblioteca')
    
    args = parser.parse_args()
    
    if args.download:
        success = download_from_gdrive()
        if not success:
            sys.exit(1)
    
    if args.index or args.download:
        index_all_books(args.path)
    
    if not args.download and not args.index:
        print("Uso:")
        print("  python download_library.py --download  # Descarga desde GDrive")
        print("  python download_library.py --index     # Indexa libros locales")
        print("  python download_library.py --download --index  # Ambos")
