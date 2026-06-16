import logging
from ETL.extract.data_request import get_user_saved_tracks
from ETL.transform.data_transform import json_to_df

def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("etl_proceso.log"),
            logging.StreamHandler() # Para ver los logs en consola también
        ]
    )

if __name__ == "__main__":
    configurar_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("Logger configurado correctamente")

    try:
        logger.info("Iniciando proceso ETL...")
        get_user_saved_tracks()
        df = json_to_df()
        print(df.columns.tolist())
        print(df.head())
        df.to_csv("spotify_saved_tracks.csv", index=False)
        logger.info("Proceso ETL finalizado exitosamente.")
    except Exception as e:
        logger.error(f"Error en el proceso ETL: {e}", exc_info=True)