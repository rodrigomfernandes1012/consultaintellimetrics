# SERVER API
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import mysql.connector
import requests
import boto3




#Amazon
selecao = []
dicionario = []
dic2 = []
dic_whats = []
dic_whats2 = []
dic_teste = []



token = "8c4EF9vXi8TZe6581e0af85c25"

client = boto3.client(
    service_name='s3',
    aws_access_key_id='',
    aws_secret_access_key='NfcacA88Tp+M1yHch9JNuUJT3pFQ+dtecEHpMlvd',
    region_name='eu-west-2' # voce pode usar qualquer regiao
)
def Upload_file(file_name):
  client.upload_file(file_name, "dbfilesintellimetrics", file_name)


def conecta_bd():
  conexao = mysql.connector.connect(
      host='dbintellimetrics.c3kc6gou2fhz.us-west-2.rds.amazonaws.com',
      user='admin',
      password='IntelliMetr!c$',
      database='DbIntelliMetrics')
  return conexao

#Selecionar registros da tabela DbIntelliMetrics.TbDestinatario
def Selecionar_TbDestinatario():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdDestinatario, dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus from DbIntelliMetrics.TbDestinatario'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado

#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbDestinatario
def Inserir_TbDestinatario(dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbDestinatario ( dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus ) values ("{dsNome}", "{nrCnpj}", "{nrIe}", "{nrInscMun}", "{dsLogradouro}", "{nrNumero}", "{dsComplemento}", "{dsBairro}", "{dsCep}", "{dsCidade}", "{dsUF}", "{dsObs}", "{cdStatus}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbDestinatario
def deletar_TbDestinatario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbDestinatario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbDestinatario
def Alterar_TbDestinatario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbDestinatario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO





def pesquisa_posicoes():
  conexao = conecta_bd()
  cursor = conexao.cursor(dictionary=True)
  comando = f'SELECT * FROM TbPosicao order by dtData, dtHora;'
  cursor.execute(comando)
  selecao = cursor.fetchall()  # ler o banco de dados
  cursor.close()
  conexao.close()
  return selecao


def pesquisa_geral():
  conexao = conecta_bd()
  cursor = conexao.cursor(dictionary=True)
  comando = f'SELECT * FROM TbChamados;'
  cursor.execute(comando)
  selecao = cursor.fetchall()  # ler o banco de dados
  cursor.close()
  conexao.close()
  return selecao


def pesquisa_chamados(di, df, dt):
  conexao = conecta_bd()
  cursor = conexao.cursor(dictionary=True)
  comando = f'SELECT  dsTipo, dsDescricao, nrQtde FROM TbChamados where dtOperacao >= STR_TO_DATE("{di}","%d/%m/%Y") and dtOperacao <= STR_TO_DATE("{df}","%d/%m/%Y") and dsTipo = "{dt}";'
  cursor.execute(comando)
  selecao = cursor.fetchall()  # ler o banco de dados
  cursor.close()
  conexao.close()
  return selecao


def pesquisa_ticket(di, df):
  conexao = conecta_bd()
  cursor = conexao.cursor(dictionary=True)
  comando = f'SELECT dtOperacao, dsAtendimento, nrAbertos, nrFechados, nrPendentes FROM TbTicket where dtOperacao >= STR_TO_DATE("{di}","%d/%m/%Y") and dtOperacao <= STR_TO_DATE("{df}","%d/%m/%Y");'
  cursor.execute(comando)
  selecao = cursor.fetchall()  # ler o banco de dados
  cursor.close()
  conexao.close()
  return selecao


def pesquisa_ticket_resumo(di, df):
  conexao = conecta_bd()
  cursor = conexao.cursor(dictionary=True)
  comando = f'SELECT dtOperacao, dsAtendimento, dsNaoAtribuido, dsSemResolucao, dsAtualizado, dsPendente, dsResolvido FROM TbTicketResumo where  dtOperacao >= STR_TO_DATE("{di}","%d/%m/%Y") and dtOperacao <= STR_TO_DATE("{df}","%d/%m/%Y");'
  cursor.execute(comando)
  selecao = cursor.fetchall()  # ler o banco de dados
  cursor.close()
  conexao.close()
  return selecao

#Selecionar registros da tabela DbIntelliMetrics.TbChamados
def Selecionar_TbChamados():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdChamados, dtOperacao, dsTipo, dsDescricao, nrQtde from DbIntelliMetrics.TbChamados'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbChamados
def Inserir_TbChamados(dtOperacao, dsTipo, dsDescricao, nrQtde):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbChamados ( dtOperacao, dsTipo, dsDescricao, nrQtde ) values ("{dtOperacao}", "{dsTipo}", "{dsDescricao}", "{nrQtde}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbChamados
def deletar_TbChamados(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbChamados where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbChamados
def Alterar_TbChamados(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbChamados set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbCliente
def Selecionar_TbCliente():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdCliente, dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus from DbIntelliMetrics.TbCliente'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbCliente
def Inserir_TbCliente(dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbCliente ( dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus ) values ("{dsNome}", "{nrCnpj}", "{nrIe}", "{nrInscMun}", "{dsLogradouro}", "{nrNumero}", "{dsComplemento}", "{dsBairro}", "{dsCep}", "{dsCidade}", "{dsUF}", "{dsObs}", "{cdStatus}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbCliente
def deletar_TbCliente(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbCliente where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbCliente
def Alterar_TbCliente(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbCliente set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO




#Selecionar registros da tabela DbIntelliMetrics.TbDispositivo
def Selecionar_TbDispositivo():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdDispositivo, dsDispositivo, dsModelo, dsDescricao, dsObs, dsLayout, nrChip, cdStatus from DbIntelliMetrics.TbDispositivo'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbDispositivo
def Inserir_TbDispositivo(dsDispositivo, dsModelo, dsDescricao, dsObs, dsLayout, nrChip, cdStatus):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbDispositivo ( dsDispositivo, dsModelo, dsDescricao, dsObs, dsLayout, nrChip, cdStatus ) values ("{dsDispositivo}", "{dsModelo}", "{dsDescricao}", "{dsObs}", "{dsLayout}", "{nrChip}", "{cdStatus}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbDispositivo
def deletar_TbDispositivo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbDispositivo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbDispositivo
def Alterar_TbDispositivo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbDispositivo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbPosicao
def Selecionar_TbPosicao():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdPosicao, dsModelo, dtData, dtHora, dsLat, dsLong, nrTemp, nrBat, nrSeq, dsArquivo, cdDispositivo, dsEndereco from DbIntelliMetrics.TbPosicao'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbPosicao
def Inserir_TbPosicao(dsModelo, dtData, dtHora, dsLat, dsLong, nrTemp, nrBat, nrSeq, dsArquivo, cdDispositivo, dsEndereco):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbPosicao ( dsModelo, dtData, dtHora, dsLat, dsLong, nrTemp, nrBat, nrSeq, dsArquivo, cdDispositivo, dsEndereco ) values ("{dsModelo}", "{dtData}", "{dtHora}", "{dsLat}", "{dsLong}", "{nrTemp}", "{nrBat}", "{nrSeq}", "{dsArquivo}", "{cdDispositivo}", "{dsEndereco}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbPosicao
def deletar_TbPosicao(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbPosicao where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbPosicao
def Alterar_TbPosicao(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbPosicao set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbProduto
def Selecionar_TbProduto():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdProduto, dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus from DbIntelliMetrics.TbProduto'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbProduto
def Inserir_TbProduto(dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbProduto ( dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus ) values ("{dsNome}", "{dsDescricao}", "{nrCodigo}", "{nrLarg}", "{nrComp}", "{nrAlt}", "{cdStatus}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbProduto
def deletar_TbProduto(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbProduto where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbProduto
def Alterar_TbProduto(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbProduto set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbRelacionamento
def Selecionar_TbRelacionamento():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdRelacionamento, cdPai, cdFilho, cdTipo, dsDescricao, cdStatus from DbIntelliMetrics.TbRelacionamento'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbRelacionamento
def Inserir_TbRelacionamento(cdPai, cdFilho, cdTipo, dsDescricao, cdStatus):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbRelacionamento ( cdPai, cdFilho, cdTipo, dsDescricao, cdStatus ) values ("{cdPai}", "{cdFilho}", "{cdTipo}", "{dsDescricao}", "{cdStatus}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbRelacionamento
def deletar_TbRelacionamento(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbRelacionamento where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbRelacionamento
def Alterar_TbRelacionamento(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbRelacionamento set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbSensor
def Selecionar_TbSensor():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdSensor, dsNome, cdTipo, dsDescricao, cdUnidade, nrUnidadeIni, nrUnidadeFim from DbIntelliMetrics.TbSensor'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbSensor
def Inserir_TbSensor(dsNome, cdTipo, dsDescricao, cdUnidade, nrUnidadeIni, nrUnidadeFim):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbSensor ( dsNome, cdTipo, dsDescricao, cdUnidade, nrUnidadeIni, nrUnidadeFim ) values ("{dsNome}", "{cdTipo}", "{dsDescricao}", "{cdUnidade}", "{nrUnidadeIni}", "{nrUnidadeFim}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbSensor
def deletar_TbSensor(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbSensor where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbSensor
def Alterar_TbSensor(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbSensor set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbStatus
def Selecionar_TbStatus():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdStatus, dsStatus from DbIntelliMetrics.TbStatus'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbStatus
def Inserir_TbStatus(dsStatus):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbStatus ( dsStatus ) values ("{dsStatus}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbStatus
def deletar_TbStatus(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbStatus where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbStatus
def Alterar_TbStatus(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbStatus set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbTag
def Selecionar_TbTag():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdTag, dsDescricao, dsConteudo from DbIntelliMetrics.TbTag'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbTag
def Inserir_TbTag(dsDescricao, dsConteudo):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbTag ( dsDescricao, dsConteudo ) values ("{dsDescricao}", "{dsConteudo}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbTag
def deletar_TbTag(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbTag where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbTag
def Alterar_TbTag(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbTag set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbTicket
def Selecionar_TbTicket():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdTicket, dtOperacao, dsAtendimento, nrAbertos, nrFechados, nrPendentes from DbIntelliMetrics.TbTicket'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbTicket
def Inserir_TbTicket(dtOperacao, dsAtendimento, nrAbertos, nrFechados, nrPendentes):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbTicket ( dtOperacao, dsAtendimento, nrAbertos, nrFechados, nrPendentes ) values ("{dtOperacao}", "{dsAtendimento}", "{nrAbertos}", "{nrFechados}", "{nrPendentes}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbTicket
def deletar_TbTicket(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbTicket where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbTicket
def Alterar_TbTicket(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbTicket set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbTicketResumo
def Selecionar_TbTicketResumo():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdTicketResumo, dtOperacao, dsAtendimento, dsNaoAtribuido, dsSemResolucao, dsAtualizado, dsPendente, dsResolvido from DbIntelliMetrics.TbTicketResumo'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbTicketResumo
def Inserir_TbTicketResumo(dtOperacao, dsAtendimento, dsNaoAtribuido, dsSemResolucao, dsAtualizado, dsPendente, dsResolvido):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbTicketResumo ( dtOperacao, dsAtendimento, dsNaoAtribuido, dsSemResolucao, dsAtualizado, dsPendente, dsResolvido ) values ("{dtOperacao}", "{dsAtendimento}", "{dsNaoAtribuido}", "{dsSemResolucao}", "{dsAtualizado}", "{dsPendente}", "{dsResolvido}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbTicketResumo
def deletar_TbTicketResumo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbTicketResumo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbTicketResumo
def Alterar_TbTicketResumo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbTicketResumo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbTipo
def Selecionar_TbTipo():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdTipo, dsDescricao from DbIntelliMetrics.TbTipo'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbTipo
def Inserir_TbTipo(dsDescricao):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbTipo ( dsDescricao ) values ("{dsDescricao}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbTipo
def deletar_TbTipo(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbTipo where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbTipo
def Alterar_TbTipo(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbTipo set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbUnidade
def Selecionar_TbUnidade():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdUnidade, dsUnidade, dsSimbolo from DbIntelliMetrics.TbUnidade'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbUnidade
def Inserir_TbUnidade(dsUnidade, dsSimbolo):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbUnidade ( dsUnidade, dsSimbolo ) values ("{dsUnidade}", "{dsSimbolo}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbUnidade
def deletar_TbUnidade(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbUnidade where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbUnidade
def Alterar_TbUnidade(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbUnidade set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbUsuario
def Selecionar_TbUsuario():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdUsuario, dsNome, dsLogin, dsSenha, cdPerfil from DbIntelliMetrics.TbUsuario'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbUsuario
def Inserir_TbUsuario(dsNome, dsLogin, dsSenha, cdPerfil):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbUsuario ( dsNome, dsLogin, dsSenha, cdPerfil ) values ("{dsNome}", "{dsLogin}", "{dsSenha}", "{cdPerfil}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbUsuario
def deletar_TbUsuario(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbUsuario where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbUsuario
def Alterar_TbUsuario(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbUsuario set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbVisita
def Selecionar_TbVisita():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdVisita, cdCliente, cdVisitante, dtData from DbIntelliMetrics.TbVisita'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbVisita
def Inserir_TbVisita(cdCliente, cdVisitante, dtData):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbVisita ( cdCliente, cdVisitante, dtData ) values ("{cdCliente}", "{cdVisitante}", "{dtData}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbVisita
def deletar_TbVisita(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbVisita where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbVisita
def Alterar_TbVisita(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbVisita set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbVisitante
def Selecionar_TbVisitante():
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'select cdVisitante, dsNome, nrTelefone, nrDocumento, dsEmail from DbIntelliMetrics.TbVisitante'
    cursor.execute(comando)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.close()
    return  resultado
#FIM DA FUNÇÃO


#Inserir registros da tabela DbIntelliMetrics.TbVisitante
def Inserir_TbVisitante(dsNome, nrTelefone, nrDocumento, dsEmail):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'insert into DbIntelliMetrics.TbVisitante ( dsNome, nrTelefone, nrDocumento, dsEmail ) values ("{dsNome}", "{nrTelefone}", "{nrDocumento}", "{dsEmail}")'
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Deletar registros da tabela DbIntelliMetrics.TbVisitante
def deletar_TbVisitante(Campo, Dado):
    conexao = conecta_bd()
    cursor = conexao.cursor(dictionary=True)
    comando = f'delete from DbIntelliMetrics.TbVisitante where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO


#Alterar registros da tabela DbIntelliMetrics.TbVisitante
def Alterar_TbVisitante(Campo, Dado, UpCampo, UpDado):
    conexao = conecta_bd()
    comando = f'update DbIntelliMetrics.TbVisitante set  {UpCampo}="{UpDado}"  where {Campo}="{Dado}"  '
    cursor.execute(comando)
    conexao.commit()
#FIM DA FUNÇÃO




app = Flask(__name__)  # cria o site
CORS(app, resources={r"*": {"origins": "*"}})




@app.route('/chamados')
def home():
  resultado = Selecionar_TbChamados()
  return resultado

@app.route("/whats")
def pesquisa_whats():
  resultado = dic_whats2
  return resultado

@app.route("/whats", methods=['POST'])
def whats_post():
  dic_whats = request.get_json()
  dic = json.dumps(dic_whats)
  dic0 = json.loads(dic)
  dic_whats2.append(dic0)
  resultado = dic_whats2
  return resultado




@app.route("/gps")
def pesquisa_gps_get():
  resultado = pesquisa_posicoes()
  return resultado


@app.route("/gps", methods=['POST'])
def gps_post():
  dicionario = request.get_json()
  dic = json.dumps(dicionario)
  dic0 = json.loads(dic)
  dic2.append(dic0)
  resultado = dic2
  return resultado


# PESQUISA O ENDEREÇO PELA COORDENADA
@app.route("/coordenadas", methods=['POST'])
def get_endereco_coordenada():
  dicionario = request.get_json()
  lat = dicionario['lat']
  long = dicionario['long']
  payload = (
      f'http://osm.taxidigital.net:4000/v1/reverse?point.lon={long}&point.lat={lat}&layers=address&sources=oa&size=1&cdFilial=0&cdTipoOrigem=0'
  )
  requisicao = (requests.get(payload))
  dic = (requisicao.json())
  #print(dic)
  adress = (dic['features'])
  for campos in adress:
    #print(campos['properties'])
    dados = (campos['properties'])
    rua = (dados.get("label"))
    return rua


@app.route("/coordenadas_osm", methods=['POST'])
def get_endereco_coordenada_osm():
  dicionario = request.get_json()
  lat = dicionario['lat']
  long = dicionario['long']
  payload = (
      f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={long}&format=json&zoom=18&addressdetails=1'
  )
  requisicao = requests.get(payload)
  dic = (requisicao.json())
  address = (dic['address'])
  rua = ('Endereço: ' + address["road"] + ', ' + address['suburb'] + ' - ' +
         address['municipality'] + ' - ' + address['state'])

  return rua


@app.route("/")
def pesquisa_get():
  resultado = dicionario
  return resultado



@app.route("/", methods=['POST'])
def chamados2_post():
  dicionario = request.get_json()
  dic0 = dicionario['token']
  dic1 = dicionario['dtInicio']
  dic2 = dicionario['dtFinal']
  dic3 = dicionario['dsTipo']
  if dic0 == token:
    resultado = pesquisa_chamados(dic1, dic2, dic3)
    return resultado
  else:
    return "Token inválido !"


@app.route("/chamados", methods=['POST'])
def chamados_post():
  dicionario = request.get_json()
  dic0 = dicionario['token']
  dic1 = dicionario['dtInicio']
  dic2 = dicionario['dtFinal']
  dic3 = dicionario['dsTipo']
  if dic0 == token:
    resultado = pesquisa_chamados(dic1, dic2, dic3)
    return resultado
  else:
    return "Token inválido !"


@app.route("/ticket", methods=['POST'])
def ticket_post():
  dicionario = request.get_json()
  dic0 = dicionario['token']
  dic1 = dicionario['dtInicio']
  dic2 = dicionario['dtFinal']
  if dic0 == token:
    resultado = pesquisa_ticket(dic1, dic2)
    return resultado
  else:
    return "Token Inválido !"


@app.route("/ticketresumo", methods=['POST'])
def ticket_resumo_post():
  dicionario = request.get_json()
  dic0 = dicionario['token']
  dic1 = dicionario['dtInicio']
  dic2 = dicionario['dtFinal']
  if dic0 == token:
    resultado = pesquisa_ticket_resumo(dic1, dic2)
    return resultado
  else:
    return "Token inválido !"



#Selecionar registros da tabela DbIntelliMetrics.TbChamados
@app.route("/Chamados")
def get_Chamados():
    resultado = Selecionar_TbChamados()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbCliente
@app.route("/Cliente")
def get_Cliente():
    resultado = Selecionar_TbCliente()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbDestinatario
@app.route("/Destinatario")
def get_Destinatario():
    resultado = Selecionar_TbDestinatario()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbDispositivo
@app.route("/Dispositivo")
def get_Dispositivo():
    resultado = Selecionar_TbDispositivo()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbPosicao
@app.route("/Posicao")
def get_Posicao():
    resultado = Selecionar_TbPosicao()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbProduto
@app.route("/Produto")
def get_Produto():
    resultado = Selecionar_TbProduto()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbRelacionamento
@app.route("/Relacionamento")
def get_Relacionamento():
    resultado = Selecionar_TbRelacionamento()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbSensor
@app.route("/Sensor")
def get_Sensor():
    resultado = Selecionar_TbSensor()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbStatus
@app.route("/Status")
def get_Status():
    resultado = Selecionar_TbStatus()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbTag
@app.route("/Tag")
def get_Tag():
    resultado = Selecionar_TbTag()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbTicket
@app.route("/Ticket")
def get_Ticket():
    resultado = Selecionar_TbTicket()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbTicketResumo
@app.route("/TicketResumo")
def get_TicketResumo():
    resultado = Selecionar_TbTicketResumo()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbTipo
@app.route("/Tipo")
def get_Tipo():
    resultado = Selecionar_TbTipo()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbUnidade
@app.route("/Unidade")
def get_Unidade():
    resultado = Selecionar_TbUnidade()
    return resultado
#FIM DA FUNÇÃO


#Selecionar registros da tabela DbIntelliMetrics.TbUsuario
@app.route("/Usuario")
def get_Usuario():
    resultado = Selecionar_TbUsuario()
    return resultado
#FIM DA FUNÇÃO
########################################################
#INSERIR REGISTROS
########################################################
#Inserir registros no EndPoint Chamados
@app.route('/Chamados', methods=['POST'])
def post_Chamados():
    payload = request.get_json()
    dtOperacao = payload ['dtOperacao']
    dsTipo = payload ['dsTipo']
    dsDescricao = payload ['dsDescricao']
    nrQtde = payload ['nrQtde']
    Inserir_TbChamados(dtOperacao, dsTipo, dsDescricao, nrQtde)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Cliente


#Inserir registros no EndPoint Cliente
@app.route('/Cliente', methods=['POST'])
def post_Cliente():
    payload = request.get_json()
    dsNome = payload ['dsNome']
    nrCnpj = payload ['nrCnpj']
    nrIe = payload ['nrIe']
    nrInscMun = payload ['nrInscMun']
    dsLogradouro = payload ['dsLogradouro']
    nrNumero = payload ['nrNumero']
    dsComplemento = payload ['dsComplemento']
    dsBairro = payload ['dsBairro']
    dsCep = payload ['dsCep']
    dsCidade = payload ['dsCidade']
    dsUF = payload ['dsUF']
    dsObs = payload ['dsObs']
    cdStatus = payload ['cdStatus']
    Inserir_TbCliente(dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Destinatario


#Inserir registros no EndPoint Destinatario
@app.route('/Destinatario', methods=['POST'])
def post_Destinatario():
    payload = request.get_json()
    dsNome = payload ['dsNome']
    nrCnpj = payload ['nrCnpj']
    nrIe = payload ['nrIe']
    nrInscMun = payload ['nrInscMun']
    dsLogradouro = payload ['dsLogradouro']
    nrNumero = payload ['nrNumero']
    dsComplemento = payload ['dsComplemento']
    dsBairro = payload ['dsBairro']
    dsCep = payload ['dsCep']
    dsCidade = payload ['dsCidade']
    dsUF = payload ['dsUF']
    dsObs = payload ['dsObs']
    cdStatus = payload ['cdStatus']
    Inserir_TbDestinatario(dsNome, nrCnpj, nrIe, nrInscMun, dsLogradouro, nrNumero, dsComplemento, dsBairro, dsCep, dsCidade, dsUF, dsObs, cdStatus)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Dispositivo


#Inserir registros no EndPoint Dispositivo
@app.route('/Dispositivo', methods=['POST'])
def post_Dispositivo():
    payload = request.get_json()
    dsDispositivo = payload ['dsDispositivo']
    dsModelo = payload ['dsModelo']
    dsDescricao = payload ['dsDescricao']
    dsObs = payload ['dsObs']
    dsLayout = payload ['dsLayout']
    nrChip = payload ['nrChip']
    cdStatus = payload ['cdStatus']
    Inserir_TbDispositivo(dsDispositivo, dsModelo, dsDescricao, dsObs, dsLayout, nrChip, cdStatus)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Posicao


#Inserir registros no EndPoint Posicao
@app.route('/Posicao', methods=['POST'])
def post_Posicao():
    payload = request.get_json()
    dsModelo = payload ['dsModelo']
    dtData = payload ['dtData']
    dtHora = payload ['dtHora']
    dsLat = payload ['dsLat']
    dsLong = payload ['dsLong']
    nrTemp = payload ['nrTemp']
    nrBat = payload ['nrBat']
    nrSeq = payload ['nrSeq']
    dsArquivo = payload ['dsArquivo']
    cdDispositivo = payload ['cdDispositivo']
    dsEndereco = payload ['dsEndereco']
    Inserir_TbPosicao(dsModelo, dtData, dtHora, dsLat, dsLong, nrTemp, nrBat, nrSeq, dsArquivo, cdDispositivo, dsEndereco)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Produto


#Inserir registros no EndPoint Produto
@app.route('/Produto', methods=['POST'])
def post_Produto():
    payload = request.get_json()
    dsNome = payload ['dsNome']
    dsDescricao = payload ['dsDescricao']
    nrCodigo = payload ['nrCodigo']
    nrLarg = payload ['nrLarg']
    nrComp = payload ['nrComp']
    nrAlt = payload ['nrAlt']
    cdStatus = payload ['cdStatus']
    Inserir_TbProduto(dsNome, dsDescricao, nrCodigo, nrLarg, nrComp, nrAlt, cdStatus)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Relacionamento


#Inserir registros no EndPoint Relacionamento
@app.route('/Relacionamento', methods=['POST'])
def post_Relacionamento():
    payload = request.get_json()
    cdPai = payload ['cdPai']
    cdFilho = payload ['cdFilho']
    cdTipo = payload ['cdTipo']
    dsDescricao = payload ['dsDescricao']
    cdStatus = payload ['cdStatus']
    Inserir_TbRelacionamento(cdPai, cdFilho, cdTipo, dsDescricao, cdStatus)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Sensor


#Inserir registros no EndPoint Sensor
@app.route('/Sensor', methods=['POST'])
def post_Sensor():
    payload = request.get_json()
    dsNome = payload ['dsNome']
    cdTipo = payload ['cdTipo']
    dsDescricao = payload ['dsDescricao']
    cdUnidade = payload ['cdUnidade']
    nrUnidadeIni = payload ['nrUnidadeIni']
    nrUnidadeFim = payload ['nrUnidadeFim']
    Inserir_TbSensor(dsNome, cdTipo, dsDescricao, cdUnidade, nrUnidadeIni, nrUnidadeFim)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Status


#Inserir registros no EndPoint Status
@app.route('/Status', methods=['POST'])
def post_Status():
    payload = request.get_json()
    dsStatus = payload ['dsStatus']
    Inserir_TbStatus(dsStatus)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Tag


#Inserir registros no EndPoint Tag
@app.route('/Tag', methods=['POST'])
def post_Tag():
    payload = request.get_json()
    dsDescricao = payload ['dsDescricao']
    dsConteudo = payload ['dsConteudo']
    Inserir_TbTag(dsDescricao, dsConteudo)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Ticket


#Inserir registros no EndPoint Ticket
@app.route('/Ticket', methods=['POST'])
def post_Ticket():
    payload = request.get_json()
    dtOperacao = payload ['dtOperacao']
    dsAtendimento = payload ['dsAtendimento']
    nrAbertos = payload ['nrAbertos']
    nrFechados = payload ['nrFechados']
    nrPendentes = payload ['nrPendentes']
    Inserir_TbTicket(dtOperacao, dsAtendimento, nrAbertos, nrFechados, nrPendentes)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/TicketResumo


#Inserir registros no EndPoint TicketResumo
@app.route('/TicketResumo', methods=['POST'])
def post_TicketResumo():
    payload = request.get_json()
    dtOperacao = payload ['dtOperacao']
    dsAtendimento = payload ['dsAtendimento']
    dsNaoAtribuido = payload ['dsNaoAtribuido']
    dsSemResolucao = payload ['dsSemResolucao']
    dsAtualizado = payload ['dsAtualizado']
    dsPendente = payload ['dsPendente']
    dsResolvido = payload ['dsResolvido']
    Inserir_TbTicketResumo(dtOperacao, dsAtendimento, dsNaoAtribuido, dsSemResolucao, dsAtualizado, dsPendente, dsResolvido)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Tipo


#Inserir registros no EndPoint Tipo
@app.route('/Tipo', methods=['POST'])
def post_Tipo():
    payload = request.get_json()
    dsDescricao = payload ['dsDescricao']
    Inserir_TbTipo(dsDescricao)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Unidade


#Inserir registros no EndPoint Unidade
@app.route('/Unidade', methods=['POST'])
def post_Unidade():
    payload = request.get_json()
    dsUnidade = payload ['dsUnidade']
    dsSimbolo = payload ['dsSimbolo']
    Inserir_TbUnidade(dsUnidade, dsSimbolo)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Usuario


#Inserir registros no EndPoint Usuario
@app.route('/Usuario', methods=['POST'])
def post_Usuario():
    payload = request.get_json()
    dsNome = payload ['dsNome']
    dsLogin = payload ['dsLogin']
    dsSenha = payload ['dsSenha']
    cdPerfil = payload ['cdPerfil']
    Inserir_TbUsuario(dsNome, dsLogin, dsSenha, cdPerfil)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO

#https://replit.taxidigital.net/Visita


#Inserir registros no EndPoint Visita
@app.route('/Visita', methods=['POST'])
def post_Visita():
    payload = request.get_json()
    cdCliente = payload ['cdCliente']
    cdVisitante = payload ['cdVisitante']
    dtData = payload ['dtData']
    Inserir_TbVisita(cdCliente, cdVisitante, dtData)
    return "Cadastramento realizado com sucesso"
#FIM DA FUNÇÃO






@app.route('/Foto', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = (file.filename)
    Upload_file(filename)
    return "Upload realizado com sucesso"


#nova alteracao

app.run()
#app.run(host="0.0.0.0")  # coloca o site no ar
