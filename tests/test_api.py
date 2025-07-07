import pytest
from app import app, db, User, Game
import json


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SECRET_KEY"] = "testsecretkey"

    with app.app_context():
        db.create_all()
        new_user = User(name="TestUser", email="test@example.com")
        new_user.set_password("1234")
        db.session.add(new_user)
        db.session.commit()

        with app.test_client() as client:
            yield client


@pytest.fixture
def token(client):
    response = client.post(
        "/auth", json={"email": "test@example.com", "password": "1234"}
    )
    data = json.loads(response.data)
    return data["token"]


# ======= Testes =======


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_login_success(client):
    response = client.post(
        "/auth", json={"email": "test@example.com", "password": "1234"}
    )
    assert response.status_code == 200
    assert "token" in response.json


def test_login_failure(client):
    response = client.post(
        "/auth", json={"email": "wrong@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert response.json["error"] == "Credenciais inválidas!"


def test_create_game_success(client, token):
    response = client.post(
        "/game",
        json={"title": "Minecraft", "year": 2012, "price": 20},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert "id" in response.json


def test_list_games(client, token):
    client.post(
        "/game",
        json={"title": "Minecraft", "year": 2012, "price": 20},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get("/games", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["title"] == "Minecraft"


def test_create_game_invalid_data(client, token):
    response = client.post(
        "/game",
        json={"title": "", "year": 1800, "price": -50},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "errors" in response.json


def test_unauthorized_access(client):
    response = client.get("/games")
    assert response.status_code == 401
    assert response.json["error"] == "Token não fornecido ou inválido"
