# ReviewScraper

**Redis Queue Managemant**

rq worker



**Run Flask APP**

export FLASK_APP=app.main:app && flask run --reload



Create a MySQL database with one table 

The table Schema:

review1(
jod_id LONGTEXT,
time LONGTEXT,
filename LONGTEXT,
retailer VARCHAR(10),
url LONGTEXT,
status LONGTEXT)

Specify the db credentials in "mysql_connection.py" and "main.py"(inside fetch function) files
