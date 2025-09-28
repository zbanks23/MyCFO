import plaid
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from .extensions import supabase, plaid_client

def get_or_create_manual_account(user_db_id):
        """Finds the 'Manual' account for a user, or creates one if it doesn't exist."""
        
        # Create a manual item
        manual_item = supabase.table('plaid_items').select('id').eq('user_id', user_db_id).eq('is_manual', True).execute().data
        if not manual_item:
            # Create a manual Plaid Item entry for this user
            item_insert = supabase.table('plaid_items').insert({
                'user_id': user_db_id,
                'plaid_item_id': f'manual_{user_db_id}',
                'plaid_access_token': 'manual_access_token',
                'is_manual': True
            }).execute().data[0]
            item_id = item_insert['id']
        else:
            item_id = manual_item[0]['id']

        # Find or create the manual account linked to this item
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

def sync_accounts(access_token: str, item_db_id: str, user_db_id: str):
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
                    'name': acc['name'],
                    'mask': acc['mask'],
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
                    'pending': t['pending']
                })
                
            if tx_to_insert:
                supabase.table('transactions').insert(tx_to_insert).execute()
                print(f"Successfully inserted {len(tx_to_insert)} transactions.")

        except plaid.ApiException as e:
            print(f"Error syncing transactions: {e.body}")