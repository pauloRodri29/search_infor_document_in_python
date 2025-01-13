import logging
from extraindo import tariffs_grouped
def main(
        list_input_files=["files/fatura.pdf"],
        references_dict= {
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
        "Complemento": r"Complemento:\s+([^\n]+)(?=\s+Fatura|$)",
        "N° Fatura": r"Fatura:\s+(\d+)",
        "Classe Principal": r"Classe Principal\s*[^0-9]*\s*(\d+)",
        "Classe de Consumo": r"Classe de Consumo(?:.*?\n)*?.*?(?:\d+\n)(\d+)",
        "Tensão": r"(?<=\bTensão\b)(?:\D*\d+){2}\s*(\S+)",
        "Fase": r"(?<=\bFase\b)(?:\D*\d+){3}\D*(\S+)",
        "Data Fatura": r"(?<=\bData Fat\b)(?:\D*\d+){5}\D*(\S+)",
        "Dias Fatura": r"(?<=\bDias Fat\b)(?:\D*\d+){8}\D*(\S+)",
        "Data Leitura Anterior": r"(?<=\bDta\.Leit\.Ant\b|\bDat\.Leit\.Ant\b)(?:\D*\d+){9}\D*(\S+)",
        "Data Leitura Atual": r"(?<=\bDta\.Leit\.Ant\b|\bDat\.Leit\.Ant\b)(?:\D*\d+){12}\D*(\S+)",
        
        # "Reaviso": r"(?<=\bReaviso\b)",
        # "Corte": r"(?<=\bDta\.Leit\.Ant\b|\bDat\.Leit\.Ant\b)(?:\D*\d+){12}\D*(\S+)",
        
        "V.T.: Icms(BaseCalculo)": r"ICMS\s+(?:\D*\d+.+?\d+\n){0}([\d,\.]+)",
        "V.T.: Icms(Aliquota)": r"ICMS\s+(?:\D*\d+.+?\d+\n){1}([\d,\.]+)",
        "V.T.: Icms(Valor)": r"ICMS\s+(?:\D*\d+.+?\d+\n){2}([\d,\.]+)",
        "V.T.: Cofins": r"COFINS\s+(?:\D*\d+.+?\d+\n){0}([\d,\.]+)",
        "V.T.: Cofins(Aliquota)": r"COFINS\s+(?:\D*\d+.+?\d+\n){1}([\d,\.]+)",
        "V.T.: Cofins(Valor)": r"COFINS\s+(?:\D*\d+.+?\d+\n){2}([\d,\.]+)",
        "V.T.: Pis": r"PIS\s+(?:\D*\d+.+?\d+\n){0}([\d,\.]+)",
        "V.T.: Pis(Aliquota)": r"PIS\s+(?:\D*\d+.+?\d+\n){1}([\d,\.]+)",
        "V.T.: Pis(Valor)": r"PIS\s+(?:\D*\d+.+?\d+\n){2}([\d,\.]+)",
        
        # "V.M.: Esp": r"(\bCAT\b)([A-Z])?\b",
        "V.M.: Medidor": r"CAT\s+(?:\D*\d+.+?\d+\n){0}([\d,\.]+)",
        # "V.M.: CTE": r"CAT\s+(?:\D*\d+.+?\d+\n){1}([\d,\.]+)",
        # "V.M.: FP": r"CAT\s+(?:\D*\d+.+?\d+\n){2}([\d,\.]+)",
        # "V.M.: Leitura_Anterior": r"CAT\s+(?:\D*\d+.+?\d+\n){3}([\d,\.]+)",
        # "V.M.: Leitura_Atual": r"CAT\s+(?:\D*\d+.+?\d+\n){4}([\d,\.]+)",
        # "V.M.: Medido": r"CAT\s+(?:\D*\d+.+?\d+\n){5}([\d,\.]+)",
        # "V.M.: Faturado": r"CAT\s+(?:\D*\d+.+?\d+\n){6}([\d,\.]+)",
        
        # "V.F.: Consumo(Quantidade)": r"Consumo\s+(?:)([\d.,]+)[\s\S]*?",
        # "V.F.: Consumo(Preço)": r"Consumo\s+(?:)([\d.,]+)[\s\S]*?",
        # "V.F.: Consumo(Valor)": r"Consumo\s+(?:)([\d.,]+)[\s\S]*?",
        # "Cip-Ilum Pub Pref Munic (Valor)":r"Cip-Ilum Pub Pref Munic\s+([\d\.,]+)",
        # "V.F.: Adcional Bandeira (Valor)": r"Adicional Bandeira\s+([\d\.,]+)",
        # "V.F.: Crédito Prazo Atendimento (Valor)": r"Crédito Prazo Atendimento\s+([\d\.,]+)",
        # "V.F.: Tributo a Reter IRPJ (Valor) ": r"Tributo a Reter IRPJ\s+([\d\.,]+)",
        # "V.F.: Saldo em Aberto (Valor)": r"Saldo em aberto\s+([\d\.,]+)",
    },
    name_output_file="tarifas_agrupadas.xlsx",
    pages_to_extract=None,
    max_pages=None,
    start_page=1
    ):
    
    try:
        # Extração de dados do PDF
        extracted_data = tariffs_grouped(
            list_input_files=list_input_files,
            references_dict=references_dict,
            name_output_file=name_output_file,
            start_page=start_page,
            max_pages=max_pages,
            pages_to_extract=pages_to_extract
        )
        return extracted_data
    except Exception as e:
        logging.error(f"Erro ao extrair referências dos PDFs: {e}")
        return None
    
if __name__ == "__main__":
    main()