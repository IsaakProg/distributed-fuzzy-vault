'''Resumindo, o arquivo `app.py` é um aplicativo Python que realiza algumas funcoes de impressao digital:

1. Inicialização e Boas-Vindas
2. Menu de Opções: Ele apresenta um menu de opções para o usuário escolher entre:
   - Cadastrar uma nova impressão digital.
   - Verificar uma impressão digital.
   - Sair do aplicativo.

3.Ele permite que o usuário capture novas impressões digitais usando o sensor
 Adafruit (Adafruit_Handler.py) e garante que haja informações suficientes capturadas.

4.Ele executa o processo de cadastro de uma nova impressão digital, que envolve a geração de um
 segredo (Chave secreta), a criação de um "vault" e o armazenamento dessas informações em um banco de dados Cosmos DB.

5.Ele verifica uma impressão digital em relação aos dados armazenados no banco de dados Cosmos DB

6.Registro e Log:Ele registra informações detalhadas sobre o tempo de execução e o resultado da ação 
(sucesso ou falha).

7.Ele remove arquivos temporários gerados durante o processo de captura e decodificação da impressão digital.

'''

# Importação de bibliotecas necessárias
from subprocess import Popen, PIPE  # Para executar processos externos
import time  # Para medições de tempo
import os  # Para operações relacionadas ao sistema de arquivos
import Constants  # Importa um módulo (arquivo) chamado Constants
from Main import initialize_log_dict, generate_smallest_secret, generate_vault, verify_secret, store_in_cosmos_db, retrieve_from_cosmos_db
from DBHandler import DBHandler
from Adafruit_Handler import AdafruitHandler

# Função principal que executa o aplicativo
def run_app(renew_log=False):
    print('========================================================================')
    print(APP_WELCOME)  # Exibe mensagem de boas-vindas definida em algum lugar
    print('========================================================================')
    print('\n')

    # Calcula o comprimento do segredo com base no grau do polinômio e na CRC
    secret_length = len(generate_smallest_secret(POLY_DEGREE, CRC_LENGTH, min_size=128, echo=False)) * 8

    # Inicializa o log se não existir e se renovar o log estiver ativado
    if not os.path.exists('out'):
        os.makedirs('out')
    if renew_log:
        initialize_app_log(LOG_FILE_APP)

    running = True
    while running:
        # Lista as opções para o usuário
        print(APP_CHOOSE_FUNCTION)
        for key in APP_FUNCTIONAILTIES.keys():
            print("%s: %s" % (key, APP_FUNCTIONAILTIES[key]))
        print()

        # Obtém a opção de entrada do usuário
        correct_option = False
        input_option = ''
        while not correct_option:
            input_option = input(APP_DESIRED_OPTION)
            if input_option not in APP_FUNCTIONAILTIES.keys():
                print(APP_OPTION_FALSE)
            else:
                correct_option = True

        # Cria um manipulador de banco de dados
        db_handler = DBHandler()
        # Inicializa um dicionário de log do aplicativo
        app_log_dict = dict()
        initialize_app_log_dict(app_log_dict)

        # Encerra o aplicativo
        if input_option == list(APP_FUNCTIONAILTIES.keys())[2]:
            running = False
            print(APP_BYE)

        # Inscreve uma nova impressão digital
        elif input_option == list(APP_FUNCTIONAILTIES.keys())[0]:
            app_log_dict['action'] = 'ENCODE'
            new_id = get_id()
            app_log_dict['vault_id'] = new_id
            print(APP_SCAN_FP)

            # Captura da impressão digital, recaptura se não houver informações suficientes
            good_fp = False
            capture_time_start = time.time()
            capture_time_end = time.time()
            while not good_fp:
                capture_time_start = time.time()
                good_fp = capture_new_fp_xyt(new_id)
                capture_time_end = time.time()
                if not good_fp:
                    print(APP_RETRY_FP)
            app_log_dict['capture_time'] = round(capture_time_end - capture_time_start, 2)

            action_fp_time = time.time()
            enroll_new_fingerprint(db_handler, new_id, FP_TEMP_FOLDER + FP_OUTPUT_NAME + new_id + '.xyt', app_log_dict)
            print('\n')
            print('Tempo de execução do algoritmo fuzzy vault incluindo DB: {}'.format(round(time.time() - action_fp_time, 2)))
            write_app_log(LOG_FILE_APP, app_log_dict)
            remove_temp_files(new_id)

        # Verifica uma impressão digital
        elif input_option == list(APP_FUNCTIONAILTIES.keys())[1]:
            app_log_dict['action'] = 'DECODE'
            id_to_verify = get_id()
            app_log_dict['vault_id'] = id_to_verify
            print(APP_SCAN_FP)

            # Captura da impressão digital, recaptura se não houver informações suficientes
            good_fp = False
            while not good_fp:
                capture_time_start = time.time()
                good_fp = capture_new_fp_xyt(id_to_verify)
                capture_time_end = time.time()
                if not good_fp:
                    print(APP_RETRY_FP)
            app_log_dict['capture_time'] = round(capture_time_end - capture_time_start, 2)

            action_fp_time = time.time()
            verify_fingerprint(db_handler, id_to_verify, FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_to_verify + '.xyt',
                               secret_length, app_log_dict)
            print('\n')
            print('Tempo de execução do algoritmo fuzzy vault incluindo DB: {}'.format(round(time.time() - action_fp_time, 2)))
            write_app_log(LOG_FILE_APP, app_log_dict)
            remove_temp_files(id_to_verify)

        else:
            print(APP_ERROR)

        print('========================================================================')
        print('\n')
        time.sleep(1)
        db_handler.close_handler()

# Função para obter um ID válido a partir do usuário
def get_id():
    correct_id = False
    new_id = 0
    while not correct_id:
        new_id = input(APP_NEW_ID)
        if new_id.isdigit():
            new_id = int(new_id)
            correct_id = True
        else:
            print(APP_ID_ERROR)
    return str(new_id)

# Função para capturar uma nova impressão digital e verificar se há informações suficientes
def capture_new_fp_xyt(id_number):
    try:
        AdafruitHandler.download_fingerprint(id_number)
    except Exception:
        return False

    run_mindtct(FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number + '.jpg', id_number)

    # Contagem das linhas no arquivo .xyt
    num_lines = sum(1 for _ in open(FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number + '.xyt'))
    if num_lines >= MINUTIAE_POINTS_AMOUNT:
        return True
    else:
        print('Infelizmente, apenas {} minutiae foram encontradas...'.format(num_lines))
        return False

# Função para inscrever uma nova impressão digital
def enroll_new_fingerprint(db_handler, vault_id, xyt_path, app_log_dict):
    encode_time_start = time.time()
    secret_bytes = generate_smallest_secret(POLY_DEGREE, CRC_LENGTH, min_size=128, echo=False)
    print(APP_FV_SECRET)

    log_dict = dict()
    initialize_log_dict(log_dict)

    fuzzy_vault = generate_vault(xyt_path, MINUTIAE_POINTS_AMOUNT, CHAFF_POINTS_AMOUNT, POLY_DEGREE,
                                 secret_bytes, CRC_LENGTH, GF_2_M, log_dict, echo=False)
    print(APP_FV_GENERATED)
    encode_time_end = time.time()
    app_log_dict['action_time'] = round(encode_time_end - encode_time_start, 2)

    try:
        db_time_start = time.time()
        store_in_cosmos_db(db_handler, fuzzy_vault, vault_id)
        db_time_end = time.time()
        app_log_dict['db_time'] = round(db_time_end - db_time_start, 2)
    except Exception as e:
        print('Mensagem de exceção: ' + str(e))
        print('Ocorreu um erro durante o manuseio do banco de dados.')
        app_log_dict['success'] = 'FALHA'
        return
    print(APP_FV_SENT_DB)
    print('\n')
    print(APP_ENROLL_SUCCESS)
    app_log_dict['success'] = 'SUCESSO'
    return

# Função para verificar uma impressão digital
def verify_fingerprint(db_handler, vault_id, xyt_path, secret_length, app_log_dict):
    log_dict = dict()
    initialize_log_dict(log_dict)
    db_time_start = time.time()
    db_vault = retrieve_from_cosmos_db(db_handler, vault_id)
    db_time_end = time.time()
    app_log_dict['db_time'] = round(db_time_end - db_time_start, 2)
    if db_vault:
        decode_time_start = time.time()
        db_vault.create_geom_table()
        success = verify_secret(xyt_path, MINUTIAE_POINTS_AMOUNT, POLY_DEGREE, CRC_LENGTH, secret_length,
                                GF_2_M, db_vault, log_dict, echo=False)
        db_vault.clear_vault()
        decode_time_end = time.time()
        app_log_dict['action_time'] = round(decode_time_end - decode_time_start, 2)
        if success:
            print(APP_VERIFY_SUCCESS)
            app_log_dict['success'] = 'SUCESSO'
            return
        else:
            print(APP_VERIFY_FAILURE)
            app_log_dict['success'] = 'FALHA'
            return
    else:
        print(APP_VERIFY_FAILURE)
        app_log_dict['success'] = 'FALHA'
        return

# Função para executar o comando Mindtct em um arquivo JPG
def run_mindtct(jpg_path, id_number):
    mindtct = Popen(['mindtct', jpg_path, FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number], stdout=PIPE, stderr=PIPE)
    mindtct.communicate()

# Função para remover arquivos temporários gerados pelo Mindtct
def remove_temp_files(id_number):
    process = Popen(['rm', FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number + '*'], stdout=PIPE, stderr=PIPE)
    process.communicate()

# Inicializa um dicionário de log do aplicativo
def initialize_app_log_dict(app_log_dict):
    app_log_dict['action'] = 'codificar ou decodificar'
    app_log_dict['capture_time'] = 0
    app_log_dict['db_time'] = 0
    app_log_dict['action_time'] = 0
    app_log_dict['success'] = 'FALHA'
    app_log_dict['vault_id'] = 0

# Inicializa um arquivo de log do aplicativo
def initialize_app_log(log_path):
    open(log_path, 'w+').close()
    with open(log_path, 'a') as log:
        log.write('action;'
                  'action time [s];'
                  'capture time [s];'
                  'db time [s];'
                  'success;'
                  'date;'
                  'time;'
                  'vault id\n')

# Escreve uma linha no arquivo de log do aplicativo
def write_app_log(log_path, app_log_dict):
    datetime_now = datetime.datetime.now()
    date_now = datetime_now.strftime("%Y%m%d")
    time_now = datetime_now.strftime("%H%M")
    action = app_log_dict['action']
    action_time = app_log_dict['action_time']
    capture_time = app_log_dict['capture_time']
    db_time = app_log_dict['db_time']
    success = app_log_dict['success']
    vault_id = app_log_dict['vault_id']
    with open(log_path, 'a') as log:
        log.write('{};{};{};{};{};{};{};{}\n'.format(action, action_time, capture_time, db_time, success,
                                                     date_now, time_now, vault_id))

# Executa o aplicativo quando o arquivo é executado diretamente
if __name__ == '__main__':
    run_app(renew_log=False)
