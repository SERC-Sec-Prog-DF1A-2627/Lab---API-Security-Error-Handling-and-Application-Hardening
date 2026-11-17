"""Fixtures are setup helpers supplied automatically to test functions."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from app import create_app
from lab_client import sign_in


@pytest.fixture
def app(tmp_path):
    # A fresh temporary database for EVERY test prevents tests contaminating
    # each other or changing the browser's instance/notes.sqlite database.
    return create_app({"TESTING":True, "DATABASE":str(tmp_path/"test.sqlite"),
                       "SECRET_KEY":"test-only-key", "SESSION_COOKIE_SECURE":False})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def login(client):
    return lambda username="editor": sign_in(client, username)
