import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "NLtoSQL_Project.settings")

try:
    application = get_wsgi_application()
    app = application
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
    raise e