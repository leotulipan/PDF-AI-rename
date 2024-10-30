# PDFs-AI-rename

Imagine you have a folder full of PDF documents, and you're looking for a quick and creative way to rename them. This Python script is designed to help you do just that! It's like having a personal assistant who reads through your PDFs and suggests new, concise names for each file.

> Fork of https://github.com/Brandon-c-tech/PDFs-AI-rename

Changes from Original

- using .env for API Key
- command line Arguments with argparse
- loguru for better debugging/log output
- only send 3000 chars (top and bottom) of pdf, when bigger
- use gpt-40-mini instead of 3.5 turbo
- extended system prompt
- use structured output feature of new model (json_object)
- exit, when no PDFs found in directory


Here's how it works:

1. **Read PDFs**: The script scans a specified folder on your computer, looking for PDF files. It then reads the text from each PDF, pulling out the first and last 1500 characters of text that will inspire the new file names.

2. **Generate Names**: With the content of your PDFs in hand, the script sends a message to a Open AI service (gpt-4o-mini). This AI takes the content, thinks about it, and comes up with a short, catchy name for each file – no more than 15 characters long.

3. **Rename Files**: Once the AI has suggested new names, the script goes back to your folder and renames each PDF accordingly. Now, instead of generic names like "document1.pdf" or "report.pdf," you have meaningful, concise titles that reflect the content of each file.

This script is perfect for anyone who wants to organize their digital files more efficiently or add a touch of creativity to their file naming process. It's a simple tool that can save you time and make your file management a little more enjoyable.

# Installation

Remember, to use this script, you'll need to have Python installed on your computer, along with the necessary libraries (PyPDF2 and requests). You'll also need an API key from OpenAI, which you can obtain by signing up for their services. The script assumes you're comfortable with renaming files on your computer and that you're looking for a fun, easy way to refresh your file organization.


## Install UV
I suggest to use the tool uv to manage python and the needed dependcies

See https://docs.astral.sh/uv/getting-started/installation/ for details. Ideall it is just

´´´
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
´´´

## Configure

1. Get an API Key at https://platform.openai.com/api-keys
2. Save key to a file called **.env** use the env.template and rename it

## Usage

usage: pdfs_ai_rename.py [-h] -d DIR [-n]


´´´
uv run .\pdfs_ai_rename.py -d <DirectoryName>
´´´