#!/usr/bin/env python3
"""Script para verificar número de páginas em um PDF usando WeasyPrint."""
import sys

def count_pdf_pages(pdf_path):
    """Conta o número de páginas em um PDF lendo os bytes."""
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
            # Contar ocorrências de /Type /Page (não /Pages)
            pages = content.count(b'/Type /Page')
            # Descontar /Type /Pages (catalog)
            pages_catalog = content.count(b'/Type /Pages')
            actual_pages = pages - pages_catalog
            return actual_pages
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return 0

if __name__ == "__main__":
    pdf_file = sys.argv[1] if len(sys.argv) > 1 else "relatorio_detalhado_teste.pdf"
    num_pages = count_pdf_pages(pdf_file)
    print(f"✅ Número de páginas no PDF: {num_pages}")
