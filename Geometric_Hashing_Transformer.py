'''Esse código implementa um conjunto de classes relacionados à transformação e 
manipulação de minutias (pontos característicos) de impressões digitais de hashing geométrico. 

1. `GHTransformer`:
   - Gera uma tabela de hashing geométrica com base em pares de elementos do vault, convertendo 
   a representação das minutias para MinutiaNBIS_GH.
   - Gera um elemento de tabela de verificação com base em minutias de sonda e uma base.
   - Converte uma lista de minutiae MinutiaNBIS em MinutiaNBIS_GH.
   - Transforma uma minutia em uma nova base, permitindo que seja fora dos limites da minutia original.
   - Transforma uma lista de minutiae em uma nova base.

2. `GHElementEnrollment`:
   - Representa um elemento da tabela de hash geométrica para inscrição usando o vault.
   - Armazena a base e as minutias transformadas em relação a essa base.
   - Permite salvar representações em um banco de dados.

3. `GHElementVerification`:
   - Representa um elemento da tabela de hash geométrica para verificação usando a impressão de sonda.
   - Armazena a base e as minutiae transformadas em relação a essa base.
   
'''
import math
from Minutia import MinutiaNBIS_GH
from Minutia_Converter import MinutiaConverter

class GHTransformer:
    @staticmethod
    def generate_enrollment_table(vault_element_pairs):
        """
        Gera uma tabela de hashing geométrica com pares de elementos do vault
        convertendo a representação de minutia para MinutiaNBIS_GH
        :param vault_element_pairs: lista de tuplas VaultElements: (minutia, mapeamento polinomial da minutia)
        :returns tabela de hashing geométrica como lista de GHElementEnrollment
        """
        geom_table = []
        # Lista de MinutiaNBIS_GH
        minutiae_list = []
        function_points = []
        m_conv = MinutiaConverter()
        for element in vault_element_pairs:
            minutia_uint = element.x_rep
            minutia = m_conv.get_minutia_from_uint(minutia_uint)
            minutiae_list.append(MinutiaNBIS_GH.convert_from_MinutiaNBIS(minutia))
            function_points.append(element.y_rep)

        assert len(minutiae_list) == len(vault_element_pairs)
        for basis in minutiae_list:
            # Os índices de minutiae_list em GHElementEnrollment são os mesmos que vault_element_pairs
            geom_table.append(GHElementEnrollment(basis, minutiae_list, function_points))
        return geom_table

    @staticmethod
    def generate_verification_table_element(basis, minutiae_list):
        """
        Gera um elemento de tabela de verificação a partir de minutiae de sonda e base
        :param basis: base para transformar minutiae de sonda
        :param minutiae_list: lista de minutiae (Minutia_NBIS_GH)
        :return: elemento de tabela de verificação
        """
        return GHElementVerification(basis, minutiae_list)

    @staticmethod
    def convert_list_to_MinutiaNBIS_GH(minutiae_list):
        """
        Converte uma lista de MinutiaNBIS para MinutiaNBIS_GH
        :return: lista de MinutiaNBIS_GH
        """
        result = []
        for minutia in minutiae_list:
            result.append(MinutiaNBIS_GH.convert_from_MinutiaNBIS(minutia))
        return result

    @staticmethod
    def transform_minutia_to_basis(m_basis: MinutiaNBIS_GH, m: MinutiaNBIS_GH):
        """
        Transforma uma MinutiaNBIS_GH para uma nova base
        (cuidado: a minutia transformada pode estar fora dos limites da minutia original!)
        :param m_basis: Minutia usada como base como MinutiaNBIS_GH
        :param m: Minutia a ser transformada como MinutiaNBIS_GH
        :return: MinutiaNBIS_GH transformada
        """
        x_diff = m.x - m_basis.x
        y_diff = m.y - m_basis.y
        cos_basis_theta = math.cos(math.radians(m_basis.theta))
        sin_basis_theta = math.sin(math.radians(m_basis.theta))
        x_transformed = int(round(x_diff * cos_basis_theta + y_diff * sin_basis_theta))
        y_transformed = int(round(-x_diff * sin_basis_theta + y_diff * cos_basis_theta))
        theta_diff = m.theta - m_basis.theta
        theta_transformed = theta_diff if theta_diff >= 0 else theta_diff + 360

        return MinutiaNBIS_GH(x_transformed, y_transformed, theta_transformed)

    @staticmethod
    def transform_minutiae_to_basis(basis, minutiae_list):
        """
        Transforma todas as minutiae na lista para a base
        :param basis: Minutia usada como base como MinutiaNBIS_GH
        :param minutiae_list: lista de MinutiaNBIS_GH
        :return: lista de MinutiaNBIS_GH transformada
        """
        transformed_minutiae_list = []
        for m in minutiae_list:
            transformed_minutiae_list.append(GHTransformer.transform_minutia_to_basis(basis, m))
        return transformed_minutiae_list

class GHElementEnrollment:
    """ Elemento da tabela de hash geométrica para inscrição usando o vault """
    def __init__(self, basis, minutiae_list, function_points, save_to_db=False):
        """
        :param basis: Minutia usada como base como MinutiaNBIS_GH
        :param minutiae_list: lista de MinutiaNBIS_GH
        """
        self.basis = basis
        self.transformed_minutiae_list = GHTransformer.transform_minutiae_to_basis(self.basis, minutiae_list)

        if save_to_db:
            # Representações a serem armazenadas no banco de dados
            m_conv = MinutiaConverter()
            self.basis_rep = m_conv.get_uint_from_minutia(self.basis, non_negative=False)
            self.minutiae_rep = []
            for m in self.transformed_minutiae_list:
                self.minutiae_rep.append(m_conv.get_uint_from_minutia(m, non_negative=False))
            self.function_points_rep = function_points

    def __str__(self):
        return '(Base:\n' \
            'x = {}\n' \
            'y = {}\n' \
            'theta = {}\n' \
            '#Minutiae:' \
            '{})'.format(self.basis.x, self.basis.y, self.basis.theta, len(self.transformed_minutiae_list))

    def __repr__(self):
        return '{}(Base: ({}, {}, {}))'.format(
            self.__class__.__name__, self.basis.x, self.basis.y, self.basis.theta
        )

class GHElementVerification:
    """ Elemento da tabela de hash geométrica para verificação usando a impressão de sonda """
    def __init__(self, basis, minutiae_list):
        """
        :param basis: Minutia usada como base como MinutiaNBIS_GH
        :param minutiae_list: lista de MinutiaNBIS_GH
        """
        self.basis = basis
        self.transformed_minutiae_list = GHTransformer.transform_minutiae_to_basis(self.basis, minutiae_list)

    def __str__(self):
        return '(Base:\n' \
               'x = {}\n' \
               'y = {}\n' \
               'theta = {}\n' \
               '#Minutiae:' \
               '{})'.format(self.basis.x, self.basis.y, self.basis.theta, len(self.transformed_minutiae_list))

    def __repr__(self):
        return '{}(Base: ({}, {}, {}))'.format(
            self.__class__.__name__, self.basis.x, self.basis.y, self.basis.theta
        )
