git pull
pkill -9 uwsgi
uwsgi --wsgi-file blog_backend/wsgi.py -d --ini blog_backend/uwsgi.ini