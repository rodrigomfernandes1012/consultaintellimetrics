from constantes import campos_tabelas


def valida_campo(field, value, field_type, required):
    """
    Valida o valor de um campo com base no tipo e se é obrigatório.

    Parâmetros:
    - field (str): Nome do campo.
    - value (any): Valor do campo.
    - field_type (str): Tipo do campo.
    - required (bool): Se o campo é obrigatório.

    Retorna:
    - bool: True se o campo for válido, False caso contrário.
    - str: Mensagem de erro, se houver.
    """
    # Handle empty strings for text and timestamp fields
    if field_type in ("text", "character varying", "timestamp"):
        if value == "":
            if required:
                return False, f"Campo {field} é necessário."
            # se o campo é vazio e não necessário, retornar True
            return True, None

    # Validate the type
    if (field_type == "integer" or field_type == "bigint") and not isinstance(
        value, int
    ):
        return False, f"Campo {field} deve ser do tipo inteiro."
    elif field_type in ("text", "character varying", "uuid") and not isinstance(
        value, str
    ):
        return False, f"Campo {field} deve ser do tipo texto."
    elif field_type == "boolean" and not isinstance(value, bool):
        return False, f"Campo {field} deve ser do tipo boolean."
    elif field_type in ("double precision", "real") and (
        not isinstance(value, float) and not isinstance(value, int)
    ):
        return False, f"Campo {field} deve ser do tipo número com precisão dupla."
    elif field_type in ("timestamp", "timestamp with time zone") and not isinstance(
        value, str
    ):
        return False, f"Campo {field} deve ser do tipo timestamp."

    return True, None


def valida_e_constroi_insert(table, payload):
    """
    Valida e constrói o dicionário de dados para inserção em uma tabela com base no payload fornecido.

    Parâmetros:
    - table (str): Nome da tabela onde os dados serão inseridos.
    - payload (dict): Dicionário contendo os dados para inserção.

    Retorna:
    - dict: Dicionário com os dados validados e prontos para inserção.
    - str: Mensagem de erro, se houver.
    """
    if table not in campos_tabelas:
        return None, f"Tabela {table} não é suportada."

    fields = campos_tabelas[table]
    data = {}

    for field, attributes in fields.items():
        required = attributes["required"]
        field_type = attributes["type"]

        if required and field not in payload:
            return None, f"Campo {field} é necessário."

        if field in payload:
            value = payload[field]

            # Validate the field
            is_valid, error_message = valida_campo(field, value, field_type, required)
            if not is_valid:
                return None, error_message

            data[field] = value

    return data, None


def valida_e_constroi_update(table, payload):
    """
    Valida e constrói o dicionário de dados para atualização em uma tabela com base no payload fornecido.

    Parâmetros:
    - table (str): Nome da tabela onde os dados serão atualizados.
    - payload (dict): Dicionário contendo os dados para atualização.

    Retorna:
    - dict: Dicionário com os dados validados e prontos para atualização.
    - str: Mensagem de erro, se houver.
    """
    if table not in campos_tabelas:
        return None, f"Tabela {table} não é suportada."

    fields = campos_tabelas[table]
    data = {}

    for field, attributes in fields.items():
        required = attributes["required"]
        field_type = attributes["type"]

        if field in payload:
            value = payload[field]

            # Validate the field
            is_valid, error_message = valida_campo(field, value, field_type, required)
            if not is_valid:
                return None, error_message

            data[field] = value

    if not data:
        return None, "Nenhum campo válido para atualizar."

    return data, None
