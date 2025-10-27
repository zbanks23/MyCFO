import uuid
from flask import Blueprint, request, jsonify
from ..extensions import supabase

transactions_bp = Blueprint('transactions', __name__)
@transactions_bp.route('/', methods=['GET'])
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

@transactions_bp.route('/note/<transaction_id>', methods=['PUT'])
def update_transaction_note(transaction_id):
        data = request.json
        clerk_id = data.get('clerk_id') # Always verify ownership
        note = data.get('note', '') # Get the note, default to empty string if not provided
        
        user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute().data
        if not user: return jsonify({"error": "User not found"}), 404
        user_db_id = user[0]['id']

        # Update only the note field of the transaction, ensuring it belongs to the user
        updated = supabase.table('transactions').update({
            "note": note
        }).match({'id': transaction_id, 'user_id': user_db_id}).execute().data
        
        if not updated:
            return jsonify({"error": "Transaction not found or unauthorized"}), 404
        return jsonify(updated[0])