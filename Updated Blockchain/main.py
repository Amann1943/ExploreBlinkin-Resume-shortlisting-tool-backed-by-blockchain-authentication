import hashlib
import fitz  # PyMuPDF
import cv2
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
import tkinter as tk
from tkinter import filedialog
from difflib import SequenceMatcher
import os
from blockchain import Blockchain

# Initialize Blockchain instance
blockchain = Blockchain()

# Utility Functions
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

def extract_images_from_pdf(pdf_path):
    """Extract images from a PDF file."""
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            img_pil = Image.open(BytesIO(image_bytes))
            images.append(img_pil)
    return images

def decode_qr_codes(image):
    """Decode QR codes from an image."""
    qr_codes = decode(image)
    decoded_text = []
    for qr_code in qr_codes:
        qr_data = qr_code.data.decode("utf-8")
        decoded_text.append(qr_data)
    return decoded_text

def generate_pdf_hash(pdf_path):
    """Generate hash for a PDF file."""
    with open(pdf_path, "rb") as file:
        file_data = file.read()
        return hashlib.sha256(file_data).hexdigest()

def generate_image_hash(image):
    """Generate hash for an image file (PIL Image object)."""
    image_bytes = image.tobytes()  # Convert the image to bytes
    return hashlib.sha256(image_bytes).hexdigest()

def normalize_text(text):
    """Normalize text for comparison."""
    return ' '.join(text.split()).lower()

def text_similarity(text1, text2):
    """Calculate similarity between two texts."""
    if text1 is None or text2 is None:
        return 0.0
    return SequenceMatcher(None, normalize_text(text1), normalize_text(text2)).ratio()

def qr_code_similarity(qr1, qr2):
    """Calculate similarity between QR code data."""
    if qr1 is None or qr2 is None:
        return 0.0
    return 1.0 if qr1 == qr2 else 0.0

def find_matching_file_path(file_hash, prepopulate_files):
    """Find the matching file path for a given hash from pre-populated files."""
    for file_path in prepopulate_files:
        if generate_pdf_hash(file_path) == file_hash:
            return file_path
    return None

def compare_pdf_with_blockchain(uploaded_pdf_path, prepopulate_files):
    """Compare the uploaded PDF file with the blockchain."""
    # Generate the hash for the uploaded PDF
    uploaded_file_hash = generate_pdf_hash(uploaded_pdf_path)
    print(f"Generated Hash for uploaded PDF: {uploaded_file_hash}")
    
    # Check if this hash matches any block in the blockchain
    transaction = blockchain.compare_file_with_blockchain(uploaded_pdf_path)
    if transaction["message"] == "File found in blockchain":
        print("This file's hash matches a block in the blockchain.")
        
        # Find the matching pre-populated file path
        existing_pdf_path = find_matching_file_path(uploaded_file_hash, prepopulate_files)
        if not existing_pdf_path:
            print("Error: Matching file path not found.")
            return
        
        # Extract text from the matching PDF in the blockchain
        existing_text = extract_text_from_pdf(existing_pdf_path)

        # Extract text from the uploaded PDF
        uploaded_text = extract_text_from_pdf(uploaded_pdf_path)
        
        # Extract images and QR codes from the uploaded PDF
        uploaded_images = extract_images_from_pdf(uploaded_pdf_path)
        uploaded_qr_codes = []
        for img in uploaded_images:
            uploaded_qr_codes.extend(decode_qr_codes(img))
        
        print(f"Extracted Text (uploaded PDF): {uploaded_text}")
        print(f"Extracted QR Codes (uploaded PDF): {uploaded_qr_codes}")
        
        # Extract images and QR codes from the matching PDF in the blockchain
        existing_images = extract_images_from_pdf(existing_pdf_path)
        existing_qr_codes = []
        for img in existing_images:
            existing_qr_codes.extend(decode_qr_codes(img))
        
        print(f"Extracted Text (existing PDF): {existing_text}")
        print(f"Extracted QR Codes (existing PDF): {existing_qr_codes}")

        # Compare text
        text_similarity_score = text_similarity(uploaded_text, existing_text)

        # Compare images and QR codes
        if uploaded_images and existing_images:
            image_similarity_score = sum(1 for img in uploaded_images if generate_image_hash(img) in [generate_image_hash(eimg) for eimg in existing_images]) / max(len(uploaded_images), 1)
        else:
            image_similarity_score = 1.0

        if uploaded_qr_codes and existing_qr_codes:
            qr_similarity_score = sum(1 for qr in uploaded_qr_codes if qr in existing_qr_codes) / max(len(uploaded_qr_codes), 1)
        else:
            qr_similarity_score = 1.0

        overall_similarity = (text_similarity_score + image_similarity_score + qr_similarity_score) / 3 * 100
        print(f"Text Similarity Score: {text_similarity_score:.2f}")
        print(f"Image Similarity Score: {image_similarity_score:.2f}")
        print(f"QR Code Similarity Score: {qr_similarity_score:.2f}")
        print(f"Overall Similarity Score: {overall_similarity:.2f}%")
        
        # Add the file and metadata to the blockchain
        blockchain.add_file_to_blockchain(
            uploaded_pdf_path,
            text_data=uploaded_text,
            image_hashes=[generate_image_hash(img) for img in uploaded_images],
            qr_codes=uploaded_qr_codes
        )
    else:
        print("No match found for the uploaded file in the blockchain.")

# Pre-populate the blockchain with predefined files (files to be compared)
prepopulate_files = [
    r"C:\\Users\\Hp\\Downloads\\PrepopulateFiles\\1-fd4d8f96-d9c0-4c21-918d-585fd15183f2.pdf",
    r"C:\\Users\\Hp\\Downloads\\PrepopulateFiles\\1234resume.pdf"
]

# Pre-populate blockchain with hashes of predefined files
for file_path in prepopulate_files:
    extracted_text = extract_text_from_pdf(file_path)  # Extract text from PDF
    file_hash = generate_pdf_hash(file_path)
    blockchain.add_file_to_blockchain(file_path, text_data=extracted_text)

# Tkinter file dialog function to select PDF file
def select_pdf_file():
    """Allow the user to select a PDF file."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select PDF file to upload",
        filetypes=[("PDF Files", "*.pdf")]
    )
    return file_path

# Main function to execute the file comparison
def run_comparison():
    """Run the PDF comparison with blockchain."""
    # Open the file dialog to select a PDF file
    uploaded_pdf_path = select_pdf_file()
    if uploaded_pdf_path:
        print(f"Selected PDF file: {uploaded_pdf_path}")
        compare_pdf_with_blockchain(uploaded_pdf_path, prepopulate_files)
    else:
        print("No file selected.")

# Run the comparison
if __name__ == "__main__":
    run_comparison()
