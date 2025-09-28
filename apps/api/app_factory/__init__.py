import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest

from .extensions import cors, supabase, plaid_client
from .endpoints.core import core_bp
from .endpoints.users import users_bp
from .endpoints.transactions import transactions_bp
from .endpoints.plaid import plaid_bp

def create_app():
    load_dotenv()

    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-key-that-you-should-change')
        
        # Supabase Configuration
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
        
        # Plaid Configuration
        PLAID_CLIENT_ID = os.environ.get("PLAID_CLIENT_ID")
        PLAID_SECRET = os.environ.get("PLAID_SECRET")
        PLAID_ENV = os.environ.get("PLAID_ENV", "sandbox")

    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_blueprints(app)

    return app

def register_extensions(app: Flask):
    cors.init_app(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    supabase.init_app(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])
    
    plaid_client.init_app(
        client_id=app.config['PLAID_CLIENT_ID'],
        secret=app.config['PLAID_SECRET'],
        environment=app.config['PLAID_ENV']
    )

def register_blueprints(app: Flask):
    app.register_blueprint(core_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(transactions_bp, url_prefix='/api')
    app.register_blueprint(plaid_bp, url_prefix='/api')