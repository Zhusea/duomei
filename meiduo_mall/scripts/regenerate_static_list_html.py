#! /usr/bin/env python

import os
import django
import sys


sys.path.insert(0,'./../')
sys.path.insert(0,'./../meiduo_mall/apps')
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

django.setup()

if __name__ == '__main__':
    from celery_tasks.html.tasks import generate_static_list_html
    generate_static_list_html()
