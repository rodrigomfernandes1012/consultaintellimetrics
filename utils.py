from constantes import campos_tabelas


def valida_e_constroi_insert(table, payload):
    """
    Valida e constrói o dicionário de dados para inserção em uma tabela com base no payload fornecido.

    Parâmetros:
    - table (str): Nome da tabela onde os dados serão inseridos.
    - payload (dict): Dicionário contendo os dados para inserção.

    Retorna:
    - dict: Dicionário com os dados validados e prontos para inserção.
    - str: Mensagem de erro, se houver.

    Se a tabela não estiver na lista de tabelas suportadas (`campos_tabelas`), retorna um erro indicando 
    que a tabela não é suportada.

    Para cada campo na tabela:
    - Verifica se o campo é obrigatório e se está presente no payload. Se um campo obrigatório não estiver 
    presente, retorna um erro indicando que o campo é necessário.
    - Se o campo estiver presente, valida o tipo de valor fornecido com base na definição do campo:
      - `text`, `character varying`, e `timestamp`: Se o valor for uma string vazia e o campo não for obrigatório,
      o campo é ignorado.
      - `integer`, `bigint`: O valor deve ser um número inteiro.
      - `text`, `character varying`: O valor deve ser uma string.
      - `boolean`: O valor deve ser um booleano.
      - `double precision`, `real`: O valor deve ser um número com precisão dupla.
      - `timestamp`: O valor deve ser uma string representando uma data e hora.

    Se todas as validações forem passadas, retorna o dicionário de dados com os campos validados. 
    Caso contrário, retorna uma mensagem de erro apropriada.
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

            # Handle empty strings for text and timestamp fields
            if field_type in ("text", "character varying", "timestamp"):
                if value == "":
                    if required:
                        return None, f"Campo {field} é necessário."

                    # se o campo eh vazio e nao necessario, nao inclua-o no dict
                    continue

            # Validate the type
            if (field_type == "integer" or field_type == "bigint") and not isinstance(
                value, int
            ):
                return None, f"Campo {field} deve ser do tipo inteiro."
            elif field_type == "text" and not isinstance(value, str):
                return None, f"Campo {field} deve ser do tipo texto."
            elif field_type == "character varying" and not isinstance(value, str):
                return None, f"Campo {field} deve ser do tipo texto."
            elif field_type == "boolean" and not isinstance(value, bool):
                return None, f"Campo {field} deve ser do tipo boolean."
            elif (
                field_type == "double precision" or field_type == "real"
            ) and not isinstance(value, float):
                return (
                    None,
                    f"Campo {field} deve ser do tipo número com precisão dupla.",
                )
            elif field_type == "timestamp" and not isinstance(value, str):
                return None, f"Campo {field} deve ser do tipo timestamp."

            data[field] = value

    return data, None
