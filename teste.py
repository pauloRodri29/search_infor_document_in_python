# import pdfplumber

# def extrair_com_pdfplumber(arquivo):
#     with pdfplumber.open(arquivo) as pdf:
#         for page in pdf.pages:
#             # Extrai texto simples da página
#             texto = page.extract_text()
#             print(texto)

# # Substitua pelo caminho do seu PDF
# extrair_com_pdfplumber("fatura-2-3-1.pdf")

# from PyPDF2 import PdfReader

# def extrair_com_pypdf2(arquivo):
#     reader = PdfReader(arquivo)
#     for page in reader.pages:
#         texto = page.extract_text()
#         print(texto)

# # Substitua pelo caminho do seu PDF
# extrair_com_pypdf2("fatura-2-3-1.pdf")

# import fitz  # PyMuPDF

# def abrir(arquivo):
#     # Retorna o objeto Document do arquivo PDF
#     return fitz.open(arquivo)

# def extrair(arquivo):
#     # Abre o arquivo PDF e obtém o objeto Document
#     documento = abrir(arquivo)

#     # Dicionário para armazenar informações (se necessário)
#     informacao = {}
#     curso = ""

#     # Itera pelas páginas do PDF
#     for page in documento:
#         # Obtém o texto da página em formato de dicionário
#         blocks = page.get_text('dict')['blocks']
#         for block in blocks:
#             for line in block.get('lines', []):
#                 for span in line.get('spans', []):
#                     # Exibe cada linha de texto
#                     print(span['text'])

# if __name__ == "__main__":
#     # Substitua pelo caminho correto para seu arquivo PDF
#     extrair("fatura-2-3-1.pdf")

# from tabula import read_pdf

# def extrair_tabelas_com_tabula(arquivo):
#     tabelas = read_pdf(arquivo, pages="all", lattice=True)
#     for tabela in tabelas:
#         print(tabela)

# # Substitua pelo caminho do seu PDF
# extrair_tabelas_com_tabula("fatura-2-3-1.pdf")

# from tika import parser

# def extrair_com_tika(arquivo):
#     raw = parser.from_file(arquivo)
#     conteudo = raw.get('content', '')
    
#     # Remover linhas vazias e organizar melhor a saída
#     linhas = conteudo.split('\n')
#     linhas_limpa = [linha.strip() for linha in linhas if linha.strip()]
    
#     for linha in linhas_limpa:
#         print(linha)

# # Substitua pelo caminho do seu PDF
# extrair_com_tika("fatura-2-3-1.pdf")

# from pdfminer.high_level import extract_text

# pdf_path = "fatura-2-3-1.pdf"
# text = extract_text(pdf_path)
# print(text)

# # Exemplo fictício (substituir por chamada real)
# response = openai.Completion.create(
#     engine="text-davinci-003",
#     prompt="Extraia as informações importantes deste texto:\n" + text,
#     max_tokens=100,
# )
# print(response["choices"][0]["text"])
import tabula
import pandas as pd

# Caminho para o arquivo PDF
pdf_path = "fatura-2-3-1.pdf"

# Extrair tabelas do PDF
tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)

# Verificar quantas tabelas foram extraídas
print(f"Tabelas extraídas: {len(tables)}")

# Se houver tabelas, salve cada uma como uma aba no Excel
if tables:
    with pd.ExcelWriter("dados_extraidos3.xlsx") as writer:
        for i, table in enumerate(tables):
            # Escrever cada tabela em uma aba separada
            table.to_excel(writer, sheet_name=f"tabela_{i + 1}", index=False)
else:
    print("Nenhuma tabela encontrada no PDF.")
