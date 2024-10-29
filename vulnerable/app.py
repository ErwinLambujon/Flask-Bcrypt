from flask import Flask, request, jsonify
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "hardcoded_secret_key"  # Vulnerable: Hardcoded secret

def get_db():
    return sqlite3.connect('vulnerable.db')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    # Vulnerable: Using MD5
    password_hash = hashlib.md5(password.encode()).hexdigest()
    
    # Vulnerable: SQL Injection
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password_hash}')")
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Registered'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    # Vulnerable: SQL Injection
    password_hash = hashlib.md5(password.encode()).hexdigest()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password_hash}'")
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({'message': 'Login successful', 'token': 'static_token'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/data', methods=['GET'])
def get_data():
    # Vulnerable: No authentication
    return jsonify({'sensitive_data': 'exposed'})

if __name__ == '__main__':
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                   (username TEXT, password TEXT)''')
    conn.close()
    app.run(debug=True)  # Vulnerable: Debug mode in production