from flask import Blueprint, jsonify, request, session
import plaid
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
import traceback

from ..extensions import supabase, plaid_client

def sync_bank_account_info(access_token: str, item_db_id: str = None, user_db_id: str = None):
    """Fetches account details from Plaid and stores them in our DB."""
    try:
        request = AccountsGetRequest(access_token=access_token)
        response = plaid_client.accounts_get(request)
        # response['accounts'] is a list of AccountBase objects
        accounts = response['accounts'] 
        
        if session.get('user_type') == 'guest':
            print("---Guest user account sync - storing in session only.---")
            accounts = [account.to_dict() for account in response['accounts']]

            # Transform data structure for EACH account
            for account in accounts:
                
                # Rename 'account_id' to 'bank_account_id'
                account['bank_account_id'] = account.pop('account_id', None)

                # Pop the nested 'balances' dict and move its values to the top level
                if account.get("balances"):
                    balances = account.pop("balances") # Pop the whole nested dict
                    
                    # Create the new top-level keys
                    account["available_balance"] = balances.get("available", None)
                    account["current_balance"] = balances.get("current", None)
                    account["balance_limit"] = balances.get("limit", None)
                else:
                    # Ensure keys exist even if 'balances' was missing
                    account["available_balance"] = None
                    account["current_balance"] = None
                    account["balance_limit"] = None
            
            session['bank_account_info'] = [acc for acc in accounts]
            print(session['bank_account_info'])
            return

        if not user_db_id or not item_db_id:
            print("Registered user sync requires both user_db_id and item_db_id.")
            return
        # Storing accounts in our database
        accounts_to_upsert = []
        for acc in accounts:
            balances_dict = acc.balances.to_dict()

            accounts_to_upsert.append({
                'bank_account_id': acc.account_id,
                'item_id': item_db_id,
                'user_id': user_db_id,
                'mask': acc.mask,
                'name': acc.name,
                'official_name': acc.official_name,
                
                # Use the balances_dict we created
                'available_balance': balances_dict.get('available'),
                'current_balance': balances_dict.get('current'),
                'balance_limit': balances_dict.get('limit'),
                
                'type': acc.type.value, # .value is correct for enums
                'subtype': acc.subtype.value
            })

        if accounts_to_upsert:
            # Use 'upsert' to update existing accounts and insert new ones
            supabase.table('accounts').upsert(accounts_to_upsert).execute()
            print(f"---Successfully upserted {len(accounts_to_upsert)} accounts.---")

    except plaid.ApiException as e:
        print(f"Error syncing accounts: {e.body}")
    except Exception as e:
        traceback.print_exc()
        print(f"A general error occurred in sync_bank_account_info: {e}")


def sync_transactions(access_token: str, user_db_id: str = None):
        """Fetches transactions for an item and stores them in our DB."""
        try:
            request = TransactionsSyncRequest(access_token=access_token)
            response = plaid_client.transactions_sync(request)
            # response['added'] is a list of Transaction objects
            transactions = response['added']

            # guest user handling
            if session.get('user_type') == 'guest':
                print("---Guest user transaction sync - storing in session only.---")
                session['transactions'] = [t.to_dict() for t in transactions]
                print(session['transactions'])
                return
            
            # registered user handling
            if not user_db_id:
                print("User ID is required to sync transactions for registered users.")
                return
            tx_to_upsert = []
            for t in transactions:
                # t is an object, use dot notation (e.g., t.transaction_id)
                tx_to_upsert.append({
                    'transaction_id': t.transaction_id, # Use .property
                    'account_id': t.account_id, # Use .property
                    'user_id': user_db_id,
                    'date': t.date.isoformat(), # Use .property
                    'name': t.name, # Use .property
                    'amount': t.amount, # Use .property
                    # Safely access the first category
                    'category': t.category[0] if t.category else 'Other',
                    'pending': t.pending, # Use .property
                    'note': ''
                })
                
            if tx_to_upsert:
                # Use 'upsert' to update/insert transactions
                supabase.table('transactions').upsert(tx_to_upsert).execute()
                print(f"---Successfully upserted {len(tx_to_upsert)} transactions.---")

        except plaid.ApiException as e:
            print(f"Error syncing transactions: {e.body}")
        except Exception as e:
            traceback.print_exc()
            print(f"A general error occurred in sync_transactions: {e}")

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
            
        # Guest user handling
        else:
            session['plaid_access_token'] = access_token
            session['plaid_item_id'] = item_id
            print(session)
        
        # Sync accounts and transactions for the new item
        print("Item stored. Syncing bank accounts...")
        sync_bank_account_info(access_token, item_db_id, user_db_id)

        print("Accounts synced. Syncing transactions...")
        sync_transactions(access_token, user_db_id)
        return jsonify({'status': 'success', 'message': 'Account linked and synced successfully'})
        
    except plaid.ApiException as e:
        return jsonify({'error': f"Plaid API Error: {e.body}"}), 500
    except Exception as e:
        # This will catch any other error and return a proper JSON 500 response.
        print(f"An unexpected error occurred: {str(e)}")
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500
    
@plaid_bp.route('/retrieve_bank_account_info', methods=['GET'])
def retrieve_account_info():
    clerk_id = request.args.get('clerk_id')
    print(clerk_id)
    try:
        accounts = []
        # Guest user handling
        if clerk_id == "null" or clerk_id == "undefined":
            if not session.get('plaid_access_token'):
                print("No Plaid access token found in session for guest user.")
                return jsonify([]), 200
            print("---Retrieving account info for guest user from session---")
            if 'bank_account_info' not in session:
                sync_bank_account_info(session['plaid_access_token'], session['plaid_item_id'], None)
            accounts = session['bank_account_info']
            print(f"---Retrieved guest accounts from session---")

        # If it's a registered user, retrieve account info from our DB
        else:
            print("---Retrieving account info for registered user from DB---")
            user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute().data
            if not user:
                return jsonify({"error": "User not found"}), 404
            user_db_id = user[0]['id']
            # This data is already flat because services.py flattens it
            accounts = supabase.table('accounts').select('*').eq('user_id', user_db_id).execute().data
            print(f"---Retrieved registered user accounts from DB---")
        return jsonify(accounts)
        
    except plaid.ApiException as e:
        return jsonify({'error': f"Plaid API Error: {e.body}"}), 500
    except Exception as e:
        traceback.print_exc()
        print(f"An unexpected error occurred in /retrieve_account_info: {str(e)}")
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500

    
@plaid_bp.route('/retrieve_transactions', methods=['GET'])
def retrieve_transactions():
    clerk_id = request.args.get('clerk_id')
    print(clerk_id)

    try:
        transactions = []
        # Guest user handling
        if clerk_id == "null" or clerk_id == "undefined":
            if not session.get('plaid_access_token'):
                print("No Plaid access token found in session for guest user.")
                return jsonify([]), 200
            print("---Retrieving transactions for guest user from session---")
            if 'transactions' not in session:
                sync_transactions(session['plaid_access_token'], None)
            transactions = session['transactions']
            print("---Retrieved transactions for guest user from session---")
        
        # Registered user handling
        else:
            print("---Retrieving transactions for registered user from DB---")
            user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute().data
            if not user:
                return jsonify({"error": "User not found"}), 404
            user_db_id = user[0]['id']
            # Fetch all Plaid items for the user
            transactions = supabase.table('transactions').select('*').eq('user_id', user_db_id).execute().data
            print(f"---Retrieved transactions for registered user from DB---")
        return jsonify(transactions)

    except plaid.ApiException as e:
        return jsonify({'error': f"Plaid API Error: {e.body}"}), 500