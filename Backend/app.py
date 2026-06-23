import os

from flask import Flask

from flask_jwt_extended import JWTManager

from config import Config
from database.db import db

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.kyc_routes import kyc_bp
from routes.wallet_routes import wallet_bp
from routes.transaction_routes import transaction_bp
from routes.mtn_routes import mtn_bp
from routes.orange_routes import orange_bp
from routes.transfer_routes import transfer_bp

from routes.mtn_routes import (
    mtn_bp
)










# Initialize extensions
jwt = JWTManager()


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {
        "success": False,
        "message": "Invalid token"
    }, 422


@jwt.unauthorized_loader
def missing_token_callback(error):
    return {
        "success": False,
        "message": "Authorization token required"
    }, 401


app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs("uploads/kyc", exist_ok=True)

# Initialize DB + JWT
db.init_app(app)
jwt.init_app(app)


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

app.register_blueprint(
    mtn_bp, 
    url_prefix="/api/mtn")

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)