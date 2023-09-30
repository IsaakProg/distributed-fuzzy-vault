# Distributed Fuzzy Vault

## Repositório Recompilado, Comentado e Traduzido para PT-BR

Este repositório aborda um conjunto de ferramentas chamado NBIS (Sistema Nacional de Informação Biométrica), desenvolvido pelo governo dos Estados Unidos para processamento e análise de informações biométricas. Para que esse programa funcione, é necessário uma versão específica de uma biblioteca chamada libpng (Portable Network Graphics), usada para manipular imagens PNG (Portable Network Graphics) e fundamental em muitos programas de processamento de imagens.

No entanto, ao tentar compilar o código-fonte com uma versão mais recente do libpng, ocorrem erros de compatibilidade, pois os novos componentes das versões mais recentes do libpng não são compatíveis com os antigos.

Basicamente, o que esta API faz é criar um sistema de autenticação biométrica que utiliza o conceito de um "fuzzy vault" como componente central. Esta tese apresenta um sistema de autenticação distribuído que armazena os dados de impressão digital de forma segura em um servidor ou infraestrutura de nuvem, com respeito à privacidade.

## Parâmetros Obrigatórios:

### Implementação de "Fuzzy Vault"

Este pacote contém o código principal da tese de mestrado, incluindo o algoritmo de "fuzzy vault" e a aplicação distribuída de "fuzzy vault". Várias funções de teste podem ser encontradas em `Tests.py`. `Plot_Minutiae.py` pode ser usado para visualizar minutias com arquivos .xyt, que é o formato de saída do detector de minutias MINDTCT do NBIS. Consulte o relatório da tese de mestrado para obter mais informações sobre a biblioteca e o código usados para habilitar o algoritmo de "fuzzy vault" e a aplicação distribuída de "fuzzy vault".

### Algoritmo de "Fuzzy Vault"

O algoritmo principal é executado em `Main.py`. As constantes e parâmetros para o algoritmo de "fuzzy vault" são armazenados em `Constants.py` e podem ser alterados de acordo com os experimentos desejados. Consulte o relatório da tese de mestrado para obter mais informações. O banco de dados de impressões digitais de entrada com arquivos .xyt é armazenado em `/input_images`. Todas as imagens de entrada precisam ser convertidas em arquivos .xyt antes de executar o algoritmo. Os registros normais do algoritmo são armazenados em `/out`. A última parte em `Constants.py` é usada para o registro de testes completos do banco de dados (executados por todo o banco de dados com dois protocolos diferentes descritos abaixo), onde a pasta é definida onde os registros devem ser gravados.

O algoritmo atualmente está configurado para ser executado no banco de dados FVC2006 DB 2A ou 2B. Isso pode ser alterado com a flag `DATABASE_2A_FLAG` em `Constants.py`, onde o valor `True` indica que a execução é no DB 2A e no DB 2B quando o valor é `False`. O código é especificamente projetado para os dois bancos de dados com o número de dedos e capturas alinhados para comparação. `SPLIT_COMPUTATION` pode ser definido como `True` em `Constants.py` para executar o algoritmo em partes diferentes do banco de dados FVC2006 DB 2A. `FINGER_START` e `FINGER_END` indicam quais dedos são usados como galeria. Os modelos de prova a serem comparados são sempre o banco de dados inteiro (1.680 imagens). Existem dois protocolos para executar o banco de dados: 1x1 e protocolo FVC. Consulte o relatório da tese de mestrado para obter mais informações.

O algoritmo de "fuzzy vault" deve ser executado com o PyPy3, pois é muito mais rápido do que o Python3. Para executar o algoritmo, execute o `Main.py` com um número inteiro positivo como parâmetro. Se o número inteiro for 0, o algoritmo será executado em todo o banco de dados. Caso contrário, apenas correspondências entre XYT_GALLERY e XYT_PROBE serão conduzidas, como definido em `Constants.py`. Nesse caso, o número inteiro positivo representa quantas correspondências são conduzidas com esses dois modelos.

## Processos da Prova de Conceito:

1. **Registro do Usuário:**
   - No processo de registro, o usuário fornece uma ou várias impressões digitais que serão usadas para criar um "fuzzy vault". Essas impressões digitais são capturadas por um dispositivo de sensor de impressão digital (por exemplo, um sensor Adafruit FPS).

2. **Extração de Minutiae:**
   - As impressões digitais fornecidas pelo usuário são processadas para extrair as minutiae. Minutiae são pontos de referência específicos nas impressões digitais, como bifurcações e terminações.

3. **Geração do Fuzzy Vault:**
   - O "fuzzy vault" é criado a partir das minutiae extraídas. Ele é projetado para ser uma estrutura matemática que combina as minutiae do usuário com pontos fictícios (também chamados de chaff points) de forma que seja difícil para um adversário distinguir os pontos genuínos dos fictícios.
   - O grau polinomial (n) é um parâmetro importante aqui. Ele determina quantas minutiae genuínas precisam ser correspondidas para decodificar o "fuzzy vault." Um grau polinomial mais alto torna o processo de correspondência mais conservador e seguro, mas pode aumentar o tempo de execução.

4. **Armazenamento do Fuzzy Vault:**
   - O "fuzzy vault" gerado é armazenado de forma segura, pois ele representa a chave de autenticação do usuário.

5. **Autenticação do Usuário:**
   - Quando um usuário deseja se autenticar, ele fornece uma nova impressão digital.

6. **Extração de Minutiae da Nova Impressão Digital:**
   - A nova impressão digital é processada para extrair suas minutiae.

7. **Correspondência de Minutiae:**
   - As minutiae da nova impressão digital são comparadas com as minutiae armazenadas no "fuzzy vault." Isso envolve uma correspondência das características da impressão digital atual com as características armazenadas no "fuzzy vault."

8. **Decodificação do Fuzzy Vault:**
   - Se a correspondência das minutiae atingir um limite predefinido

 (determinado por limiares de correspondência), o "fuzzy vault" é decodificado.
   - A decodificação envolve a aplicação de técnicas matemáticas, como a interpolação de polinômios, para reconstruir os pontos genuínos a partir dos pontos fictícios do "fuzzy vault."

9. **Verificação de Autenticidade:**
   - A autenticidade do usuário é verificada comparando os pontos genuínos reconstruídos com os dados originais do usuário armazenados no "fuzzy vault."
   - Se a verificação for bem-sucedida, o usuário é autenticado com sucesso.

O "fuzzy vault" é projetado para garantir que a autenticação seja segura, mesmo se um adversário tentar decodificar o "fuzzy vault" usando minutiae fictícias. O grau polinomial e outros parâmetros são ajustados para equilibrar a segurança com o desempenho do sistema. Isso torna o processo de autenticação biométrica robusto e adequado para uma variedade de casos de uso.
