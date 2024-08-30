from collections import defaultdict
from typing import Any, Dict, List

import pandas as pd
import requests
from flask import jsonify

from db_utils import supabase_api
from utils import calcular_distancia, valida_e_constroi_insert


def Selecionar_VwTbProdutoTotalStatus(cdProdutoFiltro, db_client=supabase_api):
    query = db_client.table("VwTbProdutoTotalStatus").select(
        "cdProduto",
        "dsDescricao",
        "dsNome",
        "nrAlt",
        "nrCodigo",
        "nrComp",
        "nrLarg",
        "nrQtde",
        "StatusDispositivo",
        "QtdeTotal",
        "cdCliente",
        "imagens:TbImagens(cdCodigo, dsCaminho)",
    )

    if cdProdutoFiltro != "0":
        query.eq("cdProduto", cdProdutoFiltro)

    resultado = query.execute()

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

    for produto in resultado.data:
        cdProduto = produto["cdProduto"]

        # inicializa o produto se ele ainda nao existe no dict
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

        # adiciona status a lista
        if produto["nrQtde"] and produto["StatusDispositivo"]:
            produtos_dict[cdProduto]["status"].append(
                {"cdStatus": produto["StatusDispositivo"], "nrQtde": produto["nrQtde"]}
            )

    # Converte para lista para poder serializar como json
    produtos_list: List[Dict[str, Any]] = list(produtos_dict.values())

    return jsonify(produtos_list)


def Selecionar_TbCliente():
    resultado = (
        supabase_api.table("TbCliente")
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
            "cdUser",
            "dtRegistro",
        )
        .execute()
    )

    return resultado.data


# Inserir registros da tabela public.TbCliente
def Inserir_TbCliente(data):
    resultado = supabase_api.table("TbCliente").insert(data).execute()
    return resultado.data


def Selecionar_TbDestinatario(cdDestinatario, cdCliente, db_client=supabase_api):
    query = db_client.table("TbDestinatario").select("*")

    if cdDestinatario != "0":
        query.eq("cdDestinatario", cdDestinatario)

    query.eq("cdCliente", cdCliente)

    resultado = query.execute()

    return resultado.data


def Inserir_TbDestinatario(data):
    resultado = supabase_api.table("TbDestinatario").insert(data).execute()
    return resultado.data


def Selecionar_TbDispositivo(codigo, db_client=supabase_api):
    query = db_client.table("TbDispositivo").select("*")

    if codigo != "0":
        query.eq("cdDispositivo", codigo)

    resultado = query.execute()

    return resultado.data


def Inserir_TbDispositivo(data):
    resultado = supabase_api.table("TbDispositivo").insert(data).execute()
    return resultado.data


def Selecionar_TbImagens(codigo, db_client=supabase_api):
    query = db_client.table("TbImagens").select("*")

    if codigo != "0":
        query.eq("cdProduto", codigo)

    resultado = query.execute()

    return resultado.data


def Inserir_TbImagens(data, db_client=supabase_api):
    resultado = db_client.table("TbImagens").insert(data).execute()
    return resultado.data


def Selecionar_TbPosicao(filtros, db_client=supabase_api):
    query = db_client.table("TbPosicao").select("*")

    # aplica filtros
    for campo, valor in filtros.items():
        if campo == "dtRegistro":
            valor = f"{valor[:4]}-{valor[4:6]}-{valor[6:]}"
            query = query.gte(campo, f'{valor + " 00:00:00"}')
            query = query.lte(campo, f'{valor + " 23:59:59"}')
        else:
            query = query.eq(campo, valor)

    resultado = query.execute()

    return resultado.data


def get_endereco_coordenada(lat, long):
    payload = f"http://osm.taxidigital.net:4000/v1/reverse?point.lon={long}&point.lat={lat}&layers=address&sources=oa&size=1&cdFilial=0&cdTipoOrigem=0"
    requisicao = requests.get(payload)
    dic = requisicao.json()
    adress = dic["features"]

    for campos in adress:
        dados = campos["properties"]
        dsLogradouro = dados.get("street")
        dsNum = dados.get("housenumber")
        dsBairro = dados.get("neighbourhood")
        dsCidade = dados.get("locality")
        dsUF = dados.get("region_a")
        dsCep = dados.get("postalcode")
        dsPais = dados.get("country_code")

    return {
        "dsLogradouro": dsLogradouro,
        "dsNum": dsNum,
        "dsBairro": dsBairro,
        "dsCidade": dsCidade,
        "dsUF": dsUF,
        "dsCep": dsCep,
        "dsPais": dsPais,
    }


def is_dentro_area(cdDispositivo, dsLat, dsLong):
    dic_endereco_pdv = Selecionar_VwTbDestinatarioDispositivo(codigoDisp=cdDispositivo)
    dic_endereco_pdv = dict(dic_endereco_pdv[0])

    dsLatPdv = dic_endereco_pdv["dsLat"]
    dsLongPdv = dic_endereco_pdv["dsLong"]
    nrRaio = dic_endereco_pdv["nrRaio"]
    nrDistancia = calcular_distancia(dsLat, dsLong, dsLatPdv, dsLongPdv)

    return float(nrDistancia) <= float(nrRaio)


def get_produto_item_from_sensores_result(sensores_result, cdSensor):
    for sensor in sensores_result:
        if cdSensor == sensor["cdSensor"]:
            return sensor["cdProdutoItem"], None

    return None, f"sensor com id {cdSensor} nao foi encontrado"


def prepara_insert_registros(dic_sensores, cdDispositivo):
    dataSensoresRegistro = []

    # busca produto itens pelos sensores
    sensores_query = supabase_api.table("TbSensor").select("cdSensor", "cdProdutoItem")
    id_sensores = []

    for sensor in dic_sensores:
        if "cdSensor" not in sensor:
            return None, "Objeto sensor sem cdSensor"
        if "nrValor" not in sensor:
            return None, "Objeto sensor sem nrValor"

        id_sensores.append(sensor["cdSensor"])

    sensores_result = sensores_query.in_("cdSensor", id_sensores).execute()

    for sensor in dic_sensores:
        cdProdutoItem, error = get_produto_item_from_sensores_result(
            sensores_result=sensores_result.data, cdSensor=sensor["cdSensor"]
        )

        if error:
            return None, error

        payload_sensor_registro = {
            "cdDispositivo": cdDispositivo,
            "cdSensor": sensor["cdSensor"],
            "nrValor": sensor["nrValor"],
            "cdProdutoItem": cdProdutoItem,
        }

        data, error = valida_e_constroi_insert(
            table="TbSensorRegistro",
            payload=payload_sensor_registro,
            ignorar_fields=["cdPosicao"],
        )

        if error:
            return None, error

        dataSensoresRegistro.append(data)

    return dataSensoresRegistro, None


def Inserir_TbSensorRegistro(data):
    resultado = supabase_api.table("TbSensorRegistro").insert(data).execute()
    return resultado.data


def Inserir_TbPosicao(data):
    resultado = supabase_api.table("TbPosicao").insert(data).execute()
    return resultado.data


def Selecionar_VwTbDestinatarioDispositivo(codigoDisp):
    resultado = (
        supabase_api.table("VwTbDestinatarioDispositivo")
        .select("*")
        .eq("cdDispositivo", codigoDisp)
        .execute()
    )
    return resultado.data


def Inserir_TbProduto(data, db_client=supabase_api):
    resultado = db_client.table("TbProduto").insert(data).execute()
    return resultado.data


def Alterar_TbProduto(Campo, Dado, UpData, db_client=supabase_api):
    response = db_client.table("TbProduto").update(UpData).eq(Campo, Dado).execute()
    return response.data


def deletar_TbProduto(cdProduto):
    resultado = (
        supabase_api.table("TbProduto").delete().eq("cdProduto", cdProduto).execute()
    )
    return resultado.data


def Inserir_TbSensor(data):
    resultado = supabase_api.table("TbSensor").insert(data).execute()
    return resultado.data


def Selecionar_VwTbProdutoTipo(codigo, db_client=supabase_api):
    query = db_client.table("VwTbProdutoTipo").select("*")

    if codigo != "0":
        query.eq("cdProduto", codigo)

    resultado = query.execute()

    return resultado.data


def Selecionar_VwTbProdutoTotal(codigo, db_client=supabase_api):
    query = db_client.table("VwTbProdutoTotal").select("*")

    if codigo != "0":
        query.eq("cdProduto", codigo)

    resultado = query.execute()

    return resultado.data


def Selecionar_VwRelHistoricoDispositivoProduto(filtros, db_client=supabase_api):
    query = db_client.table("VwRelHistoricoDispositivoProduto").select("*")

    # aplica filtros
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
def Selecionar_HistoricoPaginaDispositivo(filtros, db_client=supabase_api):
    resultado = Selecionar_VwRelHistoricoDispositivoProduto(filtros, db_client)

    if len(resultado) == 0:
        return resultado

    # converte em pandas dataframe
    df = pd.DataFrame(resultado)

    # mantem os dados originais para serem mergidos depois
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


def Selecionar_VwRelDadosDispositivo(filtros, db_client=supabase_api):
    query = db_client.table("VwRelDadosDispositivo").select("*")

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


def Selecionar_VwTbPosicaoAtual(filtros, db_client=supabase_api):
    query = db_client.table("VwTbPosicaoAtual").select("*")

    for campo, valor in filtros.items():
        query = query.eq(campo, valor)

    resultado = query.execute()
    return resultado.data

def Selecionar_TbChamados(db_client=supabase_api):
    resultado = (
        db_client.table("TbChamados")
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
def Inserir_TbChamados(data, db_client=supabase_api):
    resultado = db_client.table("TbChamados").insert(data).execute()
    return resultado.data
