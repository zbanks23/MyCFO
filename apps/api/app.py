import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid
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

# IMPORTANT: This assumes you are passing the clerk_id from your frontend
# and using it to look up your internal user UUID.

# GET all transactions for a user
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    clerk_id = request.args.get('clerk_id') # Pass clerk_id as a query param
    # 1. Find your internal user ID
    user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute().data
    if not user:
        return jsonify({"error": "User not found"}), 404
    user_db_id = user[0]['id']
    
    # 2. Fetch transactions
    transactions = supabase.table('transactions').select('*').eq('user_id', user_db_id).order('date', desc=True).execute().data
    return jsonify(transactions)

# POST a new transaction
@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    data = request.json
    clerk_id = data.get('clerk_id')
    
    user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute().data
    if not user: return jsonify({"error": "User not found"}), 404
    user_db_id = user[0]['id']

    # Get the ID of the user's manual account
    manual_account_id = get_or_create_manual_account(user_db_id)

    # Insert new transaction
    new_transaction = {
        "id": f"manual_txn_{uuid.uuid4()}", # Generate a unique ID
        "account_id": manual_account_id,
        "user_id": user_db_id,
        "date": data.get('date'),
        "name": data.get('name'),
        "amount": data.get('amount'),
        "category": data.get('category')
    }
    inserted = supabase.table('transactions').insert(new_transaction).execute().data
    return jsonify(inserted[0]), 201

# PUT (update) an existing transaction
@app.route('/api/transactions/<transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    data = request.json
    clerk_id = data.get('clerk_id') # Always verify ownership
    
    user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute().data
    if not user: return jsonify({"error": "User not found"}), 404
    user_db_id = user[0]['id']

    # Update the transaction, ensuring it belongs to the user
    updated = supabase.table('transactions').update({
        "date": data.get('date'),
        "name": data.get('name'),
        "amount": data.get('amount'),
        "category": data.get('category')
    }).match({'id': transaction_id, 'user_id': user_db_id}).execute().data
    
    if not updated:
        return jsonify({"error": "Transaction not found or unauthorized"}), 404
    return jsonify(updated[0])

# DELETE a transaction
@app.route('/api/transactions/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    clerk_id = request.args.get('clerk_id') # Get clerk_id from query params
    
    user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute().data
    if not user: return jsonify({"error": "User not found"}), 404
    user_db_id = user[0]['id']
    
    # Delete the transaction, ensuring it belongs to the user
    deleted = supabase.table('transactions').delete().match({'id': transaction_id, 'user_id': user_db_id}).execute().data

    if not deleted:
        return jsonify({"error": "Transaction not found or unauthorized"}), 404
    return jsonify({"message": "Transaction deleted successfully"}), 200

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

# Helper function
def get_or_create_manual_account(user_db_id):
    """Finds the 'Manual' account for a user, or creates one if it doesn't exist."""
    # Check if a manual account already exists for this user
    # NOTE: Your accounts.id is TEXT, but the item_id is UUID. This is a bit tricky.
    # We will use a placeholder UUID for the item_id for now.
    # A better approach would be to create a 'manual' item in plaid_items table.
    
    # Let's create a manual item first.
    manual_item = supabase.table('plaid_items').select('id').eq('user_id', user_db_id).eq('is_manual', True).execute().data
    if not manual_item:
        # Create a manual Plaid Item entry for this user
        item_insert = supabase.table('plaid_items').insert({
            'user_id': user_db_id,
            'plaid_item_id': f'manual_{user_db_id}',
            'plaid_access_token': 'manual_access_token', # This is a placeholder
            'is_manual': True # Add this boolean column to your plaid_items table!
        }).execute().data[0]
        item_id = item_insert['id']
    else:
        item_id = manual_item[0]['id']

    # Now find or create the manual account linked to this item
    manual_account = supabase.table('accounts').select('id').eq('item_id', item_id).eq('name', 'Manual Transactions').execute().data
    if not manual_account:
        account_id = f'manual_acct_{user_db_id}'
        account_insert = supabase.table('accounts').insert({
            'id': account_id,
            'item_id': item_id,
            'user_id': user_db_id,
            'name': 'Manual Transactions',
            'mask': '0000',
            'type': 'other',
            'subtype': 'manual'
        }).execute().data[0]
        return account_insert['id']
    else:
        return manual_account[0]['id']

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)