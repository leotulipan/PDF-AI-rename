import json
import os
import sys
import tiktoken
from PyPDF2 import PdfReader
from openai import OpenAI
import re
import time
import argparse  # Added for command-line argument parsing
from dotenv import load_dotenv  # Added for loading environment variables from .env file
from loguru import logger  # Added for logging

# Load environment variables from .env file
load_dotenv()

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Rename PDF files using OpenAI")
parser.add_argument("-d", "--dir", required=True, help="Directory containing PDF files")
parser.add_argument("-n", "--dry-run", action="store_true", help="Only list the PDF files found, don't rename")
args = parser.parse_args()

# Set up logging
logger.remove()  # Remove default logger
logger.add(sys.stderr, level="INFO")  # Add console logger at INFO level

# Initialize OpenAI client with API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.error("OpenAI API key not found in environment variables. Please set the OPENAI_API_KEY variable.")
    sys.exit(1)

client = OpenAI()

max_length = 15000

def get_new_filename_from_openai(pdf_content, original_filename):
    if len(pdf_content) > 3000:
        content_snippet = pdf_content[:1500] + pdf_content[-1500:]
    else:
        content_snippet = pdf_content
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON. Please reply with a filename that consists only of English characters, dashes, numbers, spaces and underscores, and is no longer than 50 characters. Do not include characters outside of these, as the system may crash. If you find a document date (i.e. an invoice date) to start the filename with the date in ISO YYYY-MM-DD followed by a space a dash and another space then the rest of the filename. Do not include an extension. Mention the name of the company writing the invoice, if it is one. Remove superflous text that do not add context like e.g. miscellaneous, completion, etc"},
            {"role": "user", "content": f"Original filename '{original_filename}', content: {content_snippet}"}
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_object"
        }
    )
    json_response = response.choices[0].message.content
    try:
        filename = json.loads(json_response)["filename"]
    except (KeyError, json.JSONDecodeError):
        logger.error(f"Error parsing JSON response: {json_response}")
        filename = None
    
    if filename:
        filename = validate_and_trim_filename(filename)
    return filename

def validate_and_trim_filename(initial_filename):
    allowed_chars = r'[a-zA-Z0-9_]'
    
    if not initial_filename:
        timestamp = time.strftime('%Y%m%d%H%M%S', time.gmtime())
        return f'empty_file_{timestamp}'
    
    if re.match("^[A-Za-z0-9_]$", initial_filename):
        return initial_filename if len(initial_filename) <= 100 else initial_filename[:100]
    else:
        cleaned_filename = re.sub("^[A-Za-z0-9_]$", '', initial_filename)
        return cleaned_filename if len(cleaned_filename) <= 100 else cleaned_filename[:100]

def rename_pdfs_in_directory(directory):
    pdf_contents = []
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    for filename in files:
        if filename.endswith(".pdf"):
            filepath = os.path.join(directory, filename)
            print(f"Reading file {filepath}")
            pdf_content = pdfs_to_text_string(filepath)
            new_file_name = get_new_filename_from_openai(pdf_content, filename)
            if new_file_name in [f for f in os.listdir(directory) if f.endswith(".pdf")]:
                print(f"The new filename '{new_file_name}' already exists.")
                new_file_name += "_01"

            new_filepath = os.path.join(directory, new_file_name + ".pdf")
            try:
                os.rename(filepath, new_filepath)
                print(f"File renamed to {new_filepath}")
            except Exception as e:
                print(f"An error occurred while renaming the file: {e}")

def pdfs_to_text_string(filepath):
    with open(filepath, 'rb') as file:
        reader = PdfReader(file)
        content = reader.pages[0].extract_text()
        if not content.strip():
            content = "Content is empty or contains only whitespace."
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(content))
        if num_tokens > max_length:
            content = content_token_cut(content, num_tokens, max_length)
        return content

def content_token_cut(content, num_tokens, max_length):
    content_length = len(content)
    while num_tokens > max_length:
        ratio = num_tokens / max_length
        new_length = int(content_length * num_tokens * (90 / 100))
        content = content[:new_length]
        num_tokens = len(tiktoken.get_encoding("cl100k_base").encode(content))
    return content

def main():
    directory = args.dir

    # List PDF files in the directory
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
    if not pdf_files:
        logger.info(f"No PDF files found in {directory}")
        return

    logger.info(f"Found {len(pdf_files)} PDF file(s) in {directory}")

    # Dry run: only list the PDF files
    if args.dry_run:
        for pdf_file in pdf_files:
            logger.info(pdf_file)
        return

    # Rename PDF files
    rename_pdfs_in_directory(directory)

if __name__ == "__main__":
    main()
