from flask_cors import CORS
from supabase import create_client, Client
import plaid
from plaid.api import plaid_api

cors = CORS()

# Supabase Client Wrapper
class SupabaseClient:
    """A wrapper for the Supabase client to allow initialization within the app factory."""
    def __init__(self):
        self.client: Client = None

    def init_app(self, url: str, key: str):
        if not url or not key:
            raise ValueError("Supabase URL and Key must be set in your environment variables.")
        self.client = create_client(url, key)

    def __getattr__(self, name):
        # Forward any attribute access to the actual Supabase client
        return getattr(self.client, name)

supabase = SupabaseClient()

# Plaid Client Wrapper
class PlaidClient:
    """A wrapper for the Plaid client to allow initialization within the app factory."""
    def __init__(self):
        self.client: plaid_api.PlaidApi = None

    def init_app(self, client_id: str, secret: str, environment: str):
        if not client_id or not secret:
            raise ValueError("Plaid Client ID and Secret must be set in your environment variables.")
        
        host = self._get_host_from_env(environment)
        
        configuration = plaid.Configuration(
            host=host,
            api_key={
                'clientId': client_id,
                'secret': secret,
            }
        )
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def _get_host_from_env(self, environment):
        if environment == 'sandbox':
            return plaid.Environment.Sandbox
        elif environment == 'development':
            return plaid.Environment.Development
        elif environment == 'production':
            return plaid.Environment.Production
        raise ValueError(f"Invalid Plaid environment specified: {environment}")

    def __getattr__(self, name):
        # Forward any attribute access to the actual Plaid client
        return getattr(self.client, name)

plaid_client = PlaidClient()