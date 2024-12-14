from flask import Flask, request, jsonify
from blockchain import Blockchain
import os

app = Flask(__name__)

# Initialize blockchain
blockchain = Blockchain()

# Prepopulate files (replace with actual paths)
prepopulate_files = [
    r"C:\\Users\\Hp\\Downloads\\PrepopulateFiles\\1-fd4d8f96-d9c0-4c21-918d-585fd15183f2.pdf",
    r"C:\\Users\\Hp\\Downloads\\PrepopulateFiles\\1234resume.pdf"
]

@app.before_first_request
def prepopulate_blockchain():
    """Prepopulate the blockchain with files before the first request."""
    for file_path in prepopulate_files:
        if os.path.exists(file_path):
            blockchain.add_file_to_blockchain(file_path, text_data="Prepopulated text data")
        else:
            print(f"File not found: {file_path}")

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and add to blockchain."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    # Add file to blockchain
    try:
        blockchain.add_file_to_blockchain(file_path, text_data="Uploaded file data")
        return jsonify({"message": "File added to blockchain"}), 200
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/compare', methods=['POST'])
def compare_file():
    """Compare uploaded file with blockchain."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    # Compare file hash with blockchain
    result = blockchain.compare_file_with_blockchain(file_path)
    return jsonify(result), 200

@app.route('/')
def home():
    """Basic home route."""
    return jsonify({"message": "Welcome to the blockchain-based file hash verification app!"})

if __name__ == "__main__":
    app.run(debug=True)
