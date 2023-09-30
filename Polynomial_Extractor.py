"""
    No contexto desse código, o polinômio interpolador é usado pra recuperação de informações de um cofre,
    e a verificação da correção dos dados recuperados por meio do CRC (Cyclic Redundancy Check). O polinômio interpolador
     é usado para estimar os valores originais dos dados a partir dos pontos de dados conhecidos e, em seguida, 
     verificar se o CRC corresponde ao valor calculado.

     
     Polynomial Extractor extracts a polynomial from points with interpolation
    It also provides methods to verify if the extracted polynomial (secret) is correct using CRC or Hash

    interpolate_lagrange_poly_in_field by user6655984 on StackOverflow
    https://stackoverflow.com/questions/48065360/interpolate-polynomial-over-a-finite-field
"""

from functools import reduce
from bitstring import BitArray
import binascii
from itertools import combinations
from random import shuffle, sample
from math import factorial

import Constants
from Vault import Vault
from Galois.Poly_Ring import PolyRing
from Galois.Galois_Converter import GaloisConverter
from Galois.Galois_Field import GF


class PolynomialExtractor:
    def __init__(self, gf_exp):
        """
        Inicializa o extrator de polinômios com o expoente do campo Galois.
        :param gf_exp: O expoente do campo Galois, que define o tamanho do campo.
        """
        self.gf_exp = gf_exp
        self.K = GF(2, gf_exp)

    def extract_polynomial_gf_2(self, X, Y):
        """ 
        Extrai um polinômio a partir de X e Y usando interpolação de Lagrange sobre o campo K = GF(2^m).
        :param X: As coordenadas x dos pontos.
        :param Y: As coordenadas y dos pontos.
        :returns: Os coeficientes do polinômio interpolador.
        """
        poly = self.interpolate_lagrange_poly_in_field(X, Y)
        return GaloisConverter.convert_gf_2_list_to_int_list(poly, self.gf_exp)

    def interpolate_lagrange_poly_in_field(self, X, Y):
        """ 
        Interpola um polinômio usando interpolação de Lagrange sobre o campo K.
        :param X: As coordenadas x dos pontos.
        :param Y: As coordenadas y dos pontos.
        :returns: O polinômio interpolador no formato de coeficientes [1, 0, 0, ...].
        """
        R = PolyRing(self.K)
        poly = [[]]
        for j, y in enumerate(Y):
            Xe = X[:j] + X[j + 1:]
            numerator = reduce(lambda p, q: R.mul(p, q), ([[1], self.K.sub([], x)] for x in Xe))
            denominator = reduce(lambda x, y: self.K.mul(x, y), (self.K.sub(X[j], x) for x in Xe))
            poly = R.add(poly, R.mul(numerator, [self.K.mul(y, self.K.inv(denominator))]))
        return poly

    @staticmethod
    def check_crc_in_poly(poly, degree, crc_length, secret_length):
        """ 
        Extrai uma sequência de bits a partir dos coeficientes do polinômio e verifica se o CRC está correto.
        :param poly: A lista de coeficientes do polinômio.
        :param degree: O grau do polinômio.
        :param crc_length: O comprimento do CRC em bits.
        :param secret_length: O comprimento do segredo em bits.
        :returns: True se o CRC na codificação do polinômio (segredo) estiver correto, False caso contrário.
        """
        poly = poly[len(poly) - (degree + 1):]
        result = BitArray()
        assert (crc_length + secret_length) % (degree + 1) == 0
        coefficient_length = (crc_length + secret_length) // (degree + 1)
        for coefficient in poly:
            if coefficient.bit_length() > coefficient_length:
                return False
            result.append(BitArray(uint=coefficient, length=coefficient_length))
        crc_code = result[-crc_length:]
        extracted_crc = crc_code.uint
        secret = result[:-crc_length]
        calculated_crc = binascii.crc32(secret.bytes)
        return extracted_crc == calculated_crc

    def interpolate_and_check_crc(self, vault: Vault, degree: int, crc_length, secret_length, log_dict,
                                  echo=False):
        """ 
        Obtém os pontos candidatos dos cofres, interpola em subconjuntos e verifica o CRC.
        :param vault: O cofre decodificado.
        :param degree: O grau do polinômio interpolador.
        :param crc_length: O comprimento do CRC.
        :param secret_length: O comprimento do segredo.
        :param log_dict: Dicionário para registrar informações (quantidade de subconjuntos avaliados se o CRC corresponder).
        :param echo: Se True, imprime mensagens intermediárias no console.
        :returns: True se houver correspondência, False caso contrário.
        """
        def generate_all_subsets_version(candidate_tuples):
            subsets = list(combinations(candidate_tuples, degree + 1))
            shuffle(subsets)
            if echo:
                print('Total de {} minutiae candidatas e {} subconjuntos encontrados'.format(
                    len(candidate_tuples), len(subsets)
                ))
            log_dict['total_subsets'] = len(subsets)

            for i, subset in enumerate(subsets, 1):
                if echo:
                    print('Interpolando subconjunto #{}...'.format(i))
                X, Y = list(zip(*subset))
                X = GaloisConverter.convert_int_list_to_gf_2_list(X, gf_exp)
                Y = GaloisConverter.convert_int_list_to_gf_2_list(Y, gf_exp)
                poly = self.extract_polynomial_gf_2(X, Y)
                if echo:
                    print('Polinômio secreto interpolado: {}'.format(poly))
                if PolynomialExtractor.check_crc_in_poly(poly, degree, crc_length, secret_length):
                    log_dict['evaluated_subsets'] = i
                    if echo:
                        print('Correspondência encontrada com subconjuntos avaliados: {}'.format(i))
                    return True
                else:
                    if echo:
                        print('Infelizmente, falha na verificação do CRC no polinômio interpolado acima')
            if echo:
                print('Falha em todas as verificações de CRC dos polinômios\n')
            log_dict['evaluated_subsets'] = -1
            return False

        def evaluate_random_subsets(candidate_tuples):
            n = len(candidate_tuples)
            k = degree + 1
            try:
                max_threshold = factorial(n) // factorial(k) // factorial(n - k)
            except ValueError:
                max_threshold = 0

            log_dict['total_subsets'] = max_threshold

            for i in range(max_threshold):
                if echo:
                    print('Interpolando subconjunto #{}...'.format(i))
                subset = sample(candidate_tuples, k)
                X, Y = list(zip(*subset))
                X = GaloisConverter.convert_int_list_to_gf_2_list(X, gf_exp)
                Y = GaloisConverter.convert_int_list_to_gf_2_list(Y, gf_exp)
                poly = self.extract_polynomial_gf_2(X, Y)
                if echo:
                    print('Polinômio secreto interpolado: {}'.format(poly))
                if PolynomialExtractor.check_crc_in_poly(poly, degree, crc_length, secret_length):
                    log_dict['evaluated_subsets'] = i
                    if echo:
                        print('Correspondência encontrada com subconjuntos avaliados: {}'.format(i))
                    return True
                else:
                    if echo:
                        print('Infelizmente, falha na verificação do CRC no polinômio interpolado acima')
            if echo:
                print('Falha em todas as verificações de CRC dos polinômios\n')
            log_dict['evaluated_subsets'] = -1
            return False

        gf_exp = self.gf_exp

        candidate_vault_tuples = set(zip(vault.vault_original_minutiae_rep, vault.vault_function_points_rep))
        if len(candidate_vault_tuples) > Constants.SUBSET_EVAL_THRES or Constants.RANDOM_SUBSET_EVAL:
            log_dict['subset_eval_random'] = True
            return evaluate_random_subsets(candidate_vault_tuples)
        else:
            log_dict['subset_eval_random'] = False
            return generate_all_subsets_version(candidate_vault_tuples)
