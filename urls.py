from tornado.web import url

from apps.main.views import LoginView
from apps.main.views import LogoutView
from apps.pdf_loader.views import PdfListView
from apps.pdf_loader.views import PdfUploaderView
from apps.pdf_loader.views import PdfDownloaderView


url_patterns = [
    url(r'/', PdfListView),
    url(r'/login', LoginView),
    url(r'/logout', LoginView),
    url(r'/upload', PdfUploaderView),
    url(r'/storage/(?P<path>.*)', PdfDownloaderView),
]
