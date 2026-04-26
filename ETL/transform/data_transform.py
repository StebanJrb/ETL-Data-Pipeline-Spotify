import pandas as pd
import json
import logging

logger = logging.getLogger(__name__)

data_json_path = "./data.json"

def json_to_df() -> pd.DataFrame:
    try:
        with open(data_json_path, "r", encoding="utf-8") as file:
            items = json.load(file)

        rows = [_transform_item(item) for item in items]
        rows = [r for r in rows if r is not None]

        df = pd.DataFrame(rows)
        logger.info(f"DataFrame creado con {len(df)} filas y {len(df.columns)} columnas.")
        return df

    except Exception as e:
        logger.error(f"Error al transformar los datos: {e}", exc_info=True)
        return pd.DataFrame()


def _transform_item(item: dict) -> dict | None:
    try:
        track = item["track"]
        album = track["album"]
        return {
            "added_at":           item["added_at"],
            "track_id":           track["id"],
            "track_name":         track["name"],
            "track_number":       track["track_number"],
            "disc_number":        track["disc_number"],
            "duration_ms":        track["duration_ms"],
            "duration_min":       round(track["duration_ms"] / 60000, 2),
            "explicit":           track["explicit"],
            "popularity":         track["popularity"],
            "is_local":           track["is_local"],
            "is_playable":        track.get("is_playable"),
            "track_uri":          track["uri"],
            "track_url":          track["external_urls"]["spotify"],
            "isrc":               track.get("external_ids", {}).get("isrc"),
            "track_artists":      ", ".join([a["name"] for a in track["artists"]]),
            "track_artist_ids":   ", ".join([a["id"] for a in track["artists"]]),
            "album_id":           album["id"],
            "album_name":         album["name"],
            "album_type":         album["album_type"],
            "album_release_date": album["release_date"],
            "album_total_tracks": album["total_tracks"],
            "album_uri":          album["uri"],
            "album_url":          album["external_urls"]["spotify"],
            "album_artists":      ", ".join([a["name"] for a in album["artists"]]),
            "album_image_url":    album["images"][0]["url"] if album.get("images") else None,
        }
    except KeyError as e:
        logger.warning(f"Falta la clave {e} en track: {item.get('track', {}).get('name', 'unknown')}")
        return None
