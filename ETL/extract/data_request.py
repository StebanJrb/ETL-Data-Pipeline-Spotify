import requests
import base64
import yaml
import json
import os
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

cache_path = "./token_cache.json"
saving_path = "./data.json"

def getting_credencials():
    """
    1️ Getting credentials from .env file
    
    """
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    if not CLIENT_ID or not CLIENT_SECRET:
        logger.error("Error: Las variables de entorno SPOTIFY_CLIENT_ID o SPOTIFY_CLIENT_SECRET no están definidas. Asegúrate de que el archivo .env exista y contenga estas variables.")
        exit()
    
    logger.info("Credentials loaded successfully.")
    return CLIENT_ID, CLIENT_SECRET
    
def get_access_token():
    """
    # 2 Getting access token (Client Credentials Flow)
    
    """
    credentialsdata = getting_credencials()
    client_id = credentialsdata[0]
    client_secret = credentialsdata[1]

    redirect_uri = "http://127.0.0.1:8000/callback"
    scope = "user-library-read"

    try:
        sp_oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_path=cache_path,
        )

        # Trying getting token from cache
        token_info = sp_oauth.get_cached_token()

        if not token_info:
            logger.info("No hay token válido en cache. Abriendo navegador para autenticación...")
            auth_url = sp_oauth.get_authorize_url()
            logger.info(f"Por favor autoriza el acceso en esta URL:\n{auth_url}")

            import webbrowser
            webbrowser.open(auth_url)

            response_url = input("\nPaste token access here:\n")
            token_info = sp_oauth.get_access_token(response_url)

        # Renew token if expired
        if sp_oauth.is_token_expired(token_info):
            logger.info("Token expirado, solicitando nuevo...")
            token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])

        # Safe Updated Token
        with open(cache_path, "w", encoding="utf-8") as file:
            json.dump(token_info, file, indent=4)

        logger.info("Token listo y guardado exitosamente.")
        return token_info["access_token"]

    except Exception as e:
        logger.error(f"Error en la autenticación con Spotify: {e}", exc_info=True)
        return None

def token_getter():
    with open(cache_path,'r') as file:
        config = json.load(file)
        auth = config["token_type"]
        token = config["access_token"]
        return auth, token

def get_user_saved_tracks():
    get_access_token()  # Genera o renueva el token
    total_tracks = []
    index = 0

    if not os.path.exists(saving_path):
        while True:
            try:
                auth, token = token_getter()
                url = f"https://api.spotify.com/v1/me/tracks?market=ES&limit=50&offset={index}"
                header = {"Authorization": f"{auth} {token}"}

                response = requests.get(url, headers=header)
                if response.status_code != 200:
                    raise Exception(f"Error getting tracks: {response.status_code} - {response.text}")

                data = response.json()
                items = data.get("items", [])
                total_tracks.extend(items)

                logger.info(f"Fetched {len(items)} tracks (offset {index})")
                index += 50
                time.sleep(0.3)

                if not items:
                    logger.info("No more tracks to fetch.")
                    break

            except Exception as e:
                logger.error(f">> Error {e}")

            # Guardar todo al final
        with open(saving_path, "w", encoding="utf-8") as file:
            json.dump(total_tracks, file, indent=4)
        logger.info(f"Saved total: {len(total_tracks)} tracks")
    else:
        logger.info("Archivo de datos ya existe, no se realizará la extracción.")  
