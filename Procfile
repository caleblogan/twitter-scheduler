web: gunicorn twitter_site.wsgi --log-file - --log-level debug
worker: celery -A twitter_site worker -l info