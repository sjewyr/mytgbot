python admin/manage.py migrate --noinput
python admin/manage.py loaddata admin/backup.json
python admin/manage.py runserver 0.0.0.0:8045
