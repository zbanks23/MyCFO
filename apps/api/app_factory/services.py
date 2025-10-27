import plaid
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from .extensions import supabase, plaid_client

def sync_bank_account_info(access_token: str, item_db_id: str, user_db_id: str):
        """Fetches account details from Plaid and stores them in our DB."""
        try:
            request = AccountsGetRequest(access_token=access_token)
            response = plaid_client.accounts_get(request)
            # response['accounts'] is a list of AccountBase objects
            accounts = response['accounts'] 

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
                print(f"Successfully upserted {len(accounts_to_upsert)} accounts.")

        except plaid.ApiException as e:
            print(f"Error syncing accounts: {e.body}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"A general error occurred in sync_bank_account_info: {e}")


def sync_transactions(access_token: str, user_db_id: str):
        """Fetches transactions for an item and stores them in our DB."""
        try:
            request = TransactionsSyncRequest(access_token=access_token)
            response = plaid_client.transactions_sync(request)
            # response['added'] is a list of Transaction objects
            added_tx = response['added']
            
            tx_to_upsert = []
            for t in added_tx:
                # t is an object, use dot notation (e.g., t.transaction_id)
                tx_to_upsert.append({
                    'id': t.transaction_id, # Use .property
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
                print(f"Successfully upserted {len(tx_to_upsert)} transactions.")

        except plaid.ApiException as e:
            print(f"Error syncing transactions: {e.body}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"A general error occurred in sync_transactions: {e}")