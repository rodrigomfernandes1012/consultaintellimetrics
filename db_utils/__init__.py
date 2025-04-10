import os

import jwt
from supabase import Client, create_client
from supabase.client import ClientOptions

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase_api: Client = create_client(url, key)


def verify_token(token):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_supabase_client_from_request(request):
    auth_header = request.headers.get("Authorization", None)
    if auth_header is None or not auth_header.startswith("Bearer "):
        return None, "Não autorizado"

    token = auth_header.split("Bearer ")[1]
    user_info = verify_token(token)
    if user_info is None:
        return None, "Token inválido"

    user_id = user_info.get("sub")
    if not user_id:
        return None, "ID do usuário não encontrado no token"

    headers = {"Authorization": f"Bearer {token}"}
    supabase_client: Client = create_client(
        url, key, options=ClientOptions(headers=headers)
    )
    return supabase_client, None
