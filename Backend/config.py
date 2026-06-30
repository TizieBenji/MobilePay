#mobilepay/Backend/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:

    # A full DATABASE_URL (if provided by the host/platform) takes precedence;
    # otherwise the URI is assembled from the individual DB_* variables.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        f"postgresql://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    # Short-lived access token (the flask-jwt-extended default of 15 min was too
    # short and logged users out mid-session). The client uses the longer-lived
    # refresh token to mint a new access token via POST /auth/refresh.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "1"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "30"))
    )