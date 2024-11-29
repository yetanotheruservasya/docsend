import os
from flask import Flask, request, jsonify, send_file
from docsend import DocSend
from urllib.parse import urlparse

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_document():
    data = request.get_json()

    if 'doc_url' not in data:
        return jsonify({'error': 'doc_id is required'}), 400

    doc_url = data['doc_url']
    parsed_url = urlparse(doc_url)
    doc_id = parsed_url.path.rpartition('/')[-1]
    email = data.get('email')
    passcode = data.get('passcode')
    format = data.get('format', 'pdf')

    output = os.path.join(os.getcwd(), f'docsend_{doc_id}.pdf') if format == 'pdf' else os.path.join(os.getcwd(), f'docsend_{doc_id}')

    ds = DocSend(doc_url)

    try:
        ds.fetch_meta()
        if email:
            if passcode:
                ds.authorize(email, passcode)
            else:
                ds.authorize(email)
        ds.fetch_images()

        if format == 'pdf':
            ds.save_pdf(output)
        elif format == 'png':
            ds.save_images(output)
        else:
            return jsonify({'error': 'Invalid format specified. Use "pdf" or "png".'}), 400

        if not os.path.exists(output):
            return jsonify({'error': f'File not created: {output}'}), 500

        response = send_file(output, as_attachment=True)
        return response
    except Exception as e:
        return jsonify({'error': f'Failed to process document: {str(e)}'}), 500
    finally:
        if os.path.exists(output):
            try:
                os.remove(output)
            except Exception as e:
                app.logger.error(f'Failed to delete the file {output}: {str(e)}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
