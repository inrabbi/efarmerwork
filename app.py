from flask import Flask, render_template, request, jsonify, session
import json
import base64
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# In-memory storage for demo purposes (use a database in production)
farmers_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture_location', methods=['POST'])
def capture_location():
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude and longitude:
            # Store location in session
            session['location'] = {
                'latitude': latitude,
                'longitude': longitude,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify({
                'status': 'success',
                'message': 'Location captured successfully',
                'data': session['location']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid location data'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/save_photo', methods=['POST'])
def save_photo():
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if image_data:
            # Store image in session (in production, save to file system or database)
            session['photo'] = image_data
            
            return jsonify({
                'status': 'success',
                'message': 'Photo saved successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No image data received'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/start_webauthn_registration', methods=['POST'])
def start_webauthn_registration():
    # This would normally generate registration options for the client
    # For this demo, we'll return a simulated response
    try:
        # In a real implementation, you would:
        # 1. Generate a challenge
        # 2. Store the challenge in the session
        # 3. Return registration options to the client
        
        challenge = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
        session['webauthn_challenge'] = challenge
        
        registration_options = {
            'challenge': challenge,
            'rp': {
                'name': 'eFarmerID System'
            },
            'user': {
                'id': base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8').rstrip('='),
                'name': session.get('email', 'farmer@example.com'),
                'displayName': f"{session.get('first_name', 'Farmer')} {session.get('last_name', 'User')}"
            },
            'pubKeyCredParams': [
                {'type': 'public-key', 'alg': -7},  # ES256
                {'type': 'public-key', 'alg': -257}  # RS256
            ],
            'timeout': 60000,
            'attestation': 'direct'
        }
        
        return jsonify({
            'status': 'success',
            'options': registration_options
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/verify_webauthn_registration', methods=['POST'])
def verify_webauthn_registration():
    # This would verify the WebAuthn registration response
    # For this demo, we'll simulate a successful verification
    try:
        data = request.get_json()
        
        # In a real implementation, you would:
        # 1. Verify the challenge matches the one stored in session
        # 2. Verify the attestation signature
        # 3. Store the credential ID and public key for future authentication
        
        session['biometric_verified'] = True
        session['credential_id'] = data.get('credentialId', 'simulated-credential-id')
        
        return jsonify({
            'status': 'success',
            'message': 'Biometric registration successful'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/submit_registration', methods=['POST'])
def submit_registration():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'idNumber', 'phone', 'county']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Check if biometrics are verified
        if not session.get('biometric_verified', False):
            return jsonify({
                'status': 'error',
                'message': 'Biometric verification required'
            }), 400
        
        # Create farmer record
        farmer_id = f"F-{datetime.now().strftime('%Y%m%d')}-{len(farmers_data) + 1:04d}"
        
        farmer_data = {
            'id': farmer_id,
            'firstName': data['firstName'],
            'lastName': data['lastName'],
            'idNumber': data['idNumber'],
            'phone': data['phone'],
            'county': data['county'],
            'village': data.get('village', ''),
            'farmSize': data.get('farmSize', ''),
            'primaryCrop': data.get('primaryCrop', ''),
            'registrationDate': datetime.now().isoformat(),
            'location': session.get('location', {}),
            'photo': session.get('photo', ''),
            'biometricVerified': session.get('biometric_verified', False)
        }
        
        # Store farmer data (in production, save to database)
        farmers_data[farmer_id] = farmer_data
        
        # Clear session data
        for key in ['location', 'photo', 'biometric_verified', 'credential_id', 'webauthn_challenge']:
            if key in session:
                del session[key]
        
        return jsonify({
            'status': 'success',
            'message': 'Farmer registered successfully',
            'farmerId': farmer_id,
            'data': farmer_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)