import requests
import webbrowser
import json
import pandas as pd
import os
import time
from spotipy.oauth2 import SpotifyOAuth
import logging
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("etl_process.log"),
            logging.StreamHandler()
        ]
)

load_dotenv()

#Paths
data_json_path = "./data.json"
cache_path = "./token_cache.json"
saving_path = "./data.json"

def extract():
    #1 Getting Credentials from .env
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not CLIENT_ID or not CLIENT_SECRET:
        return logger.error("Undefined credentials")
    logger.info("Credentials loaded successfully")

    #2 Getting access Token 
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET

    # uri config by API Spotify
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
    
        # Manejo de error específico para tokens revocados
        try:
            token_info = sp_oauth.get_cached_token()
        except Exception as cache_error:
            logger.warning(f"Error al leer caché o token revocado: {cache_error}. Se forzará nueva autenticación.")
            if os.path.exists(cache_path):
                os.remove(cache_path)
            token_info = None
    
        if not token_info:
            logger.info("Not valid Cache, opening webBrowser for autentication")
            auth_url = sp_oauth.get_authorize_url()
            logger.info(f"Authorize in:\n{auth_url}")

            webbrowser.open(auth_url)
    
            response_url = input("\nPaste token access here:\n")
            token_info = sp_oauth.get_access_token(response_url)
    
            # Safe Updated Token
            with open(cache_path, "w", encoding="utf-8") as file:
                json.dump(token_info, file, indent=4)
    
        logger.info("New token taken sucessfully")

    except Exception as e:
        logger.error(f"Auth error Spotify: {e}", exc_info=True)
        return None

    #Tracks info
    total_tracks = []
    index = 0

    if not os.path.exists(saving_path):
        while True:
            try:
                # Request for spotify API
                with open(cache_path,'r') as file:
                        config = json.load(file)
                        auth = config["token_type"]
                        token = config["access_token"]

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

            #Saving everything
        with open(saving_path, "w", encoding="utf-8") as file:
            json.dump(total_tracks, file, indent=4)
        logger.info(f"Saved total: {len(total_tracks)} tracks")
    else:
        logger.info("Tracklist JSON File alredy in path")  

def transform() -> pd.DataFrame:
    def transform_item(item: dict) -> dict | None:
        try:
            track = item["track"]
            album = track["album"]
            return {
                "added_at":           item["added_at"],
                "track_name":         track["name"],
                "duration_ms":        track["duration_ms"],
                "duration_min":       round(track["duration_ms"] / 60000, 2),
                "explicit":           track["explicit"],
                "popularity":         track["popularity"],
                "is_local":           track["is_local"],
                "is_playable":        track.get("is_playable"),
                "track_artists":      ", ".join([a["name"] for a in track["artists"]]),
                "album_name":         album["name"],
                "album_type":         album["album_type"],
                "album_release_date": album["release_date"],
                "album_url":          album["external_urls"]["spotify"],
                "album_image_url":    album["images"][0]["url"] if album.get("images") else None,
            }
        except KeyError as e:
                logger.warning(f"Falta la clave {e} en track: {item.get('track', {}).get('name', 'unknown')}")
                return None
    
        
    def json_to_df() -> pd.DataFrame:
        try:
            with open(data_json_path, "r", encoding="utf-8") as file:
                items = json.load(file)

            rows = [transform_item(item) for item in items]
            rows = [r for r in rows if r is not None]

            df = pd.DataFrame(rows)
            logger.info(f"DataFrame Created with {len(df)} raws and {len(df.columns)} columns")
            return df

        except Exception as e:
            logger.error(f"Corrupted Data: {e}", exc_info=True)
            return pd.DataFrame()
    # Working with DataFrame
    df_spotify = json_to_df()
    df_spotify["added_at"] = pd.to_datetime(df_spotify["added_at"], format='ISO8601')
    df_spotify["album_release_date"] = pd.to_datetime(df_spotify["album_release_date"], format='ISO8601')
    return df_spotify

def load(df_spotify: pd.DataFrame):
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    try:
        engine = create_engine(url)
        df_spotify.to_sql(name= "music",
                          con= engine,
                          index= False,
                          if_exists= "fail")
        logger.info("Data loaded to database.")
        return engine
    except SQLAlchemyError as e:
        logger.error(f"Connection error to MySQL: {e}")
        raise

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Correct Start of Log")

    try:
        logger.info("Starting ETL")
        extract()
        logger.info("Extract step done")
        df = transform()
        logger.info("Transform step done")
        load(df)
        logger.info("Load step done")
        logger.info("ETL Process done succesfully.")
    except Exception as e:
        logger.error(f"In ETL Process: {e}", exc_info=True)