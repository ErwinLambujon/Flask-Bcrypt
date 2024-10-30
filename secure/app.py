from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from functools import wraps
import sqlite3
import re
import jwt
from datetime import datetime, timedelta
from config import Config
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)
CORS(app)

# Secure database connection
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def validate_username(username):
    pattern = r'^[a-zA-Z0-9_]{4,30}$'
    return bool(re.match(pattern, username))

def validate_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
    return bool(re.match(pattern, password))

# JWT token verification
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except:
            return jsonify({'error': 'Token is invalid'}), 401
            
        return f(*args, **kwargs)
    return decorated

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
        
    username = data['username']
    password = data['password']
    
    if not validate_username(username):
        return jsonify({'error': 'Invalid username format'}), 400
    if not validate_password(password):
        return jsonify({'error': 'Invalid password format'}), 400
        
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                      (username, hashed_password))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'User registered successfully'}), 201
        
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (data['username'],))
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.check_password_hash(user['password'], data['password']):
        return jsonify("Successful Login"), 200
        
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': 'Access granted to protected data'})

if __name__ == '__main__':
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                   (username TEXT PRIMARY KEY, password TEXT)''')
    conn.close()
    app.run(debug=app.config['DEBUG'])