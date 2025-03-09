"""
Flask service for downloading documents from DocSend.
"""

import os
import tempfile
import threading
import sys
from urllib.parse import urlparse
from flask import Flask, request, jsonify, send_file, after_this_request

# Try importing DocSend and handle the specific lxml dependency error
try:
    from docsend import DocSend
except ImportError as e:
    if "lxml.html.clean module is now a separate project" in str(e):
        print("Error: Missing required dependency.")
        print("The lxml.html.clean module is now a separate project.")
        print("Please run: pip install lxml[html_clean] or pip install lxml_html_clean")
        sys.exit(1)
    else:
        # Re-raise if it's a different import error
        raise

app = Flask(__name__)

def delayed_remove_file(path):
    """
    Remove the specified file after a delay.
    """
    def remove():
        try:
            os.remove(path)
        except (OSError, PermissionError) as e:
            app.logger.error('Failed to delete the file %s: %s', path, str(e))
    threading.Timer(5, remove).start()

@app.route('/download', methods=['POST'])
def download_document():
    """
    Endpoint to download a document from DocSend.
    Expects a JSON payload with 'doc_url', and optionally 'email', 'passcode', and 'format'.
    """
    data = request.get_json()

    if 'doc_url' not in data:
        return jsonify({'error': 'doc_id is required'}), 400

    doc_url = data['doc_url']
    parsed_url = urlparse(doc_url)
    doc_id = parsed_url.path.rpartition('/')[-1]
    email = data.get('email')
    passcode = data.get('passcode')
    file_format = data.get('format', 'pdf')

    print(doc_url, doc_id, email, passcode, file_format)

    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_format}') as temp_file:
        output = temp_file.name

    ds = DocSend(doc_url)

    try:
        ds.fetch_meta()
        if email:
            if passcode:
                ds.authorize(email, passcode)
            else:
                ds.authorize(email)
        ds.fetch_images()

        if file_format == 'pdf':
            ds.save_pdf(output)
        elif file_format == 'png':
            ds.save_images(output)
        else:
            return jsonify({'error': 'Invalid format specified. Use "pdf" or "png".'}), 400

        if not os.path.exists(output):
            return jsonify({'error': f'File not created: {output}'}), 500

        @after_this_request
        def remove_file(response):
            delayed_remove_file(output)
            return response

        return send_file(output, as_attachment=True)
    except (ValueError, ConnectionError, FileNotFoundError) as e:
        return jsonify({'error': f'Failed to process document: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
