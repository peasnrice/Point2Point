# application_python cookbook expects manage.py in a top level
# instead of app level dir, so the relative import can fail
try:
    from .Point2Point.Point2Point.settings import *
except ImportError:
    from Point2Point.settings import *

try:
    from local_settings import *
except ImportError:
    pass