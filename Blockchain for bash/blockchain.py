import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        """Create a new block and add it to the blockchain."""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []  # Reset current transactions
        self.chain.append(block)
        return block

    def new_transaction(self, file_hash, text_data=None, image_hashes=None, qr_codes=None):
        """Add a new transaction with file hash and other data."""
        transaction = {
            "file_hash": file_hash,
            "text_data": text_data,
            "image_hashes": image_hashes,
            "qr_codes": qr_codes,
        }
        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """Generate a hash for a given block."""
        # Ensure the block dictionary is serialized consistently
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """Return the last block in the chain."""
        return self.chain[-1]

    def generate_file_hash(self, file_path):
        """Generate the hash for a given file."""
        try:
            with open(file_path, "rb") as file:
                file_data = file.read()
                file_hash = hashlib.sha256(file_data).hexdigest()
            return file_hash
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

    def add_file_to_blockchain(self, file_path, text_data=None, image_hashes=None, qr_codes=None):
        """Add a new file's hash and data to the blockchain."""
        # Generate the hash of the uploaded file
        file_hash = self.generate_file_hash(file_path)

        # Add the file hash to the blockchain transaction
        self.new_transaction(
            file_hash=file_hash,
            text_data=text_data,
            image_hashes=image_hashes,
            qr_codes=qr_codes,
        )

        # Add the new block to the blockchain after the transaction
        self.new_block(proof=100)
        print(f"Added file hash: {file_hash} to blockchain")

    def compare_file_with_blockchain(self, file_path):
        """Compare file hash with hashes in the blockchain."""
        # Generate the hash of the file to be compared
        file_hash = self.generate_file_hash(file_path)
        
        # Search for the file hash in the blockchain
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['file_hash'] == file_hash:
                    return {
                        "message": "File found in blockchain",
                        "block_index": block['index'],
                        "transaction": transaction
                    }
        return {
            "message": "File not found in blockchain",
            "file_hash": file_hash
        }

if __name__ == "__main__":
    # Test the Blockchain class
    blockchain = Blockchain()

    # Add a sample file to the blockchain
    test_file_path = "sample.pdf"  # Replace with the path to your PDF file
    try:
        blockchain.add_file_to_blockchain(test_file_path, text_data="Sample text data")

        # Test the comparison method
        result = blockchain.compare_file_with_blockchain(test_file_path)
        print(json.dumps(result, indent=4))
    except FileNotFoundError as e:
        print(str(e))
