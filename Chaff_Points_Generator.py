'''O terceiro arquivo é o "ChaffPointsGenerator.py". Ele serve para gerar pontos falsos 
de forma aleatória 

No contexto do Fuzzy Vault , os chaff points são uns pontos adicionais que são incluídos no conjunto de dados biométricos
 armazenados no cofre, juntamente com os pontos genuínos, com o objetivo de confundir os invasores.

Os pontos biométricos genuínos (por exemplo, as minutias) 
são usados para gerar uma chave secreta que é usada para criptografar ou descriptografar informações. 
Para aumentar a segurança desse processo, os chaff points são adicionados ao conjunto de minutias genuínas antes 
que a chave seja gerada.

'''

import random  # Importa o módulo random para gerar números aleatórios
from Minutia import MinutiaNBIS  # Importa uma classe chamada MinutiaNBIS do arquivo Minutia.py
import Constants  # Importa o modulo Constants.py

# Classe ChaffPointsGenerator responsável por gerar chaff points
class ChaffPointsGenerator:
    @staticmethod
    def generate_chaff_points_randomly(amount, genuine_minutiae, smallest_minutia_rep, minutia_converter):
        """ Cria a quantidade desejada de pontos chaff (Minutias)
        Os pontos chaff precisam estar a uma distância especificada de todas as outras minutias genuínas e pontos chaff
          :retorna uma lista de Minutia geradas aleatoriamente """
        

        chaff_points_list = []  # Inicializa uma lista vazia para armazenar os chaff points
        all_vault_points = genuine_minutiae.copy()  # Cria uma cópia das minutias genuínas existentes
        for _ in range(amount):  # Executa o loop para criar a quantidade desejada de chaff points
            plausible_minutia = False
            while not plausible_minutia:
                # Gera coordenadas aleatórias para o chaff point
                x_random = random.randrange(MinutiaNBIS.X_MIN, MinutiaNBIS.X_MAX)
                y_random = random.randrange(MinutiaNBIS.Y_MIN, MinutiaNBIS.Y_MAX)
                theta_random = random.randrange(MinutiaNBIS.THETA_MIN, MinutiaNBIS.THETA_MAX)
                quality_random = random.randrange(MinutiaNBIS.QUALITY_MIN, MinutiaNBIS.QUALITY_MAX)
                chaff_point = MinutiaNBIS(x_random, y_random, theta_random, quality_random)

                # Verifica se a representação da minutia é maior ou igual à metade da menor representação genuína
                if minutia_converter.get_uint_from_minutia(chaff_point) >= (smallest_minutia_rep // 2):
                    too_close = False
                    for minutia in all_vault_points:
                        # Verifica se o chaff point está muito próximo de outras minutias genuínas ou chaff points
                        if chaff_point.distance_to(minutia) <= Constants.POINTS_DISTANCE:
                            too_close = True
                            break
                    if not too_close:
                        chaff_points_list.append(chaff_point)
                        all_vault_points.append(chaff_point)
                        plausible_minutia = True
        return chaff_points_list  # Retorna a lista de chaff points gerados aleatoriamente

