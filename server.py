from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import json
import wallet

app = Flask(__name__)
CORS(app)

user_info = wallet.get_user('some_user_id')
print(user_info)

def get_user(user_id):
    with open('database.json', 'r') as f:
        data = json.load(f)
    return data.get(user_id)

@app.route('/get_balance', methods=['POST'])
def get_balance():
    data = request.json
    user_id = str(data.get('user_id'))

    # Fetch the user from your JSON database
    user_info = wallet.get_user(user_id)
    

    if not user_info:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    # Return the user's wallet balance with no-store caching
    response = make_response(jsonify({'status': 'success', 'balance': user_info['wallet_balance']}))
    response.headers['Cache-Control'] = 'no-store'
    return response, 200

@app.route('/verify_purchase', methods=['POST'])
def verify_purchase():
    data = request.json
    user_id = str(data.get('user_id'))
    entered_pin = data.get('pin')
    bundle_price = float(data.get('bundle_price'))

    # Fetch the user from your JSON database
    user_info = wallet.get_user(user_id)

    if not user_info:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    # Verify the PIN
    if user_info['pin'] != entered_pin:
        return jsonify({'status': 'error', 'message': 'Invalid PIN'}), 400

    # Check if the wallet balance is sufficient
    if user_info['wallet_balance'] < bundle_price:
        return jsonify({'status': 'error', 'message': 'Insufficient balance'}), 400

    # Deduct the amount and update the wallet
    new_balance = user_info['wallet_balance'] - bundle_price
    wallet.update_wallet(user_id, -bundle_price, 'debit', 'Data Purchase')

    # Call your VTU API here to process the data purchase
    # For now, we'll assume the purchase is successful

    # Return the success response with the new balance and no-store caching
    response = make_response(jsonify({
        'status': 'success',
        'message': 'Data purchase successful',
        'new_balance': new_balance
    }))
    response.headers['Cache-Control'] = 'no-store'
    return response, 200

# Root route
@app.route('/')
def home():
    return "Welcome to the VTU Data Purchase API!"  # Simple text response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

