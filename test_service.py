import requests

# URL вашего сервера Flask
url = 'http://localhost:5000/download'


#docsend_url = "https://docsend.com/view/nzppxee7abw8p487/d/wqywyjs8pwg42eac"
#docsend_url = "https://docsend.com/view/wwjxgffq5trma9g9"
#docsend_url = "https://sizable.docsend.com/view/ixntv94j3i8kuuah"
docsend_url = "https://docsend.com/view/izmhj5kjdiqjsbk2"

doc_id = docsend_url.rsplit('/', 1)[-1]

# Данные для отправки в запросе
data = {
    'doc_url': docsend_url,  # Замените на реальный doc_id
    'email': 'ak@rpv.global',       # (Необязательно) Укажите email, если нужно
    'passcode': 'your_passcode',       # (Необязательно) Укажите passcode, если нужно
    'format': 'pdf'                    # Можно заменить на 'png' для формата изображений
}

# Заголовки HTTP
headers = {
    'Content-Type': 'application/json'
}

# Отправка POST-запроса
response = requests.post(url, json=data, headers=headers)

# Проверка успешности ответа
if response.status_code == 200:
    # Сохранение загруженного файла
    with open('downloaded_document.pdf', 'wb') as file:
        file.write(response.content)
    print("Документ успешно скачан и сохранен.")
else:
    print(f"Ошибка при скачивании документа: {response.status_code}")
    print("Ответ:", response.json())
