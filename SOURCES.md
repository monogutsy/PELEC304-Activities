# Source repositories

All four repositories contained Django project files when inspected on
November 24, 2026. They were cloned into a temporary folder outside this
repository. No original repository was modified, and no nested Git metadata,
virtual environment, database, or credentials were copied.

| Activity | Repository | Inspected commit |
| --- | --- | --- |
| Login/register | [Developing-Login-Register-Form](https://github.com/monogutsy/Developing-Login-Register-Form) | `19c07f6b87909206cdc3f498c09bbb6510ad5ae7` |
| Static/media | [All-About-Static-Media-Files](https://github.com/monogutsy/All-About-Static-Media-Files) | `29b310948b1e9175698e4f68c339f1e256c33c8d` |
| Enrollment | [Profile-View-for-an-Online-Enrollment-System](https://github.com/monogutsy/Profile-View-for-an-Online-Enrollment-System) | `57ce52696e0f290551d69a4a911dd0036e849a6a` |
| Product API | [API-for-an-e-commerce-website](https://github.com/monogutsy/API-for-an-e-commerce-website) | `48bbf2b9c6740cc7fd5ee7ceec28925d8e4e2cb1` |

## Conflict resolution

1. Replaced the four project configurations with `pelec304`. The source `froms`,
   `enrollment`, and `ecommerce_project` settings are not used or copied.
2. Renamed the login source's `accounts` app to `login_activity` and the media
   source's `accounts` app to `media_activity`. Updated AppConfig, URL names,
   redirects, tests, and explicit login URLs. One Django User model serves both.
3. Moved templates under their app names and updated `extends`, `include`, and
   view template paths. The portal's `home.html` cannot shadow the login home.
4. Moved the three original static directories under app-specific prefixes.
   Original CSS and SVG files remain unchanged, including relative CSS image
   paths. No source media uploads were present; new images use `/media/`.
5. Kept the original student/product migrations and the media Profile migration.
   The Profile migration now belongs to `media_activity`; there is no competing
   `accounts` migration label. This is a fresh database, not a migration of the
   old private databases.
6. Pinned one dependency set: Django 5.2.19, Django REST Framework 3.17.2,
   Pillow 13.0.0. The media source requested Django 6.1, but its forms, model,
   upload handling, templates, and regression tests also work on Django 5.2.
   Django 5.2 LTS supports Python 3.14 starting with 5.2.8; see the
   [official release notes](https://docs.djangoproject.com/en/5.2/releases/5.2/).
7. Kept the original student seed command and product fixture. Added a
   repeatable product seed command that preserves edits instead of reloading IDs.
8. Added the homepage, shared production settings, deployment example, API tests,
   and integration tests. Updated source test expectations for the new URLs and
   asset paths. Student tests now expect the root homepage to link to their list.

The product API remains read-only. The enrollment activity still displays one
selected class at a time, preserves the class in profile links, and does not
require login. Profile pictures still accept JPG, PNG, and WebP up to 5 MB.
