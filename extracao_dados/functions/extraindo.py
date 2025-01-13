import os
import re
import pandas as pd
import logging
import fitz
from datetime import date

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s -----> %(message)s ")

def extract_info_from_text(patterns, text):
    results = []  # Lista para armazenar os arquivo encontrados
    client_info = {}  # Dicionário temporário para armazenar as informações do cliente
    client_number = 1
    while True:
        # Flag para verificar se todos os valores são None
        all_none = True

        for key, regex in patterns.items():
            match = re.findall(regex, text, flags=re.IGNORECASE | re.DOTALL)  # Busca o padrão no texto

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
            if os.path.splitext(file)[1] == ".pdf" and os.path.exists(file):
                # logging.info(f"Arquivo PDF encontrado: {file}")
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
                    if page_number < len(reader):
                        page = reader[page_number]
                        text = page.get_text()  # Extraindo o texto da página
                        # if page_number == 38:
                        # logging.info(text)
                        found_values = extract_info_from_text(references_dict, text)
                        for value in found_values:
                            value["Página-Arquivo"] = f" P{page_number} - A{count_file}"  # Adiciona o número da página
                            extracted_data.append(value)  # Adiciona cada cliente encontrado à lista

                count_file += 1

            else:
                logging.info(f"Arquivo {file} não suportado ou arquivo não existe")

        except Exception as e:
            logging.error(f"Erro ao processar o arquivo {file}: {e}")

    return extracted_data

"""
Função responsável por preparar os dados em uma tabela (excel)
Vai receber paramentros que é os dados achados e o dicionário de referências
"""
def create_table(extracted_data, references_dict):
    # Cria uma lista para armazenar os dados formatados
    table_data = []

    # Itera sobre os dados extraídos (lista de dicionários)
    for page_data in extracted_data:
        row = {}  # Cria um dicionário para a linha
        # Adiciona o nome da página se disponível
        row["Página-Arquivo"] = page_data.get("Página-Arquivo", "N/A")

        # Itera sobre o dicionário de referências
        for key in references_dict.keys():
            value = page_data.get(key, "N/A")
            if isinstance(value, list):  # Se houver múltiplos valores, converte para uma string
                row[key] = ", ".join(value)
            else:
                row[key] = value

        # Adiciona o dicionário formatado à lista de dados
        table_data.append(row)

    # Converte os dados em um DataFrame do pandas
    df = pd.DataFrame(table_data)
    return df

def save_table_to_file(dataframe, output_file):
    date_now = date.today()
    try:
        # Salva o DataFrame em um arquivo Excel
        return dataframe.to_excel( f"{date_now}-" + output_file, index=False, sheet_name="Base de dados")
        # logging.info(f"Dados salvos com sucesso no arquivo Excel: {output_file}")
    except Exception as e:
        logging.error(f"Erro ao salvar o arquivo Excel: {e}")

def tariffs_grouped(
    list_input_files=None,
    references_dict= None,
    name_output_file="ArquivosExtraidos.xlsx",
    pages_to_extract=None,
    max_pages=None,
    start_page=1
    ):
    
    if list_input_files is None:
        return "Nenhum Arquivo de Entrada fornecido."
    else:
        try:
            # Extração de dados do PDF
            extracted_data = extract_references_from_pdfs(
                list_input_files, references_dict, start_page=start_page, max_pages=max_pages, pages_to_extract=pages_to_extract
            )
            df = create_table(extracted_data, references_dict)
            logging.info(f"Dados salvos com sucesso no arquivo Excel: {name_output_file}")
            file_save = save_table_to_file(df, name_output_file)
            return file_save
        except Exception as e:
            logging.error(f"Erro ao extrair referências dos PDFs: {e}")
            return None  # Ou um valor padrão