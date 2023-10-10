"""
WSGI config for reservacancha project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

BASE_DIR = sys.path.dirname(sys.path.dirname(sys.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = 'reservacancha.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reservacancha.settings')


application = get_wsgi_application()
