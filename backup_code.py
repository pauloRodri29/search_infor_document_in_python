import PyPDF2
import re
import logging
from tabulate import tabulate
from openpyxl import Workbook

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s -----> %(message)s ")

"""Função para procurar o valor com uma referência específica"""
def search_value(regex, text):
    if regex:
        matches = re.findall(regex, text)
        return matches if matches else None
    return None

"""Função para procurar todas as referências no texto"""
def search_references(references_dict, text):
    found_values = {}
    for key, regex in references_dict.items():
        if isinstance(regex, dict):  # Verificar se o valor é um subdicionário
            found_values[key] = search_references(regex, text)
        else:
            found_value = search_value(regex, text)
            if found_value:
                found_values[key] = found_value
    return found_values

"""Função para extrair referências de PDFs"""
# Função para extrair referências de PDFs
def extract_references_from_pdfs(input_files, references_dict, pages_to_extract=None, max_pages=None, start_page=0):
    extracted_data = []
    for file in input_files:
        try:
            reader = PyPDF2.PdfReader(file)
            
            # Determina quais páginas processar
            if pages_to_extract:
                pages_to_process = [p for p in pages_to_extract if 0 <= p < len(reader.pages)]
            elif max_pages:
                pages_to_process = range(min(len(reader.pages), max_pages))
            else:
                pages_to_process = range(len(reader.pages))  # Todas as páginas

            # Se start_page for especificado, começa da página indicada
            if start_page >= 0:
                pages_to_process = [p for p in pages_to_process if p >= start_page]

            # Processa as páginas selecionadas
            for page_number in pages_to_process:
                page = reader.pages[page_number]
                text = page.extract_text()
                found_values = search_references(references_dict, text)
                if found_values:
                    extracted_data.append({f"Page {page_number}": found_values})
        except Exception as e:
            logging.error(f"Erro ao processar o arquivo {file}: {e}")
    return extracted_data

"""
Função responsável por preparar os dados em uma tabela (excel)
Vai receber paramentros que é os dados achados e o dicionário de referências
"""
def create_table(extracted_data, references_dict):
    table_data = []
    for page_data in extracted_data:
        for page, values in page_data.items():
            row = [page]  # Adiciona o nome da página
            row.extend([values.get(key, "N/A") for key in references_dict.keys()])
            table_data.append(row)
            
    return table_data

"""
 Função para salvar os dados em um arquivo Excel
"""
def save_to_excel(data, headers, output_file):
    wb = Workbook()
    ws = wb.active
    ws.title = "Base de dados"

    # Adicionar os cabeçalhos
    ws.append(headers)

    # Adicionar os dados extraídos
    for row in data:
        formatted_row = []
        for cell in row:
            if isinstance(cell, (tuple, list)):  # Converte tuplas ou listas para strings
                formatted_row.append(", ".join(map(str, cell)))
            else:
                formatted_row.append(cell)
        ws.append(formatted_row)

    # Salvar o arquivo
    wb.save(output_file)
    logging.info(f"Dados salvos com sucesso no arquivo Excel: {output_file}")

# Função principal
def main():
    input_files = ["fatura.pdf", "fatura-2-3.pdf"]
    
    # Dicionário com as referências e expressões regulares
    references_dict = {
        # "conta_contrato": r"CONTA CONTRATO:\s*(\d+)",
        # "Hash_Code": r"Hash Code:\s+([\w\d\.]+)",
        # "Documento": r"Documento:\s+(\d+)",
        # "Empresa": r"Empresa:\s+([^\n]+)",
        # "Municipio": r"Município:\s+([\w\s]+?)(?=\s+Bairro|$)",
        "Endereço": (r"Endereço:\s+([^\n]+)(?=\s+Município|$)"),
        "Instalacao": r"Instalação:\s+(\d+)",
        "Vencimento": r"Vencimento:\s*(\d{2}\-\d{2}\-\d{4})",
        # "Bairro": r"Bairro:\s+([A-Za-z\s]+)(?=\s+Referência)",
        "Cip-Ilum Pub Pref Munic":r"Cip-Ilum Pub Pref Munic\s+([\d\.,]+)",
        "Valor_total": r"Valor:\s+([\d,\.]+)",
        "Tensao": r"Tensão\s+([\w\d\.,]+)",
        "Recolhimento": r"Recolhimento:\s+(\d{2}/\d{2}/\d{4})",
        "Tributos_Icms": r"ICMS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "Tributos_Cofins": r"COFINS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "Tributos_Pis": r"PIS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "Valores_Medidos_Esp": r"Esp\.\s+([\w\d\.,]+)",
        "Valores_Medidos_Medidor": r"Medidor\s+([\w\d\.,]+)",
        "Valores_Medidos_CTE": r"Cte\.\s+([\w\d\.,]+)",
        "Valores_Medidos_FP": r"%FP\s+([\w\d\.,]+)",
        "Valores_Medidos_Leitura_Anterior": r"Leit\. Anterior\s+([\d\.,]+)",
        "Valores_Medidos_Leitura_Atual": r"Leit\. Atual\s+([\d\.,]+)",
        "Valores_Medidos_Medido": r"Medido\s+([\w\d\.,]+)",
        "Valores_Medidos_Faturado": r"Faturado\s+([\d\.,]+)",
        "Valores_Faturados_Consumo_Quantidade": r"Consumo\s+([\d\.,]+)",
        "Valores_Faturados_Consumo_Preço": r"Preço\s+([\d\.,]+)",
        "Valores_Faturados_Consumo_Valor": r"Valor\s+([\d\.,]+)",
        # "valores_faturados_preco": r"Preço\s+([\d,\.]+)",
        # "valores_faturados_valor": r"Valor\s+([\d,\.]+)"
    }
    # Adcionar uma coluna para contagem de páginas
    headers = ["Pagina"] + list(references_dict.keys())
    
    # Extrair os valores do arquivo
    extracted_data = extract_references_from_pdfs(input_files, references_dict)
    
    # Preparar os dados para exibição em tabela
    table = create_table(extracted_data, references_dict)


    # Salvar os dados no Excel
    save_to_excel(table, headers, "dados_extraidos.xlsx")
    

    logging.info("Processamento concluído com sucesso.")

if __name__ == "__main__":
    main()
