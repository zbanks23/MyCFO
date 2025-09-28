import uuid
from flask import Blueprint, request, jsonify
from ..services import get_or_create_manual_account
from ..extensions import supabase

transactions_bp = Blueprint('transactions', __name__)
@transactions_bp.route('/transactions', methods=['GET'])
def get_transactions():
        clerk_id = request.args.get('clerk_id') # Pass clerk_id as a query param
        # Find internal user ID
        user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute().data
        if not user:
            return jsonify({"error": "User not found"}), 404
        user_db_id = user[0]['id']
        
        # Fetch transactions
        transactions = supabase.table('transactions').select('*').eq('user_id', user_db_id).order('date', desc=True).execute().data
        return jsonify(transactions)

    # POST a new transaction
@transactions_bp.route('/transactions', methods=['POST'])
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

    # Update an existing transaction
@transactions_bp.route('/transactions/<transaction_id>', methods=['PUT'])
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
@transactions_bp.route('/transactions/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
        clerk_id = request.args.get('clerk_id') # Get clerk_id from query params
        
        user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute().data
        if not user: return jsonify({"error": "User not found"}), 404
        user_db_id = user[0]['id']
        
        deleted = supabase.table('transactions').delete().match({'id': transaction_id, 'user_id': user_db_id}).execute().data

        if not deleted:
            return jsonify({"error": "Transaction not found or unauthorized"}), 404
        return jsonify({"message": "Transaction deleted successfully"}), 200