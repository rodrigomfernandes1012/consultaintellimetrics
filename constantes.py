campos_tabelas = {
    "TbAcessoIntelBras": {
        "dsUserId": {"type": "character varying", "required": False},
        "dsCardName": {"type": "character varying", "required": False},
        "dsCardNo": {"type": "character varying", "required": False},
        "dsUserType": {"type": "character varying", "required": False},
        "dsPassword": {"type": "character varying", "required": False},
        "dsDoor": {"type": "character varying", "required": False},
        "dsErrorCode": {"type": "character varying", "required": False},
        "dsMethod": {"type": "character varying", "required": False},
        "dsReaderID": {"type": "character varying", "required": False},
        "dsStatus": {"type": "character varying", "required": False},
        "dsType": {"type": "character varying", "required": False},
        "dsEntry": {"type": "character varying", "required": False},
        "dsUtc": {"type": "character varying", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
    "TbChamados": {
        "dtOperacao": {"type": "text", "required": False},
        "dsTipo": {"type": "text", "required": False},
        "dsDescricao": {"type": "text", "required": False},
        "nrQtde": {"type": "integer", "required": False},
        "dsUser": {"type": "character varying", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
    "TbCliente": {
        "dsNome": {"type": "text", "required": False},
        "nrCnpj": {"type": "text", "required": False},
        "nrIe": {"type": "text", "required": False},
        "nrInscMun": {"type": "text", "required": False},
        "dsLogradouro": {"type": "text", "required": False},
        "nrNumero": {"type": "text", "required": False},
        "dsComplemento": {"type": "text", "required": False},
        "dsBairro": {"type": "text", "required": False},
        "dsCep": {"type": "text", "required": False},
        "dsCidade": {"type": "text", "required": False},
        "dsUF": {"type": "text", "required": False},
        "dsObs": {"type": "text", "required": False},
        "cdStatus": {"type": "text", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
        "cdUser": {"type": "uuid", "required": False},
        "cdClientePai": {"type": "integer", "required": False},
    },
    "TbClienteChave": {
        "dsChave": {"type": "text", "required": True},
        "dtRegistro": {"type": "timestamp with time zone", "required": False},
        "nrLimite": {"type": "integer", "required": False},
        "cdCliente": {"type": "integer", "required": True},
    },
    "TbDestinatario": {
        "dsNome": {"type": "text", "required": False},
        "nrCnpj": {"type": "text", "required": False},
        "nrIe": {"type": "text", "required": False},
        "nrInscMun": {"type": "text", "required": False},
        "dsLogradouro": {"type": "text", "required": False},
        "nrNumero": {"type": "text", "required": False},
        "dsComplemento": {"type": "text", "required": False},
        "dsBairro": {"type": "text", "required": False},
        "dsCep": {"type": "text", "required": False},
        "dsCidade": {"type": "text", "required": False},
        "dsUF": {"type": "text", "required": False},
        "dsObs": {"type": "text", "required": False},
        "cdStatus": {"type": "text", "required": False},
        "dsLat": {"type": "character varying", "required": False},
        "dsLong": {"type": "character varying", "required": False},
        "nrRaio": {"type": "double precision", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
        "cdCliente": {"type": "integer", "required": False},
        "cdUser": {"type": "uuid", "required": False},
        "cdEndereco": {"type": "integer", "required": False},
    },
    "TbDispositivo": {
        "dsDispositivo": {"type": "text", "required": False},
        "dsModelo": {"type": "integer", "required": False},
        "dsDescricao": {"type": "text", "required": False},
        "dsObs": {"type": "text", "required": False},
        "dsLayout": {"type": "text", "required": False},
        "nrChip": {"type": "bigint", "required": False},
        "cdStatus": {"type": "text", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
        "cdDestinatario": {"type": "integer", "required": False},
        "cdProduto": {"type": "integer", "required": False},
        "cdCliente": {"type": "integer", "required": False},
        "cdUser": {"type": "uuid", "required": False},
    },
    "TbImagens": {
        "dsCaminho": {"type": "character varying", "required": True},
        "cdCodigo": {"type": "character varying", "required": True},
        "dtRegistro": {"type": "timestamp", "required": False},
        "cdProduto": {"type": "integer", "required": False},
        "nrImagem": {"type": "integer", "required": False},
        "cdUser": {"type": "uuid", "required": False},
    },
    "TbPosicao": {
        "dsModelo": {"type": "text", "required": False},
        "dtData": {"type": "text", "required": False},
        "dtHora": {"type": "text", "required": False},
        "dsLat": {"type": "text", "required": False},
        "dsLong": {"type": "text", "required": False},
        "nrTemp": {"type": "double precision", "required": False},
        "nrBat": {"type": "double precision", "required": False},
        "nrSeq": {"type": "integer", "required": False},
        "dsArquivo": {"type": "text", "required": False},
        "cdDispositivo": {"type": "integer", "required": False},
        "dsEndereco": {"type": "text", "required": False},
        "dsNum": {"type": "character varying", "required": False},
        "dsCep": {"type": "character varying", "required": False},
        "dsBairro": {"type": "character varying", "required": False},
        "dsCidade": {"type": "character varying", "required": False},
        "dsUF": {"type": "character varying", "required": False},
        "dsPais": {"type": "character varying", "required": False},
        "blArea": {"type": "boolean", "required": False},
        "nrDistancia": {"type": "real", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
        "cdDestinatario": {"type": "integer", "required": False},
        "cdUser": {"type": "uuid", "required": False},
    },
    "TbSensorRegistro": {
        "cdDispositivo": {"type": "integer", "required": True},
        "cdSensor": {"type": "integer", "required": True},
        "cdPosicao": {"type": "integer", "required": True},
        "cdProdutoItem": {"type": "integer", "required": False},
        "nrValor": {"type": "numeric", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
    "TbTipoSensor": {
        "dsNome": {"type": "text", "required": True},
        "dsDescricao": {"type": "text", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
        "cdUser": {"type": "uuid", "required": True},
        "dsUnidade": {"type": "text", "required": True},
    },
    "TbProduto": {
        "dsNome": {"type": "text", "required": False},
        "dsDescricao": {"type": "text", "required": False},
        "nrCodigo": {"type": "text", "required": False},
        "nrLarg": {"type": "double precision", "required": False},
        "nrComp": {"type": "double precision", "required": False},
        "nrAlt": {"type": "double precision", "required": False},
        "cdStatus": {"type": "text", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
        "cdUser": {"type": "uuid", "required": False},
        "cdCliente": {"type": "integer", "required": False},
    },
    "TbProdutoItem": {
        "dsNome": {"type": "character varying", "required": False},
        "dsDescricao": {"type": "character varying", "required": False},
        "nrCodigo": {"type": "character varying", "required": False},
        "nrLarg": {"type": "double precision", "required": False},
        "nrComp": {"type": "double precision", "required": False},
        "nrAlt": {"type": "double precision", "required": False},
        "nrPesoUnit": {"type": "double precision", "required": False},
        "nrUnidade": {"type": "character varying", "required": False},
        "nrEmpilhamento": {"type": "integer", "required": False},
        "nrLastro": {"type": "integer", "required": False},
        "nrTempMin": {"type": "double precision", "required": False},
        "nrTempMax": {"type": "double precision", "required": False},
        "nrQtdeTotalSensor": {"type": "integer", "required": False},
        "cdStatus": {"type": "text", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
        "cdUser": {"type": "uuid", "required": False},
    },
    "TbEtiqueta": {
        "dsEtiqueta": {"type": "character varying", "required": False},
        "nrFator": {"type": "real", "required": False},
        "nrLargura": {"type": "real", "required": False},
        "nrAltura": {"type": "real", "required": False},
        "nrComprimento": {"type": "real", "required": False},
        "nrPeso": {"type": "real", "required": False},
        "nrCubado": {"type": "real", "required": False},
        "dsUser": {"type": "character varying", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
    "TbSensor": {
        "cdDispositivo": {"type": "integer", "required": True},
        "cdProdutoItem": {"type": "integer", "required": False},
        "cdUnidade": {"type": "string", "required": False},
        "nrUnidadeIni": {"type": "integer", "required": False},
        "nrUnidadeFim": {"type": "integer", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
        "cdTipoSensor": {"type": "bigint", "required": True},
        "cdUser": {"type": "uuid", "required": False},
    },
    "TbTag": {
        "dsDescricao": {"type": "text", "required": False},
        "dsConteudo": {"type": "text", "required": False},
        "dsUser": {"type": "character varying", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
    "TbTicket": {
        "dtOperacao": {"type": "text", "required": False},
        "dsAtendimento": {"type": "text", "required": False},
        "nrAbertos": {"type": "integer", "required": False},
        "nrFechados": {"type": "integer", "required": False},
        "nrPendentes": {"type": "integer", "required": False},
        "dsUser": {"type": "character varying", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
    "TbTicketResumo": {
        "dtOperacao": {"type": "text", "required": False},
        "dsAtendimento": {"type": "text", "required": False},
        "dsNaoAtribuido": {"type": "integer", "required": False},
        "dsSemResolucao": {"type": "integer", "required": False},
        "dsAtualizado": {"type": "integer", "required": False},
        "dsPendente": {"type": "integer", "required": False},
        "dsResolvido": {"type": "integer", "required": False},
        "dsUser": {"type": "character varying", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
    "TbTipo": {
        "dsDescricao": {"type": "text", "required": False},
        "dsUser": {"type": "character varying", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
    "TbUnidade": {
        "dsUnidade": {"type": "text", "required": False},
        "dsSimbolo": {"type": "text", "required": False},
        "dsUser": {"type": "character varying", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
    "TbVisita": {
        "cdCliente": {"type": "integer", "required": True},
        "cdVisitante": {"type": "integer", "required": True},
        "dtData": {"type": "timestamp", "required": False},
        "dsUser": {"type": "character varying", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
    "TbVisitante": {
        "dsNome": {"type": "character varying", "required": True},
        "nrTelefone": {"type": "character varying", "required": False},
        "nrDocumento": {"type": "character varying", "required": True},
        "dsEmail": {"type": "character varying", "required": False},
        "dsUser": {"type": "character varying", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
    "TbUsuario": {
        "dsNome": {"type": "text", "required": False},
        "dsLogin": {"type": "text", "required": False},
        "dsSenha": {"type": "text", "required": False},
        "cdPerfil": {"type": "integer", "required": False},
        "dsUser": {"type": "character varying", "required": False},
        "dtRegistro": {"type": "timestamp", "required": False},
    },
}
