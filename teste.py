import re

# Texto original extraído do PDF
texto_original = """
CLIENTE:
7876076 - SAAE DE CAXIAS AGUA E ESGOTO
CONTA CONTRATO:
004000012810
Endereço:
STO ANTONIO , 0
Município:
CAXIAS
Bairro:
JOAO VIANA
Referência: 09/2024
Vencimento: 28-10-2024
Documento:
610014004445
Complemento:
SAAE - CAXIAS
Valor:
238291.26
Empresa:
C001-EQUATORIAL MARANHÃO
Local:
CAXIAS
Conj.Contrato: CX29B
Unidade de Leitura: CX29B027
Referência: 09/2024
...
"""

# Função para organizar as informações de forma mais legível
def formatar_texto(texto):
    # Usar expressões regulares para buscar os dados relevantes
    dados = {}
    
    # Buscando os dados do cliente
    dados['Cliente'] = re.search(r"CLIENTE:\s*(.*)", texto)
    dados['Conta Contrato'] = re.search(r"CONTA CONTRATO:\s*(\S+)", texto)
    dados['Endereço'] = re.search(r"Endereço:\s*(.*)", texto)
    dados['Município'] = re.search(r"Município:\s*(.*)", texto)
    dados['Bairro'] = re.search(r"Bairro:\s*(.*)", texto)
    dados['Referência'] = re.search(r"Referência:\s*(.*)", texto)
    dados['Vencimento'] = re.search(r"Vencimento:\s*(.*)", texto)
    dados['Documento'] = re.search(r"Documento:\s*(\S+)", texto)
    dados['Complemento'] = re.search(r"Complemento:\s*(.*)", texto)
    dados['Valor'] = re.search(r"Valor:\s*([\d,.]+)", texto)
    
    # Formatação do resultado
    resultado = []
    for chave, valor in dados.items():
        if valor:
            resultado.append(f"{chave}: {valor.group(1)}")
    
    return '\n'.join(resultado)

# Formatando o texto
texto_formatado = formatar_texto(texto_original)

# Exibindo o resultado
print(texto_formatado)
