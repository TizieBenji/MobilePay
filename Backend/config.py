#mobilepay/Backend/config.py
import os
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