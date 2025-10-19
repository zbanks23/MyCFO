from flask import Blueprint, jsonify, request, session
import plaid
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

from ..extensions import supabase, plaid_client
from ..services import sync_bank_accounts, sync_transactions

plaid_bp = Blueprint('plaid', __name__)

@plaid_bp.route('/create_link_token', methods=['POST'])
def create_link_token():
    try:
        clerk_id = request.json.get('clerk_id')
        internal_user_id = None
        
        # Registered user handling
        if clerk_id:
            user_query = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute()
            if not user_query.data:
                return jsonify({'error': 'User not found'}), 404
            internal_user_id = user_query.data[0]['id']
        # Guest user handling
        else:
            internal_user_id = session.get('user_id')

        plaid_request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=str(internal_user_id)),
            client_name="MyCFO",
            products=[Products('transactions')], # Requesting Plaid products, add more as needed
            country_codes=[CountryCode('US')],
            language='en'
        )
        response = plaid_client.client.link_token_create(plaid_request)
        return jsonify(response.to_dict())

    except plaid.ApiException as e:
        return jsonify({'error': f"Plaid API Error: {e.body}"}), 500
    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500

@plaid_bp.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    data = request.json
    public_token = data.get('public_token')
    clerk_id = data.get('clerk_id')

    if not public_token:
        return jsonify({'error': 'Public token is required'}), 400
    
    try:
        # Exchange public_token for access_token and item_id
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = plaid_client.client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        # Registered user handling
        if clerk_id:
            user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute().data
            if not user:
                return jsonify({"error": "User not found"}), 404
            user_db_id = user[0]['id']

            # Store the new Plaid Item in our database
            # TODO: Encrypt the access_token before storing it using Supabase Vault!
            item_data = {
                'user_id': user_db_id,
                'plaid_item_id': item_id,
                'plaid_access_token': access_token 
            }
            inserted_item = supabase.table('plaid_items').insert(item_data).execute().data[0]
            item_db_id = inserted_item['id'] # Our internal UUID for the item
            
            # Sync accounts and transactions for the new item
            print("Item stored. Syncing bank accounts...")
            sync_bank_accounts(access_token, item_db_id, user_db_id)

            print("Accounts synced. Syncing transactions...")
            sync_transactions(access_token, user_db_id)

            return jsonify({'status': 'success', 'message': 'Account linked and synced successfully'})
        # Guest user handling
        else:
            session['plaid_access_token'] = access_token
            session['plaid_item_id'] = item_id
            print(session)
            return jsonify({'status': 'success', 'message': 'Account linked for current guest session'})
        
    except plaid.ApiException as e:
        return jsonify({'error': f"Plaid API Error: {e.body}"}), 500
