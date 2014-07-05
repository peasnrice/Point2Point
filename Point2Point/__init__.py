# application_python cookbook expects manage.py in a top level
# instead of app level dir, so the relative import can fail
from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

try:
    from .Point2Point.Point2Point.settings import *
except ImportError:
    from Point2Point.settings import *

try:
    from local_settings import *
except ImportError:
    pass