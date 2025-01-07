import pdfplumber

def extrair_e_organizar(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()  # Extrair o texto da página
            print(texto)

# Caminho para o arquivo PDF
pdf_path = "fatura-2-3-1.pdf"

# Extrair dados e organizar em uma tabela
extrair_e_organizar(pdf_path)