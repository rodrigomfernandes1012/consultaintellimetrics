# SERVER API
import base64
import datetime
from random import random
import random
from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS
import json
import mysql.connector
import requests
import boto3
import os
import ast
import time
import re
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime, timedelta



# Amazon
selecao = []
dicionario = []
dic2 = []
dic_whats = []
dic_whats2 = []
dic_altura = []


token = "8c4EF9vXi8TZe6581e0af85c25"


def conecta_bd():
    conexao = mysql.connector.connect(
        host="dbintellimetrics.c3kc6gou2fhz.us-west-2.rds.amazonaws.com",
        user="admin",
        password="IntelliMetr!c$",
        database="DbIntelliMetrics",
    )
    return conexao
def obter_ip_publico():
    # Verifica o cabeçalho X-Forwarded-For
    ip = request.headers.get('X-Forwarded-For')
    if ip:
        # O X-Forwarded-For pode retornar uma lista de IPs; pegamos o primeiro
        ip = ip.split(',')[0]
    else:
        # Se não houver X-Forwarded-For, pega o remote_addr
        ip = request.remote_addr

    return ip

def Inserir_TbLog(dsTbAcesso, dsAcao, dsIp,  dsLogin):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbLog (dsTbAcesso, dsAcao, dsIp, dsLogin) values ("{dsTbAcesso}", "{dsAcao}", "{dsIp}", "{dsLogin}")'
    cursor.execute(comando)
    conexao.commit()
    cursor.close()
    conexao.close()
    username = dsLogin
    return username



def assinar_arquivo(arquivo):
    url = boto3.client("s3").generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": "dbfilesintellimetrics", "Key": arquivo},
        ExpiresIn=3600,
    )
    return url


# assinar_arquivo()


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


# Selecionar registros da tabela DbIntelliMetrics.TbAcessoIntelBras
def Selecionar_TbAcessoIntelBras():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdAcessoIntelBras, dsCardName, dsCardNo, dsDoor, dsEntry, dsErrorCode, dsMethod, dsPassword, dsReaderID, dsStatus, dsType, dsUserId, dsUserType, dsUtc from DbIntelliMetrics.TbAcessoIntelBras"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado



def Selecionar_TbPonto():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdPonto, cdAcessoIntelbras, dsCardNo, dsCardName, DATE_FORMAT(STR_TO_DATE(dsRegistro01, '%Y-%m-%d %H:%i:%s'), '%d/%m/%Y') AS dsData,  DATE_FORMAT(STR_TO_DATE(dsRegistro01, '%Y-%m-%d %H:%i:%s'), '%H:%i') AS dsRegistro01, DATE_FORMAT(STR_TO_DATE(dsRegistro02, '%Y-%m-%d %H:%i:%s'), '%H:%i') AS dsRegistro02, DATE_FORMAT(STR_TO_DATE(dsRegistro03, '%Y-%m-%d %H:%i:%s'), '%H:%i') AS dsRegistro03, DATE_FORMAT(STR_TO_DATE(dsRegistro04, '%Y-%m-%d %H:%i:%s'), '%H:%i') AS dsRegistro04, DATE_FORMAT(STR_TO_DATE(dsRegistro05, '%Y-%m-%d %H:%i:%s'), '%H:%i') AS dsRegistro05, DATE_FORMAT(STR_TO_DATE(dsRegistro06, '%Y-%m-%d %H:%i:%s'), '%H:%i') AS dsRegistro06, dtRegistro  from DbIntelliMetrics.TbPonto;"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado






def Selecionar_VwTbDestinatarioDispositivo(codigoDisp):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdDestinatario, dsLat, dsLong, nrRaio, cdFilho from DbIntelliMetrics.VwTbDestinatarioDispositivo where cdFilho ={codigoDisp} "
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO
def obter_ip_publico():
    # Verifica o cabeçalho X-Forwarded-For
    ip = request.headers.get('X-Forwarded-For')
    if ip:
        # O X-Forwarded-For pode retornar uma lista de IPs; pegamos o primeiro
        ip = ip.split(',')[0]
    else:
        # Se não houver X-Forwarded-For, pega o remote_addr
        ip = request.remote_addr

    return ip

# Inserir registros da tabela DbIntelliMetrics.TbAcessoIntelBras
def Inserir_TbAcessoIntelBras(
    dsCardName,
    dsCardNo,
    dsDoor,
    dsEntry,
    dsErrorCode,
    dsMethod,
    dsPassword,
    dsReaderID,
    dsStatus,
    dsType,
    dsUserId,
    dsUserType,
    dsUtc,
):
    dsIp = obter_ip_publico()
    print(dsIp)
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbAcessoIntelBras ( dsCardName, dsCardNo, dsDoor, dsEntry, dsErrorCode, dsMethod, dsPassword, dsReaderID, dsStatus, dsType, dsUserId, dsUserType, dsUtc, dsIp ) values ("{dsCardName}", "{dsCardNo}", "{dsDoor}", "{dsEntry}", "{dsErrorCode}", "{dsMethod}", "{dsPassword}", "{dsReaderID}", "{dsStatus}", "{dsType}", "{dsUserId}", "{dsUserType}", "{dsUtc}", "{dsIp}")'
    cursor.execute(comando)
    conexao.commit()
    cursor.close()
    conexao.close()
    datacompleta = (int(dsUtc)) - 10800
    data = (datetime.utcfromtimestamp(datacompleta).strftime('%Y-%m-%d %H:%M:%S'))
    print("cheguei em gravar no banco tabela intelbras")
    #if dsStatus == 1:
    Inserir_TbPonto(dsCardNo,dsCardName, data,dsUtc)
    return resultado





def Alterar_TbPonto(cdPonto, dsRegistro01, dsRegistro02, dsRegistro03,dsRegistro04):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"update DbIntelliMetrics.TbPonto set dsRegistro01 = '{dsRegistro01}', dsRegistro02 = '{dsRegistro02}', dsRegistro03 = '{dsRegistro03}', dsRegistro04 = '{dsRegistro04}' where cdPonto = '{cdPonto}'"
    cursor.execute(comando)
    conexao.commit()
    cursor.close()
    conexao.close()

#def Inserir_TbPonto(dsCardNo, dsCardName, dsUtc):
#    conexao = conecta_bd()
#    cursor = conexao.cursor()
#    comando = f"insert into DbIntelliMetrics.TbPonto ( dsCardNo, dsCardName, dsRegistro01, dsTipoRegistro, dsObservacao ) values ('{dsCardNo}', '{dsCardName}', '{dsUtc}','','')"
#    print(comando)
#    cursor.execute(comando)
#    conexao.commit()
#    cursor.close()
#    conexao.close()
def Inserir_TbPonto(dsCardNo, dsCardName, dsData, cdAcesso):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)

    if isinstance(dsData, str):  # Convert to datetime if dsData is a string
        dsDataHora = datetime.strptime(dsData, "%Y-%m-%d %H:%M:%S")
        dsData = datetime.strptime(dsData, "%Y-%m-%d %H:%M:%S").date()
        print(dsData)

    # Primeiro, consultar registros existentes para o dsCardNo na mesma data
    consulta = f"""
        SELECT dsRegistro01, dsRegistro02, dsRegistro03, dsRegistro04, dsRegistroAut
        FROM DbIntelliMetrics.TbPonto
        WHERE    dsCardNo = '{dsCardNo}' AND DATE(dsRegistroAut) = DATE('{dsData}')
        """
    print(consulta)
    cursor.execute(consulta)
    resultado = cursor.fetchone()
    # cursor.close()
    # conexao.close()
    if resultado:
        slots = ['dsRegistro01', 'dsRegistro02', 'dsRegistro03', 'dsRegistro04']
        slots.sort()
        for slot in slots:
            if resultado[slot]:
                registro_existente_horario = resultado[slot]
                print(registro_existente_horario)
                #print(dsDataHora)
                # Verifique se a diferença é menor que 6 minutos
                if abs(dsDataHora - registro_existente_horario) < timedelta(minutes=6):
                    print(f"Registro ignorado: diferença de horário menor que 6 minutos para {slot}.")

                    return
            else:
                # Se o slot está vazio, insere aqui

                conexao = conecta_bd()
                cursor = conexao.cursor()
                update_comando = f"""
                    UPDATE DbIntelliMetrics.TbPonto
                    SET {slot} = '{dsDataHora.strftime("%Y-%m-%d %H:%M:%S")}'
                    WHERE   dsCardNo = '{dsCardNo}' AND dsRegistroAut = '{resultado['dsRegistroAut']}'
                    """
                print(update_comando)
                print("primeiro update")

                cursor.execute(update_comando)

                conexao.commit()
                cursor.close()
                conexao.close()
                return

        print("Todos os horários de registro estão ocupados para hoje ou a diferença de tempo é menor que 6 minutos.")
    else:
        # Se não houver registros ou todos são inválidos, inserir um novo
        conexao = conecta_bd()
        cursor = conexao.cursor()
        comando = f"""
            INSERT INTO DbIntelliMetrics.TbPonto (dsCardNo, dsCardName, dsRegistro01, dsTipoRegistro, dsObservacao, cdAcessoIntelBras, stStatus, dsRegistroAut)
            VALUES ('{dsCardNo}', '{dsCardName}', '{dsDataHora.strftime("%Y-%m-%d %H:%M:%S")}', '', '', '{cdAcesso}',1,DATE('{dsData}'))
            """
        print(comando)
        print("fiz insert")
        cursor.execute(comando)
        conexao.commit()
        cursor.close()
        conexao.close()


#Inserir_TbAcessoIntelBras("rodrigo","17439772801","1","",0,25,"",1,'1',"Entry","17439772806",0,"1722531607")

# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbAcessoIntelBras
def deletar_TbAcessoIntelBras(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbAcessoIntelBras where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbAcessoIntelBras
def Alterar_TbAcessoIntelBras(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbAcessoIntelBras set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


def calcular_distancia(lat1, lon1, lat2, lon2):
    geolocator = Nominatim(user_agent="my_app")
    distancia = geodesic((lat1, lon1), (lat2, lon2)).kilometers
    return distancia


# distancia = calcular_distancia("-23.5006347","-46.4884689","-23.5331802","-46.4659015")
# distancia = calcular_distancia(lat1, lon1, lat2, lon2)


# Selecionar registros da tabela DbIntelliMetrics.VwTbPosicaoAtual
def Selecionar_VwTbPosicaoAtual(filtros):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)

    comando = f"select cdPosicao, \
    dtRegistro,\
    cdDispositivo,\
    dsLat,\
    dsLong,\
    dsEndereco,\
    dsNum,\
    dsCep,\
    dsBairro,\
    dsCidade,\
    dsUF,\
    dsPais,\
    nrBat,\
    nrCodigo,\
    cdProduto,\
    dsProduto,\
    dsDescricao,\
    dsStatus,\
    blArea\
    from DbIntelliMetrics.VwTbPosicaoAtual WHERE 1=1"

    for campo, valor in filtros.items():
        comando += f" AND {campo} = '{valor}'"

    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbChamados
def Selecionar_TbChamados():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdChamados, dtOperacao, dsTipo, dsDescricao, nrQtde, dsUser, dtRegistro from DbIntelliMetrics.TbChamados"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbChamados
def Inserir_TbChamados(dtOperacao, dsTipo, dsDescricao, nrQtde, dsUser, dtRegistro):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbChamados ( dtOperacao, dsTipo, dsDescricao, nrQtde, dsUser, dtRegistro ) values ("{dtOperacao}", "{dsTipo}", "{dsDescricao}", "{nrQtde}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbChamados
def deletar_TbChamados(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbChamados where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbChamados
def Alterar_TbChamados(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbChamados set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbCliente
def Selecionar_TbCliente():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdCliente, dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus, dsUser, dtRegistro from DbIntelliMetrics.TbCliente"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbCliente
def Inserir_TbCliente(
    dsNome,
    nrCnpj,
    nrIe,
    nrInscMun,
    dsLogradouro,
    nrNumero,
    dsComplemento,
    dsBairro,
    dsCep,
    dsCidade,
    dsUF,
    dsObs,
    cdStatus,
    dsUser,
    dtRegistro,
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbCliente ( dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus, dsUser, dtRegistro ) values ("{dsNome}", "{nrCnpj}", "{nrIe}", "{nrInscMun}", "{dsLogradouro}", "{nrNumero}", "{dsComplemento}", "{dsBairro}", "{dsCep}", "{dsCidade}", "{dsUF}", "{dsObs}", "{cdStatus}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbCliente
def deletar_TbCliente(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbCliente where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbCliente
def Alterar_TbCliente(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbCliente set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbDestinatario
def Selecionar_TbDestinatario(codigo):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    if codigo == "0":
        comando = f"select cdDestinatario, dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus, dsLat, dsLong, nrRaio, dsUser, dtRegistro from DbIntelliMetrics.TbDestinatario"
    else:
        comando = f"select cdDestinatario, dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus, dsLat, dsLong, nrRaio, dsUser, dtRegistro from DbIntelliMetrics.TbDestinatario where cdDestinatario ={codigo}"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


def Selecionar_Lat_Long_Destinatario(codigo):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"SELECT cdDestinatario, dsLat, dsLong, cdFilho FROM DbIntelliMetrics.VwTbDestinatarioDispositivo where cdFilho ={codigo}"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# print(Selecionar_Lat_Long_Destinatario(2))


# Inserir registros da tabela DbIntelliMetrics.TbDestinatario
def Inserir_TbDestinatario(
    dsNome,
    nrCnpj,
    nrIe,
    nrInscMun,
    dsLogradouro,
    nrNumero,
    dsComplemento,
    dsBairro,
    dsCep,
    dsCidade,
    dsUF,
    dsObs,
    cdStatus,
    dsLat,
    dsLong,
    nrRaio,
    dsUser,
    dtRegistro,
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbDestinatario ( dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus, dsLat, dsLong, nrRaio, dsUser, dtRegistro ) values ("{dsNome}", "{nrCnpj}", "{nrIe}", "{nrInscMun}", "{dsLogradouro}", "{nrNumero}", "{dsComplemento}", "{dsBairro}", "{dsCep}", "{dsCidade}", "{dsUF}", "{dsObs}", "{cdStatus}", "{dsLat}", "{dsLong}", "{nrRaio}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbDestinatario
def deletar_TbDestinatario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbDestinatario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbDestinatario
def Alterar_TbDestinatario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbDestinatario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbDispositivo
def Selecionar_TbDispositivo(codigo):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    if codigo == 0:
        comando = f"select cdDispositivo, dsDispositivo, dsModelo, dsDescricao, dsObs, dsLayout, nrChip, cdStatus, dsUser, dtRegistro from DbIntelliMetrics.TbDispositivo"
    else:
        comando = f"select cdDispositivo, dsDispositivo, dsModelo, dsDescricao, dsObs, dsLayout, nrChip, cdStatus, dsUser, dtRegistro from DbIntelliMetrics.TbDispositivo where cdDispositivo={codigo}"

    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbDispositivo
def Inserir_TbDispositivo(
    dsDispositivo,
    dsModelo,
    dsDescricao,
    dsObs,
    dsLayout,
    nrChip,
    cdStatus,
    dsUser,
    dtRegistro,
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbDispositivo ( dsDispositivo, dsModelo, dsDescricao, dsObs, dsLayout, nrChip, cdStatus, dsUser, dtRegistro ) values ("{dsDispositivo}", "{dsModelo}", "{dsDescricao}", "{dsObs}", "{dsLayout}", "{nrChip}", "{cdStatus}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbDispositivo
def deletar_TbDispositivo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbDispositivo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbDispositivo
def Alterar_TbDispositivo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbDispositivo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbImagens
def Selecionar_TbImagens(codigo):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    if codigo == "0":
        comando = f"select cdImagens, dsCaminho, cdCodigo, cdTipo, dsUser, dtRegistro from DbIntelliMetrics.TbImagens"
    else:
        comando = f'select cdImagens, dsCaminho, cdCodigo, cdTipo, dsUser, dtRegistro from DbIntelliMetrics.TbImagens where SUBSTRING_INDEX(cdCodigo, "-", 1) ={codigo}'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbImagens
def Inserir_TbImagens(
    dsCaminho, cdCodigo, cdTipo, dsUser, dtRegistro, cdProduto, nrImagem
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbImagens ( dsCaminho, cdCodigo, cdTipo, dsUser, dtRegistro, cdProduto, nrImagem ) values ("{dsCaminho}", "{cdCodigo}", "{cdTipo}", "{dsUser}", "{dtRegistro}", "{cdProduto}", "{nrImagem}")'
    # print(comando)
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbImagens
def deletar_TbImagens(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbImagens where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbImagens
def Alterar_TbImagens(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbImagens set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO#


# Selecionar registros da tabela DbIntelliMetrics.TbPosicao
# def Selecionar_TbPosicao(codigo):
#     conexao = conecta_bd()
#     cursor = conexao.cursor(dictionary=True)

#     if codigo == '0':
#         comando = f'select cdPosicao, dsModelo, dtData, dtHora, dsLat, dsLong, nrTemp, nrBat, nrSeq, dsArquivo, cdDispositivo, dsEndereco, dtRegistro from DbIntelliMetrics.TbPosicao'
#     else:
#         comando = f'select cdPosicao, dsModelo, dtData, dtHora, dsLat, dsLong, nrTemp, nrBat, nrSeq, dsArquivo, cdDispositivo, dsEndereco, dtRegistro from DbIntelliMetrics.TbPosicao where cdDispositivo={codigo}'
#     cursor.execute(comando)
#     resultado = cursor.fetchall()
#     cursor.close()
#     conexao.close()
#     return  resultado
# FIM DA FUNÇÃO

# Selecionar_TbDestinatario()


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
        return (dsLogradoruro, dsNum, dsBairro, dsCidade, dsUF, dsCep, dsPais)


# get_endereco_coordenada(lat, long)


# Inserir registros da tabela DbIntelliMetrics.TbPosicao
def Inserir_TbPosicao(
    dsModelo,
    dtData,
    dtHora,
    dsLat,
    dsLong,
    nrTemp,
    nrBat,
    nrSeq,
    dsArquivo,
    cdDispositivo,
    dsEndereco,
    dsNum,
    dsBairro,
    dsCidade,
    dsUF,
    dsCep,
    dsPais,
    dsLatPdv,
    dsLongPdv,
    nrRaio,
    blArea,
    nrDistancia,
    dsUser,
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbPosicao ( dsModelo, dtData, dtHora, dsLat, dsLong, nrTemp, nrBat, nrSeq, dsArquivo, cdDispositivo, dsEndereco, dsNum, dsBairro, dsCidade,  dsUF, dsCep, dsPais,  dsLatPdv, dsLongPdv, nrRaio, blArea, nrDistancia, dsUser ) values ("{dsModelo}", "{dtData}", "{dtHora}", "{dsLat}", "{dsLong}", "{nrTemp}", "{nrBat}", "{nrSeq}", "{dsArquivo}", "{cdDispositivo}", "{dsEndereco}", "{dsNum}", "{dsBairro}", "{dsCidade}", "{dsUF}", "{dsCep}","{dsPais}", "{dsLatPdv}", "{dsLongPdv}", "{nrRaio}", "{blArea}", "{nrDistancia}", "{dsUser}")'
    # print(comando)
    cursor.execute(comando)
    conexao.commit()
    return cursor.lastrowid

def Alterar_StatusTbPosicao(codigo, status):
    conexao = conecta_bd()
    cursor = conexao.cursor()
    comando = f'update DbIntelliMetrics.TbDispositivo set cdStatus= {status}  where cdDispositivo = {codigo}  '
    cursor.execute(comando)
    conexao.commit()



def Inserir_TbSensorRegistro(cdDispositivo, cdSensor, cdPosicao, nrValor):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbSensorRegistro (cdDispositivo, cdSensor, cdPosicao, nrValor) values ("{cdDispositivo}", "{cdSensor}", "{cdPosicao}", "{nrValor}")'
    cursor.execute(comando)
    conexao.commit()
    return cursor.lastrowid


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbPosicao
def deletar_TbPosicao(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbPosicao where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbPosicao
def Alterar_TbPosicao(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbPosicao set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbProduto
def Selecionar_TbProduto(codigo):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    # Consulta os dados da tabela produtos
    comando = f"SELECT cdProduto, dsDescricao, dsNome, nrAlt, nrCodigo, nrComp, nrLarg, nrQtde, dsStatus FROM VwTbProdutoTotalStaus where cdProduto = {codigo}"
    cursor.execute(comando)
    produtos = cursor.fetchall()

    # Array para armazenar os resultados
    produtos_json = []

    # Percorre os produtos
    for produto in produtos:
        (
            cdProduto,
            dsDescricao,
            dsNome,
            nrAlt,
            nrCodigo,
            nrComp,
            nrLarg,
            nrQtde,
            dsStatus,
        ) = produto

        # Consulta os dados da tabela imagens para o produto atual
        comando = (
            f"SELECT cdCodigo, dsCaminho  FROM TbImagens WHERE cdProduto = {codigo}"
        )
        # query = "SELECT cdCodigo, dsCaminho  FROM TbImagens WHERE cdImagens = 26"
        cursor.execute(comando)
        imagens = cursor.fetchall()

        # Array para armazenar as imagens
        imagens_array = []

        # Percorre as imagens e adiciona ao array
        for imagem in imagens:
            cdCodigo, dsCaminho = imagem
            imagens_array.append({"cdImagens": cdCodigo, "dsCaminho": dsCaminho})

        # Cria um dicionário com os dados do produto e o array de imagens
        produto_json = {
            "cdProduto": cdProduto,
            "dsDescricao": dsDescricao,
            "dsNome": dsNome,
            "nrAlt": nrAlt,
            "nrCodigo": nrCodigo,
            "nrComp": nrComp,
            "nrLarg": nrLarg,
            "nrQtde": nrQtde,
            "dsStatus": dsStatus,
            "imagens": imagens_array,
        }
        # produtos_json.append(produto_json)
        produtos_json.append(produto)
        produtos_json.append(imagens_array)

    # Fecha a conexão com o banco de dados
    cursor.close()
    conexao.close()
    return jsonify(produtos_json)


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbProduto
def Inserir_TbProduto(
    dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus, dsUser, dtRegistro
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbProduto ( dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus, dsUser, dtRegistro ) values ("{dsNome}", "{dsDescricao}", "{nrCodigo}", "{nrLarg}", "{nrComp}", "{nrAlt}", "{cdStatus}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()
    return cursor.lastrowid


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbProduto
def deletar_TbProduto(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbProduto where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbRelacionamento
def Selecionar_TbRelacionamento():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdRelacionamento, cdPai, cdFilho, cdTipo, dsDescricao, cdStatus, dsUser, dtRegistro from DbIntelliMetrics.TbRelacionamento"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbRelacionamento
def Inserir_TbRelacionamento(
    cdPai, cdFilho, cdTipo, dsDescricao, cdStatus, dsUser, dtRegistro
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbRelacionamento ( cdPai, cdFilho, cdTipo, dsDescricao, cdStatus, dsUser, dtRegistro ) values ("{cdPai}", "{cdFilho}", "{cdTipo}", "{dsDescricao}", "{cdStatus}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbRelacionamento
def deletar_TbRelacionamento(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbRelacionamento where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbRelacionamento
def Alterar_TbRelacionamento(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbRelacionamento set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbSensor
def Selecionar_TbSensor():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdSensor, dsNome, cdTipo, dsDescricao, cdUnidade, nrUnidadeIni, nrUnidadeFim, dsUser, dtRegistro from DbIntelliMetrics.TbSensor"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbSensor
def Inserir_TbSensor(
    dsNome,
    cdTipo,
    dsDescricao,
    cdUnidade,
    nrUnidadeIni,
    nrUnidadeFim,
    dsUser,
    dtRegistro,
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbSensor ( dsNome, cdTipo, dsDescricao, cdUnidade, nrUnidadeIni, nrUnidadeFim, dsUser, dtRegistro ) values ("{dsNome}", "{cdTipo}", "{dsDescricao}", "{cdUnidade}", "{nrUnidadeIni}", "{nrUnidadeFim}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbSensor
def deletar_TbSensor(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbSensor where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbSensor
def Alterar_TbSensor(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbSensor set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbStatus
def Selecionar_TbStatus():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = (
        f"select cdStatus, dsStatus, dsUser, dtRegistro from DbIntelliMetrics.TbStatus"
    )
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbStatus
def Inserir_TbStatus(dsStatus, dsUser, dtRegistro):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbStatus ( dsStatus, dsUser, dtRegistro ) values ("{dsStatus}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbStatus
def deletar_TbStatus(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbStatus where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbStatus
def Alterar_TbStatus(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbStatus set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbTag
def Selecionar_TbTag():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdTag, dsDescricao, dsConteudo, dsUser, dtRegistro from DbIntelliMetrics.TbTag"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbTag
def Inserir_TbTag(dsDescricao, dsConteudo, dsUser, dtRegistro):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbTag ( dsDescricao, dsConteudo, dsUser, dtRegistro ) values ("{dsDescricao}", "{dsConteudo}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbTag
def deletar_TbTag(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbTag where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbTag
def Alterar_TbTag(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbTag set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbTicket
def Selecionar_TbTicket():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdTicket, dtOperacao, dsAtendimento, nrAbertos, nrFechados, nrPendentes, dsUser, dtRegistro from DbIntelliMetrics.TbTicket"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbTicket
def Inserir_TbTicket(
    dtOperacao, dsAtendimento, nrAbertos, nrFechados, nrPendentes, dsUser, dtRegistro
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbTicket ( dtOperacao, dsAtendimento, nrAbertos, nrFechados, nrPendentes, dsUser, dtRegistro ) values ("{dtOperacao}", "{dsAtendimento}", "{nrAbertos}", "{nrFechados}", "{nrPendentes}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbTicket
def deletar_TbTicket(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbTicket where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbTicket
def Alterar_TbTicket(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbTicket set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbTicketResumo
def Selecionar_TbTicketResumo():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdTicketResumo, dtOperacao, dsAtendimento, dsNaoAtribuido, dsSemResolucao, dsAtualizado, dsPendente, dsResolvido, dsUser, dtRegistro from DbIntelliMetrics.TbTicketResumo"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbTicketResumo
def Inserir_TbTicketResumo(
    dtOperacao,
    dsAtendimento,
    dsNaoAtribuido,
    dsSemResolucao,
    dsAtualizado,
    dsPendente,
    dsResolvido,
    dsUser,
    dtRegistro,
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbTicketResumo ( dtOperacao, dsAtendimento, dsNaoAtribuido, dsSemResolucao, dsAtualizado, dsPendente, dsResolvido, dsUser, dtRegistro ) values ("{dtOperacao}", "{dsAtendimento}", "{dsNaoAtribuido}", "{dsSemResolucao}", "{dsAtualizado}", "{dsPendente}", "{dsResolvido}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbTicketResumo
def deletar_TbTicketResumo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbTicketResumo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbTicketResumo
def Alterar_TbTicketResumo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbTicketResumo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbTipo
def Selecionar_TbTipo():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = (
        f"select cdTipo, dsDescricao, dsUser, dtRegistro from DbIntelliMetrics.TbTipo"
    )
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbTipo
def Inserir_TbTipo(dsDescricao, dsUser, dtRegistro):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbTipo ( dsDescricao, dsUser, dtRegistro ) values ("{dsDescricao}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbTipo
def deletar_TbTipo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbTipo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbTipo
def Alterar_TbTipo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbTipo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbUnidade
def Selecionar_TbUnidade():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdUnidade, dsUnidade, dsSimbolo, dsUser, dtRegistro from DbIntelliMetrics.TbUnidade"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbUnidade
def Inserir_TbUnidade(dsUnidade, dsSimbolo, dsUser, dtRegistro):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbUnidade ( dsUnidade, dsSimbolo, dsUser, dtRegistro ) values ("{dsUnidade}", "{dsSimbolo}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbUnidade
def deletar_TbUnidade(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbUnidade where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbUnidade
def Alterar_TbUnidade(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbUnidade set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbUsuario
def Selecionar_TbUsuario():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdUsuario, dsNome, dsLogin, dsSenha, cdPerfil, dsUser, dtRegistro from DbIntelliMetrics.TbUsuario"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbUsuario
def Inserir_TbUsuario(dsNome, dsLogin, dsSenha, cdPerfil, dsUser, dtRegistro):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbUsuario ( dsNome, dsLogin, dsSenha, cdPerfil, dsUser, dtRegistro ) values ("{dsNome}", "{dsLogin}", "{dsSenha}", "{cdPerfil}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbUsuario
def deletar_TbUsuario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbUsuario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbUsuario
def Alterar_TbUsuario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbUsuario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbVisita
def Selecionar_TbVisita():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdVisita, cdCliente, cdVisitante, dtData, dsUser, dtRegistro from DbIntelliMetrics.TbVisita"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbVisita
def Inserir_TbVisita(cdCliente, cdVisitante, dtData, dsUser, dtRegistro):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbVisita ( cdCliente, cdVisitante, dtData, dsUser, dtRegistro ) values ("{cdCliente}", "{cdVisitante}", "{dtData}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbVisita
def deletar_TbVisita(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbVisita where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbVisita
def Alterar_TbVisita(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbVisita set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbVisitante
def Selecionar_TbVisitante():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdVisitante, dsNome, nrTelefone, nrDocumento, dsEmail, dsUser, dtRegistro from DbIntelliMetrics.TbVisitante"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbVisitante
def Inserir_TbVisitante(dsNome, nrTelefone, nrDocumento, dsEmail, dsUser, dtRegistro):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbVisitante ( dsNome, nrTelefone, nrDocumento, dsEmail, dsUser, dtRegistro ) values ("{dsNome}", "{nrTelefone}", "{nrDocumento}", "{dsEmail}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbVisitante
def deletar_TbVisitante(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbVisitante where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbVisitante
def Alterar_TbVisitante(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbVisitante set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbPosicao
def Selecionar_TbPosicao(filtros):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)

    # Inicializa a consulta SQL básica
    comando = "SELECT dtData, dtHora, dsLat, dsLong, nrTemp, nrBat, dsEndereco, dtRegistro FROM DbIntelliMetrics.TbPosicao WHERE 1=1"
    # Adiciona condições à consulta SQL com base nos filtros fornecidos
    for campo, valor in filtros.items():
        if campo == "dtRegistro":
            campo = f"DATE({campo})"
            valor = f"{valor[:4]}-{valor[4:6]}-{valor[6:]}"
        comando += f" AND {campo} = '{valor}'"

    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbPosicao
def deletar_TbPosicao(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbPosicao where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbPosicao
def Alterar_TbPosicao(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbPosicao set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


def Selecionar_VwRelHistoricoDispositivoProduto(filtros):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)

    comando = f"select cdProduto, nrCodigo, dsDescricao, dtRegistro, cdDispositivo, dsNome, dsEndereco, nrBatPercentual, nrPorta, nrTemperatura, dsProdutoItem, nrQtdItens, dsStatus, dsStatusDispositivo, cdSensor from VwRelHistoricoDispositivoProduto where 1=1"
    # Adiciona condições à consulta SQL com base nos filtros fornecidos
    for campo, valor in filtros.items():
        if campo == "dtRegistro":
            campo = f"DATE({campo})"
            valor = f"{valor[:4]}-{valor[4:6]}-{valor[6:]}"
        comando += f" AND {campo} = '{valor}'"

    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()

    return resultado

# busca dados de VwRelHistoricoDispositivoProduto, mas retorna cada produtoItem como uma coluna.
def Selecionar_HistoricoPaginaDispositivo(filtros):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)

    comando = f"select cdProduto, nrCodigo, dsDescricao, dtRegistro, cdDispositivo, dsNome, dsEndereco, nrBatPercentual, nrPorta, nrTemperatura, dsProdutoItem, nrQtdItens, dsStatus, dsStatusDispositivo, cdSensor from VwRelHistoricoDispositivoProduto where 1=1"
    # Adiciona condições à consulta SQL com base nos filtros fornecidos
    for campo, valor in filtros.items():
        if campo == "dtRegistro":
            campo = f"DATE({campo})"
            valor = f"{valor[:4]}-{valor[4:6]}-{valor[6:]}"
        comando += f" AND {campo} = '{valor}'"

    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    
    if len(resultado) == 0:
        return resultado

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(resultado)
    
    # Retain the original data for merging later
    original_df = df.drop(columns=['nrQtdItens', 'dsProdutoItem', 'cdSensor']).drop_duplicates()
    
    # Pivot the data
    pivot_df = df.pivot_table(index='dtRegistro', columns=['dsProdutoItem', 'cdSensor'], values='nrQtdItens', fill_value=0)
    
    # Flatten the multi-index columns
    pivot_df.columns = [f"{item[0]}_{item[1]}" for item in pivot_df.columns]
    
    # Reset index to have dtRegistro as a column again
    pivot_df = pivot_df.reset_index()
    
    # Merge the pivoted data with the original data
    final_df = pd.merge(original_df, pivot_df, on='dtRegistro', how='left')
    
    result_json = final_df.to_json(orient='records', date_format='iso')

    return result_json


def Selecionar_VwRelDadosDispositivo(filtros):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)

    comando = f"select cdProduto, dsNome, cdDispositivo, nrBat, dsNomeDest, dsEnderecoDest, nrNumeroDest, dsBairroDest, dsCidadeDest, dsUfDest, dsCepDest, dsLatDest, dsLongDest, dsRaio, dsEnderecoAtual, dsNumeroAtual, dsBairroAtual, dsCidadeAtual, dsUFAtual, dsCEPAtual, dsLatAtual, dsLongAtual, blArea, dtRegistro, dtCadastro from VwRelDadosDispositivo where 1=1"
    # Adiciona condições à consulta SQL com base nos filtros fornecidos
    for campo, valor in filtros.items():
        if campo == "dtRegistro":
            campo = f"DATE({campo})"
            valor = f"{valor[:4]}-{valor[4:6]}-{valor[6:]}"
        comando += f" AND {campo} = '{valor}'"

    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# Selecionar registros da tabela DbIntelliMetrics.TbProdutoTipo
def Selecionar_VwTbProdutoTipo(codigo):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    if codigo == "0":
        comando = f"select cdProduto, dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus, cdDispositivo, dsDispositivo, dsModelo, DescDispositivo, dsObs, dsLayout, nrChip, StatusDispositivo from DbIntelliMetrics.VwTbProdutoTipo"
    else:
        comando = f'select cdProduto, dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus, cdDispositivo, dsDispositivo, dsModelo, DescDispositivo, dsObs, dsLayout, nrChip, StatusDispositivo from DbIntelliMetrics.VwTbProdutoTipo where cdProduto = "{codigo}"'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.VwTbProdutoTipo
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
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.VwTbProdutoTipo ( dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus, cdDispositivo, dsDispositivo, dsModelo, DescDispositivo, dsObs, dsLayout, nrChip, StatusDispositivo ) values ("{dsNome}", "{dsDescricao}", "{nrCodigo}", "{nrLarg}", "{nrComp}", "{nrAlt}", "{cdStatus}", "{cdDispositivo}", "{dsDispositivo}", "{dsModelo}", "{DescDispositivo}", "{dsObs}", "{dsLayout}", "{nrChip}", "{StatusDispositivo}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.VwTbProdutoTipo
def deletar_VwTbProdutoTipo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.VwTbProdutoTipo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.VwTbProdutoTipo
def Alterar_VwTbProdutoTipo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.VwTbProdutoTipo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.VwTbProdutoTotalStaus
def Selecionar_VwTbProdutoTotalStaus(codigo):
    try:
        # Conecta ao banco de dados
        conexao = conecta_bd()
        cursor = conexao.cursor(dictionary=True)

        # Consulta os dados da tabela produtos
        comandoProduto = "SELECT cdProduto, dsDescricao, dsNome, nrAlt, nrCodigo, nrComp, nrLarg, dsStatus, nrQtde, QtdeTotal FROM VwTbProdutoTotalStaus"
        comandoImagem = "SELECT cdCodigo, dsCaminho, cdProduto FROM TbImagens"

        if codigo != "0":
            comandoProduto = comandoProduto + f" where cdProduto = {codigo}"
            comandoImagem = comandoImagem + f" WHERE cdProduto = {codigo}"

        cursor.execute(comandoProduto)
        produtos = cursor.fetchall()

        cursor.execute(comandoImagem)
        imagens = cursor.fetchall()

        # dicionario para armazenar os resultados
        produtos_json = {}

        # Percorre os produtos
        for produto in produtos:
            cdProduto = produto["cdProduto"]

            # cria produto no dicionario se ainda nao existe
            if cdProduto not in produtos_json:
                produtos_json[cdProduto] = {
                    "cdProduto": produto["cdProduto"],
                    "dsDescricao": produto["dsDescricao"],
                    "dsNome": produto["dsNome"],
                    "nrAlt": produto["nrAlt"],
                    "nrCodigo": produto["nrCodigo"],
                    "nrComp": produto["nrComp"],
                    "nrLarg": produto["nrLarg"],
                    "QtdeTotal": produto["QtdeTotal"],
                    "status": [],
                    "imagens": [],
                }

            # adiciona status no array
            if produto["nrQtde"] and produto["dsStatus"]:
                produtos_json[cdProduto]["status"].append(
                    {"dsStatus": produto["dsStatus"], "nrQtde": produto["nrQtde"]}
                )

        # adiciona imagens nos produtos corretos
        for img in imagens:
            cdProduto = img["cdProduto"]
            if cdProduto in produtos_json:
                produtos_json[cdProduto]["imagens"].append(img)

        # Fecha a conexão com o banco de dados
        cursor.close()
        conexao.close()

        return jsonify(list(produtos_json.values()))

    except mysql.connector.Error as error:
        return jsonify({"error": f"Erro ao acessar o banco de dados: {error}"})


# FIM DA FUNÇÃO


def Selecionar_VwTbProdutoTotal(codigo):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    if codigo == "0":
        comando = f"select cdProduto, dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, nrQtde from DbIntelliMetrics.VwTbProdutoTotal"
    else:
        comando = f"select cdProduto, dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, nrQtde from DbIntelliMetrics.VwTbProdutoTotal where cdProduto = {codigo}"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    print(comando)
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.VwTbProdutoTotalStaus
def Inserir_VwTbProdutoTotalStaus(
    dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, Status, nrQtde
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.VwTbProdutoTotalStaus ( dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, Status, nrQtde ) values ("{dsNome}", "{dsDescricao}", "{nrCodigo}", "{nrLarg}", "{nrComp}", "{nrAlt}", "{Status}", "{nrQtde}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.VwTbProdutoTotalStaus
def deletar_VwTbProdutoTotalStaus(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = (
        f'delete from DbIntelliMetrics.VwTbProdutoTotalStaus where {Campo}="{Dado}"  '
    )
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.VwTbProdutoTotalStaus
def Alterar_VwTbProdutoTotalStaus(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.VwTbProdutoTotalStaus set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbFuncionario
def Selecionar_TbFuncionario():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdFuncionario, dsBairro, dsCidade, dsComplemento, dsFuncao, dsLogradouro, dsNomeEmpregado, dsNumCasa, dsUser, dtRegistro, nrCodEmpregado, TbFuncionariocol from DbIntelliMetrics.TbFuncionario"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbFuncionario
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
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbFuncionario ( dsBairro, dsCidade, dsComplemento, dsFuncao, dsLogradouro, dsNomeEmpregado, dsNumCasa, dsUser, dtRegistro, nrCodEmpregado, TbFuncionariocol ) values ("{dsBairro}", "{dsCidade}", "{dsComplemento}", "{dsFuncao}", "{dsLogradouro}", "{dsNomeEmpregado}", "{dsNumCasa}", "{dsUser}", "{dtRegistro}", "{nrCodEmpregado}", "{TbFuncionariocol}")'
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbFuncionario
def deletar_TbFuncionario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbFuncionario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbFuncionario
def Alterar_TbFuncionario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbFuncionario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Selecionar registros da tabela DbIntelliMetrics.TbFuncionario
def Selecionar_TbEtiqueta(dsEtiqueta):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    if dsEtiqueta == "0":
        comando = f"select dsEtiqueta, nrFator, nrLargura, nrAltura, nrComprimento, nrPeso, nrCubado, dsUser, dtRegistro from DbIntelliMetrics.TbEtiqueta order by cdEtiqueta desc"
    else:
        comando = f"select dsEtiqueta, nrFator, nrLargura, nrAltura, nrComprimento, nrPeso, nrCubado, dsUser, dtRegistro from DbIntelliMetrics.TbEtiqueta where dsEtiqueta ={dsEtiqueta}"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# FIM DA FUNÇÃO


# Inserir registros da tabela DbIntelliMetrics.TbEtiqueta
def Inserir_TbEtiqueta(
    dsEtiqueta,
    nrFator,
    nrLargura,
    nrAltura,
    nrComprimento,
    nrPeso,
    nrCubado,
    dsUser,
    dtRegistro,
):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbEtiqueta (dsEtiqueta, nrFator, nrLargura, nrAltura, nrComprimento, nrPeso, nrCubado, dsUser, dtRegistro) values ("{dsEtiqueta}", "{nrFator}", "{nrLargura}", "{nrAltura}", "{nrComprimento}", "{nrPeso}", "{nrCubado}", "{dsUser}", "{dtRegistro}")'
    cursor.execute(comando)
    conexao.commit()
    return cursor.lastrowid


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
    dtOperacao = payload["dtOperacao"]
    dsTipo = payload["dsTipo"]
    dsDescricao = payload["dsDescricao"]
    nrQtde = payload["nrQtde"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbChamados(dtOperacao, dsTipo, dsDescricao, nrQtde, dsUser, dtRegistro)
    return "Cadastramento realizado com sucesso"


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbChamados
def deletar_TbChamados(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbChamados where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbChamados
def Alterar_TbChamados(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbChamados set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
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
    dsNome = payload["dsNome"]
    nrCnpj = payload["nrCnpj"]
    nrIe = payload["nrIe"]
    nrInscMun = payload["nrInscMun"]
    dsLogradouro = payload["dsLogradouro"]
    nrNumero = payload["nrNumero"]
    dsComplemento = payload["dsComplemento"]
    dsBairro = payload["dsBairro"]
    dsCep = payload["dsCep"]
    dsCidade = payload["dsCidade"]
    dsUF = payload["dsUF"]
    dsObs = payload["dsObs"]
    cdStatus = payload["cdStatus"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbCliente(
        dsNome,
        nrCnpj,
        nrIe,
        nrInscMun,
        dsLogradouro,
        nrNumero,
        dsComplemento,
        dsBairro,
        dsCep,
        dsCidade,
        dsUF,
        dsObs,
        cdStatus,
        dsUser,
        dtRegistro,
    )
    return "Cadastramento realizado com sucesso"


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbCliente
def deletar_TbCliente(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbCliente where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbCliente
def Alterar_TbCliente(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbCliente set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
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
    dsNome = payload["dsNome"]
    nrCnpj = payload["nrCnpj"]
    nrIe = payload["nrIe"]
    nrInscMun = payload["nrInscMun"]
    dsLogradouro = payload["dsLogradouro"]
    nrNumero = payload["nrNumero"]
    dsComplemento = payload["dsComplemento"]
    dsBairro = payload["dsBairro"]
    dsCep = payload["dsCep"]
    dsCidade = payload["dsCidade"]
    dsUF = payload["dsUF"]
    dsObs = payload["dsObs"]
    cdStatus = payload["cdStatus"]
    dsLat = payload["dsLat"]
    dsLong = payload["dsLong"]
    nrRaio = payload["nrRaio"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbDestinatario(
        dsNome,
        nrCnpj,
        nrIe,
        nrInscMun,
        dsLogradouro,
        nrNumero,
        dsComplemento,
        dsBairro,
        dsCep,
        dsCidade,
        dsUF,
        dsObs,
        cdStatus,
        dsLat,
        dsLong,
        nrRaio,
        dsUser,
        dtRegistro,
    )
    return "Cadastramento realizado com sucesso"


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbDestinatario
def deletar_TbDestinatario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbDestinatario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbDestinatario
def Alterar_TbDestinatario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbDestinatario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
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
    dsDispositivo = payload["dsDispositivo"]
    dsModelo = payload["dsModelo"]
    dsDescricao = payload["dsDescricao"]
    dsObs = payload["dsObs"]
    dsLayout = payload["dsLayout"]
    nrChip = payload["nrChip"]
    cdStatus = payload["cdStatus"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbDispositivo(
        dsDispositivo,
        dsModelo,
        dsDescricao,
        dsObs,
        dsLayout,
        nrChip,
        cdStatus,
        dsUser,
        dtRegistro,
    )
    return payload


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbDispositivo
def deletar_TbDispositivo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbDispositivo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbDispositivo
def Alterar_TbDispositivo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbDispositivo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Imagens


# Selecionar registros no EndPoint Imagens
@app.route("/Imagens/<codigo>")
def get_Imagens(codigo):
    resultado = Selecionar_TbImagens(codigo)
    return resultado


# FIM DA FUNÇÃO


# Inserir registros no EndPoint Imagens
@app.route("/Imagens", methods=["POST"])
def post_Imagens():
    payload = request.get_json()
    dsCaminho = payload["dsCaminho"]
    cdCodigo = payload["cdCodigo"]
    cdTipo = payload["cdTipo"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    cdProduto = payload["cdProduto"]
    nrImagem = payload["nrImagem"]
    Inserir_TbImagens(
        dsCaminho, cdCodigo, cdTipo, dsUser, dtRegistro, cdProduto, nrImagem
    )
    return payload


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbImagens
def deletar_TbImagens(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbImagens where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbImagens
def Alterar_TbImagens(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbImagens set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
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


# FIM DA FUNÇÃO

dic_endereco_pdv = []


@app.route("/Posicao", methods=["POST"])
def post_Posicao():
    payload = request.get_json()
    print(payload)
    dsModelo = payload["dsModelo"]
    dtData = payload["dtData"]
    dtHora = payload["dtHora"]
    dsLat = payload["dsLat"]
    dsLong = payload["dsLong"]
    nrTemp = payload["nrTemp"]
    nrBat = payload["nrBat"]
    nrSeq = payload["nrSeq"]

    dsArquivo = payload["dsArquivo"]
    cdDispositivo = payload["cdDispositivo"]
    dsUser = payload["dsUser"]
    dic = get_endereco_coordenada(dsLat, dsLong)
    dsEndereco = dic[0]
    dsNum = dic[1]
    dsBairro = dic[2]
    dsCidade = dic[3]
    dsUF = dic[4]
    dsCep = dic[5]
    dsPais = dic[6]
    dic_endereco_pdv = Selecionar_VwTbDestinatarioDispositivo(cdDispositivo)
    # print(dic_endereco_pdv)
    dic_endereco_pdv = dict(dic_endereco_pdv[0])
    dsLatPdv = dic_endereco_pdv["dsLat"]
    dsLongPdv = dic_endereco_pdv["dsLong"]
    nrRaio = dic_endereco_pdv["nrRaio"]
    DistanciaArea = calcular_distancia(dsLat, dsLong, dsLatPdv, dsLongPdv)
    nrDistancia = DistanciaArea
    # print(nrRaio)
    if float(DistanciaArea) > float(nrRaio):
        Alterar_StatusTbPosicao(cdDispositivo, 6)
        blArea = 0
    else:
        Alterar_StatusTbPosicao(cdDispositivo, 1)
        blArea = 1
    dic_sensores = payload["sensores"]
    # print(dic_sensores)
    cd = Inserir_TbPosicao(
        dsModelo,
        dtData,
        dtHora,
        dsLat,
        dsLong,
        nrTemp,
        nrBat,
        nrSeq,
        dsArquivo,
        cdDispositivo,
        dsEndereco,
        dsNum,
        dsBairro,
        dsCidade,
        dsUF,
        dsCep,
        dsPais,
        dsLatPdv,
        dsLongPdv,
        nrRaio,
        blArea,
        nrDistancia,
        dsUser,
    )
    cdSensor = dic_sensores["cdSensor"]
    nrValor = dic_sensores["nrValor"]
    cdSensor1 = dic_sensores["cdSensor1"]
    nrValor1 = dic_sensores["nrValor1"]
    cdPosicao = cd

    # print(nome)  # Saída: Carlos
    Inserir_TbSensorRegistro(cdDispositivo, cdSensor, cdPosicao, nrValor)
    Inserir_TbSensorRegistro(cdDispositivo, cdSensor1, cdPosicao, nrValor1)

    return jsonify({"cdPosicao": cd})


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbPosicao
def deletar_TbPosicao(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbPosicao where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbPosicao
def Alterar_TbPosicao(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbPosicao set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/Produto

cd = []


# Inserir registros no EndPoint Produto
@app.route("/Produto", methods=["POST"])
def post_Produto():
    payload = request.get_json()
    dsNome = payload["dsNome"]
    dsDescricao = payload["dsDescricao"]
    nrCodigo = payload["nrCodigo"]
    nrLarg = payload["nrLarg"]
    nrComp = payload["nrComp"]
    nrAlt = payload["nrAlt"]
    cdStatus = payload["cdStatus"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    cd = Inserir_TbProduto(
        dsNome,
        dsDescricao,
        nrCodigo,
        nrLarg,
        nrComp,
        nrAlt,
        cdStatus,
        dsUser,
        dtRegistro,
    )
    return jsonify({"cdProduto": cd})


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
    dsEtiqueta = payload["dsEtiqueta"]
    nrLargura = payload["nrLargura"]
    nrAltura = payload["nrAltura"]
    nrComprimento = payload["nrComprimento"]
    nrPeso = payload["nrPeso"]
    nrCubado = payload["nrCubado"]
    nrFator = payload["nrFator"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    cd = Inserir_TbEtiqueta(
        dsEtiqueta,
        nrFator,
        nrLargura,
        nrAltura,
        nrComprimento,
        nrPeso,
        nrCubado,
        dsUser,
        dtRegistro,
    )
    # return payload
    return jsonify(
        {
            "cdCodigo": cd,
            "dsEtiqueta": dsEtiqueta,
            "nrLargura": nrLargura,
            "nrAltura": nrAltura,
            "nrComprimento": nrComprimento,
            "nrPeso": nrPeso,
            "nrCubado": nrCubado,
            "nrFator": nrFator,
            "dsUser": dsUser,
            "dtRegistro": dtRegistro,
        }
    )


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbProduto
def deletar_TbProduto(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbProduto where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbProduto
def Alterar_TbProduto(Campo, Dado, UpData):
    comando = "update DbIntelliMetrics.TbProduto set"

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
    cdPai = payload["cdPai"]
    cdFilho = payload["cdFilho"]
    cdTipo = payload["cdTipo"]
    dsDescricao = payload["dsDescricao"]
    cdStatus = payload["cdStatus"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbRelacionamento(
        cdPai, cdFilho, cdTipo, dsDescricao, cdStatus, dsUser, dtRegistro
    )
    return payload


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
    dsNome = payload["dsNome"]
    cdTipo = payload["cdTipo"]
    dsDescricao = payload["dsDescricao"]
    cdUnidade = payload["cdUnidade"]
    nrUnidadeIni = payload["nrUnidadeIni"]
    nrUnidadeFim = payload["nrUnidadeFim"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbSensor(
        dsNome,
        cdTipo,
        dsDescricao,
        cdUnidade,
        nrUnidadeIni,
        nrUnidadeFim,
        dsUser,
        dtRegistro,
    )
    return payload


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
    dsStatus = payload["dsStatus"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbStatus(dsStatus, dsUser, dtRegistro)
    return payload


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
    dsDescricao = payload["dsDescricao"]
    dsConteudo = payload["dsConteudo"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbTag(dsDescricao, dsConteudo, dsUser, dtRegistro)
    return payload


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
    dtOperacao = payload["dtOperacao"]
    dsAtendimento = payload["dsAtendimento"]
    nrAbertos = payload["nrAbertos"]
    nrFechados = payload["nrFechados"]
    nrPendentes = payload["nrPendentes"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbTicket(
        dtOperacao,
        dsAtendimento,
        nrAbertos,
        nrFechados,
        nrPendentes,
        dsUser,
        dtRegistro,
    )
    return payload


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
    dtOperacao = payload["dtOperacao"]
    dsAtendimento = payload["dsAtendimento"]
    dsNaoAtribuido = payload["dsNaoAtribuido"]
    dsSemResolucao = payload["dsSemResolucao"]
    dsAtualizado = payload["dsAtualizado"]
    dsPendente = payload["dsPendente"]
    dsResolvido = payload["dsResolvido"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbTicketResumo(
        dtOperacao,
        dsAtendimento,
        dsNaoAtribuido,
        dsSemResolucao,
        dsAtualizado,
        dsPendente,
        dsResolvido,
        dsUser,
        dtRegistro,
    )
    return payload


# FIM DA FUNÇÃO


# Selecionar registros no EndPoint Tipo
@app.route("/Tipo")
def get_Tipo():
    resultado = Selecionar_TbTipo()
    return resultado


# FIM DA FUNÇÃO


def Selecionar_NrImagensMaior(codigo):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    if codigo == "0":
        comando = f'select  SUBSTRING_INDEX(cdCodigo, "-",1) as cdProduto, max(SUBSTRING_INDEX(SUBSTRING_INDEX(cdCodigo, "-",-1),".",1)) as nrMaior from DbIntelliMetrics.TbImagens where cdTipo = 10  group by cdProduto order by cdProduto'
    else:
        comando = f'select  SUBSTRING_INDEX(cdCodigo, "-",1) as cdProduto, max(SUBSTRING_INDEX(SUBSTRING_INDEX(cdCodigo, "-",-1),".",1)) as nrMaior from DbIntelliMetrics.TbImagens where cdTipo = 10 and cdCodigo = {codigo} group by cdProduto'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# Inserir registros no EndPoint Tipo
@app.route("/Tipo", methods=["POST"])
def post_Tipo():
    payload = request.get_json()
    dsDescricao = payload["dsDescricao"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbTipo(dsDescricao, dsUser, dtRegistro)
    return payload


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbTipo
def deletar_TbTipo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbTipo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbTipo
def Alterar_TbTipo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbTipo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
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
    dsUnidade = payload["dsUnidade"]
    dsSimbolo = payload["dsSimbolo"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbUnidade(dsUnidade, dsSimbolo, dsUser, dtRegistro)
    return payload


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbUnidade
def Alterar_TbUnidade(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbUnidade set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
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
    dsNome = payload["dsNome"]
    dsLogin = payload["dsLogin"]
    dsSenha = payload["dsSenha"]
    cdPerfil = payload["cdPerfil"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbUsuario(dsNome, dsLogin, dsSenha, cdPerfil, dsUser, dtRegistro)
    return payload


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbUsuario
def deletar_TbUsuario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbUsuario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbUsuario
def Alterar_TbUsuario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbUsuario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
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
    cdCliente = payload["cdCliente"]
    cdVisitante = payload["cdVisitante"]
    dtData = payload["dtData"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbVisita(cdCliente, cdVisitante, dtData, dsUser, dtRegistro)
    return payload


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbVisita
def deletar_TbVisita(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbVisita where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbVisita
def Alterar_TbVisita(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbVisita set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
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
    dsNome = payload["dsNome"]
    nrTelefone = payload["nrTelefone"]
    nrDocumento = payload["nrDocumento"]
    dsEmail = payload["dsEmail"]
    dsUser = payload["dsUser"]
    dtRegistro = payload["dtRegistro"]
    Inserir_TbVisitante(dsNome, nrTelefone, nrDocumento, dsEmail, dsUser, dtRegistro)
    return payload


# FIM DA FUNÇÃO


# Deletar registros da tabela DbIntelliMetrics.TbVisitante
def deletar_TbVisitante(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbVisitante where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbVisitante
def Alterar_TbVisitante(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbVisitante set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO
# https://replit.taxidigital.net/TbPosicao


# Deletar registros da tabela DbIntelliMetrics.TbPosicao
def deletar_TbPosicao(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbPosicao where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.TbPosicao
def Alterar_TbPosicao(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbPosicao set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
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


# Deletar registros da tabela DbIntelliMetrics.VwTbProdutoTipo
def deletar_VwTbProdutoTipo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.VwTbProdutoTipo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()


# FIM DA FUNÇÃO


# Alterar registros da tabela DbIntelliMetrics.VwTbProdutoTipo
def Alterar_VwTbProdutoTipo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.VwTbProdutoTipo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
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


# FIM DA FUNÇÃO

# Selecionar registros no EndPoint TbProdutoTotalStaus

img = {"Imagens": []}
status = {"Status": []}
produto = {"Produto": []}
resultado = []


# alunos = {"alunos": []}
@app.route("/TbProdutoTotal/<codigo>")
def get_TbProdutoTotal(codigo):

    # resultado = Selecionar_VwTbProdutoTotal(codigo)
    produto["Produto"] = Selecionar_VwTbProdutoTotal(codigo)
    status["Status"] = Selecionar_VwTbProdutoTotalStaus(codigo)
    img["Imagens"] = Selecionar_TbImagens(codigo)
    resultado.append(produto)
    resultado.append(status)
    resultado.append(img)
    return resultado


# FIM DA FUNÇÃO

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


# FIM DA FUNÇÃO


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
    Inserir_TbImagens(
        "produtos/",
        pathfile,
        "10",
        "TESTE",
        datetime.datetime.now(),
        cdProduto,
        nrImagem,
    )
    return pathfile


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


# Selecionar_NrImagensMaior


@app.route("/NrImagensMaior/<codigo>")
def get_NrImagensMaior(codigo):
    resultado = Selecionar_NrImagensMaior(codigo)
    return resultado


# https://replit.taxidigital.net/AcessoIntelBras


# Selecionar registros no EndPoint AcessoIntelBras



@app.route("/AcessoIntelBras", methods=["GET"])
def get_AcessoIntelBras():
    resultado = Selecionar_TbAcessoIntelBras()
    return resultado



# FIM DA FUNÇÃO

@app.route('/AcessoIntelBras', methods=['POST'])
def post_AcessoIntelBras():
    payload = request.get_json()
    dsCardName = payload ['dsCardName']
    dsCardNo = payload ['dsCardNo']
    dsDoor = payload ['dsDoor']
    dsEntry = payload ['dsEntry']
    dsErrorCode = payload ['dsErrorCode']
    dsMethod = payload ['dsMethod']
    dsPassword = payload ['dsPassword']
    dsReaderID = payload ['dsReaderID']
    dsStatus = payload ['dsStatus']
    dsType = payload ['dsType']
    dsUserId = payload ['dsUserId']
    dsUserType = payload ['dsUserType']
    dsUtc = payload ['dsUtc']
   # TbAcessoIntelBrascol = payload ['TbAcessoIntelBrascol']
    if dsStatus == "1":
        Inserir_TbAcessoIntelBras(dsCardName, dsCardNo, dsDoor, dsEntry, dsErrorCode, dsMethod, dsPassword, dsReaderID, dsStatus, dsType, dsUserId, dsUserType, dsUtc)
        print("cheguei no endpoint")
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

@app.route("/Ponto")
def get_Ponto():
    resultado = Selecionar_TbPonto()
    return resultado


dic_dados = []



@app.route("/notification", methods=["POST"])
def event_receiver():
    if request.method == "POST":
        print(obter_ip_publico())
        res = request.data
        print(res)
        data_list = res.split(b"--myboundary\r\n")

        if data_list:
            for a_info in data_list:
                if b"Content-Type" in a_info:
                    lines = a_info.split(b"\r\n")
                    a_type = lines[0].split(b": ")[1]

                    if a_type == b"image/jpeg":
                        image_data = b"\r\n".join(lines[3:-3])
                        image_data = lines[3:-3]
                        #print(image_data)
                    else:
                        text_data = b"\r\n".join(lines[3:-1])

        evento_str = text_data.decode("utf-8")
        evento_dict = ast.literal_eval(evento_str.replace("--myboundary--", " "))
        json_object = json.dumps(evento_dict, indent=4)
        resp_dict = json.loads(json_object)

        #print(resp_dict)

        event_code = resp_dict.get("Events")[0].get("Code")
        #print("################## ", event_code, " ##################")

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

            #print("UserID: ", user_id)
            print("UserType", user_type)
            #print("CardName: ", card_name)
            #print("CardNo: ", card_no)
            #print("CardType: ", card_type)
            #print("Password: ", pwd)
            #print("Door: ", door)
            #print("ErrorCode: ", error_code)
            #print("Method: ", method)
            #print("ReaderID: ", reader_id)
            #print("Status: ", event_status)
            #print("Type: ", event_type)
            #print("Entry: ", event_entry)
            #print("UTC: ", event_utc)
            #print(49 * "#")
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
            if user_id == 41205257837:
                Inserir_TbLog('userid', '41205257837', '10.0.0.1', 'system')
                return jsonify(
                    {
                        "message": "Ponto Registrado",
                        "code": "200",
                        "auth": "true",
                    }
                )
            elif card_no in [
                "41205257837",
                "09201802",
            ]:  # Caso o código do cartão esteja listado libera o acesso
                Inserir_TbLog('cartao', '41205257837', '10.0.0.1', 'system')

                return jsonify(
                    {"message": "Ponto Registrado !", "code": "200", "auth": "true"}
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

           # print("Door Status: ", door_status)
           # print("UTC", door_utc)
           # print(20 * "#")
            return jsonify({"message": "xxxxxxx", "code": "200", "auth": "false"})

        elif event_code == "BreakIn":
            event_data = resp_dict.get("Events")[0].get("Data")

            door_name = event_data.get("Name")
            door_utc = event_data.get("UTC")

           # print("Door Name: ", door_name)
           # print("UTC", door_utc)
           # print(49 * "#")
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
                        #envia_whatstexto("Olá eu quero essa viagem ! " + msg)

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
   # port = int(os.environ.get("PORT", 8080))
   # app.run(host="127.0.0.1", port=port)
    port = int(os.environ.get("PORT", 80))
    app.run(host="192.168.0.200", port=port)


if __name__ == "__main__":
    main()
