from flask import Flask, request, jsonify
from docsend import DocSend

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_document():
    data = request.get_json()
    
    # Проверка обязательных параметров
    if 'doc_id' not in data:
        return jsonify({'error': 'doc_id is required'}), 400
    
    doc_id = data['doc_id']
    email = data.get('email')
    passcode = data.get('passcode')
    format = data.get('format', 'pdf')
    output = data.get('output')
    
    # Инициализация объекта DocSend
    ds = DocSend(doc_id)
    
    # Получаем метаданные документа
    try:
        ds.fetch_meta()
    except Exception as e:
        return jsonify({'error': f'Failed to fetch document metadata: {str(e)}'}), 500

    # Авторизация
    if email:
        try:
            if passcode:
                ds.authorize(email, passcode)
            else:
                ds.authorize(email)
        except Exception as e:
            return jsonify({'error': f'Failed to authorize: {str(e)}'}), 403
    
    # Получаем изображения документа
    try:
        ds.fetch_images()
    except Exception as e:
        return jsonify({'error': f'Failed to fetch document images: {str(e)}'}), 500
    
    # Генерация имени для выходного файла, если не передано
    if not output:
        output = f'docsend_{doc_id}.pdf' if format == 'pdf' else f'docsend_{doc_id}'
    
    # Сохранение документа в нужном формате
    try:
        if format == 'pdf':
            ds.save_pdf(output)
        elif format == 'png':
            ds.save_images(output)
        else:
            return jsonify({'error': 'Invalid format specified. Use "pdf" or "png".'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to save document: {str(e)}'}), 500
    
    return jsonify({'message': f'Successfully saved to {output}'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5006)
