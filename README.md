# ETL Data Pipeline — Spotify

## Overview
A simple ETL pipeline that extracts data from the Spotify Web API (user's saved tracks), transforms it, and loads it into a JSON file. Built with Python and Spotipy for API interaction.

## Architecture
- **Extract**: Retrieves user's saved tracks from Spotify API using OAuth 2.0 authentication, handles pagination and rate limits.
- **Transform**: Processes and cleans the raw data (placeholder for future transformations).
- **Load**: Saves the processed data to a JSON file (placeholder for future database loading).

## Tech Stack
- Python 3.x
- Spotipy (Spotify API library)
- Requests, Pandas (for data handling)
- Dotenv (for environment variables)

## Key Features
- OAuth 2.0 authentication with token caching
- Error handling and logging
- Modular structure with ETL folders

## Status
🚧 In Development (Basic extract implemented, transform and load are placeholders)

## Project Structure
```
├── .env                          # Environment variables (Spotify credentials)
├── .gitignore                    # Git ignore file
├── data.json                     # Output data file
├── etl_proceso.log               # Log file
├── main.py                       # Main entry point for the ETL process
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── token_cache.json              # Cached OAuth tokens
├── ETL/                          # ETL modules
│   ├── __init__.py
│   ├── extract/
│   │   ├── __init__.py
│   │   └── data_request.py       # Extract module (Spotify API client)
│   ├── load/
│   │   ├── __init__.py
│   │   └── data_load.py          # Load module (placeholder)
│   └── transform/
│       ├── __init__.py
│       └── data_transform.py     # Transform module (placeholder)
└── spotyenv/                     # Virtual environment
```

