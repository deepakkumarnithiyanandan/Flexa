# import base64
# import json
# import os
# import requests
# from dotenv import load_dotenv
# import re

# # Load environment variables
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # Updated Gemini API Endpoint (Using gemini-1.5-flash)
# GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# def encode_image_to_base64(image_file):
#     """Convert image file to base64 encoding."""
#     return base64.b64encode(image_file.read()).decode("utf-8")

# def process_bill(uploaded_file):
#     """Processes the uploaded bill image and extracts details using Gemini API."""
#     if not GEMINI_API_KEY:
#         raise ValueError("GEMINI_API_KEY is missing. Make sure it's set in your .env file.")
    
#     # Convert image to base64
#     image_base64 = encode_image_to_base64(uploaded_file)
    
#     headers = {"Content-Type": "application/json"}
#     data = {
#         "contents": [
#             {"parts": [
#                 {"text": "Extract the structured bill details including bill_name, items with their quantity and price, all taxes, total price and tips from this image. Return data in structured JSON format."},
#                 {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}}
#             ]}
#         ]
#     }
    
#     response = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", json=data, headers=headers)
    
#     if response.status_code != 200:
#         raise ValueError(f"Failed to process bill. API response error: {response.text}")
    
#     response_data = response.json()
#     print("🔍 Raw API Response:", json.dumps(response_data, indent=4))  # Debugging output
    
#     extracted_text = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    
#     if not extracted_text:
#         print("⚠ No text extracted from the bill image!")
#         return {}
    
#     # Remove markdown-style JSON formatting
#     extracted_text = re.sub(r'^```json\n|```$', '', extracted_text.strip(), flags=re.MULTILINE)
    
#     # Parse the extracted text into structured data
#     structured_data = parse_bill_text(extracted_text)
    
#     # Save structured data to JSON file
#     save_bill_data(structured_data)
    
#     return structured_data

# def parse_bill_text(extracted_text):
#     """Parses extracted text into structured JSON format."""
#     try:
#         structured_data = json.loads(extracted_text)
#     except json.JSONDecodeError:
#         print("⚠ Failed to parse structured JSON, returning raw text.")
#         structured_data = {
#             "raw_text": extracted_text
#         }
#     return structured_data

# def save_bill_data(data):
#     """Saves the extracted bill data to a JSON file in ./database."""
#     os.makedirs("./database", exist_ok=True)
#     file_path = os.path.join("./database", "bill_data.json")
    
#     with open(file_path, "w") as json_file:
#         json.dump(data, json_file, indent=4)
    
#     print(f"Bill data saved successfully to {file_path}")

# def main(image_path):
#     """Main function to test bill processing."""
#     with open(image_path, "rb") as image_file:
#         print("📸 Processing bill image...")
#         structured_data = process_bill(image_file)
    
#     if not structured_data or not structured_data.get("items"):
#         print("⚠ No data extracted from bill!")
#         return

#     print("✅ Extracted Bill Data:")
#     print(json.dumps(structured_data, indent=4))

# # Run the script with your image file
# if __name__ == "__main__":
#     image_path = "./random_bill.png"  # Change this to your image path
#     main(image_path)

import base64
import json
import os
import requests
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Updated Gemini API Endpoint (Using gemini-1.5-flash)
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def encode_image_to_base64(image_file):
    """Convert image file to base64 encoding."""
    return base64.b64encode(image_file.read()).decode("utf-8")

def get_next_bill_id():
    """Retrieve the next available bill ID from stored data."""
    file_path = os.path.join("./database", "bill_data.json")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as json_file:
                existing_data = json.load(json_file)
                return existing_data.get("bill_id", 0) + 1
        except json.JSONDecodeError:
            return 1
    return 1

def process_bill(uploaded_file):
    """Processes the uploaded bill image and extracts details using Gemini API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing. Make sure it's set in your .env file.")
    
    # Convert image to base64
    image_base64 = encode_image_to_base64(uploaded_file)
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [
                {"text": "Extract the structured bill details including bill_name, items with their quantity and price, all taxes, and tips from this image. Return data in structured JSON format."},
                {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}}
            ]}
        ]
    }
    
    response = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", json=data, headers=headers)
    
    if response.status_code != 200:
        raise ValueError(f"Failed to process bill. API response error: {response.text}")
    
    response_data = response.json()
    print("🔍 Raw API Response:", json.dumps(response_data, indent=4))  # Debugging output
    
    extracted_text = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    
    if not extracted_text:
        print("⚠ No text extracted from the bill image!")
        return {}
    
    # Remove markdown-style JSON formatting
    extracted_text = re.sub(r'^```json\n|```$', '', extracted_text.strip(), flags=re.MULTILINE)
    
    # Parse the extracted text into structured data
    structured_data = parse_bill_text(extracted_text)
    
    # Assign auto-incremented bill ID
    structured_data["bill_id"] = get_next_bill_id()
    
    # Save structured data to JSON file
    save_bill_data(structured_data)
    
    return structured_data

def parse_bill_text(extracted_text):
    """Parses extracted text into structured JSON format."""
    try:
        structured_data = json.loads(extracted_text)
    except json.JSONDecodeError:
        print("⚠ Failed to parse structured JSON, returning raw text.")
        structured_data = {
            "raw_text": extracted_text
        }
    return structured_data

def save_bill_data(data):
    """Saves the extracted bill data to a JSON file in ./database."""
    os.makedirs("./database", exist_ok=True)
    file_path = os.path.join("./database", "bill_data.json")
    
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"Bill data saved successfully to {file_path}")

def main(image_path):
    """Main function to test bill processing."""
    with open(image_path, "rb") as image_file:
        print("📸 Processing bill image...")
        structured_data = process_bill(image_file)
    
    if not structured_data or not structured_data.get("items"):
        print("⚠ No data extracted from bill!")
        return

    print("✅ Extracted Bill Data:")
    print(json.dumps(structured_data, indent=4))

# Run the script with your image file
if __name__ == "__main__":
    image_path = "./random_bill.png"  # Change this to your image path
    main(image_path)
