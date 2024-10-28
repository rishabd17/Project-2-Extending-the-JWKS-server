from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import jwt  # PyJWT

app = Flask(__name__)

# Function to get private keys from the database
def get_private_key(expired=False):
    conn = sqlite3.connect('totally_not_my_privateKeys.db')
    cursor = conn.cursor()
    current_time = int(datetime.now().timestamp())

    if expired:
        cursor.execute("SELECT key FROM keys WHERE exp < ?", (current_time,))
    else:
        cursor.execute("SELECT key FROM keys WHERE exp > ?", (current_time,))

    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

# POST /auth endpoint
@app.route('/auth', methods=['POST'])
def auth():
    expired = request.args.get('expired', default=False, type=bool)
    private_key_pem = get_private_key(expired)

    if private_key_pem:
        # Sign JWT using the private key
        token = jwt.encode({"user": "userABC"}, private_key_pem, algorithm="RS256")
        return jsonify({"jwt": token})
    else:
        return jsonify({"error": "No valid key found"}), 404

# GET /.well-known/jwks.json endpoint
@app.route('/.well-known/jwks.json', methods=['GET'])
def jwks():
    conn = sqlite3.connect('totally_not_my_privateKeys.db')
    cursor = conn.cursor()
    current_time = int(datetime.now().timestamp())

    cursor.execute("SELECT key FROM keys WHERE exp > ?", (current_time,))
    rows = cursor.fetchall()
    conn.close()

    jwks_response = {
        "keys": [
            {"kty": "RSA", "use": "sig", "kid": i + 1, "n": "modulus", "e": "AQAB"}
            for i, row in enumerate(rows)
        ]
    }
    return jsonify(jwks_response)

if __name__ == '__main__':
    app.run(debug=True)
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('totally_not_my_privateKeys.db')

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# Create the 'keys' table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS keys (
        kid INTEGER PRIMARY KEY AUTOINCREMENT,
        key BLOB NOT NULL,
        exp INTEGER NOT NULL
    )
''')

# Insert a new private key (example data)
cursor.execute('INSERT INTO keys (key, exp) VALUES (?, ?)', ('example_private_key', 1728631021))

# Commit the changes
conn.commit()

# Fetch and print all rows in the 'keys' table
cursor.execute('SELECT * FROM keys')
rows = cursor.fetchall()

for row in rows:
    print(row)

# Close the connection
conn.close()
import sqlite3
import jwt  # PyJWT library for JWT signing
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Function to fetch a private key from SQLite based on whether it's expired or not
def get_private_key(expired=False):
    conn = sqlite3.connect('totally_not_my_privateKeys.db')
    cursor = conn.cursor()

    current_time = int(datetime.now().timestamp())

    if expired:
        cursor.execute("SELECT key FROM keys WHERE exp < ?", (current_time,))
    else:
        cursor.execute("SELECT key FROM keys WHERE exp > ?", (current_time,))

    key_row = cursor.fetchone()
    conn.close()

    if key_row:
        return key_row[0]  # Return the private key (stored as a string or blob)
    return None

# POST /auth endpoint
@app.route('/auth', methods=['POST'])
def auth():
    # Check if the 'expired' query parameter is present (to fetch an expired key)
    expired = request.args.get('expired', default=False, type=bool)

    # Fetch the private key from the SQLite database
    private_key_pem = get_private_key(expired)

    if not private_key_pem:
        return jsonify({"error": "No valid key found"}), 404

    # Now we have the private key, use it to sign a JWT
    payload = {
        "user": "userABC",  # This would typically be based on the authenticated user
        "exp": datetime.utcnow()  # Add more claims as needed (e.g., expiration, roles)
    }

    # Encode the JWT using the fetched private key and RS256 algorithm
    token = jwt.encode(payload, private_key_pem, algorithm="RS256")

    return jsonify({"jwt": token})

if __name__ == '__main__':
    app.run(debug=True)
