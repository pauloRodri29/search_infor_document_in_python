import re
import pandas as pd
import logging
import fitz
from openpyxl import Workbook
import pdfplumber

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s -----> %(message)s ")

import re

def extract_info_from_text(patterns, text):
    results = []  # Lista para armazenar os resultados encontrados
    client_info = {}  # Dicionário temporário para armazenar as informações do cliente
    client_number = 1
    
    while True:
        # Flag para verificar se todos os valores são None
        all_none = True
        
        for key, regex in patterns.items():
            match = re.findall(regex, text, flags=re.IGNORECASE)  # Busca o padrão no texto
            
            if match:
                # Se match for uma lista de tuplas (com grupos de captura), a primeira tupla é a que você quer
                if isinstance(match[0], tuple):
                    # Se houver grupos de captura, pegamos o grupo específico
                    if client_number <= len(match[0]):
                        client_info[key] = match[0][client_number - 1].strip()  # Ajuste para acessar o grupo correto
                    else:
                        client_info[key] = None  # Se não houver grupo suficiente
                else:
                    # Caso contrário, apenas pega o valor encontrado
                    if client_number <= len(match):
                        client_info[key] = match[client_number - 1].strip()  # Ajuste para acessar o item correto
                    else:
                        client_info[key] = None  # Se não houver valor suficiente
            
            else:
                client_info[key] = None  # Caso não encontre, registra como None

            # Verifica se algum valor foi atribuído, caso contrário, indica que todos são None
            if client_info[key] is not None:
                all_none = False

        # Se todos os valores forem None, interrompe o loop
        if all_none:
            break
        
        # Após processar todas as chaves, adiciona o client_info à lista de resultados
        if any(value is not None for value in client_info.values()):  # Garante que ao menos um valor seja encontrado
            results.append(client_info)
            client_number += 1
            client_info = {}  # Limpa o dicionário para o próximo cliente
        else:
            break
    
    return results


def extract_references_from_pdfs(input_files, references_dict, pages_to_extract=None, max_pages=None, start_page=0):
    extracted_data = []

    for file in input_files:
        count_file = 1
        try:
            # Abrindo o arquivo PDF
            reader = fitz.open(file)
            num_pages = reader.page_count

            # Determina quais páginas processar
            if pages_to_extract:
                pages_to_process = [p for p in pages_to_extract if 0 <= p < num_pages]
            elif max_pages:
                pages_to_process = range(min(num_pages, max_pages))
            else:
                pages_to_process = range(num_pages)

            # Aplica o filtro de página inicial
            if start_page >= 0:
                pages_to_process = [p for p in pages_to_process if p >= start_page]

            # Processa cada página
            for page_number in pages_to_process:
                page = reader[page_number]
                text = page.get_text()  # Extraindo o texto da página
                # logging.info(text)
                found_values = extract_info_from_text(references_dict, text)
                for value in found_values:
                    value["Page"] = f"File - Page {count_file} - {page_number}"  # Adiciona o número da página
                    extracted_data.append(value)  # Adiciona cada cliente encontrado à lista
            
            count_file += 1

        except Exception as e:
            logging.error(f"Erro ao processar o arquivo {file}: {e}")

    return extracted_data

"""
Função responsável por preparar os dados em uma tabela (excel)
Vai receber paramentros que é os dados achados e o dicionário de referências
"""
# Função para criar a tabela
def create_table(extracted_data, references_dict):
    table_data = []
    
    # Itera sobre os dados extraídos (lista de dicionários)
    for page_data in extracted_data:
        row = []  # Cria uma nova linha para a tabela
        # Adiciona o nome da página se disponível
        page_name = page_data.get('Page', 'N/A')
        row.append(page_name)
        
        # Itera sobre o dicionário de referências
        for key in references_dict.keys():
            value = page_data.get(key, "N/A")
            if isinstance(value, list):  # Se houver múltiplos valores, converte para uma string
                row.append(", ".join(value))
            else:
                row.append(value)
        
        # Adiciona a linha com os dados da página
        table_data.append(row)
    
    return table_data

# Função para salvar os dados em um arquivo Excel
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
    input_files = [ "fatura.pdf"]
    
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
        
        # "V.T.: Icms(BaseCalculo)": r"ICMS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        # "V.T.: Icms(Aliquota)": r"ICMS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        # "V.T.: Icms(Valor)": r"ICMS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        # "V.T.: Cofins": r"COFINS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        # "V.T.: Cofins(Aliquota)": r"COFINS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        # "V.T.: Cofins(Valor)": r"COFINS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        # "V.T.: Pis": r"PIS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        # "V.T.: Pis(Aliquota)": r"PIS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        # "V.T.: Pis(Valor)": r"PIS\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)",
        # "V.M.: Esp": r"Esp\.\s+([\w\d\.,]+)",
        # "V.M.: Medidor": r"Medidor\s+([\w\d\.,]+)",
        # "V.M.: CTE": r"Cte\.\s+([\w\d\.,]+)",
        # "V.M.: FP": r"%FP\s+([\w\d\.,]+)",
        # "V.M.: Leitura_Anterior": r"Leit\. Anterior\s+([\d\.,]+)",
        # "V.M.: Leitura_Atual": r"Leit\. Atual\s+([\d\.,]+)",
        # "V.M.: Medido": r"Medido\s+([\w\d\.,]+)",
        # "V.M.: Faturado": r"Faturado\s+([\d\.,]+)",
        # "V.F.: Consumo(Quantidade)": r"Consumo\s+([\d\.,]+)",
        # "V.F.: Consumo(Preço)": r"Preço\s+([\d\.,]+)",
        # "V.F.: Consumo(Valor)": r"Valor\s+([\d\.,]+)",
        # "Cip-Ilum Pub Pref Munic(Quantidade)":r"Cip-Ilum Pub Pref Munic\s+([\d\.,]+)",
        # "Cip-Ilum Pub Pref Munic(Preço)":r"Cip-Ilum Pub Pref Munic\s+([\d\.,]+)",
        # 'Cip-Ilum Pub Pref Munic(Valor)':r"Cip-Ilum Pub Pref Munic\s+([\d\.,]+)",
        # "V.F.: Adcional Bandeira (Quantidade)": r"Preço\s+([\d\.,]+)",
        # "V.F.: Adcional Bandeira (Preço)": r"Preço\s+([\d\.,]+)",
        # "V.F.: Adcional Bandeira (Valor)": r"Valor\s+([\d\.,]+)",
        # "V.F.: Crédito Prazo Atendimento (Quantidade)": r"Valor\s+([\d\.,]+)",
        # "V.F.: Crédito Prazo Atendimento (Preço)": r"Preço\s+([\d\.,]+)",
        # "V.F.: Crédito Prazo Atendimento (Valor)": r"Valor\s+([\d\.,]+)",
        # "V.F.: Tributo a Reter IRPJ (Quantidade)": r"Preço\s+([\d\.,]+)",
        # "V.F.: Tributo a Reter IRPJ (Preço)": r"Preço\s+([\d\.,]+)",
        # "V.F.: Tributo a Reter IRPJ (Valor)": r"Valor\s+([\d\.,]+)",
        # "V.F.: Saldo em Aberto (Quantidade)": r"Preço\s+([\d\.,]+)",
        # "V.F.: Saldo em Aberto (Preço)": r"Preço\s+([\d\.,]+)",
        # "V.F.: Saldo em Aberto (Valor)": r"Valor\s+([\d\.,]+)",
    }
    
    # Adicionar uma coluna para contagem de páginas
    headers = ["Pagina"] + list(references_dict.keys())
    
    # # # Extrair os valores do arquivo
    extracted_data = extract_references_from_pdfs(input_files, references_dict)
    # logging.info(extracted_data)
    
    # # Preparar os dados para exibição em tabela
    table = create_table(extracted_data, references_dict)

    # # Salvar os dados no Excel
    save_to_excel(table, headers, "dados_extraidos.xlsx")
    # logging.info(text)
    
    
# Use o caminho correto do arquivo PDF
    # with pdfplumber.open(input_files[0]) as pdf:
    #     for page in pdf.pages:
    #         # Extrai o texto com layout, inclui informações de coordenadas
    #         text = page.extract_tables_text()
    #         logging.info(text)

if __name__ == "__main__":
    main()