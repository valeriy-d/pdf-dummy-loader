import os
import io
import uuid
import copy

from operator import itemgetter
from itertools import groupby

from tornado import gen
from tornado.web import authenticated

from wand.image import Image
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
from sqlalchemy import inspect

from utils import make_session
from settings import settings
from settings import PROJECT_ROOT
from apps.main.views import LoginRequiredView
from .models import BookModel, PageModel

upload_path = settings.get('upload_path')

def get_file_dir(name):
    return os.path.join(upload_path, name)

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


class PdfDownloaderView(LoginRequiredView):
    @gen.coroutine
    def get(self, path):
        file_name = path.split()[-1]
        file_path = os.path.join(PROJECT_ROOT, settings['upload_path'], path)
        buf_size = 4096
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)
        self.finish()


class PdfUploaderView(LoginRequiredView):
    @gen.coroutine
    def _save_in_db(self, model, **kwargs):
        row = model(**kwargs)
        with make_session() as session:
            session.add(row)
            session.flush()
            session.commit()
            id = row.id

        return id

    @gen.coroutine
    def write_origin_file(self, stream, name):
        """
        Сохраняет информацию о файле в БД
        и записывает его в директорию
        """

        file_name = str(uuid.uuid4())
        path = os.path.join(settings['upload_path'], 'pdf', ''.join([file_name, '.pdf']))
        @gen.coroutine
        def write_to_disk():
            with open(path, 'wb') as f:
                f.write(stream.read())

        result = yield [
            self._save_in_db(BookModel, name=name, path=path, username=self.current_user),
            write_to_disk()
        ]
        # возвращаем id новой записи
        return result[0]

    @gen.coroutine
    def write_page(self, book, page, name, book_id):
        name = ''.join([name, '-page', str(page), '.png'])
        file_name = str(uuid.uuid4())
        path = os.path.join(settings['upload_path'], 'png', ''.join([file_name, '.png']))

        @gen.coroutine
        def write_to_disk():
            dst_pdf = PdfFileWriter()
            dst_pdf.addPage(book.getPage(page))
            pdf_bytes = io.BytesIO()
            dst_pdf.write(pdf_bytes)
            pdf_bytes.seek(0)
            with Image(file=pdf_bytes, resolution=72) as img:
                img.convert("png")
                img.save(filename=path)

        yield [
            write_to_disk(),
            self._save_in_db(
                PageModel,
                name=name,
                path=path,
                book_id=book_id
            )
        ]

    @gen.coroutine
    def read_pdf(self, pdf, name):
        stream = io.BytesIO(pdf.get('body'))
        stream1 = copy.deepcopy(stream)

        f = PdfFileReader(stream)
        book_id = yield from self.write_origin_file(stream1, name)
        tasks = [self.write_page(f, page, name, book_id) for page in range(f.getNumPages())]
        coroutines = yield from tasks

    @gen.coroutine
    @authenticated
    def post(self, *args, **kwargs):
        """
        Загрузка файла, разбиение на png, редирект на главную
        """
        attachment = self.request.files['attachment'][0]
        yield self.read_pdf(attachment, attachment.get('filename'))

        self.redirect('/')


class PdfListView(LoginRequiredView):
    @gen.coroutine
    def get_data(self):
        with make_session() as session:
            q = session.query(BookModel, PageModel)
            q = q.join(PageModel, PageModel.book_id == BookModel.id, isouter=True)

        return q.all()

    @gen.coroutine
    @authenticated
    def get(self, *args, **kwargs):
        res = yield self.get_data()
        res = [u._asdict() for u in res]
        items = []
        for book, page in groupby(res, key=itemgetter('BookModel')):
            el = dict()
            el['book'] = book
            pages = [i for i in page]
            el['pages'] = pages
            items.append(el)

        self.render('main.html', items=items)
