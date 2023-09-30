"""
    Aqui e onde a magica acontece e onde o rojas me pergunta de onde sao extraidos as features dos arquivos(templates)
    (eles usam o NBIS para extrair as features dos arquivos .xyt)
"""


from Minutia import MinutiaNBIS  # Importa a classe MinutiaNBIS da biblioteca Minutia

class MinutiaeExtractor:
    NBIS_FORMAT = 1  # Define uma constante para o formato NBIS (pode ser usado como padrão)

    def __init__(self, extractor_format=NBIS_FORMAT):
        self.extractor_type = extractor_format  # Inicializa o tipo de extrator com o formato especificado

    def extract_minutiae_from_xyt(self, file_path):
        """ Extrai minutias de um arquivo de impressão digital .xyt
        :returns uma lista de Minutia com ordem descendente de qualidade """

        minutiae_list = []  # Inicializa uma lista vazia para armazenar as minutias extraídas
        with open(file_path, 'r') as file:  # Abre o arquivo .xyt em modo de leitura
            for line in file:  # Itera sobre as linhas do arquivo
                x, y, theta, quality = line.split(' ')  # Divide a linha em valores de coordenadas e qualidade
                # Cria uma instância da classe MinutiaNBIS com os valores extraídos e adiciona à lista
                minutia = MinutiaNBIS(int(x), int(y), int(theta), int(quality))
                minutiae_list.append(minutia)
        
        # Classifica a lista de minutias com base na qualidade em ordem decrescente
        minutiae_list.sort(key=lambda m: int(m.quality), reverse=True)
        return minutiae_list  # Retorna a lista de minutias extraídas
    
