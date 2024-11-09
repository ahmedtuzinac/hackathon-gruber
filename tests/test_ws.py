import pytest
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient

from config.application import manager, service as app


client = TestClient(app)

def test_websocket():
    with client.websocket_connect("/ws/123") as websocket:
        websocket.send_text("Hello, WebSocket!")
        response = websocket.receive_text()
        assert response == "Message text was: Hello, WebSocket!"

        response = websocket.receive_text()
        assert response == "Client #123 says: Hello, WebSocket!"
