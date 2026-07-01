import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config import Config
from database.db import db
from extensions import limiter

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.kyc_routes import kyc_bp
from routes.wallet_routes import wallet_bp
from routes.transaction_routes import transaction_bp
from routes.mtn_routes import mtn_bp
from routes.orange_routes import orange_bp
from routes.transfer_routes import transfer_bp
from routes.pawapay_routes import pawapay_bp

from models.token_blocklist import TokenBlocklist


# Initialize extensions
jwt = JWTManager()
migrate = Migrate()

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {"success": False, "message": "Invalid token"}, 422

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {"success": False, "message": "Authorization token required"}, 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {"success": False, "message": "Token has been revoked"}, 401

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return TokenBlocklist.query.filter_by(jti=jti).first() is not None


app = Flask(__name__)
app.config.from_object(Config)

# CORS: the frontend (Expo web in a browser, or Expo Go on a phone) calls this
# API from a different origin. Auth is via the Authorization header (not cookies),
# so a permissive dev policy on /api/* is safe here. Tighten ALLOWED_ORIGINS for
# production. Set CORS_ORIGINS in .env (comma-separated) to override.
_cors_origins = os.getenv("CORS_ORIGINS", "*")
_origins = "*" if _cors_origins.strip() == "*" else [o.strip() for o in _cors_origins.split(",") if o.strip()]
CORS(app, resources={r"/api/*": {"origins": _origins}})

# Ensure upload directory exists
os.makedirs("uploads/kyc", exist_ok=True)

# Initialize DB + JWT + migrations
db.init_app(app)
jwt.init_app(app)
# render_as_batch keeps ALTERs working on SQLite (dev); compare_type lets
# autogenerate notice column type changes (e.g. Float -> Numeric).
migrate.init_app(app, db, render_as_batch=True, compare_type=True)
limiter.init_app(app)

@app.route("/")
def home():
    return {"message": "MobilePay Backend Running"}


#Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(kyc_bp, url_prefix="/api/kyc")
app.register_blueprint(wallet_bp, url_prefix="/api/wallet")
app.register_blueprint(transaction_bp, url_prefix="/api/transactions")
app.register_blueprint(orange_bp, url_prefix="/api/orange")
app.register_blueprint(transfer_bp, url_prefix="/api/transfer")
app.register_blueprint(mtn_bp, url_prefix="/api/mtn")
app.register_blueprint(pawapay_bp, url_prefix="/api/pawapay")


# Schema is now managed by Flask-Migrate / Alembic.
# Create or upgrade the database with:  flask db upgrade


if __name__ == "__main__":
    # debug=True must never be hardcoded — read from env var.
    # Set FLASK_DEBUG=true in .env for local development only.
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)