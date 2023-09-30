""" Esse código é uma classe que lida com operações de banco de dados no CosmosDB usando a API do MongoDB.
 Ele inclui métodos para listar, inserir e buscar vaults  na coleção FuzzyVault do banco de dados.
 """

from pymongo import MongoClient
import json
from Vault_Converter import VaultConverter
import Constants

class DBHandler:
    def __init__(self):
        # Inicializa a conexão com o CosmosDB usando a API do MongoDB
        # Certifique-se de adicionar a chave da API do MongoDB no campo apropriado
        self.client = MongoClient("mongodb://MONGODB_API_STRING")

        # Seleciona o banco de dados
        self.db = self.client['FingerprintDB']

        # Seleciona a coleção (collection) "FuzzyVault"
        self.col_fuzzy_vault = self.db['FuzzyVault']

    # Lista todos os documentos na coleção "FuzzyVault"
    def list_all_fuzzy_vault(self):
        docs = self.col_fuzzy_vault.find()
        for doc in docs:
            print(doc)

    # Insere um vault na coleção "FuzzyVault" com um ID específico
    def insert_fuzzy_vault(self, vault, vault_id):
        self.col_fuzzy_vault.insert_one(VaultConverter.serialize(vault, vault_id))

    # Procura e retorna um vault na coleção "FuzzyVault" com um ID específico
    # Se "dump" for True, também salva o vault em um arquivo JSON
    def find_fuzzy_vault(self, vault_id, dump=False):
        result_cursor = self.col_fuzzy_vault.find({Constants.JSON_VAULT_ID: vault_id})
        
        if result_cursor.count() == 0:
            print("Nenhuma correspondência encontrada com o ID fornecido!")
            return None
        elif result_cursor.count() != 1:
            # Tratamento de colisão se vários IDs corresponderem NÃO ESTÁ IMPLEMENTADO
            print("Mais de um resultado encontrado!")

        result = self.col_fuzzy_vault.find_one({Constants.JSON_VAULT_ID: vault_id})
        
        if dump:
            del result['_id']  # Remove o campo '_id' antes de salvar em JSON
            with open('out/vault_{}.json'.format(vault_id), 'w') as json_file:
                json.dump(result, json_file)

        return VaultConverter.deserialize(result)

    # Fecha a conexão com o banco de dados
    def close_handler(self):
        self.client.close()
