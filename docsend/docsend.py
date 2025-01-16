"""
Module for interacting with DocSend to download documents.
"""

from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

from urllib.parse import urlparse
from PIL import Image
from requests_html import HTMLSession


class DocSend:
    """
    A class to interact with DocSend to fetch and save documents as PDF or images.
    """

    def __init__(self, view_url):
        """
        Initialize the DocSend object with the document view URL.
        """
        parsed_url = urlparse(view_url)
        self.domain = parsed_url.netloc  # Извлекаем домен (например, cft.docsend.com)
        self.doc_id = parsed_url.path.rpartition('/')[-1]  # Извлекаем идентификатор документа
        self.url = view_url  # Собираем полный URL
        self.s = HTMLSession()
        self.auth_token = None
        self.pages = None
        self.image_urls = []
        self.images = []

    def fetch_meta(self):
        """
        Fetch metadata for the document, including the authenticity token and number of pages.
        """
        r = self.s.get(self.url)
        r.raise_for_status()
        if r.html.find('input[@name="authenticity_token"]'):
            self.auth_token = r.html.find('input[@name="authenticity_token"]')[0].attrs['value']
        self.pages = int(r.html.find('.document-thumb-container')[-1].attrs['data-page-num'])

    def authorize(self, email, passcode=None):
        """
        Authorize access to the document using email and optional passcode.
        """
        form = {
            'utf8': '✓',
            '_method': 'patch',
            'authenticity_token': self.auth_token,
            'link_auth_form[email]': email,
            'link_auth_form[passcode]': passcode,
            'commit': 'Continue',
        }
        f = self.s.post(self.url, data=form)
        f.raise_for_status()

    def fetch_images(self):
        """
        Fetch images of all pages in the document.
        """
        pool = ThreadPoolExecutor(self.pages)
        self.images = list(pool.map(self._fetch_image, range(1, self.pages + 1)))

    def _fetch_image(self, page):
        """
        Fetch a single page image from the document.
        """
        meta = self.s.get(f'{self.url}/page_data/{page}')
        meta.raise_for_status()
        data = self.s.get(meta.json()['imageUrl'])
        data.raise_for_status()
        rgba = Image.open(BytesIO(data.content))
        rgb = Image.new('RGB', rgba.size, (255, 255, 255))
        rgb.paste(rgba)
        return rgb

    def save_pdf(self, name=None):
        """
        Save the fetched images as a PDF file.
        """
        self.images[0].save(
            name,
            format='PDF',
            append_images=self.images[1:],
            save_all=True
        )

    def save_images(self, name):
        """
        Save the fetched images as individual PNG files.
        """
        path = Path(name)
        path.mkdir(exist_ok=True)
        for page, image in enumerate(self.images, start=1):
            image.save(path / f'{page}.png', format='PNG')
