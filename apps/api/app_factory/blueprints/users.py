from flask import Blueprint, jsonify, request, session
from ..extensions import supabase
import uuid

users_bp = Blueprint("user", __name__)

@users_bp.route('/sync_user', methods=['POST'])
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

            existing_user = supabase.table('users').select('id').eq('clerk_id', clerk_id).execute() 
            session['user_id'] = existing_user.data[0]['id'] # Set session for the new user

            if insert_response.data:
                return jsonify({"message": "User created successfully", "user": insert_response.data[0]}), 201
            else:
                return jsonify({"error": "Failed to create user"}), 500
        else:
            session['user_id'] = existing_user.data[0]['id'] # Set session for existing user
            return jsonify({"message": "User already exists", "user": existing_user.data[0]}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route('/continue_as_guest', methods=['POST'])
def continue_as_guest():
    try:
        session['user_id'] = str(uuid.uuid4()) # Set session for guest user
        if "user_id" not in session:
            return jsonify({"error": "Guest user creation failed"}), 400
        else:
            return jsonify({"message": "Guest user session created"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
