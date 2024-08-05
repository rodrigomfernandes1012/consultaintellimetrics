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

  return conexao

def Selecionar_TbProduto():
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    comando = f'select cdProduto, dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus, dsUser, dtRegistro from public.TbProduto'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    produtos["produtos"].append(resultado)
    cursor.close()
    conexao.close()
    return  resultado

def Selecionar_TbImagens():
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    comando = f'select cdImagens, dsCaminho, cdCodigo, cdTipo, dsUser, dtRegistro from public.TbImagens'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO
print(Selecionar_TbImagens())