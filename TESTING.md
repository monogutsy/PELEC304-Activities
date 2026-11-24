# Local verification

Verified on November 24, 2026, with Python 3.14.6, Django 5.2.19,
Django REST Framework 3.17.2, and Pillow 13.0.0 on Windows.

## Automated tests

From the repository, using the environment created in README.md:

```powershell
& ..\pelec304-venv\Scripts\python.exe manage.py test login_activity media_activity students products pelec304
& ..\pelec304-venv\Scripts\python.exe manage.py check
& ..\pelec304-venv\Scripts\python.exe manage.py makemigrations --check --dry-run
& ..\pelec304-venv\Scripts\python.exe -m pip check
```

**Result: 69 tests passed.** System checks found no issues, no model changes
required migrations, and dependency checks found no broken requirements.
The test runner creates and destroys its own database. Photo tests use
in-memory file storage, so they do not alter actual uploaded pictures.

Coverage includes:

- Registration fields, duplicate usernames, password validation and hashing,
  invalid emails, invalid/inactive login, authenticated redirects, username
  fallback, POST-only logout, session clearing, and CSRF enforcement.
- Media profile login protection, default pictures, valid uploads/replacements,
  persistence across logins, per-user ownership, missing/fake/wrong-format/large
  upload rejection, and safe/unsafe login redirect targets.
- Public student pages, class selection, profile links and class scope, field
  display, missing fields, missing students, empty classes/database, cache
  control, unique student numbers, and repeatable fictional-data seeding.
- API list ordering and original data, detail/404 responses, JSON and HTML
  rendering, rejection of write methods even for admins, product administration,
  and repeatable sample-product seeding.
- All four homepage links, separate templates and asset paths, shared accounts,
  shared logout, duplicate usernames across both forms, and shared admin access.

## Database, deployment, and source checks

A fresh temporary SQLite database was migrated successfully, then populated
with five students and 20 products. `collectstatic` gathered **161 files** without
filename collisions. All six original CSS/SVG assets matched their source
files byte for byte, and all four temporary source clones remained unchanged.

Production settings were tested locally using a generated private config outside
the repository. Verified WSGI loading, disabled debug, hostname restriction,
HTTP-to-HTTPS redirect, the forwarded HTTPS header, secure CSRF cookies, HSTS,
product JSON/404 responses, exclusion of Django's development media route, and
startup failure for missing or too-short secrets.

`check --deploy --settings=pelec304.production` completed with only the documented
optional HSTS warnings `security.W005` and `security.W021` (subdomain coverage
and browser preload are off). See DEPLOYMENT.md for the intended configuration.

## Browser checks

An isolated headless Microsoft Edge session exercised the local server with
generated test data and an uploaded test image. The in-app browser connection
was unavailable, so the browser test used temporary Playwright tooling outside
the repository. Playwright is not an application dependency.

Verified through the browser:

1. Homepage navigation to login/registration.
2. Complete registration and login, followed by the personalized welcome page.
3. Shared session access to PaceBuk without a second login.
4. Uploading and displaying a picture, then persistence after logout/login.
5. Student list, detail, and return-to-class navigation.
6. Styled browsable API, 20-product JSON list, and product detail JSON.
7. Logout from PaceBuk also removes access to the login activity's private page.

Inspected desktop and mobile screenshots. Homepage, profile, and student list
had no horizontal overflow at 390px width. No page JavaScript errors occurred;
all activity pages and required assets loaded successfully. Test databases, images, screenshots,
and the test environment were kept outside the repository.

## After deployment

Local checks do not verify PythonAnywhere's live environment. Follow the live
verification steps in DEPLOYMENT.md after configuring its WSGI app and file
mappings. The project has been prepared and tested locally; it has not been
published, pushed to GitHub, or deployed to PythonAnywhere by this task.
