# PELEC304 Activities

Four existing college activities combined into one Django project and one
PythonAnywhere web app. The original activity layouts, CSS, images, forms,
student profiles, and read-only product API are preserved.

## Activities

| Page | Local URL | Django app |
| --- | --- | --- |
| Light-mode homepage | http://127.0.0.1:8000/ | `pelec304` |
| Login and registration | http://127.0.0.1:8000/login-register/ | `login_activity` |
| Static/media and PaceBuk profile | http://127.0.0.1:8000/static-media/ | `media_activity` |
| Student list and profiles | http://127.0.0.1:8000/students/ | `students` |
| Product API | http://127.0.0.1:8000/api/products/ | `products` |
| Django admin | http://127.0.0.1:8000/admin/ | Django admin |

The two authentication activities share users and sessions. Register once in
either activity, then use that account in both. Logging out of either logs you
out of both. Each activity still uses its own login, registration, and landing
page design. The student pages and product API remain public, as in the sources.

## Run locally on Windows

Use Python 3.12, 3.13, or 3.14. Run these PowerShell commands from this repository.
The virtual environment is created outside the repository; activation is optional.

```powershell
python -m venv ..\pelec304-venv
& ..\pelec304-venv\Scripts\python.exe -m pip install -r requirements.txt
& ..\pelec304-venv\Scripts\python.exe manage.py migrate
& ..\pelec304-venv\Scripts\python.exe manage.py seed_students
& ..\pelec304-venv\Scripts\python.exe manage.py seed_products
& ..\pelec304-venv\Scripts\python.exe manage.py createsuperuser
& ..\pelec304-venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/. Create your own activity account in a registration
form. `createsuperuser` is only needed to manage students and products in admin;
there are no supplied accounts or passwords. Stop the server with Ctrl+C.

For macOS/Linux, create `../pelec304-venv` using `python3 -m venv`, activate it
with `source ../pelec304-venv/bin/activate`, and use `python` for the commands above.

The seed commands add the original five fictional students and 20 sample
products. Repeating them preserves existing records and edits. The original
`products.json` fixture is retained, but `loaddata products` would overwrite
matching product IDs; prefer `seed_products`.

## Files and settings

- `pelec304/`: shared settings, URL routing, WSGI/ASGI entry points, integration tests.
- `login_activity/` and `media_activity/`: renamed copies of the original `accounts` apps.
- `students/` and `products/`: original student and product apps with their migrations.
- Each app owns its namespaced templates and static files; no `base.html` or `style.css` collisions.
- `templates/home.html` and `static/portal/home.css`: the new homepage.
- `deploy/pythonanywhere_wsgi.py`: ready-to-copy PythonAnywhere WSGI configuration.
- [DEPLOYMENT.md](DEPLOYMENT.md): complete deployment and update instructions for `monogutsy`.
- [SOURCES.md](SOURCES.md): source commit IDs and integration changes.
- [TESTING.md](TESTING.md): tests, manual checks, and verification results.

Local `db.sqlite3`, uploaded `media/`, generated `staticfiles/`, secrets, and
virtual environments are ignored by Git. They are created when needed, not
distributed in this repository. Tests use a disposable database and in-memory
upload storage. No source databases or user-uploaded files were imported.

Local settings generate a temporary development secret when `DJANGO_SECRET_KEY`
is not set, so a server restart can sign you out. To keep local sessions across
restarts, set that environment variable to your own random value. Production
requires a persistent private config file outside the repository.

## API examples

```text
GET /api/products/                 # all products
GET /api/products/1/               # one product
GET /api/products/?format=json     # explicit JSON response
```

A browser displays Django REST Framework's original browsable API. Requests with
`Accept: application/json` return JSON. Product fields are `id`, `name`,
`category`, `description`, `price`, and `stock`. Prices are decimal strings.
Missing products return 404; POST, PUT, PATCH, and DELETE return 405.
Use Django admin to add, edit, or delete products.
