import PyPDF2
import re
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Função para procurar o valor com uma referência específica
def search_value(regex, text):
    if regex:
        match = re.search(regex, text)
        if match:
            return match.group(0)  # Retorna o valor do grupo capturado
    return None


# Função para procurar todas as referências no texto
def search_references(references_dict, text):
    found_values = {}
    for key, regex in references_dict.items():
        found_value = search_value(regex, text)
        if found_value:
            found_values[key] = found_value
    return found_values


# Função para processar todos os arquivos PDF e encontrar valores
def extract_references_from_pdfs(input_files, references_dict):
    extracted_data = []
    for file in input_files:
        try:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text = page.extract_text()
                found_values = search_references(references_dict, text)
                if found_values:
                    extracted_data.append(found_values)
        except Exception as e:
            logging.error(f"Erro ao processar o arquivo {file}: {e}")
    return extracted_data


# Função principal
def main():
    input_files = ["fatura.pdf"]

    # Dicionário com as referências e expressões regulares
    references_dict = {
        "Referente ao ano": r"Atedqwdwqdqnção",
    }

    # Extrair os valores
    extracted_data = extract_references_from_pdfs(input_files, references_dict)
    print(extracted_data)

    # Exibir os resultados
    # for index, data in enumerate(extracted_data):
    #     logging.info(f"Dados extraídos da página {index + 1}: {data}")


if __name__ == "__main__":
    main()
