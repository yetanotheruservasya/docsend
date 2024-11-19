# docsend

Convert docsend.com to PDF or PNG image sequence via Flask service.

## Install

Python 3.6+ is required.

```
pip install docsend
```

## Usage

From command line:

```shell
# download a pdf
docsend doc_id --email me@example.com

# include passcode if required
docsend doc_id -e me@example.com --passcode 123example123

# download png sequence
docsend doc_id -e me@example.com --format png

# specify output file or directory name
docsend doc_id -e me@example.com -f pdf --output doc.pdf

# all options combined
docsend doc_id -e me@example.com -p 123example123 -f png -o pages
```

From Python code:

```python
from docsend import DocSend

ds = DocSend('abcdef9')
ds.fetch_meta()
ds.authorize('me@example.com')
ds.fetch_images()
ds.save_pdf('doc.pdf')
ds.save_images('pages')
```

From Flask service:
You can now interact with the service via a REST API built using Flask. Here's an example of how to call the service:

Start the Flask server:

```shell
flask run
```

Call the Flask service via HTTP:
```shell
Copy code
curl -X POST \
  http://127.0.0.1:5000/download \
  -H "Content-Type: application/json" \
  -d '{"doc_id": "abcdef9", "email": "me@example.com", "passcode": "123example123", "format": "pdf", "output": "doc.pdf"}'
```

## Missing features

You are welcome to contribute.
