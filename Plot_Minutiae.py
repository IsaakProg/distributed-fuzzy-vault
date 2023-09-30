'''Esse código faz o seguinte:

1Importa várias classes e módulos necessários para o processamento de minutias.

2Define os nomes dos arquivos de imagem de galeria e sonda.

3Define uma função plot_minutiae que extrai minutias das imagens de sonda e galeria,
 as converte para o formato GH (Geometric Hashing) se a opção GH estiver ativada e as plota em um gráfico.
 
4Cria instâncias de classes como MinutiaeExtractor e MinutiaePlotter para extrair minutias e plotá-las.

5Se a opção GH estiver ativada, define minutias de base para sonda e galeria, transforma as minutias extraídas 
para essas bases e plota as minutias transformadas em cores diferentes.

6Exibe o gráfico resultante das minutias.

7Chama a função plot_minutiae com a opção GH desativada quando o script é executado.'''
from Plotter import MinutiaePlotter
from Minutiae_Extractor import MinutiaeExtractor
from Minutia import MinutiaNBIS_GH
from Geometric_Hashing_Transformer import GHTransformer
import Constants


GALLERY_IMAGE = '2_6'
PROBE_IMAGE = '4_2'
XYT_GALLERY_PATH = 'input_images/' + 'FVC2006_DB_2B/' + GALLERY_IMAGE + '.xyt'
XYT_PROBE_PATH = 'input_images/' + 'FVC2006_DB_2B/' + PROBE_IMAGE + '.xyt'


def plot_minutiae(gh=False):
    nbis_minutiae_extractor = MinutiaeExtractor()
    probe_list = []
    for m in nbis_minutiae_extractor.extract_minutiae_from_xyt(XYT_PROBE_PATH)[0:Constants.MINUTIAE_POINTS_AMOUNT]:
        probe_list.append(MinutiaNBIS_GH.convert_from_MinutiaNBIS(m))
    gallery_list = []
    for m in nbis_minutiae_extractor.extract_minutiae_from_xyt(XYT_GALLERY_PATH)[0:Constants.MINUTIAE_POINTS_AMOUNT]:
        gallery_list.append(MinutiaNBIS_GH.convert_from_MinutiaNBIS(m))
    plotter = MinutiaePlotter
    if gh:
        probe_basis = MinutiaNBIS_GH(-200, 14, 67)
        plotter.plot_minutiae(GHTransformer.transform_minutiae_to_basis(probe_basis, probe_list), 1, 'ro')
        gallery_basis = MinutiaNBIS_GH(-253, 23, 67)
        plotter.plot_minutiae(GHTransformer.transform_minutiae_to_basis(gallery_basis, gallery_list), 1, 'bo')
    else:
        plotter.plot_minutiae(probe_list, 1, 'ro')
        plotter.plot_minutiae(gallery_list, 1, 'bo')
    plotter.show_plot()


if __name__ == '__main__':
    plot_minutiae(False)
