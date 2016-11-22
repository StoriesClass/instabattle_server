# instabattle_server

[![Build Status](https://travis-ci.org/StoriesClass/instabattle_server.svg?branch=master)](https://travis-ci.org/StoriesClass/instabattle_server)

# Building
1. Install Postgres (instructions are not provided because it's system dependent).
2. Install dependencies from `requirements.txt`:
```
pip install -r requirements.txt
```
3. Create Postgres db and user:
```
bash> sudo -u postgres psql
postgres-# CREATE USER test WITH PASSWORD 'test';
CREATE ROLE
postgres=# CREATE DATABASE instabattle_test;
CREATE DATABASE
postgres=# GRANT ALL PRIVILEGES ON DATABASE instabattle_test TO test;
GRANT
```
4. Update database according to schemas:
```
bash> python manage.py db init
bash> python manage.py db migrate
bash> python manage.py db upgrade
```
5. Generate fake data if you want to:
```
bash> python manage.py generate_fake
```

## Links
* Front-end: [repository][1]
* Diagram: [Gliffy][2]


[1]: https://github.com/StoriesClass/instabattle
[2]: https://www.gliffy.com/go/publish/11338561

