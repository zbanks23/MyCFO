import plaid
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from .extensions import supabase, plaid_client

def sync_bank_account_info(access_token: str, item_db_id: str, user_db_id: str):
        """Fetches account details from Plaid and stores them in our DB."""
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = plaid_client.accounts_get(request)
            accounts = response['accounts']

            accounts_to_insert = []
            for acc in accounts:
                accounts_to_insert.append({
                    'id': acc['account_id'], # Using Plaid's ID as our PK
                    'item_id': item_db_id,
                    'user_id': user_db_id,
                    'mask': acc['mask'],
                    'name': acc['name'],
                    'official_name': acc.get('official_name', ''),
                    'available_balance': acc['balances'].get('available'),
                    'current_balance': acc['balances'].get('current'),
                    'balance_limit': acc['balances'].get('limit'),
                    'type': acc['type'].value, # .value gets the string representation
                    'subtype': acc['subtype'].value
                })

            if accounts_to_insert:
                supabase.table('accounts').insert(accounts_to_insert).execute()
                print(f"Successfully inserted {len(accounts_to_insert)} accounts.")

        except plaid.ApiException as e:
            print(f"Error syncing accounts: {e.body}")

def sync_transactions(access_token: str, user_db_id: str):
        """Fetches transactions for an item and stores them in our DB."""
        try:
            request = TransactionsSyncRequest(access_token=access_token)
            response = plaid_client.transactions_sync(request)
            added_tx = response['added']
            
            tx_to_insert = []
            for t in added_tx:
                tx_to_insert.append({
                    'id': t['transaction_id'], # Using Plaid's ID as our PK
                    'account_id': t['account_id'],
                    'user_id': user_db_id,
                    'date': t['date'].isoformat(),
                    'name': t['name'],
                    'amount': t['amount'],
                    'category': t['category'][0] if t['category'] else 'Other',
                    'pending': t['pending'],
                    'note': ''
                })
                
            if tx_to_insert:
                supabase.table('transactions').insert(tx_to_insert).execute()
                print(f"Successfully inserted {len(tx_to_insert)} transactions.")

        except plaid.ApiException as e:
            print(f"Error syncing transactions: {e.body}")