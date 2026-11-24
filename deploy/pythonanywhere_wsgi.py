"""Copy this into the WSGI configuration file linked on PythonAnywhere's Web tab."""
import os
import sys

project_path = "/home/monogutsy/PELEC304-Activities"
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ["DJANGO_SETTINGS_MODULE"] = "pelec304.production"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
