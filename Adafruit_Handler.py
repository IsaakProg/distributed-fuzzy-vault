'''
ADAFRUIT E O SENSOR DE IMPRESSÃO DIGITAL QUE VAI RODAR JUNTO COM O RASPBERRY PI

O que o arquivo faz é o seguinte:

1.Inicializa o sensor de impressão digital Adafruit com configurações específicas.
2.Verifica se a senha do sensor está correta e, se não estiver, gera uma exceção.
3.Aguarda até que uma impressão digital seja lida com sucesso pelo sensor.
4.Ativa e desativa um LED no sensor para indicar o processo de captura da impressão digital.
5.Salva a impressão digital capturada como uma imagem BMP.
6.Converte a imagem BMP em uma imagem JPG.
7.Salva a imagem JPG no diretorio CONSTANTS.PY.
8.Retorna informações sobre o sucesso da operação, incluindo o nome da imagem capturada e o local onde ela foi salva.

Esse arquivo lida com a captura e o processamento das impressões digitais usando o sensor Adafruit 
e salva as imagens resultantes em um diretório . 
Ele também inclui verificações de erros.
'''

# Importação das bibliotecas necessárias
from Pyfingerprint import PyFingerprint  # Para interagir com o sensor de impressão digital Adafruit
import os  # Para operações relacionadas ao sistema de arquivos
from PIL import Image  # Para manipulação de imagens
import Constants  # Importa as constantes definidas no arquivo Constants.py

# Definição da classe AdafruitHandler
class AdafruitHandler:
    @staticmethod
    def download_fingerprint(id_number):
        # Tentativa de iniciar o sensor
        try:
            # Criação de uma instância do sensor com configurações específicas
            f = PyFingerprint('/dev/serial0', 57600, 0xFFFFFFFF, 0x00000000)

            # Verificação da senha do sensor, gerando uma exceção se a senha estiver incorreta
            if not f.verifyPassword():
                raise ValueError('A senha do sensor de impressão digital fornecida está incorreta!')

        except Exception as e:
            # Tratamento de exceção em caso de falha na inicialização do sensor
            print('Não foi possível inicializar o sensor de impressão digital!')
            print('Mensagem de exceção: ' + str(e))
            exit(1)

        # Tentativa de leitura da impressão digital e download da imagem
        try:
            # Geração de um nome para a imagem baseado no Constants.FP_OUTPUT_NAME e no número de identificação
            image_name = Constants.FP_OUTPUT_NAME + str(id_number)

            # Ativação do LED para indicar a captura da impressão digital
            f.turnLEDon()

            print('Aguardando o toque do dedo...')

            # Aguarda até que a impressão digital seja lida com sucesso
            while not f.readImage():
                pass

            print('Fazendo o download da imagem (isso pode levar um tempo)...\n')

            # Desativação do LED após a captura
            f.turnLEDoff()

            # Verificação da existência da pasta de destino para salvar a imagem; criação se não existir
            folder_path = Constants.FP_TEMP_FOLDER
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

            # Geração de um nome para a imagem se image_name for None
            if image_name is None:
                image_name = 'impressao_digital_' + str(len(os.listdir(folder_path)))

            # Salva a imagem como um arquivo BMP
            image_destination_bmp = folder_path + image_name + '.bmp'
            f.downloadImage(image_destination_bmp)

            # Converte e salva a imagem como um arquivo JPG
            img = Image.open(image_destination_bmp)
            image_destination_jpg = folder_path + image_name + '.jpg'
            img.save(image_destination_jpg)

            # Impressão de informações sobre o sucesso da operação, incluindo o nome da imagem capturada e o local de salvamento
            print('A imagem de %s foi salva em %s.' % (image_name, folder_path))
            print('Captura da impressão digital %s finalizada.\n' % image_name)

        except Exception as e:
            # Tratamento de exceção em caso de falha na operação
            print('Operação falhou!')
            raise Exception('Ocorreu um erro interno no manuseio do sensor Adafruit.')

# Fim da classe AdafruitHandler
