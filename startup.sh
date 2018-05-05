#!bin/sh

cd src/backend_api
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt
FLASK_DEBUG=TRUE FLASK_APP=app.py flask initdb
FLASK_DEBUG=TRUE FLASK_APP=app.py flask run 
