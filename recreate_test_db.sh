# BE CAREFUL!
rm -rf migrations/
rm data-test.sqlite
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
python manage.py generate_fake
