"""Unit tests for the sample Flask application."""
from app.app import app


def test_index():
    client = app.test_client()
    res = client.get("/")
    assert res.status_code == 200
    assert b"Meenakshi DevOps Lab" in res.data


def test_health():
    client = app.test_client()
    res = client.get("/health")
    assert res.status_code == 200
    assert b"UP" in res.data


def test_info():
    client = app.test_client()
    res = client.get("/info")
    assert res.status_code == 200
    assert b"Meenakshi" in res.data
