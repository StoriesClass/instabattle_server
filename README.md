# instabattle_server

[![Build Status](https://travis-ci.org/StoriesClass/instabattle_server.svg?branch=master)](https://travis-ci.org/StoriesClass/instabattle_server)

# Build

```
$> pip install -r requirements.txt
$> python manage.py db upgrade
$> python manage.py generate_fake
```

If you want to use Postgres:
```
$> sudo -u postgres psql
postgres-# CREATE USER test WITH PASSWORD 'test';
CREATE ROLE
postgres=# CREATE DATABASE instabattle_test;
CREATE DATABASE
postgres=# GRANT ALL PRIVILEGES ON DATABASE instabattle_test TO test;
GRANT
```

# Run
You can either use Flask's built-in server:

```
$> python manage.py runserver
```
or gunicorn:
```
$> gunicorn manage:app
```

# Links
* Front-end: [repository][1]
* Diagram: [Gliffy][2]
* Live: [Heroku][3]


[1]: https://github.com/StoriesClass/instabattle
[2]: https://www.gliffy.com/go/publish/11338561
[3]: https://instabattle2.herokuapp.com

