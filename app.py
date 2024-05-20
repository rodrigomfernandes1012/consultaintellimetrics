# SERVER API
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import mysql.connector
import requests
import boto3
import os

#Amazon
selecao = []
dicionario = []
dic2 = []
dic_whats = []
dic_whats2 = []
produtos = {"produtos": []}




imagens = []


token = "8c4EF9vXi8TZe6581e0af85c25"

def conecta_bd():
  conexao = mysql.connector.connect(
      host='dbintellimetrics.c3kc6gou2fhz.us-west-2.rds.amazonaws.com',
      user='admin',
      password='IntelliMetr!c$',
      database='DbIntelliMetrics')
  return conexao

def Selecionar_TbProduto():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdProduto, dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus, dsUser, dtRegistro from DbIntelliMetrics.TbProduto'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    produtos["produtos"].append(resultado)
    cursor.close()
    conexao.close()
    return  resultado

#alunos["alunos"].append(
#        {
#            "Nome": NomesAlunos[j],
#            "Media": Media[j]
#        }
#    )



print(produtos)

def Selecionar_TbImagens():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdImagens, dsCaminho, cdCodigo, cdTipo, dsUser, dtRegistro from DbIntelliMetrics.TbImagens'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO
print(Selecionar_TbImagens())