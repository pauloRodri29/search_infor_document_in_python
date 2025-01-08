import PyPDF2
import re
import logging
import fitz
from openpyxl import Workbook
from pdfminer.high_level import extract_text
import pdfplumber

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s -----> %(message)s ")

"""Função para procurar o valor com uma referência específica"""
def search_value(regex, text):
    matches = []
    if regex:
        for match in re.finditer(regex, text):
            try:
                matches.append(match.group(1))  # Adiciona todos os grupos encontrados
            except IndexError:
                continue  # Caso não encontre o grupo desejado, ignora
    return matches  # Retorna todas as correspondências encontradas

"""Função para procurar todas as referências no texto"""
def search_references(references_dict, text):
    found_values = {}
    for key, regex in references_dict.items():
        if isinstance(regex, dict):  # Verificar se o valor é um subdicionário
            found_values[key] = search_references(regex, text)
        else:
            found_values_for_key = search_value(regex, text)  # Buscar todas as ocorrências
            if found_values_for_key:
                found_values[key] = found_values_for_key  # Armazenar todas as ocorrências encontradas
    return found_values

"""Função para extrair referências de PDFs"""
def extract_references_from_pdfs(input_files, references_dict, pages_to_extract=None, max_pages=None, start_page=0):
    extracted_data = []
    for file in input_files:
        try:
            # Abrindo o arquivo PDF com fitz
            reader = fitz.open(file)
            
            # Obter o número total de páginas
            num_pages = reader.page_count

            # Determina quais páginas processar
            if pages_to_extract:
                pages_to_process = [p for p in pages_to_extract if 0 <= p < num_pages]
            elif max_pages:
                pages_to_process = range(min(num_pages, max_pages))
            else:
                pages_to_process = range(num_pages)  # Todas as páginas

            # Se start_page for especificado, começa da página indicada
            if start_page >= 0:
                pages_to_process = [p for p in pages_to_process if p >= start_page]

            # Processa as páginas selecionadas
            for page_number in pages_to_process:
                page = reader[page_number]
                text = page.get_text()  # Extraindo o texto da página
                # logging.info(f"Texto extraído da página {page_number}: {text}")  # Mostra os primeiros 500 caracteres
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
            for key in references_dict.keys():
                value = values.get(key, "N/A")
                if isinstance(value, list):  # Se houver múltiplos valores, converte para uma string
                    row.append(", ".join(value))
                else:
                    row.append(value)
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
    input_files = ["fatura-2-3-1.pdf"]
    
    # Dicionário com as referências e expressões regulares
    references_dict = {
        # "Conta Contrato": r"CONTA CONTRATO:\s*(\d+)",
        # "Hash_Code": r"Hash Code:\s+([\w\d\.]+)",
        # "Documento": r"Documento:\s+(\d+)",
        # "Empresa": r"Empresa:\s+([^\n]+)",
        # "Municipio": r"Município:\s+([\w\s]+?)(?=\s+Bairro|$)",
        # "Vencimento": r"Vencimento:\s*(\d{2}\-\d{2}\-\d{4})",
        # "Valor_total": r"Valor:\s+([\d,\.]+)",
        "Instalacao": r"Instalação:\s+(\d+)",
        "Endereço, N°": r"Endereço:\s+((?!STO ANTONIO , 0)[^\n]+)(?=\s+Bairro|$)",
        "Bairro": r"Bairro:\s+([A-Za-z\s]+)(?=\s+Instalação|$)",
        "Complemento": r"Complemento:\s+([A-Za-z\s]+)(?=\s+Fatura|$)",
        "N° Fatura": r"Fatura:\s+(\d+)",
        
        "Classe Principal": r"Classe Principal\s*[^0-9]*\s*(\d+)",
        "Classe de Consumo": r"(?<=\bClasse de Consumo\b)(?:\D*\d+){1}\D*(\d+)",
        "Tensão": r"(?<=\bTensão\b)(?:\D*\d+){2}\s*(\S+)",
        "Fase": r"(?<=\bFase\b)(?:\D*\d+){3}\D*(\S+)",
        "Data Fatura": r"(?<=\bData Fat\b)(?:\D*\d+){5}\D*(\S+)",
        "Dias Fatura": r"(?<=\bDias Fat\b)(?:\D*\d+){8}\D*(\S+)",
        "Data Leitura Anterior": r"(?<=Dta\.Leit\.Ant)(?:\D*\d+){9}\D*(\S+)",
        "Data Leitura Atual": r"(?<=Dta\.Leit\.Atual)(?:\D*\d+){12}\D*(\S+)",
        
        "V.T.: Icms(BaseCalculo)": r"ICMS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Icms(Aliquota)": r"ICMS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Icms(Valor)": r"ICMS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Cofins": r"COFINS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Cofins(Aliquota)": r"COFINS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Cofins(Valor)": r"COFINS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Pis": r"PIS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Pis(Aliquota)": r"PIS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.T.: Pis(Valor)": r"PIS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        "V.M.: Esp": r"Esp\.\s+([\w\d\.,]+)",
        "V.M.: Medidor": r"Medidor\s+([\w\d\.,]+)",
        "V.M.: CTE": r"Cte\.\s+([\w\d\.,]+)",
        "V.M.: FP": r"%FP\s+([\w\d\.,]+)",
        "V.M.: Leitura_Anterior": r"Leit\. Anterior\s+([\d\.,]+)",
        "V.M.: Leitura_Atual": r"Leit\. Atual\s+([\d\.,]+)",
        "V.M.: Medido": r"Medido\s+([\w\d\.,]+)",
        "V.M.: Faturado": r"Faturado\s+([\d\.,]+)",
        "V.F.: Consumo(Quantidade)": r"Consumo\s+([\d\.,]+)",
        "V.F.: Consumo(Preço)": r"Preço\s+([\d\.,]+)",
        "V.F.: Consumo(Valor)": r"Valor\s+([\d\.,]+)",
        "Cip-Ilum Pub Pref Munic(Quantidade)":r"Cip-Ilum Pub Pref Munic\s+([\d\.,]+)",
        "Cip-Ilum Pub Pref Munic(Preço)":r"Cip-Ilum Pub Pref Munic\s+([\d\.,]+)",
        'Cip-Ilum Pub Pref Munic(Valor)':r"Cip-Ilum Pub Pref Munic\s+([\d\.,]+)",
        "V.F.: Adcional Bandeira (Quantidade)": r"Preço\s+([\d\.,]+)",
        "V.F.: Adcional Bandeira (Preço)": r"Preço\s+([\d\.,]+)",
        "V.F.: Adcional Bandeira (Valor)": r"Valor\s+([\d\.,]+)",
        "V.F.: Crédito Prazo Atendimento (Quantidade)": r"Valor\s+([\d\.,]+)",
        "V.F.: Crédito Prazo Atendimento (Preço)": r"Preço\s+([\d\.,]+)",
        "V.F.: Crédito Prazo Atendimento (Valor)": r"Valor\s+([\d\.,]+)",
        "V.F.: Tributo a Reter IRPJ (Quantidade)": r"Preço\s+([\d\.,]+)",
        "V.F.: Tributo a Reter IRPJ (Preço)": r"Preço\s+([\d\.,]+)",
        "V.F.: Tributo a Reter IRPJ (Valor)": r"Valor\s+([\d\.,]+)",
        "V.F.: Saldo em Aberto (Quantidade)": r"Preço\s+([\d\.,]+)",
        "V.F.: Saldo em Aberto (Preço)": r"Preço\s+([\d\.,]+)",
        "V.F.: Saldo em Aberto (Valor)": r"Valor\s+([\d\.,]+)",
    }
    
    # Adicionar uma coluna para contagem de páginas
    headers = ["Pagina"] + list(references_dict.keys())
    
    # # Extrair os valores do arquivo
    extracted_data = extract_references_from_pdfs(input_files, references_dict)
    
    # # Preparar os dados para exibição em tabela
    table = create_table(extracted_data, references_dict)

    # # Salvar os dados no Excel
    save_to_excel(table, headers, "dados_extraidos.xlsx")
    # text = extract_text(input_files[0])
    # logging.info(text)
    
    
# Use o caminho correto do arquivo PDF
    # with pdfplumber.open(input_files[0]) as pdf:
    #     for page in pdf.pages:
    #         # Extrai o texto com layout, inclui informações de coordenadas
    #         text = page.extract_tables_text()
    #         logging.info(text)

if __name__ == "__main__":
    main()
