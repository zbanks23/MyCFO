import os
from flask import Flask
from dotenv import load_dotenv
import uuid
import redis

from .extensions import cors, supabase, plaid_client, session
from .blueprints.core import core_bp
from .blueprints.users import users_bp
from .blueprints.transactions import transactions_bp
from .blueprints.plaid import plaid_bp

def create_app():
    load_dotenv()

    class Config: 
        # Supabase Configuration
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        
        # Plaid Configuration
        PLAID_SANDBOX_CLIENT_ID = os.environ.get("PLAID_SANDBOX_CLIENT_ID")
        PLAID_SANDBOX_SECRET = os.environ.get("PLAID_SANDBOX_SECRET")
        PLAID_ENV = os.environ.get("PLAID_ENV", "sandbox")

        # Session Configuration
        SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", str(uuid.uuid4()))
        SESSION_TYPE = "redis"
        SESSION_PERMANENT = False
        SESSION_USE_SIGNER = True
        SESSION_REDIS = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))

    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_blueprints(app)

    return app

def register_extensions(app: Flask):
    origin = os.environ.get("FRONT_END_URL", "http://localhost:3000")
    cors.init_app(app, supports_credentials=True, resources={r"/api/.*": {"origins": origin}})

    supabase.init_app(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

    plaid_client.init_app(
        client_id=app.config['PLAID_SANDBOX_CLIENT_ID'],
        secret=app.config['PLAID_SANDBOX_SECRET'],
        environment=app.config['PLAID_ENV']
    )

    session.init_app(app)

def register_blueprints(app: Flask):
    app.register_blueprint(core_bp, url_prefix='/api/core')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(plaid_bp, url_prefix='/api/plaid')