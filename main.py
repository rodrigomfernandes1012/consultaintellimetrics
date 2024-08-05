# SERVER API
import ast
import base64
import json
import os
import time
from collections import defaultdict
from typing import Any, Dict, List

import boto3
import pandas as pd
import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from supabase import Client, create_client

from utils import valida_e_constroi_insert

# possibilita pegar variaveis do .env
load_dotenv()

# Amazon
selecao = []
dicionario = []
dic2 = []
dic_whats = []
dic_whats2 = []
dic_altura = []

# Supabase setup client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def conecta_bd():
    conexao = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=os.getenv("DB_PORT"),
    )
    return conexao


def envia_whatstexto(msg):
    import json

    import requests

    url = "https://app.whatsgw.com.br/api/WhatsGw/Send"

    payload = json.dumps(
        {
            "apikey": "fea4fe42-3cd6-4002-bd33-31badb5074dc",
            "phone_number": "5511945480370",
            "contact_phone_number": "5511987674750",
            "message_custom_id": "yoursoftwareid",
            "message_type": "text",
            "message_body": msg,
            "check_status": "1",
        }
    )
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def assinar_arquivo(arquivo):
    url = boto3.client("s3").generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": "dbfilesintellimetrics", "Key": arquivo},
        ExpiresIn=3600,
    )
    return url


def upload_file(file_name, bucket, object_name):
    client = boto3.client("s3")
    try:
        response = client.upload_file(
            file_name, bucket, object_name, ExtraArgs={"ACL": "public-read"}
        )
    except ClientError as e:
        logging.error(e)
        return False
    return True


##DAQUI PRA BAIXO GERADOR DE API CONSULTAS NO BANCO
##ATUALIZADO EM 29-05-2024


def guarda_medidas(altura, largura, comprimento, pesoreal, cubado):
    with open("cubagem.txt", "w") as arquivo:
        altura = str(altura).ljust(10)
        largura = str(largura).ljust(10)
        comprimento = str(comprimento).ljust(10)
        cubado = str(cubado).ljust(10)
        pesoreal = str(pesoreal).ljust(20)
        # linha = f"'altura':{altura}, 'largura':{largura}, 'comprimento':{comprimento}, 'pesoreal':{pesoreal}, 'cubado':{cubado}"
        linha = f"{altura}{comprimento}{cubado}{largura}{pesoreal}"
        arquivo.write(linha)
    arquivo.close()


def Pegar_Medidas():

    # nrPeso = float(random.randrange(1, 50))
    # nrCubado = round((nrLargura * nrAltura * nrComprimento) / 167, 2)
    with open("cubagem.txt", "r") as arquivo:
        linhas = arquivo.readlines()
        for linha in linhas:
            nrAltura = float(linha[00:10])
            nrComprimento = float(linha[10:20])
            nrCubado = float(linha[20:30])
            nrLargura = float(linha[30:40])
            nrPeso = float(linha[40:60])

    medidas = {
        "nrLargura": nrLargura,
        "nrAltura": nrAltura,
        "nrComprimento": nrComprimento,
        "nrPeso": nrPeso,
        "nrCubado": nrCubado,
    }

    return medidas


# Selecionar registros da tabela public.TbAcessoIntelBras
def Selecionar_TbAcessoIntelBras():
    resultado = (
        supabase.table("TbAcessoIntelBras")
        .select(
            "cdAcessoIntelBras, dsCardName, dsCardNo, dsDoor, dsEntry, dsErrorCode, dsMethod, dsPassword, dsReaderID, dsStatus, dsType, dsUserId, dsUserType, dsUtc"
        )
        .execute()
    )
    return resultado.data


def Selecionar_VwTbDestinatarioDispositivo(codigoDisp):
    resultado = (
        supabase.table("VwTbDestinatarioDispositivo")
        .select("cdDestinatario", "dsLat", "dsLong", "nrRaio", "cdFilho")
        .eq("cdFilho", codigoDisp)
        .execute()
    )
    return resultado.data


# Inserir registros da tabela public.TbAcessoIntelBras
def Inserir_TbAcessoIntelBras(data):
    resultado = supabase.table("TbAcessoIntelBras").insert(data).execute()
    return resultado.data


# Deletar registros da tabela public.TbAcessoIntelBras
def deletar_TbAcessoIntelBras(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbAcessoIntelBras where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# Alterar registros da tabela public.TbAcessoIntelBras
def Alterar_TbAcessoIntelBras(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.TbAcessoIntelBras set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


def calcular_distancia(lat1, lon1, lat2, lon2):
    geolocator = Nominatim(user_agent="my_app")
    distancia = geodesic((lat1, lon1), (lat2, lon2)).kilometers
    return distancia


# Selecionar registros da tabela public.VwTbPosicaoAtual
def Selecionar_VwTbPosicaoAtual(filtros):
    query = supabase.table("VwTbPosicaoAtual").select(
        "cdPosicao",
        "dtRegistro",
        "cdDispositivo",
        "dsLat",
        "dsLong",
        "dsEndereco",
        "dsNum",
        "dsCep",
        "dsBairro",
        "dsCidade",
        "dsUF",
        "dsPais",
        "nrBat",
        "nrCodigo",
        "cdProduto",
        "dsProduto",
        "dsDescricao",
        "dsStatus",
        "blArea",
    )

    for campo, valor in filtros.items():
        query = query.eq(campo, valor)

    resultado = query.execute()
    return resultado.data


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbChamados
def Selecionar_TbChamados():
    resultado = (
        supabase.table("TbChamados")
        .select(
            "cdChamados",
            "dtOperacao",
            "dsTipo",
            "dsDescricao",
            "nrQtde",
            "dsUser",
            "dtRegistro",
        )
        .execute()
    )

    return resultado.data


# FIM DA FUNÇÃO


# Inserir registros da tabela public.TbChamados
def Inserir_TbChamados(data):
    resultado = supabase.table("TbChamados").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbChamados
def deletar_TbChamados(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbChamados where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbChamados
def Alterar_TbChamados(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbChamados set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbCliente
def Selecionar_TbCliente():
    resultado = (
        supabase.table("TbCliente")
        .select(
            "cdCliente",
            "dsNome",
            "nrCnpj",
            "nrIe",
            "nrInscMun",
            "dsLogradouro",
            "nrNumero",
            "dsComplemento",
            "dsBairro",
            "dsCep",
            "dsCidade",
            "dsUF",
            "dsObs",
            "cdStatus",
            "dsUser",
            "dtRegistro",
        )
        .execute()
    )

    return resultado.data


# FIM DA FUNÇÃO


# Inserir registros da tabela public.TbCliente
def Inserir_TbCliente(data):
    resultado = supabase.table("TbCliente").insert(data).execute()
    return resultado.data


# Deletar registros da tabela public.TbCliente
def deletar_TbCliente(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbCliente where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbCliente
def Alterar_TbCliente(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbCliente set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbDestinatario
def Selecionar_TbDestinatario(codigo):
    query = supabase.table("TbDestinatario").select(
        "cdDestinatario",
        "dsNome",
        "nrCnpj",
        "nrIe",
        "nrInscMun",
        "dsLogradouro",
        "nrNumero",
        "dsComplemento",
        "dsBairro",
        "dsCep",
        "dsCidade",
        "dsUF",
        "dsObs",
        "cdStatus",
        "dsLat",
        "dsLong",
        "nrRaio",
        "dsUser",
        "dtRegistro",
    )

    if codigo != "0":
        query.eq("cdDestinatario", codigo)

    resultado = query.execute()

    return resultado.data


# FIM DA FUNÇÃO


def Selecionar_Lat_Long_Destinatario(codigo):
    resultado = (
        supabase.table("VwTbDestinatarioDispositivo")
        .select("cdDestinatario", "dsLat", "dsLong", "cdFilho")
        .eq("cdFilho", codigo)
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbDestinatario
def Inserir_TbDestinatario(data):
    resultado = supabase.table("TbDestinatario").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbDestinatario
def deletar_TbDestinatario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbDestinatario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbDestinatario
def Alterar_TbDestinatario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.TbDestinatario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbDispositivo
def Selecionar_TbDispositivo(codigo):
    query = supabase.table("TbDispositivo").select(
        "cdDispositivo",
        "dsDispositivo",
        "dsModelo",
        "dsDescricao",
        "dsObs",
        "dsLayout",
        "nrChip",
        "cdStatus",
        "dsUser",
        "dtRegistro",
    )

    if codigo != "0":
        query.eq("cdDispositivo", codigo)

    resultado = query.execute()

    return resultado.data


# FIM DA FUNÇÃO


# Inserir registros da tabela public.TbDispositivo
def Inserir_TbDispositivo(data):
    resultado = supabase.table("TbDispositivo").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbDispositivo
def deletar_TbDispositivo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbDispositivo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbDispositivo
def Alterar_TbDispositivo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.TbDispositivo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbImagens
def Selecionar_TbImagens(codigo):
    query = supabase.table("TbImagens").select(
        "cdImagens, dsCaminho, cdCodigo, cdTipo, dsUser, dtRegistro, cdProduto, nrImagem"
    )

    if codigo != "0":
        query.eq("cdProduto", codigo)

    resultado = query.execute()

    return resultado.data


# FIM DA FUNÇÃO


# Inserir registros da tabela public.TbImagens
def Inserir_TbImagens(data):
    resultado = supabase.table("TbImagens").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbImagens
def deletar_TbImagens(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbImagens where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbImagens
def Alterar_TbImagens(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbImagens set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


def get_endereco_coordenada(lat, long):
    payload = f"http://osm.taxidigital.net:4000/v1/reverse?point.lon={long}&point.lat={lat}&layers=address&sources=oa&size=1&cdFilial=0&cdTipoOrigem=0"
    requisicao = requests.get(payload)
    dic = requisicao.json()
    adress = dic["features"]

    for campos in adress:
        dados = campos["properties"]
        dsLogradoruro = dados.get("street")
        dsNum = dados.get("housenumber")
        dsBairro = dados.get("neighbourhood")
        dsCidade = dados.get("locality")
        dsUF = dados.get("region_a")
        dsCep = dados.get("postalcode")
        dsPais = dados.get("country_code")

    return {
        "dsLogradoruro": dsLogradoruro,
        "dsNum": dsNum,
        "dsBairro": dsBairro,
        "dsCidade": dsCidade,
        "dsUF": dsUF,
        "dsCep": dsCep,
        "dsPais": dsPais,
    }


# Inserir registros da tabela public.TbPosicao
def Inserir_TbPosicao(data):
    resultado = supabase.table("TbPosicao").insert(data).execute()
    return resultado.data


def Alterar_StatusTbPosicao(codigo, status):
    response = (
        supabase.table("TbDispositivo")
        .update({"cdStatus": status})
        .eq("cdDispositivo", codigo)
        .execute()
    )
    return response.data


def Inserir_TbSensorRegistro(data):
    resultado = supabase.table("TbSensorRegistro").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbPosicao
def deletar_TbPosicao(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbPosicao where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbPosicao
def Alterar_TbPosicao(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbPosicao set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbProduto
def Selecionar_TbProduto(codigo):
    resultado = (
        supabase.table("VwTbProdutoTotalStaus")
        .select(
            "cdProduto",
            "dsDescricao",
            "dsNome",
            "nrAlt",
            "nrCodigo",
            "nrComp",
            "nrLarg",
            "nrQtde",
            "dsStatus",
            "TbImagens(cdCodigo, dsCaminho)",
        )
        .eq("cdProduto", codigo)
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbProduto
def Inserir_TbProduto(data):
    resultado = supabase.table("TbProduto").insert(data).execute()
    return resultado.data


# Deletar registros da tabela public.TbProduto
def deletar_TbProduto(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbProduto where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbRelacionamento
def Selecionar_TbRelacionamento():
    resultado = (
        supabase.table("TbRelacionamento")
        .select(
            "cdRelacionamento",
            "cdPai",
            "cdFilho",
            "cdTipo",
            "dsDescricao",
            "cdStatus",
            "dsUser",
            "dtRegistro",
        )
        .execute()
    )

    return resultado.data


# FIM DA FUNÇÃO


# Inserir registros da tabela public.TbRelacionamento
def Inserir_TbRelacionamento(data):
    resultado = supabase.table("TbRelacionamento").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbRelacionamento
def deletar_TbRelacionamento(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbRelacionamento where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbRelacionamento
def Alterar_TbRelacionamento(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.TbRelacionamento set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbSensor
def Selecionar_TbSensor():
    resultado = (
        supabase.table("TbSensor")
        .select(
            "cdSensor",
            "dsNome",
            "cdTipo",
            "dsDescricao",
            "cdUnidade",
            "nrUnidadeIni",
            "nrUnidadeFim",
            "dsUser",
            "dtRegistro",
        )
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbSensor
def Inserir_TbSensor(data):
    resultado = supabase.table("TbSensor").insert(data).execute()
    return resultado.data


# Deletar registros da tabela public.TbSensor
def deletar_TbSensor(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbSensor where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbSensor
def Alterar_TbSensor(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbSensor set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbStatus
def Selecionar_TbStatus():
    resultado = (
        supabase.table("TbStatus")
        .select("cdStatus, dsStatus, dsUser, dtRegistro")
        .execute()
    )
    return resultado.data


# FIM DA FUNÇÃO


# Inserir registros da tabela public.TbStatus
def Inserir_TbStatus(data):
    resultado = supabase.table("TbStatus").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbStatus
def deletar_TbStatus(Campo, Dado):
    # conexao = conecta_bd()
    # cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # comando = f'delete from public.TbStatus where {Campo}="{Dado}"  '
    # cursor.execute(comando)
    # conexao.commit()
    resultado = supabase.table("TbStatus").delete().eq(Campo, Dado).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbStatus
def Alterar_TbStatus(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbStatus set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbTag
def Selecionar_TbTag():
    resultado = (
        supabase.table("TbTag")
        .select("cdTag", "dsDescricao", "dsConteudo", "dsUser", "dtRegistro")
        .execute()
    )

    return resultado.data


# FIM DA FUNÇÃO


# Inserir registros da tabela public.TbTag
def Inserir_TbTag(data):
    resultado = supabase.table("TbTag").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbTag
def deletar_TbTag(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbTag where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbTag
def Alterar_TbTag(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.TbTag set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbTicket
def Selecionar_TbTicket():
    resultado = (
        supabase.table("TbTicket")
        .select(
            "cdTicket",
            "dtOperacao",
            "dsAtendimento",
            "nrAbertos",
            "nrFechados",
            "nrPendentes",
            "dsUser",
            "dtRegistro",
        )
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbTicket
def Inserir_TbTicket(data):
    resultado = supabase.table("TbTicket").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbTicket
def deletar_TbTicket(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbTicket where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbTicket
def Alterar_TbTicket(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbTicket set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbTicketResumo
def Selecionar_TbTicketResumo():
    resultado = (
        supabase.table("TbTicketResumo")
        .select(
            "cdTicketResumo",
            "dtOperacao",
            "dsAtendimento",
            "dsNaoAtribuido",
            "dsSemResolucao",
            "dsAtualizado",
            "dsPendente",
            "dsResolvido",
            "dsUser",
            "dtRegistro",
        )
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbTicketResumo
def Inserir_TbTicketResumo(data):
    resultado = supabase.table("TbTicketResumo").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbTicketResumo
def deletar_TbTicketResumo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbTicketResumo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbTicketResumo
def Alterar_TbTicketResumo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.TbTicketResumo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbTipo
def Selecionar_TbTipo():
    resultado = (
        supabase.table("TbTipo")
        .select("cdTipo", "dsDescricao", "dsUser", "dtRegistro")
        .execute()
    )

    return resultado.data


# FIM DA FUNÇÃO


# Inserir registros da tabela public.TbTipo
def Inserir_TbTipo(data):
    resultado = supabase.table("TbTipo").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbTipo
def deletar_TbTipo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbTipo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbTipo
def Alterar_TbTipo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbTipo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbUnidade
def Selecionar_TbUnidade():
    resultado = (
        supabase.table("TbUnidade")
        .select("cdUnidade", "dsUnidade", "dsSimbolo", "dsUser", "dtRegistro")
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbUnidade
def Inserir_TbUnidade(data):
    resultado = supabase.table("TbUnidade").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbUnidade
def deletar_TbUnidade(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbUnidade where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbUnidade
def Alterar_TbUnidade(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbUnidade set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbUsuario
def Selecionar_TbUsuario():
    resultado = (
        supabase.table("TbUsuario")
        .select(
            "cdUsuario",
            "dsNome",
            "dsLogin",
            "dsSenha",
            "cdPerfil",
            "dsUser",
            "dtRegistro",
        )
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbUsuario
def Inserir_TbUsuario(data):
    resultado = supabase.table("TbUsuario").insert(data).execute()
    return resultado.data


# Deletar registros da tabela public.TbUsuario
def deletar_TbUsuario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbUsuario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbUsuario
def Alterar_TbUsuario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbUsuario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbVisita
def Selecionar_TbVisita():
    resultado = (
        supabase.table("TbVisita")
        .select(
            "cdVisita", "cdCliente", "cdVisitante", "dtData", "dsUser", "dtRegistro"
        )
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbVisita
def Inserir_TbVisita(data):
    resultado = supabase.table("TbVisita").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbVisita
def deletar_TbVisita(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbVisita where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbVisita
def Alterar_TbVisita(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbVisita set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbVisitante
def Selecionar_TbVisitante():
    resultado = (
        supabase.table("TbVisitante")
        .select(
            "cdVisitante",
            "dsNome",
            "nrTelefone",
            "nrDocumento",
            "dsEmail",
            "dsUser",
            "dtRegistro",
        )
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbVisitante
def Inserir_TbVisitante(data):
    resultado = supabase.table("TbVisitante").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbVisitante
def deletar_TbVisitante(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbVisitante where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbVisitante
def Alterar_TbVisitante(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbVisitante set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbPosicao
def Selecionar_TbPosicao(filtros):
    query = supabase.table("TbPosicao").select(
        "dtData",
        "dtHora",
        "dsLat",
        "dsLong",
        "nrTemp",
        "nrBat",
        "dsEndereco",
        "dtRegistro",
    )

    # Apply filters
    for campo, valor in filtros.items():
        if campo == "dtRegistro":
            # Format date as YYYY-MM-DD
            valor = f"{valor[:4]}-{valor[4:6]}-{valor[6:]}"
            query = query.gte(campo, f'{valor + " 00:00:00"}')
            query = query.lte(campo, f'{valor + " 23:59:59"}')
        else:
            query = query.eq(campo, valor)

    resultado = query.execute()

    return resultado.data


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbPosicao
def deletar_TbPosicao(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbPosicao where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbPosicao
def Alterar_TbPosicao(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbPosicao set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


def Selecionar_VwRelHistoricoDispositivoProduto(filtros):
    query = supabase.table("VwRelHistoricoDispositivoProduto").select(
        "cdProduto",
        "nrCodigo",
        "dsDescricao",
        "dtRegistro",
        "cdDispositivo",
        "dsNome",
        "dsEndereco",
        "nrBatPercentual",
        "nrPorta",
        "nrTemperatura",
        "dsProdutoItem",
        "nrQtdItens",
        "dsStatus",
        "dsStatusDispositivo",
        "cdSensor",
    )

    # Apply filters
    for campo, valor in filtros.items():
        if campo == "dtRegistro":
            # Format date as YYYY-MM-DD
            valor = f"{valor[:4]}-{valor[4:6]}-{valor[6:]}"
            query = query.gte(campo, f'{valor + " 00:00:00"}')
            query = query.lte(campo, f'{valor + " 23:59:59"}')
        else:
            query = query.eq(campo, valor)

    resultado = query.execute()

    return resultado.data


# busca dados de VwRelHistoricoDispositivoProduto, mas retorna cada produtoItem como uma coluna.
def Selecionar_HistoricoPaginaDispositivo(filtros):
    resultado = Selecionar_VwRelHistoricoDispositivoProduto

    if len(resultado) == 0:
        return resultado

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(resultado)

    # Retain the original data for merging later
    original_df = df.drop(
        columns=["nrQtdItens", "dsProdutoItem", "cdSensor"]
    ).drop_duplicates()

    # Pivot the data
    pivot_df = df.pivot_table(
        index="dtRegistro",
        columns=["dsProdutoItem", "cdSensor"],
        values="nrQtdItens",
        fill_value=0,
    )

    # Flatten the multi-index columns
    pivot_df.columns = [f"{item[0]}_{item[1]}" for item in pivot_df.columns]

    # Reset index to have dtRegistro as a column again
    pivot_df = pivot_df.reset_index()

    # Merge the pivoted data with the original data
    final_df = pd.merge(original_df, pivot_df, on="dtRegistro", how="left")

    result_json = final_df.to_json(orient="records", date_format="iso")

    return result_json


def Selecionar_VwRelDadosDispositivo(filtros):
    query = supabase.table("VwRelDadosDispositivo").select(
        "cdProduto",
        "dsNome",
        "cdDispositivo",
        "nrBat",
        "dsNomeDest",
        "dsEnderecoDest",
        "nrNumeroDest",
        "dsBairroDest",
        "dsCidadeDest",
        "dsUfDest",
        "dsCepDest",
        "dsLatDest",
        "dsLongDest",
        "dsRaio",
        "dsEnderecoAtual",
        "dsNumeroAtual",
        "dsBairroAtual",
        "dsCidadeAtual",
        "dsUFAtual",
        "dsCEPAtual",
        "dsLatAtual",
        "dsLongAtual",
        "blArea",
        "dtRegistro",
        "dtCadastro",
    )

    # Apply filters
    for campo, valor in filtros.items():
        if campo == "dtRegistro":
            # Format date as YYYY-MM-DD
            valor = f"{valor[:4]}-{valor[4:6]}-{valor[6:]}"
            query = query.gte(campo, f'{valor + " 00:00:00"}')
            query = query.lte(campo, f'{valor + " 23:59:59"}')
        else:
            query = query.eq(campo, valor)

    resultado = query.execute()

    return resultado.data


# Selecionar registros da tabela public.TbProdutoTipo
def Selecionar_VwTbProdutoTipo(codigo):
    query = supabase.table("VwTbProdutoTipo").select(
        "cdProduto",
        "dsNome",
        "dsDescricao",
        "nrCodigo",
        "nrLarg",
        "nrComp",
        "nrAlt",
        "cdStatus",
        "cdDispositivo",
        "dsDispositivo",
        "dsModelo",
        "DescDispositivo",
        "dsObs",
        "dsLayout",
        "nrChip",
        "StatusDispositivo",
    )

    if codigo != "0":
        query.eq("cdProduto", codigo)

    resultado = query.execute()

    return resultado.data


# Inserir registros da tabela public.VwTbProdutoTipo
def Inserir_VwTbProdutoTipo(
    dsNome,
    dsDescricao,
    nrCodigo,
    nrLarg,
    nrComp,
    nrAlt,
    cdStatus,
    cdDispositivo,
    dsDispositivo,
    dsModelo,
    DescDispositivo,
    dsObs,
    dsLayout,
    nrChip,
    StatusDispositivo,
):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'insert into public.VwTbProdutoTipo ( dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus, cdDispositivo, dsDispositivo, dsModelo, DescDispositivo, dsObs, dsLayout, nrChip, StatusDispositivo ) values ("{dsNome}", "{dsDescricao}", "{nrCodigo}", "{nrLarg}", "{nrComp}", "{nrAlt}", "{cdStatus}", "{cdDispositivo}", "{dsDispositivo}", "{dsModelo}", "{DescDispositivo}", "{dsObs}", "{dsLayout}", "{nrChip}", "{StatusDispositivo}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela public.VwTbProdutoTipo
def deletar_VwTbProdutoTipo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.VwTbProdutoTipo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.VwTbProdutoTipo
def Alterar_VwTbProdutoTipo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.VwTbProdutoTipo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.VwTbProdutoTotalStaus
def Selecionar_VwTbProdutoTotalStaus(codigo):
    query = supabase.table("VwTbProdutoTotalStaus").select(
        "cdProduto",
        "dsDescricao",
        "dsNome",
        "nrAlt",
        "nrCodigo",
        "nrComp",
        "nrLarg",
        "nrQtde",
        "dsStatus",
        "QtdeTotal",
        "imagens:TbImagens(cdCodigo, dsCaminho)",
    )

    if codigo != "0":
        query.eq("cdProduto", codigo)

    resultado = query.execute()

    # Dictionary to store the results
    produtos_dict: Dict[str, Any] = defaultdict(
        lambda: {
            "cdProduto": None,
            "dsDescricao": None,
            "dsNome": None,
            "nrAlt": None,
            "nrCodigo": None,
            "nrComp": None,
            "nrLarg": None,
            "QtdeTotal": None,
            "imagens": None,
            "status": [],
        }
    )

    # Iterate through the products
    for produto in resultado.data:
        cdProduto = produto["cdProduto"]

        # Initialize product if not already present
        if produtos_dict[cdProduto]["cdProduto"] is None:
            produtos_dict[cdProduto].update(
                {
                    "cdProduto": produto["cdProduto"],
                    "dsDescricao": produto["dsDescricao"],
                    "dsNome": produto["dsNome"],
                    "nrAlt": produto["nrAlt"],
                    "nrCodigo": produto["nrCodigo"],
                    "nrComp": produto["nrComp"],
                    "nrLarg": produto["nrLarg"],
                    "QtdeTotal": produto["QtdeTotal"],
                    "imagens": produto["imagens"],
                }
            )

        # Add status to the status list
        if produto["nrQtde"] and produto["dsStatus"]:
            produtos_dict[cdProduto]["status"].append(
                {"dsStatus": produto["dsStatus"], "nrQtde": produto["nrQtde"]}
            )

    # Convert to list for JSON serialization
    produtos_list: List[Dict[str, Any]] = list(produtos_dict.values())

    return jsonify(produtos_list)


# FIM DA FUNÇÃO


def Selecionar_VwTbProdutoTotal(codigo):
    query = supabase.table("VwTbProdutoTotal").select(
        "cdProduto",
        "dsNome",
        "dsDescricao",
        "nrCodigo",
        "nrLarg",
        "nrComp",
        "nrAlt",
        "cdStatus",
        "cdDispositivo",
        "dsDispositivo",
        "dsModelo",
        "DescDispositivo",
        "dsObs",
        "dsLayout",
        "nrChip",
        "StatusDispositivo",
        "nrQtde",
    )

    if codigo != "0":
        query.eq("cdProduto", codigo)

    resultado = query.execute()

    return resultado.data


# Inserir registros da tabela public.VwTbProdutoTotalStaus
def Inserir_VwTbProdutoTotalStaus(
    dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, Status, nrQtde
):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'insert into public.VwTbProdutoTotalStaus ( dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, Status, nrQtde ) values ("{dsNome}", "{dsDescricao}", "{nrCodigo}", "{nrLarg}", "{nrComp}", "{nrAlt}", "{Status}", "{nrQtde}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela public.VwTbProdutoTotalStaus
def deletar_VwTbProdutoTotalStaus(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.VwTbProdutoTotalStaus where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.VwTbProdutoTotalStaus
def Alterar_VwTbProdutoTotalStaus(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.VwTbProdutoTotalStaus set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbFuncionario
def Selecionar_TbFuncionario():
    resultado = (
        supabase.table("TbFuncionario")
        .select(
            "cdFuncionario",
            "dsBairro",
            "dsCidade",
            "dsComplemento",
            "dsFuncao",
            "dsLogradouro",
            "dsNomeEmpregado",
            "dsNumCasa",
            "dsUser",
            "dtRegistro",
            "nrCodEmpregado",
            "TbFuncionariocol",
        )
        .execute()
    )

    return resultado.data


# FIM DA FUNÇÃO


# Inserir registros da tabela public.TbFuncionario
def Inserir_TbFuncionario(
    dsBairro,
    dsCidade,
    dsComplemento,
    dsFuncao,
    dsLogradouro,
    dsNomeEmpregado,
    dsNumCasa,
    dsUser,
    dtRegistro,
    nrCodEmpregado,
    TbFuncionariocol,
):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'insert into public.TbFuncionario ( dsBairro, dsCidade, dsComplemento, dsFuncao, dsLogradouro, dsNomeEmpregado, dsNumCasa, dsUser, dtRegistro, nrCodEmpregado, TbFuncionariocol ) values ("{dsBairro}", "{dsCidade}", "{dsComplemento}", "{dsFuncao}", "{dsLogradouro}", "{dsNomeEmpregado}", "{dsNumCasa}", "{dsUser}", "{dtRegistro}", "{nrCodEmpregado}", "{TbFuncionariocol}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbFuncionario
def deletar_TbFuncionario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbFuncionario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbFuncionario
def Alterar_TbFuncionario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.TbFuncionario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela public.TbFuncionario
def Selecionar_TbEtiqueta(dsEtiqueta):
    query = supabase.table("TbEtiqueta").select(
        "dsEtiqueta",
        "nrFator",
        "nrLargura",
        "nrAltura",
        "nrComprimento",
        "nrPeso",
        "nrCubado",
        "dsUser",
        "dtRegistro",
    )

    if dsEtiqueta != "0":
        query.eq("dsEtiqueta", dsEtiqueta)

    resultado = query.order("cdEtiqueta", desc=True).execute()
    return resultado.data


# FIM DA FUNÇÃO


# Inserir registros da tabela public.TbEtiqueta
def Inserir_TbEtiqueta(data):
    resultado = supabase.table("TbEtiqueta").insert(data).execute()
    return resultado.data


# FIM DA FUNÇÃO


app = Flask(__name__)  # cria o site
app.json.sort_keys = False
CORS(app, resources={r"*": {"origins": "*"}})

##COMECA A API GERADA AUTOMATICAMENTE


# Selecionar registros no EndPoint Chamados
@app.route("/Chamados")
def get_Chamados():
    resultado = Selecionar_TbChamados()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Chamados
@app.route("/Chamados", methods=["POST"])
def post_Chamados():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbChamados", payload)

    if error:
        return jsonify({"error": error}), 400

    Inserir_TbChamados(data)
    return "Cadastramento realizado com sucesso"


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbChamados
def deletar_TbChamados(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbChamados where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbChamados
def Alterar_TbChamados(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbChamados set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Cliente


# Selecionar registros no EndPoint Cliente
@app.route("/Cliente")
def get_Cliente():
    resultado = Selecionar_TbCliente()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Cliente
@app.route("/Cliente", methods=["POST"])
def post_Cliente():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbCliente", payload)

    if error:
        return jsonify({"error": error}), 400

    Inserir_TbCliente(data)
    return "Cadastramento realizado com sucesso"


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbCliente
def deletar_TbCliente(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbCliente where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbCliente
def Alterar_TbCliente(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbCliente set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Destinatario


# Selecionar registros no EndPoint Destinatario
@app.route("/Destinatario/<codigo>")
def get_Destinatario(codigo):
    resultado = Selecionar_TbDestinatario(codigo)
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Destinatario
@app.route("/Destinatario", methods=["POST"])
def post_Destinatario():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbDestinatario", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbDestinatario(data)
    return resultado


# Deletar registros da tabela public.TbDestinatario
def deletar_TbDestinatario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbDestinatario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbDestinatario
def Alterar_TbDestinatario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.TbDestinatario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Dispositivo


# Selecionar registros no EndPoint Dispositivo
@app.route("/Dispositivo/<codigo>")
def get_Dispositivo(codigo):
    resultado = Selecionar_TbDispositivo(codigo)
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Dispositivo
@app.route("/Dispositivo", methods=["POST"])
def post_Dispositivo():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbDispositivo", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbDispositivo(data)
    return resultado


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbDispositivo
def deletar_TbDispositivo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbDispositivo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbDispositivo
def Alterar_TbDispositivo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.TbDispositivo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Imagens


# Selecionar registros no EndPoint Imagens
@app.route("/Imagens/<codigo>")
def get_Imagens(codigo):
    resultado = Selecionar_TbImagens(codigo)
    return resultado


# Deletar registros da tabela public.TbImagens
def deletar_TbImagens(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbImagens where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbImagens
def Alterar_TbImagens(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbImagens set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Posicao


# Selecionar registros no EndPoint Posicao
@app.route("/Posicao/<codigo>")
def get_Posicao(codigo):
    filtros = {
        "dtData": request.args.get("dtData"),
        "dtHora": request.args.get("dtHora"),
        "dsLat": request.args.get("dsLat"),
        "dsLong": request.args.get("dsLong"),
        "nrTemp": request.args.get("nrTemp"),
        "nrBat": request.args.get("nrBat"),
        "dsEndereco": request.args.get("dsEndereco"),
        "dtRegistro": request.args.get("dtRegistro"),
    }

    # Remove filtros que nao tem valor
    filtros = {k: v for k, v in filtros.items() if v is not None}

    # Adiciona o codigo como um filtro se for diferente de 0
    if codigo != "0":
        filtros["cdDispositivo"] = codigo

    resultado = Selecionar_TbPosicao(filtros)
    return resultado


def altera_status_posicao(cdDispositivo, dsLat, dsLong):
    dic_endereco_pdv = Selecionar_VwTbDestinatarioDispositivo(cdDispositivo)
    dic_endereco_pdv = dict(dic_endereco_pdv[0])

    dsLatPdv = dic_endereco_pdv["dsLat"]
    dsLongPdv = dic_endereco_pdv["dsLong"]
    nrRaio = dic_endereco_pdv["nrRaio"]
    nrDistancia = calcular_distancia(dsLat, dsLong, dsLatPdv, dsLongPdv)

    # TODO: verificar se necessario. Da pra saber se esta fora de area pegando a ultima posicao. Precisa guardar no dispositivo?
    if float(nrDistancia) > float(nrRaio):
        Alterar_StatusTbPosicao(cdDispositivo, 6)
        blArea = False
    else:
        Alterar_StatusTbPosicao(cdDispositivo, 1)
        blArea = True

    return blArea


def inserir_sensor_registros(dic_sensores, tb_posicao):
    dataSensorRegistro = []

    for sensor in dic_sensores:
        payload_sensor_registro = {
            "cdSensor": sensor["cdSensor"],
            "nrValor": sensor["nrValor"],
            "cdPosicao": tb_posicao[0]["cdPosicao"],
            "cdDispositivo": sensor["cdDispositivo"],
        }

        data, error = valida_e_constroi_insert(
            "TbSensorRegistro", payload_sensor_registro
        )

        if error:
            return jsonify({"error": error}), 400

        dataSensorRegistro.append(data)

    return Inserir_TbSensorRegistro(dataSensorRegistro)


@app.route("/Posicao", methods=["POST"])
def post_Posicao():
    payload = request.get_json()

    dsLat = payload["dsLat"]
    dsLong = payload["dsLong"]
    cdDispositivo = payload["cdDispositivo"]

    dict_endereco_coord = get_endereco_coordenada(dsLat, dsLong)

    for key, value in dict_endereco_coord.items():
        payload[key] = value

    blArea = altera_status_posicao(cdDispositivo, dsLat, dsLong)
    payload["blArea"] = blArea

    dic_sensores = payload["sensores"]
    del payload[
        "sensores"
    ]  # remove do payload para nao atrapalhar com o inserir tbPosicao

    data, error = valida_e_constroi_insert("TbPosicao", payload)
    if error:
        return jsonify({"error": error}), 400

    resultado_posicao = Inserir_TbPosicao(data)

    resultado_sensores = inserir_sensor_registros(dic_sensores, resultado_posicao)
    resultado_posicao[0]["sensores"] = resultado_sensores

    return resultado_posicao


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbPosicao
def deletar_TbPosicao(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbPosicao where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbPosicao
def Alterar_TbPosicao(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbPosicao set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Produto

cd = []


# Inserir registros no EndPoint Produto
@app.route("/Produto", methods=["POST"])
def post_Produto():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbProduto", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbProduto(data)
    return jsonify({"cdProduto": resultado[0]["cdProduto"]})


# FIM DA FUNÇÃO


@app.route("/Produto/<codigo>")
def get_Produto(codigo):
    resultado = Selecionar_TbProduto(codigo)
    return resultado


@app.route("/Produto/<codigo>", methods=["PUT"])
def update_Produto(codigo):
    data = request.get_json()
    Alterar_TbProduto("cdProduto", codigo, data)
    return jsonify({"message": "Produto atualizado com sucesso"})


@app.route("/Produto/<codigo>", methods=["DELETE"])
def delete_Produto(codigo):

    deletar_TbProduto("cdProduto", codigo)
    return jsonify({"message": "Produto deletado com sucesso"})


# FIM DA FUNÇÃO


@app.route("/Etiqueta/<dsEtiqueta>", methods=["GET"])
def get_Etiqueta(dsEtiqueta):
    resultado = Selecionar_TbEtiqueta(dsEtiqueta)
    return resultado


# FIM DA FUNÇÃO


@app.route("/TbEtiqueta", methods=["POST"])
def post_Etiqueta():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbEtiqueta", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbEtiqueta(data)
    return resultado


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbProduto
def deletar_TbProduto(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbProduto where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbProduto
def Alterar_TbProduto(Campo, Dado, UpData):
    comando = "update public.TbProduto set"

    for campos in UpData:
        comando += f' {campos}="{UpData[campos]}",'

    comando = comando[:-1]
    comando += f' where {Campo}="{Dado}"'

    conexao = conecta_bd()
    cursor = conexao.cursor()
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Relacionamento
# mycursor = mydb.cursor()
# sql = "UPDATE customers SET address = 'Canyon 123' WHERE address = 'Valley 345'"

# mycursor.execute(sql)

# mydb.commit()


# Selecionar registros no EndPoint Relacionamento
@app.route("/Relacionamento")
def get_Relacionamento():
    resultado = Selecionar_TbRelacionamento()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Relacionamento
@app.route("/Relacionamento", methods=["POST"])
def post_Relacionamento():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbRelacionamento", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbRelacionamento(data)
    return resultado


# FIM DA FUNÇÃO


# Selecionar registros no EndPoint Sensor
@app.route("/Sensor")
def get_Sensor():
    resultado = Selecionar_TbSensor()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Sensor
@app.route("/Sensor", methods=["POST"])
def post_Sensor():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbSensor", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbSensor(data)
    return resultado


# FIM DA FUNÇÃO


# Selecionar registros no EndPoint Status
@app.route("/Status")
def get_Status():
    resultado = Selecionar_TbStatus()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Status
@app.route("/Status", methods=["POST"])
def post_Status():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbStatus", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbStatus(data)
    return resultado


# FIM DA FUNÇÃO


# Selecionar registros no EndPoint Tag
@app.route("/Tag")
def get_Tag():
    resultado = Selecionar_TbTag()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Tag
@app.route("/Tag", methods=["POST"])
def post_Tag():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbTag", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbTag(data)
    return resultado


# FIM DA FUNÇÃO


# Selecionar registros no EndPoint Ticket
@app.route("/Ticket")
def get_Ticket():
    resultado = Selecionar_TbTicket()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Ticket
@app.route("/Ticket", methods=["POST"])
def post_Ticket():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbTicket", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbTicket(data)
    return resultado


# FIM DA FUNÇÃO


# Selecionar registros no EndPoint TicketResumo
@app.route("/TicketResumo")
def get_TicketResumo():
    resultado = Selecionar_TbTicketResumo()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint TicketResumo
@app.route("/TicketResumo", methods=["POST"])
def post_TicketResumo():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbTicketResumo", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbTicketResumo(data)
    return resultado


# FIM DA FUNÇÃO


# Selecionar registros no EndPoint Tipo
@app.route("/Tipo")
def get_Tipo():
    resultado = Selecionar_TbTipo()
    return resultado


# Inserir registros no EndPoint Tipo
@app.route("/Tipo", methods=["POST"])
def post_Tipo():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbTipo", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbTipo(data)
    return resultado


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbTipo
def deletar_TbTipo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbTipo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbTipo
def Alterar_TbTipo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbTipo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Unidade


# Selecionar registros no EndPoint Unidade
@app.route("/Unidade")
def get_Unidade():
    resultado = Selecionar_TbUnidade()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Unidade
@app.route("/Unidade", methods=["POST"])
def post_Unidade():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbUnidade", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbUnidade(data)
    return resultado


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbUnidade
def Alterar_TbUnidade(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbUnidade set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Usuario


# Selecionar registros no EndPoint Usuario
@app.route("/Usuario")
def get_Usuario():
    resultado = Selecionar_TbUsuario()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Usuario
@app.route("/Usuario", methods=["POST"])
def post_Usuario():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbUsuario", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbUsuario(data)
    return resultado


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbUsuario
def deletar_TbUsuario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbUsuario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbUsuario
def Alterar_TbUsuario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbUsuario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Visita


# Selecionar registros no EndPoint Visita
@app.route("/Visita")
def get_Visita():
    resultado = Selecionar_TbVisita()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Visita
@app.route("/Visita", methods=["POST"])
def post_Visita():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbVisita", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbVisita(data)
    return resultado


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbVisita
def deletar_TbVisita(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbVisita where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbVisita
def Alterar_TbVisita(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbVisita set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Visitante


# Selecionar registros no EndPoint Visitante
@app.route("/Visitante")
def get_Visitante():
    resultado = Selecionar_TbVisitante()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Visitante
@app.route("/Visitante", methods=["POST"])
def post_Visitante():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbVisitante", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbVisitante(data)
    return resultado


# FIM DA FUNÇÃO


# Deletar registros da tabela public.TbVisitante
def deletar_TbVisitante(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbVisitante where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbVisitante
def Alterar_TbVisitante(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbVisitante set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/TbPosicao


# Deletar registros da tabela public.TbPosicao
def deletar_TbPosicao(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.TbPosicao where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.TbPosicao
def Alterar_TbPosicao(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = (
        f'update public.TbPosicao set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/TbProdutoTipo


# Selecionar registros no EndPoint TbProdutoTipo
@app.route("/TbProdutoTipo/<codigo>")
def get_TbProdutoTipo(codigo):
    resultado = Selecionar_VwTbProdutoTipo(codigo)
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint TbProdutoTipo
@app.route("/TbProdutoTipo", methods=["POST"])
def post_TbProdutoTipo():
    payload = request.get_json()
    dsNome = payload["dsNome"]
    dsDescricao = payload["dsDescricao"]
    nrCodigo = payload["nrCodigo"]
    nrLarg = payload["nrLarg"]
    nrComp = payload["nrComp"]
    nrAlt = payload["nrAlt"]
    cdStatus = payload["cdStatus"]
    cdDispositivo = payload["cdDispositivo"]
    dsDispositivo = payload["dsDispositivo"]
    dsModelo = payload["dsModelo"]
    DescDispositivo = payload["DescDispositivo"]
    dsObs = payload["dsObs"]
    dsLayout = payload["dsLayout"]
    nrChip = payload["nrChip"]
    StatusDispositivo = payload["StatusDispositivo"]
    Inserir_VwTbProdutoTipo(
        dsNome,
        dsDescricao,
        nrCodigo,
        nrLarg,
        nrComp,
        nrAlt,
        cdStatus,
        cdDispositivo,
        dsDispositivo,
        dsModelo,
        DescDispositivo,
        dsObs,
        dsLayout,
        nrChip,
        StatusDispositivo,
    )
    return payload


# FIM DA FUNÇÃO


# Deletar registros da tabela public.VwTbProdutoTipo
def deletar_VwTbProdutoTipo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    comando = f'delete from public.VwTbProdutoTipo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela public.VwTbProdutoTipo
def Alterar_VwTbProdutoTipo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update public.VwTbProdutoTipo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/TbProdutoTotalStaus


# endpoint usado para Pagina de Dispositivo. Mesmo do que o VwRelHistoricoDispositivoProduto,
# mas com produtos sendo retornados como colunas.
@app.route("/HistoricoPaginaDispositivo/<codigo>")
def get_HistoricoPaginaDispositivo(codigo):
    filtros = {
        "dtRegistro": request.args.get("dtRegistro"),
    }

    # Remove filtros que nao tem valor
    filtros = {k: v for k, v in filtros.items() if v is not None}

    # Adiciona o codigo como um filtro se for diferente de 0
    if codigo != "0":
        filtros["cdDispositivo"] = codigo

    resultado = Selecionar_HistoricoPaginaDispositivo(filtros)
    return resultado


@app.route("/VwRelHistoricoDispositivoProduto/<codigo>")
def get_RelHistoricoDispositivoProduto(codigo):
    filtros = {
        "dtRegistro": request.args.get("dtRegistro"),
    }

    # Remove filtros que nao tem valor
    filtros = {k: v for k, v in filtros.items() if v is not None}

    # Adiciona o codigo como um filtro se for diferente de 0
    if codigo != "0":
        filtros["cdDispositivo"] = codigo

    resultado = Selecionar_VwRelHistoricoDispositivoProduto(filtros)
    return resultado


@app.route("/VwRelDadosDispositivo/<codigo>")
def get_RelVwRelDadosDispositivo(codigo):
    filtros = {
        "dtRegistro": request.args.get("dtRegistro"),
    }

    # Remove filtros que nao tem valor
    filtros = {k: v for k, v in filtros.items() if v is not None}

    # Adiciona o codigo como um filtro se for diferente de 0
    if codigo != "0":
        filtros["cdDispositivo"] = codigo

    resultado = Selecionar_VwRelDadosDispositivo(filtros)
    return resultado


# Selecionar registros no EndPoint TbProdutoTotalStaus
@app.route("/TbProdutoTotalStaus/<codigo>")
def get_TbProdutoTotalStaus(codigo):
    resultado = Selecionar_VwTbProdutoTotalStaus(codigo)
    return resultado


# https://replit.taxidigital.net/TbPosicaoAtual


# Selecionar registros no EndPoint TbPosicaoAtual
@app.route("/TbPosicaoAtual/<codigo>")
def get_TbPosicaoAtual(codigo):
    filtros = {"cdProduto": request.args.get("cdProduto")}

    # Remove filtros que nao tem valor
    filtros = {k: v for k, v in filtros.items() if v is not None}

    # Adiciona o codigo como um filtro se for diferente de 0
    if codigo != "0":
        filtros["cdDispositivo"] = codigo

    resultado = Selecionar_VwTbPosicaoAtual(filtros)
    return resultado


# Inserir registros no EndPoint TbProdutoTotalStaus
@app.route("/TbProdutoTotalStaus/", methods=["POST"])
def post_TbProdutoTotalStaus():
    payload = request.get_json()
    dsNome = payload["dsNome"]
    dsDescricao = payload["dsDescricao"]
    nrCodigo = payload["nrCodigo"]
    nrLarg = payload["nrLarg"]
    nrComp = payload["nrComp"]
    nrAlt = payload["nrAlt"]
    Status = payload["Status"]
    nrQtde = payload["nrQtde"]
    Inserir_VwTbProdutoTotalStaus(
        dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, Status, nrQtde
    )
    return payload


# FIM DA FUNÇÃO

# https://replit.taxidigital.net/Funcionario


# Selecionar registros no EndPoint Funcionario
@app.route("/Funcionario")
def get_Funcionario():
    resultado = Selecionar_TbFuncionario()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Funcionario
@app.route("/Funcionario", methods=["POST"])
def post_Funcionario():
    payload = request.get_json()
    dsBairro = payload["dsBairro"]
    dsCidade = payload["dsCidade"]
    dsComplemento = payload["dsComplemento"]
    dsFuncao = payload["dsFuncao"]
    dsLogradouro = payload["dsLogradouro"]
    dsNomeEmpregado = payload["dsNomeEmpregado"]
    dsNumCasa = payload["dsNumCasa"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    nrCodEmpregado = payload["nrCodEmpregado"]
    TbFuncionariocol = payload["TbFuncionariocol"]
    Inserir_TbFuncionario(
        dsBairro,
        dsCidade,
        dsComplemento,
        dsFuncao,
        dsLogradouro,
        dsNomeEmpregado,
        dsNumCasa,
        dsUser,
        dtRegistro,
        nrCodEmpregado,
        TbFuncionariocol,
    )
    return payload


# FIM DA FUNÇÃO

# Fim do Gerador de API

## atulizado em 04052024
##  FIM DA API GERADA AUTOMATICAMENTE###


@app.route("/Foto", methods=["POST"])
def post_Foto():
    payload = request.get_json()
    imgFoto = payload["imgFoto"]
    dsFoto = payload["dsFoto"]
    photo_data = base64.b64decode(imgFoto)
    with open(dsFoto, "wb") as fh:
        fh.write(photo_data)
    return payload


# FIM DA FUNÇÃO


@app.route("/CadastraImgProduto", methods=["POST"])
def CadastraImgProduto():

    file = request.files["arquivo"]
    pathfile = file.filename
    cdProduto = pathfile.split("-")[0]
    nrImagem = pathfile.split("-")[1]
    nrImagem = nrImagem.split(".")[0]
    file.save(pathfile)
    upload_file(pathfile, "dbfilesintellimetrics", "produtos/" + pathfile)
    os.remove(pathfile)
    payload = {
        "dsCaminho": "produtos/",
        "cdCodigo": pathfile,
        "cdTipo": 10,
        "dsUser": "TESTE",
        "cdProduto": int(cdProduto),
        "nrImagem": int(nrImagem),
    }
    data, error = valida_e_constroi_insert("TbImagens", payload)

    if error:
        return jsonify({"error": error}), 400
    resultado = Inserir_TbImagens(data)
    return resultado


@app.route("/upload", methods=["POST"])
def upload():
    # Verifica se há algum arquivo enviado na requisição
    if "images" not in request.files:
        return "Nenhum arquivo enviado", 400

    # Obtém a lista de arquivos enviados
    images = request.files.getlist("images")

    # Percorre a lista de arquivos
    for image in images:
        # Verifica se o arquivo é uma imagem válida
        if image.filename == "":
            return "Nome de arquivo inválido", 400
        if not allowed_file(image.filename):
            return "Tipo de arquivo inválido", 400

        # Grava a imagem no S3
        client = boto3.client("s3")
        client.upload_fileobj(image, "dbfilesintellimetrics/produtos", image.filename)

    return "Upload realizado com sucesso"


# Função auxiliar para verificar o tipo de arquivo permitido
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    # return "Cadastro ok "


@app.route("/Assinada", methods=["POST"])
def Assinada():
    payload = request.get_json()
    arquivo = payload["arquivo"]
    result = assinar_arquivo(arquivo)
    return result


# https://replit.taxidigital.net/AcessoIntelBras


# Selecionar registros no EndPoint AcessoIntelBras
@app.route("/AcessoIntelBras")
def get_AcessoIntelBras():
    resultado = Selecionar_TbAcessoIntelBras()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint AcessoIntelBras
@app.route("/AcessoIntelBras", methods=["POST"])
def post_AcessoIntelBras():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbCAcessoIntelBras", payload)

    if error:
        return jsonify({"error": error}), 400

    Inserir_TbAcessoIntelBras(data)
    return "Cadastramento realizado com sucesso"


# FIM DA FUNÇÃO


@app.route("/notification", methods=["POST"])
def event_receiver():
    if request.method == "POST":

        res = request.data
        data_list = res.split(b"--myboundary\r\n")

        if data_list:
            for a_info in data_list:
                if b"Content-Type" in a_info:
                    lines = a_info.split(b"\r\n")
                    a_type = lines[0].split(b": ")[1]

                    if a_type == b"image/jpeg":
                        # image_data = b"\r\n".join(lines[3:-3])
                        image_data = lines[3:-3]
                        print(image_data)
                    else:
                        text_data = b"\r\n".join(lines[3:-1])

        evento_str = text_data.decode("utf-8")
        evento_dict = ast.literal_eval(evento_str.replace("--myboundary--", " "))
        json_object = json.dumps(evento_dict, indent=4)
        resp_dict = json.loads(json_object)

        print(resp_dict)

        event_code = resp_dict.get("Events")[0].get("Code")
        print("################## ", event_code, " ##################")

        if event_code == "AccessControl":
            event_data = resp_dict.get("Events")[0].get("Data")

            card_name = event_data.get("CardName")
            card_no = event_data.get("CardNo")
            card_type = event_data.get("CardType")
            door = event_data.get("Door")
            error_code = event_data.get("ErrorCode")
            method = event_data.get("Method")
            reader_id = event_data.get("ReaderID")
            event_status = event_data.get("Status")
            event_type = event_data.get("Type")
            event_entry = event_data.get("Entry")
            event_utc = event_data.get("UTC")
            user_id = event_data.get("UserID")
            user_type = event_data.get("UserType")
            pwd = event_data.get("DynPWD")

            print("UserID: ", user_id)
            print("UserType", user_type)
            print("CardName: ", card_name)
            print("CardNo: ", card_no)
            print("CardType: ", card_type)
            print("Password: ", pwd)
            print("Door: ", door)
            print("ErrorCode: ", error_code)
            print("Method: ", method)
            print("ReaderID: ", reader_id)
            print("Status: ", event_status)
            print("Type: ", event_type)
            print("Entry: ", event_entry)
            print("UTC: ", event_utc)
            print(49 * "#")
            Inserir_TbAcessoIntelBras(
                card_name,
                card_no,
                door,
                event_entry,
                error_code,
                method,
                pwd,
                reader_id,
                event_status,
                event_type,
                user_id,
                user_type,
                event_utc,
            )

            # Exemplo de regras que podem ser implementadas
            time.sleep(1)
            if user_id == 19:
                return jsonify(
                    {
                        "message": "Pagamento não realizado!",
                        "code": "200",
                        "auth": "true",
                    }
                )
            elif card_no in [
                "EC56D271",
                "09201802",
            ]:  # Caso o código do cartão esteja listado libera o acesso
                return jsonify(
                    {"message": "Bem vindo !", "code": "200", "auth": "true"}
                )
            elif pwd != None:
                if int(pwd) == 222333:
                    return jsonify(
                        {"message": "Acesso Liberado", "code": "200", "auth": "true"}
                    )

        elif event_code == "DoorStatus":
            event_data = resp_dict.get("Events")[0].get("Data")

            door_status = event_data.get("Status")
            door_utc = event_data.get("UTC")

            print("Door Status: ", door_status)
            print("UTC", door_utc)
            print(20 * "#")
            return jsonify({"message": "xxxxxxx", "code": "200", "auth": "false"})

        elif event_code == "BreakIn":
            event_data = resp_dict.get("Events")[0].get("Data")

            door_name = event_data.get("Name")
            door_utc = event_data.get("UTC")

            print("Door Name: ", door_name)
            print("UTC", door_utc)
            print(49 * "#")
            return jsonify({"message": "", "code": "200", "auth": "false"})

    return jsonify({"message": "acesso ok entra", "code": "200", "auth": "false"})


@app.route("/keepalive", methods=["GET"])
def keep_alive():
    return "OK"


@app.route("/whats", methods=["GET", "POST"])
def whats_post():

    dic_whats = request.get_json()
    print(dic_whats)

    for campos in dic_whats:
        # print (campos)
        if campos == "contact_phone_number":
            print(dic_whats["contact_phone_number"])
        if campos == "message_body":
            # string_dados = "RT\tCidades\tEnt\tVeículo / OBS.\tM³  Do Carro\tCarregar\tRegião\tPeso R\tKM\t Valor da Tabela \tM³ Real\tManifesto\n1\tSÃO GONÇALO - SÃO PEDRO ALDEIA / \t2\t3/4 - 4M DE COMP - GAIOLAS - NOVA MUNDIAL\t25M\t GLP  MUNDIAL (GP1  GLP )\tSUDESTE\t857\t563\t R$ 1.995,74 \t26M\t22255\n2\t NOVA IGUAÇU\t2\tTRUCK - 7M DE COMP - GAIOLAS - NOVA MUNDIAL\t60M\t GLP  MUNDIAL (GLP GP1  )\tSUDESTE\t571\t368\t R$ 2.047,68 \t18M\t22259\n3\t LAGOA STA - PEDRO LEOPOLDO\t3\tTRUCK - 16 PALETS - GAIOLAS - NOVA MUNDIAL   MATRIZ\t60M\t MUNDIAL (GP1   )\tSUDESTE\t855\t648\t R$ 2.881,28 \t26M\t22260\n4\t RJ - REALENGO - VICENTE CARVALHO - MARE\t3\tTRUCK - 16 PALETS - GAIOLAS - NOVA MUNDIAL\t60M\t MUNDIAL (GP1   )\tSUDESTE\t1045\t408\t R$ 2.198,08 \t32M\t22262\n5\t RJ - STA CRUZ - DUQUE CAXIAS\t3\tTRUCK - 16 PALETS - GAIOLAS - NOVA MUNDIAL\t60M\t MUNDIAL (GP1   )\tSUDESTE\t1140\t407\t R$ 2.194,32 \t34M\t22263\n6\t PORTO ALEGRE\t1\tTRUCK - 14 PALETS - PALETIZADO\t60M\t MUNDIAL (GP1   )\tSUL\t3994\t1171\t R$ 3.674,66 \t59M\t22264\n10\t NOVA FRIBURGO - SERRA\t2\tVUC - 1 GAIOLA - DEMAIS BATIDAS\t15M\t MUNDIAL (GP1 GP2  )\tSUDESTE\t580\t934\t R$ 1.871,08 \t5M\t22270\n11\t BH\t6\tCARRETA - 18 GAIOLAS - NOVA MATRIZ\t95M\t MUNDIAL (GP1   )\tSUDESTE\t1710\t587\t R$ 5.379,54 \t51M\t22271\n12\t CONTAGEM - BETIM - STA LUZIA - VESPASIANO\t7\tCARRETA - 17 GAIOLAS - NOVA MATRIZ   GLP\t95M\t GLP  MUNDIAL (GLP GP1  )\tSUDESTE\t1616\t659\t R$ 6.069,78 \t49M\t22272\n13\t SABARA -RIBEIRAO DAS NEVES\t2\tTRUCK - 7M DE COMP - GAIOLAS - NOVA MUNDIAL\t60M\t MUNDIAL (GP1   )\tSUDESTE\t570\t664\t R$ 2.935,04 \t17M\t22273"
            string_dados = dic_whats["message_body"]
            print(string_dados)
            linhas = string_dados.split("\n")  # Dividir a string em linhas

            dados_json = []

            for linha in linhas:
                campos = linha.split(
                    "\t"
                )  # Dividir cada linha em campos usando o separador de tabulação
                rota = campos[0]
                print(rota)
                cidade = campos[1]
                entrega = campos[2]
                veiculo = campos[3]
                # print(veiculo)
                metro = campos[4]
                carregar = campos[5]
                regiao = campos[6]
                peso = campos[7]
                km = campos[8]
                # print(km)
                valor = campos[9]
                mreal = campos[10]
                manifesto = campos[11]

                # Criar um dicionário com os campos e adicionar à lista de dados JSON
                dados = {
                    "rota": rota,
                    "cidade": cidade,
                    "entrega": entrega,
                    "veiculo": veiculo,
                    "metro": metro,
                    "carregar": carregar,
                    "regiao": regiao,
                    "peso": peso,
                    "km": km,
                    "valor": valor,
                    "mreal": mreal,
                    "manifesto": manifesto,
                }
                dados_json.append(dados)

                for campos in dados_json:

                    if "fiorino" in (campos["veiculo"]).lower() and 400 > int(
                        campos["km"]
                    ):
                        msg = (
                            "Rota "
                            + campos["rota"]
                            + " Veiculo "
                            + campos["veiculo"]
                            + " Km "
                            + (campos["km"])
                            + " Valor "
                            + (campos["valor"])
                        )
                        envia_whatstexto("Olá eu quero essa viagem ! " + msg)

            # Converter a lista de dados JSON em uma string JSON formatada
            json_str = json.dumps(dados_json, indent=4)

        # print(dic_whats['message_body'])
    return "msg"


@app.route("/Medidas", methods=["GET"])
def get_Medidas():
    medidas = Pegar_Medidas()
    resultado = medidas

    return resultado


# FIM DA FUNÇÃO


@app.route("/medidassensor", methods=["GET", "POST"])
def dados():
    payload = request.get_json()
    altura = payload["altura"]
    largura = payload["largura"]
    comprimento = payload["comprimento"]
    pesoreal = payload["pesoreal"]
    cubado = payload["cubado"]
    # print(altura, largura,comprimento, pesoreal, cubado)
    guarda_medidas(altura, largura, comprimento, pesoreal, cubado)
    dic_altura = {
        "altura": altura,
        "largura": largura,
        "comprimento": comprimento,
        "pesoreal": pesoreal,
        "cubado": cubado,
    }
    # print(dic_altura)
    return dic_altura


# FIM DA FUNÇÃO


# app.run(port=8080, host='0.0.0.0', debug=True, threaded=True)
# app.run(host="0.0.0.0")  # coloca o site no ar#


def main():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="127.0.0.1", port=port, debug=True)


# port = int(os.environ.get("PORT", 80))
# app.run(host="192.168.15.200", port=port)


if __name__ == "__main__":
    main()
