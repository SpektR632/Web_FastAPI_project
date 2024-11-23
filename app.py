import sqlite3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

attr = ['id', 'title', 'genre', 'author', 'publisher', 'year', 'description', 'isbn', 'price', 'photo']


def sql_and_pagination(page, page_size):
    """
    Функция подключения с базе данных, создания списка книг и создания пагинации
    :param page: Начало страниц
    :param page_size: Количество элементов на странице
    :return: список словарей атрибутов книг, список книг на определенной странице, количество страниц
    """
    connect = sqlite3.connect('db.sqlite3')
    cursor = connect.cursor()
    books = cursor.execute('SELECT * FROM books')
    books_dicts = []
    for book in books:
        books_dicts.append(dict(
            zip(attr,
                book)))
    cursor.close()
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = books_dicts[start:end]
    total_pages = (len(books_dicts) + page_size - 1) // page_size
    return books_dicts, paginated_items, total_pages


@app.get('/')
async def index(request: Request, page: int = 1, page_size: int = 13) -> HTMLResponse:
    """
    Асинхронная функция для  отображения главной страницы сайта с пагинацией

    """
    books_dicts, paginated_items, total_pages = sql_and_pagination(page, page_size)
    books_num = len(books_dicts)
    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "books_num": books_num,
                                       "books": paginated_items,
                                       "current_page": page,
                                       "total_pages": total_pages,
                                       "page_size": page_size})


@app.get('/book_list')
async def book_list(request: Request, page: int = 1, page_size: int = 5) -> HTMLResponse:
    """
    Асинхронная функция для отображения списка книг с пагинацией

    """
    books_dicts, paginated_items, total_pages = sql_and_pagination(page, page_size)
    return templates.TemplateResponse("book_list.html",
                                      {"request": request,
                                       "books": paginated_items,
                                       "current_page": page,
                                       "total_pages": total_pages,
                                       "page_size": page_size})


@app.get('/book_list/{book_id}')
async def book_detail(request: Request, book_id: int) -> HTMLResponse:
    """
    Асинхронная функция с динамическим url для предоставления подробной информации по выбранной книге

    """
    connect = sqlite3.connect('db.sqlite3')
    cursor = connect.cursor()
    book_ = connect.execute('SELECT * FROM books WHERE id = ?', (int(book_id),))
    book = dict(zip(attr, list(book_)[0]))
    connect.close()
    return templates.TemplateResponse("book_detail.html", {"request": request, "book": book})
