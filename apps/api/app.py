import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route('/api/status')
def status():
    return jsonify({"status": "healthy", "message": "API is running!"}), 200

@app.route("/api/test_db")
def test_db_connection():
    try:
        # This is the line that actually uses the connection.
        # We are asking Supabase to select all records from the 'users' table, but limit it to 5 just to be safe.
        response = supabase.table('users').select("*").limit(5).execute()
        
        return jsonify({
            "message": "Successfully connected to Supabase and queried the users table.",
            "data": response.data # shows a list of users.
        })
    except Exception as e:
        return jsonify({
            "message": "Failed to connect to or query the database.",
            "error": str(e)
        }), 500

@app.route("/api/sync_user", methods=['POST'])
def sync_user():
    try:
        clerk_user = request.get_json()
        if not clerk_user or 'id' not in clerk_user:
            return jsonify({"error": "Clerk user data is required"}), 400
        
        clerk_id = clerk_user['id']

        existing_user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute()

        if not existing_user.data:
            user_to_insert = {
                'clerk_id': clerk_id,
                'email': clerk_user.get('emailAddresses', [{}])[0].get('emailAddress'),
                'first_name': clerk_user.get('firstName'),
                'last_name': clerk_user.get('lastName')
            }

            insert_response = supabase.table('users').insert(user_to_insert).execute()

            if insert_response.data:
                return jsonify({"message": "User created successfully", "user": insert_response.data[0]}), 201
            else:
                return jsonify({"error": "Failed to create user"}), 500
        else:
            return jsonify({"message": "User already exists", "user": existing_user.data[0]}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

plaid_client_id = os.environ.get("PLAID_CLIENT_ID")
plaid_secret = os.environ.get("PLAID_SECRET")

plaid_config = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': plaid_client_id,
        'secret': plaid_secret
    }
)
plaid_client = plaid_api.PlaidApi(plaid.ApiClient(plaid_config))

@app.route('/api/plaid/create_link_token', methods=['POST'])
def create_link_token():
    try:
        clerk_id = request.json.get('clerk_id')
        if not clerk_id:
            return jsonify({'error': 'Clerk ID is required'}), 400
        
        user_query = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute()
        if not user_query.data:
            return jsonify({'error': 'User not found'}), 404
        internal_user_id = user_query.data[0]['id']

        plaid_request = LinkTokenCreateRequest(
            client_id = plaid_client_id,
            secret = plaid_secret,
            user=LinkTokenCreateRequestUser(client_user_id=str(internal_user_id)),
            client_name="My Finance Tracker",
            products=[Products('transactions')], # We want transaction data
            country_codes=[CountryCode('US')],
            language='en'
        )
        response = plaid_client.link_token_create(plaid_request)
        return jsonify(response.to_dict())

    except plaid.ApiException as e:
        return jsonify({'error': f"Plaid API Error: {e.body}"}), 500
    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)