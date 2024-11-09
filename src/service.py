import uvicorn
from fastapi import FastAPI
import importlib

from config.application import get_service

service: FastAPI = get_service()
importlib.import_module('api')

if __name__ == '__main__':
    uvicorn.run(service, host='0.0.0.0', port=8000)
