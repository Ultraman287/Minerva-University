# Welcome to CS162 Final Project

![template ci](https://github.com/minerva-schools/template-cs162/actions/workflows/ci.yaml/badge.svg)


## Run - Docker Development Version

This project can be quickly run using Docker in a reliable and repeatable manner. There are three environment variables, the firebase credentials (DB_KEY), port (PORT=5000), host (HOST=0.0.0.0). 

The authentication file alongside the appropriate environment to run production can be seen in example.env and exampleadminkey.json which you can rename by removing the "example" for it to work.

The base development commands are

```
docker build -t nutrisafe .
docker run -d -e DB_KEY={DB_KEY_LOCATION} -p 5000:5000 nutrisafe
```
For production or other values, use:
```
docker build --build-arg PORT={PORT_NUMBER} --build-arg HOST={HOST_ADDRESS} -t nutrisafe .
docker run -d -e DB_KEY={DB_KEY_LOCATION} -p {PORT_NUMBER}:{PORT_NUMBER} nutrisafe
```

## Run - Docker Production Version w/ Gunicorn & Nginx
To deploy this project for production, we chose to use Gunicorn and Nginx. 

The environment variable DB_KEY refers to the firebase authentication file.

If DB_KEY is placed in the base directory and is called adminkey.json, you can run everything immediately with the following command:
```
docker compose up
```
However, if you have a non-default DB_KEY, use the following.
```
docker compose run -e DB_KEY="insert your value here" -d web
docker compose run -d nginx
```
## Run - Python/Virtual Environment Method

Virtual environment is a key component in ensuring that the application is configured in the right environment

##### Requirements
* Python 3
* Pip 3

```bash
$ brew install python3
```

Pip3 is installed with Python3

##### Installation
To install virtualenv via pip run:
```bash
$ pip3 install virtualenv
```

##### Usage
Creation of virtualenv:

    $ virtualenv -p python3 venv

If the above code does not work, you could also do

    $ python3 -m venv venv

To activate the virtualenv:

    $ source venv/bin/activate

Or, if you are **using Windows** - [reference source:](https://stackoverflow.com/questions/8921188/issue-with-virtualenv-cannot-activate)

    $ venv\Scripts\activate

To deactivate the virtualenv (after you finished working):

    $ deactivate

Install dependencies in virtual environment:

    $ pip3 install -r requirements.txt

## Environment Variables

All environment variables are stored within the `.env` file and loaded with dotenv package.

**Never** commit your local settings to the Github repository!

## Run Application

Start the server by running:

    $ export FLASK_ENV=development
    $ export FLASK_APP=web
    $ python3 -m flask run

## Unit Tests
To run the unit tests use the following commands:

    $ python3 -m venv venv_unit
    $ source venv_unit/bin/activate
    $ pip install -r requirements-unit.txt
    $ export DATABASE_URL='sqlite:///web.db'
    $ pytest unit_test

#### Code Coverage

Run the following commands to see testing code coverage of this project

```
    $ coverage run -m unittest discover
    $ coverage report -m

Results:
Name                               Stmts   Miss  Cover   Missing
----------------------------------------------------------------
unit_test/__init__.py                 15      2    87%   17-18
unit_test/test_app.py                 43      0   100%
unit_test/test_authentication.py      76      0   100%
unit_test/test_database.py            43      0   100%
web/__init__.py                       24      1    96%   49
web/auth.py                           61      4    93%   77, 91-93
web/firestore/main.py                164     58    65%   62-63, 85-86, 119-120, 191-192, 198-203, 215-228, 242-255, 299-310, 328-331, 343-348, 366-382
web/foodapp.py                       169     51    70%   39-63, 74-84, 102-114, 121-139, 159
web/geoapify/main.py                  14      0   100%
----------------------------------------------------------------
TOTAL                                609    116    81%
```

## Integration Tests
Start by running the web server in a separate terminal.

Now run the integration tests using the following commands:

    $ python3 -m venv venv_integration
    $ source venv_integration/bin/activate
    $ pip3 install -r requirements-integration.txt
    $ pytest integration_test

## Deployment
We will use Heroku as a tool to deploy your project, and it is FREE

We added Procfile to help you deploy your repo easier, 
but you may need to follow these steps to successfully deploy the project

1. You need to have admin permission to be able to add and deploy your repo to Heroku 
(Please ask your professor for permission)
2. You need to create a database for your website. 
We recommend you use [Heroku Postgres](https://dev.to/prisma/how-to-setup-a-free-postgresql-database-on-heroku-1dc1)
3. You may need to add environment variables to deploy successfully - [Resource](https://devcenter.heroku.com/articles/config-vars#using-the-heroku-dashboard)


## Potential improvements for application 

1. For this application, the frontend and api have been merged into one with flask which makes it so time consuming operations
(such as searching for filtered foods) happen all server side. This means that that the initial html loading happens alongside
the hydration of all the javascript and functionality of the page in one step rather than data being reactively being loaded where it is needed. In search for example, we're filtering through the entire database for all the safe foods and putting them within their respective restaurants. This step has an O(n*m) time complexity where n is the number of restaurants and m is the average number of foods. If instead, we make it so there's a javascript on click event that calls a restful api to get the appropriate restaurants foods, we'd be able to greatly reduce time cost.

2. Another aspect that comes with is the scalability of the application where by making the database noSQL we allow for a much more horizontally scalable solution without having to worry about data consistency issues. However, not having the ability to do complex joins at a smaller scale also results in performance loss until it becomes sufficiently large.

