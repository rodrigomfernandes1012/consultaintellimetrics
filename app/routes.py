import os

from flask import Blueprint, jsonify, request

from db_utils import get_supabase_client_from_request
from db_utils.storage import upload_file
from utils import valida_e_constroi_insert

from .services import (
    Inserir_TbCliente,
    Inserir_TbDestinatario,
    Inserir_TbDispositivo,
    Inserir_TbImagens,
    Inserir_TbPosicao,
    Inserir_TbSensorRegistro,
    Selecionar_TbCliente,
    Selecionar_TbDestinatario,
    Selecionar_TbDispositivo,
    Selecionar_TbImagens,
    Selecionar_TbPosicao,
    Selecionar_VwTbProdutoTotalStatus,
    get_endereco_coordenada,
    is_dentro_area,
    prepara_insert_registros,
)

main = Blueprint("main", __name__)


@main.route("/TbProdutoTotalStatus/<codigo>")
def get_TbProdutoTotalStatus(codigo):
    resultado = Selecionar_VwTbProdutoTotalStatus(codigo)
    return resultado


@main.route("/Cliente")
def get_Cliente():
    resultado = Selecionar_TbCliente()
    return resultado


@main.route("/Cliente", methods=["POST"])
def post_Cliente():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbCliente", payload)

    if error:
        return jsonify({"message": error}), 400

    Inserir_TbCliente(data)
    return "Cadastramento realizado com sucesso"


@main.route("/Destinatario/<cdDestinatario>")
def get_Destinatario(cdDestinatario):
    cdCliente = request.args.get("cdCliente")

    if not cdCliente:
        return jsonify({"message": "cdCliente necessário"}), 400

    supabase_client, error = get_supabase_client_from_request(request=request)

    if error or supabase_client is None:
        return jsonify({"message": error}), 401

    resultado = Selecionar_TbDestinatario(
        cdDestinatario=cdDestinatario, cdCliente=cdCliente, db_client=supabase_client
    )

    return resultado


@main.route("/Destinatario", methods=["POST"])
def post_Destinatario():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbDestinatario", payload)

    if error:
        return jsonify({"message": error}), 400
    resultado = Inserir_TbDestinatario(data)
    return resultado


@main.route("/Dispositivo/<codigo>")
def get_Dispositivo(codigo):
    supabase_client, error = get_supabase_client_from_request(request=request)

    if error or supabase_client is None:
        return jsonify({"message": error}), 401

    resultado = Selecionar_TbDispositivo(codigo, db_client=supabase_client)
    return resultado


# Inserir registros no EndPoint Dispositivo
@main.route("/Dispositivo", methods=["POST"])
def post_Dispositivo():
    payload = request.get_json()
    data, error = valida_e_constroi_insert("TbDispositivo", payload)

    if error:
        return jsonify({"message": error}), 400
    resultado = Inserir_TbDispositivo(data)
    return resultado


@main.route("/CadastraImgProduto", methods=["POST"])
def CadastraImgProduto():
    supabase_client, error = get_supabase_client_from_request(request=request)

    if error or supabase_client is None:
        return jsonify({"message": error}), 401

    file = request.files["arquivo"]
    pathfile = file.filename
    cdProduto = pathfile.split("-")[0]
    nrImagem = pathfile.split("-")[1]
    nrImagem = nrImagem.split(".")[0]
    file.save(pathfile)
    try:
        upload_file(file_name=pathfile, bucket="produtos", db_client=supabase_client)
    except Exception as e:
        os.remove(pathfile)
        print(e)
        print(pathfile)
        return jsonify({"message": "erro ao fazer upload da imagem"}), 400

    os.remove(pathfile)
    payload = {
        "dsCaminho": "produtos/",
        "cdCodigo": pathfile,
        "cdProduto": int(cdProduto),
        "nrImagem": int(nrImagem),
    }
    data, error = valida_e_constroi_insert("TbImagens", payload)

    if error:
        return jsonify({"message": error}), 400

    resultado = Inserir_TbImagens(data, db_client=supabase_client)
    return resultado


# Selecionar registros no EndPoint Imagens
@main.route("/Imagens/<codigo>")
def get_Imagens(codigo):
    supabase_client, error = get_supabase_client_from_request(request=request)

    if error or supabase_client is None:
        return jsonify({"message": error}), 401

    resultado = Selecionar_TbImagens(codigo, db_client=supabase_client)
    return resultado


@main.route("/Posicao/<codigo>")
def get_Posicao(codigo):
    supabase_client, error = get_supabase_client_from_request(request=request)

    if error or supabase_client is None:
        return jsonify({"message": error}), 401

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

    # Busca os primeiros 1000 resultados. Limite aplicado direto nas configs do supabase
    resultado = Selecionar_TbPosicao(filtros, db_client=supabase_client)
    return resultado


# TODO!!!!
@main.route("/Posicao", methods=["POST"])
def post_Posicao():
    payload = request.get_json()

    dsLat = payload["dsLat"]
    dsLong = payload["dsLong"]
    cdDispositivo = payload["cdDispositivo"]

    if not dsLat or not dsLong or not cdDispositivo:
        return (
            jsonify({"message": "dsLat, dsLong e cdDispositivo são necessários"}),
            400,
        )

    # busca destinatario no dispositivo
    dispositivo = Selecionar_TbDispositivo(cdDispositivo)

    if not dispositivo or len(dispositivo) == 0:
        return (
            jsonify(
                {"message": f"dispositivo com o id {cdDispositivo} não foi encontrado"}
            ),
            500,
        )

    cdDestinatario = dispositivo[0]["cdDestinatario"]

    payload["cdDestinatario"] = cdDestinatario

    dict_endereco_coord = get_endereco_coordenada(dsLat, dsLong)

    for key, value in dict_endereco_coord.items():
        payload[key] = value

    blArea = is_dentro_area(cdDispositivo, dsLat, dsLong)
    payload["blArea"] = blArea

    dic_sensores = payload["sensores"]
    del payload[
        "sensores"
    ]  # remove do payload para nao atrapalhar com o inserir tbPosicao

    # chama essa funcao novamente para validar novos campos e criar o objeto pro insert
    dataTbPosicao, error = valida_e_constroi_insert("TbPosicao", payload)
    if error:
        return jsonify({"message": error}), 400

    dataSensorRegistro, error = prepara_insert_registros(
        dic_sensores=dic_sensores, cdDispositivo=cdDispositivo
    )
    if error:
        return jsonify({"message": error}), 400

    # insere posicao e registros. AVISO: se o primeiro insert funcionar e o segundo falhar,
    # havera uma posicao sem um sensor registro correspondente
    resultado_posicao = Inserir_TbPosicao(dataTbPosicao)
    
    for sensor in dataSensorRegistro:
        sensor["cdPosicao"] = resultado_posicao[0]["cdPosicao"]
    
    resultado_sensores = Inserir_TbSensorRegistro(dataSensorRegistro)

    resultado_posicao[0]["sensores"] = resultado_sensores

    return resultado_posicao