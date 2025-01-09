from PyPDF2 import PdfReader

# Caminho do PDF
pdf_path = "fatura-2-3-1.pdf"

# Lê o PDF
reader = PdfReader(pdf_path)
text_data = []

for page in reader.pages:
    text_data.append(page.extract_text())

# Salva o texto em um arquivo .txt
with open("dados_extraidos.xlsx", "w", encoding="utf-8") as f:
    f.write("\n".join(text_data))

print("Texto extraído e salvo em dados_extraidos.txt.")
