import PyPDF2
import re
import logging
from openpyxl import Workbook

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s -----> %(message)s ")

"""Função para procurar o valor com uma referência específica"""
def search_value(regex, text):
    if regex:
        match = re.search(regex, text)
        if match:
            try:
                return match.group(1)  # Retorna o grupo encontrado
            except IndexError:
                # logging.warning(f"Grupo não encontrado para a regex: {regex}")
                return None
        else:
            # logging.warning(f"Nenhuma correspondência encontrada para a regex: {regex}")
            return None
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
                found_values[key] = found_value  # Adiciona o valor encontrado diretamente ao campo
    return found_values

"""Função para extrair referências de PDFs"""
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
                
                # Adiciona o log para visualizar o texto extraído
                # logging.info(f"Texto extraído da página {page_number}: {text[:500]}")  # Mostra os primeiros 500 caracteres para revisão
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
        "Instalacao": r"Instalação:\s+(\d+)",
        "Endereço": r"Endereço:\s+((?!STO ANTONIO , 0)[^\n]+)(?=\s+Bairro|$)",
        "Bairro, N°": r"Bairro:\s+([A-Za-z\s]+)(?=\s+Instalação|$)",
        "Complemento": r"Complemento:\s+([A-Za-z\s]+)(?=\s+Fatura|$)",
        "N° Fatura": r"Fatura:\s+(\d+)",
        "Classse Principal": r"Classe Principal:\s+(\d+)",
        "Classe de Consumo": r"Classe de Consumo:\s+(\d+)",
        "Tensão": r"Tensão\s+([\d\.,]+)",
        "Fase": r"Fase\s+([\d\.,]+)",
        "Data Fatura": r"Data F.\s+(\d{2}/\d{2}/\d{4})",
        "Dias Fatura": r"Dias Fat.\s+([\d\.,]+)",
        "Data Leitura Anterior": r"Dta. Leit. Ant.\s+(\d{2}/\d{2}/\d{4})",
        "Data Leitura Atual": r"Dta. Leit. Atual\s+(\d{2}/\d{2}/\d{4})",
        "Leitura Anterior": r"Leitura Anterior\s+([\d\.,]+)",
        "Leitura Atual": r"Leitura Atual\s+([\d\.,]+)",
        "V.T.: Icms(BaseCalculo)": r"ICMS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Icms(Aliquota)": r"ICMS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Icms(Valor)": r"ICMS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Cofins": r"COFINS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Cofins(Aliquota)": r"COFINS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Cofins(Valor)": r"COFINS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Pis": r"PIS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Pis(Aliquota)": r"PIS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Pis(Valor)": r"PIS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        # Adicione outras referências conforme necessário
    }
    
    # Adicionar uma coluna para contagem de páginas
    headers = ["Pagina"] + list(references_dict.keys())
    
    # Extrair os valores do arquivo
    extracted_data = extract_references_from_pdfs(input_files, references_dict, start_page=1, max_pages=2)
    
    # Preparar os dados para exibição em tabela
    table = create_table(extracted_data, references_dict)

    # Salvar os dados no Excel
    save_to_excel(table, headers, "dados_extraidos.xlsx")
    
    logging.info("Processamento concluído com sucesso.")

if __name__ == "__main__":
    main()
