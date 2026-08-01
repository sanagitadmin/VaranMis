import os
import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "varanmis.settings")

from varanmis.wsgi import application
