lsof -i:8000 -t | awk '{print "kill -9 " $1}' | bash

PGPASSWORD=123 psql -U hackathon template1 -c 'drop database hackathon' -c 'create database hackathon'

PYTHONPATH=.

python service.py &