import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///./test.db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from main import app
from database import get_db, Base

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_post():
    response = client.post("/posts", json={
        "title": "My First Post",
        "content": "Hello world content",
        "tag": "general"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Post"
    assert data["tag"] == "general"
    assert "id" in data


def test_get_posts_empty():
    response = client.get("/posts")
    assert response.status_code == 200
    assert response.json() == []


def test_get_posts():
    client.post("/posts", json={"title": "Post 1", "content": "Content 1"})
    client.post("/posts", json={"title": "Post 2", "content": "Content 2"})
    response = client.get("/posts")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_post_by_id():
    create_res = client.post("/posts", json={"title": "Detail Post", "content": "Detail content"})
    post_id = create_res.json()["id"]
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Detail Post"


def test_get_post_not_found():
    response = client.get("/posts/9999")
    assert response.status_code == 404


def test_update_post():
    create_res = client.post("/posts", json={"title": "Old Title", "content": "Old content"})
    post_id = create_res.json()["id"]
    response = client.put(f"/posts/{post_id}", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"
    assert response.json()["content"] == "Old content"


def test_delete_post():
    create_res = client.post("/posts", json={"title": "To Delete", "content": "bye"})
    post_id = create_res.json()["id"]
    response = client.delete(f"/posts/{post_id}")
    assert response.status_code == 204
    get_res = client.get(f"/posts/{post_id}")
    assert get_res.status_code == 404
