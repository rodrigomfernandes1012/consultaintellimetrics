# SERVER API
import ast
import base64
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List

import boto3
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase.client import ClientOptions

from db_utils import Client, create_client
from utils import valida_e_constroi_insert

# possibilita pegar variaveis do .env
load_dotenv()

# Amazon
dic_whats = []
dic_whats2 = []
dic_altura = []

# Supabase setup client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase_api: Client = create_client(url, key)


def conecta_bd():
    conexao = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        port=os.getenv("DB_PORT"),
    )
    return conexao


def get_supabase_client(token):
    headers = {"Authorization": f"Bearer {token}"}
    supabase_client: Client = create_client(
        url, key, options=ClientOptions(headers=headers)
    )
    return supabase_client


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


def guarda_medidas(altura, largura, comprimento, pesoreal, cubado):
    with open("cubagem.txt", "w") as arquivo:
        altura = str(altura).ljust(10)
        largura = str(largura).ljust(10)
        comprimento = str(comprimento).ljust(10)
        cubado = str(cubado).ljust(10)
        pesoreal = str(pesoreal).ljust(20)
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
        supabase_api.table("TbAcessoIntelBras")
        .select(
            "cdAcessoIntelBras, dsCardName, dsCardNo, dsDoor, dsEntry, dsErrorCode, dsMethod, dsPassword, dsReaderID, dsStatus, dsType, dsUserId, dsUserType, dsUtc"
        )
        .execute()
    )
    return resultado.data


def Selecionar_TbPonto():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select cdPonto, cdAcessoIntelbras, dsCardNo, dsRegistro01, dsRegistro02, dsRegistro03, dsRegistro04, dsRegistro05, dsRegistro06, dtRegistro  from DbIntelliMetrics.TbPonto;"
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return resultado


# Inserir registros da tabela public.TbAcessoIntelBras
# def Inserir_TbAcessoIntelBras(data):
#     resultado = supabase_api.table("TbAcessoIntelBras").insert(data).execute()
#     return resultado.data


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
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbAcessoIntelBras ( dsCardName, dsCardNo, dsDoor, dsEntry, dsErrorCode, dsMethod, dsPassword, dsReaderID, dsStatus, dsType, dsUserId, dsUserType, dsUtc ) values ("{dsCardName}", "{dsCardNo}", "{dsDoor}", "{dsEntry}", "{dsErrorCode}", "{dsMethod}", "{dsPassword}", "{dsReaderID}", "{dsStatus}", "{dsType}", "{dsUserId}", "{dsUserType}", "{dsUtc}")'
    cursor.execute(comando)
    data = str(datetime.utcfromtimestamp(int(dsUtc)).strftime("%Y-%m-%d %H:%M:%S"))
    # print(dsCardNo,data)
    Inserir_TbPonto(dsCardNo, data)
    conexao.commit()
    cursor.close()
    conexao.close()


def Inserir_TbPonto(dsCardNo, dsUtc):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f"select * from DbIntelliMetrics.TbPonto where dsCardNo = '{dsCardNo}' and DATE(dtRegistro) = DATE('{dsUtc}')"
    cursor.execute(comando)
    # print(comando)
    resultado = cursor.fetchall()
    # print(resultado)
    if resultado == []:
        print("vazio")
        dado = "dsRegistro01"
    else:
        print(resultado)

        for dtregistro in resultado:
            if dtregistro["dsRegistro06"] == None:
                dado = "dsRegistro06"
            if dtregistro["dsRegistro05"] == None:
                dado = "dsRegistro05"
            if dtregistro["dsRegistro04"] == None:
                dado = "dsRegistro04"
            if dtregistro["dsRegistro03"] == None:
                dado = "dsRegistro03"
            if dtregistro["dsRegistro02"] == None:
                dado = "dsRegistro02"
            if dtregistro["dsRegistro01"] == None:
                dado = "dsRegistro01"
            print(dado)

    if dado == "dsRegistro01":
        comando = f"insert into DbIntelliMetrics.TbPonto ( dsCardNo, dsRegistro01 ) values ('{dsCardNo}', '{dsUtc}')"
    print(comando)
    if dado == "dsRegistro02":
        comando = f"update DbIntelliMetrics.TbPonto set dsRegistro02 = '{dsUtc}' where dsCardNo = '{dsCardNo}' and dsRegistro02 is null"
    print(comando)
    if dado == "dsRegistro03":
        comando = f"update DbIntelliMetrics.TbPonto set dsRegistro03 = '{dsUtc}' where dsCardNo = '{dsCardNo}' and dsRegistro03 is null"
    print(comando)
    if dado == "dsRegistro04":
        comando = f"update DbIntelliMetrics.TbPonto set dsRegistro04 = '{dsUtc}' where dsCardNo = '{dsCardNo}' and dsRegistro04 is null"
    print(comando)
    if dado == "dsRegistro05":
        comando = f"update DbIntelliMetrics.TbPonto set dsRegistro05 = '{dsUtc}' where dsCardNo = '{dsCardNo}' and dsRegistro05 is null"
    print(comando)
    if dado == "dsRegistro06":
        comando = f"update DbIntelliMetrics.TbPonto set dsRegistro06 = '{dsUtc}' where dsCardNo = '{dsCardNo}' and dsRegistro06 is null"
    print(comando)

    cursor.execute(comando)
    conexao.commit()
    cursor.close()
    conexao.close()


# Selecionar registros da tabela public.TbChamados
def Selecionar_TbChamados():
    resultado = (
        supabase_api.table("TbChamados")
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


# Inserir registros da tabela public.TbChamados
def Inserir_TbChamados(data):
    resultado = supabase_api.table("TbChamados").insert(data).execute()
    return resultado.data


def Alterar_StatusTbPosicao(codigo, status):
    response = (
        supabase_api.table("TbDispositivo")
        .update({"cdStatus": status})
        .eq("cdDispositivo", codigo)
        .execute()
    )
    return response.data


# Selecionar registros da tabela public.TbStatus
def Selecionar_TbStatus():
    resultado = (
        supabase_api.table("TbStatus")
        .select("cdStatus, dsStatus, dsUser, dtRegistro")
        .execute()
    )
    return resultado.data


# Inserir registros da tabela public.TbStatus
def Inserir_TbStatus(data):
    resultado = supabase_api.table("TbStatus").insert(data).execute()
    return resultado.data


# Selecionar registros da tabela public.TbTag
def Selecionar_TbTag():
    resultado = (
        supabase_api.table("TbTag")
        .select("cdTag", "dsDescricao", "dsConteudo", "dsUser", "dtRegistro")
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbTag
def Inserir_TbTag(data):
    resultado = supabase_api.table("TbTag").insert(data).execute()
    return resultado.data


# Selecionar registros da tabela public.TbTicket
def Selecionar_TbTicket():
    resultado = (
        supabase_api.table("TbTicket")
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
    resultado = supabase_api.table("TbTicket").insert(data).execute()
    return resultado.data


# Selecionar registros da tabela public.TbTicketResumo
def Selecionar_TbTicketResumo():
    resultado = (
        supabase_api.table("TbTicketResumo")
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
    resultado = supabase_api.table("TbTicketResumo").insert(data).execute()
    return resultado.data


# Selecionar registros da tabela public.TbTipo
def Selecionar_TbTipo():
    resultado = (
        supabase_api.table("TbTipo")
        .select("cdTipo", "dsDescricao", "dsUser", "dtRegistro")
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbTipo
def Inserir_TbTipo(data):
    resultado = supabase_api.table("TbTipo").insert(data).execute()
    return resultado.data


# Selecionar registros da tabela public.TbUnidade
def Selecionar_TbUnidade():
    resultado = (
        supabase_api.table("TbUnidade")
        .select("cdUnidade", "dsUnidade", "dsSimbolo", "dsUser", "dtRegistro")
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbUnidade
def Inserir_TbUnidade(data):
    resultado = supabase_api.table("TbUnidade").insert(data).execute()
    return resultado.data


# Selecionar registros da tabela public.TbUsuario
def Selecionar_TbUsuario():
    resultado = (
        supabase_api.table("TbUsuario")
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
    resultado = supabase_api.table("TbUsuario").insert(data).execute()
    return resultado.data


# Selecionar registros da tabela public.TbVisita
def Selecionar_TbVisita():
    resultado = (
        supabase_api.table("TbVisita")
        .select(
            "cdVisita", "cdCliente", "cdVisitante", "dtData", "dsUser", "dtRegistro"
        )
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbVisita
def Inserir_TbVisita(data):
    resultado = supabase_api.table("TbVisita").insert(data).execute()
    return resultado.data


# Selecionar registros da tabela public.TbVisitante
def Selecionar_TbVisitante():
    resultado = (
        supabase_api.table("TbVisitante")
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
    resultado = supabase_api.table("TbVisitante").insert(data).execute()
    return resultado.data


# Selecionar registros da tabela public.TbFuncionario
def Selecionar_TbFuncionario():
    resultado = (
        supabase_api.table("TbFuncionario")
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


# Inserir registros da tabela public.TbFuncionario
def Inserir_TbFuncionario(data):
    resultado = supabase_api.table("TbFuncionario").insert(data).execute()
    return resultado.data


# Selecionar registros da tabela public.TbFuncionario
def Selecionar_TbEtiqueta(dsEtiqueta):
    query = supabase_api.table("TbEtiqueta").select(
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


# Inserir registros da tabela public.TbEtiqueta
def Inserir_TbEtiqueta(data):
    resultado = supabase_api.table("TbEtiqueta").insert(data).execute()
    return resultado.data


app = Flask(__name__)  # cria o site
app.json.sort_keys = False
CORS(app, resources={r"*": {"origins": "*"}})

##COMECA A API GERADA AUTOMATICAMENTE


# Selecionar registros no EndPoint Chamados
@app.route("/Chamados")
def get_Chamados():
    resultado = Selecionar_TbChamados()
    return resultado


# Inserir registros no EndPoint Chamados
@app.route("/Chamados", methods=["POST"])
def post_Chamados():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbChamados", payload)

    if error:
        print(error)
        return jsonify({"message": error}), 400

    Inserir_TbChamados(data)
    return "Cadastramento realizado com sucesso"


@app.route("/Etiqueta/<dsEtiqueta>", methods=["GET"])
def get_Etiqueta(dsEtiqueta):
    resultado = Selecionar_TbEtiqueta(dsEtiqueta)
    return resultado


@app.route("/TbEtiqueta", methods=["POST"])
def post_Etiqueta():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbEtiqueta", payload)

    if error:
        print(error)
        return jsonify({"message": error}), 400
    resultado = Inserir_TbEtiqueta(data)
    return resultado


# Selecionar registros no EndPoint Tag
@app.route("/Tag")
def get_Tag():
    resultado = Selecionar_TbTag()
    return resultado


# Inserir registros no EndPoint Tag
@app.route("/Tag", methods=["POST"])
def post_Tag():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbTag", payload)

    if error:
        print(error)
        return jsonify({"message": error}), 400
    resultado = Inserir_TbTag(data)
    return resultado


# Selecionar registros no EndPoint Ticket
@app.route("/Ticket")
def get_Ticket():
    resultado = Selecionar_TbTicket()
    return resultado


# Inserir registros no EndPoint Ticket
@app.route("/Ticket", methods=["POST"])
def post_Ticket():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbTicket", payload)

    if error:
        print(error)
        return jsonify({"message": error}), 400
    resultado = Inserir_TbTicket(data)
    return resultado


# Selecionar registros no EndPoint TicketResumo
@app.route("/TicketResumo")
def get_TicketResumo():
    resultado = Selecionar_TbTicketResumo()
    return resultado


# Inserir registros no EndPoint TicketResumo
@app.route("/TicketResumo", methods=["POST"])
def post_TicketResumo():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbTicketResumo", payload)

    if error:
        print(error)
        return jsonify({"message": error}), 400
    resultado = Inserir_TbTicketResumo(data)
    return resultado


# Selecionar registros no EndPoint Usuario
@app.route("/Usuario")
def get_Usuario():
    resultado = Selecionar_TbUsuario()
    return resultado


# Inserir registros no EndPoint Usuario
@app.route("/Usuario", methods=["POST"])
def post_Usuario():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbUsuario", payload)

    if error:
        print(error)
        return jsonify({"message": error}), 400
    resultado = Inserir_TbUsuario(data)
    return resultado


# https://replit.taxidigital.net/Visita


# Selecionar registros no EndPoint Visita
@app.route("/Visita")
def get_Visita():
    resultado = Selecionar_TbVisita()
    return resultado


# Inserir registros no EndPoint Visita
@app.route("/Visita", methods=["POST"])
def post_Visita():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbVisita", payload)

    if error:
        print(error)
        return jsonify({"message": error}), 400
    resultado = Inserir_TbVisita(data)
    return resultado


# https://replit.taxidigital.net/Visitante


# Selecionar registros no EndPoint Visitante
@app.route("/Visitante")
def get_Visitante():
    resultado = Selecionar_TbVisitante()
    return resultado


# Inserir registros no EndPoint Visitante
@app.route("/Visitante", methods=["POST"])
def post_Visitante():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbVisitante", payload)

    if error:
        print(error)
        return jsonify({"message": error}), 400
    resultado = Inserir_TbVisitante(data)
    return resultado


# Selecionar registros no EndPoint TbProdutoTipo


# Selecionar registros no EndPoint Funcionario
@app.route("/Funcionario")
def get_Funcionario():
    resultado = Selecionar_TbFuncionario()
    return resultado


# Inserir registros no EndPoint Funcionario
@app.route("/Funcionario", methods=["POST"])
def post_Funcionario():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbFuncionario", payload)

    if error:
        print(error)
        return jsonify({"message": error}), 400

    resultado = Inserir_TbFuncionario(data)
    return resultado


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


@app.route("/Ponto")
def get_Ponto():
    resultado = Selecionar_TbPonto()
    return resultado


@app.route("/AcessoIntelBras", methods=["GET"])
def get_AcessoIntelBras():
    resultado = Selecionar_TbAcessoIntelBras()
    return resultado


# Inserir registros no EndPoint AcessoIntelBras
# @app.route("/AcessoIntelBras", methods=["POST"])
# def post_AcessoIntelBras():
#     payload = request.get_json()
#     data, error = valida_e_constroi_insert("TbAcessoIntelBras", payload)

#     if error:
#         return jsonify({"message": error}), 400

#     Inserir_TbAcessoIntelBras(data)


@app.route("/AcessoIntelBras", methods=["POST"])
def post_AcessoIntelBras():
    payload = request.get_json()
    dsCardName = payload["dsCardName"]
    dsCardNo = payload["dsCardNo"]
    dsDoor = payload["dsDoor"]
    dsEntry = payload["dsEntry"]
    dsErrorCode = payload["dsErrorCode"]
    dsMethod = payload["dsMethod"]
    dsPassword = payload["dsPassword"]
    dsReaderID = payload["dsReaderID"]
    dsStatus = payload["dsStatus"]
    dsType = payload["dsType"]
    dsUserId = payload["dsUserId"]
    dsUserType = payload["dsUserType"]
    dsUtc = payload["dsUtc"]
    # TbAcessoIntelBrascol = payload ['TbAcessoIntelBrascol']
    if dsStatus == "1":
        Inserir_TbAcessoIntelBras(
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
        )
    return "Cadastramento realizado com sucesso"


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

    return dic_altura


def main():
    port = int(os.getenv("APP_PORT", 80))
    host = os.getenv("APP_HOST", "192.168.15.200")
    env = os.getenv("ENV", "local")

    debug = False if env != "local" else True
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
