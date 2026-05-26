def test_create_user(client):
    response = client.post("/users/", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_create_user_duplicate_username(client, sample_user):
    response = client.post("/users/", json={
        "username": sample_user["username"],
        "email": "different@example.com",
        "password": "password123",
    })
    assert response.status_code == 409


def test_create_user_duplicate_email(client, sample_user):
    response = client.post("/users/", json={
        "username": "different",
        "email": sample_user["email"],
        "password": "password123",
    })
    assert response.status_code == 409


def test_create_user_short_password(client):
    response = client.post("/users/", json={
        "username": "bob",
        "email": "bob@example.com",
        "password": "short",
    })
    assert response.status_code == 422


def test_create_user_invalid_email(client):
    response = client.post("/users/", json={
        "username": "charlie",
        "email": "not-an-email",
        "password": "password123",
    })
    assert response.status_code == 422


def test_list_users(client, sample_user):
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["username"] == sample_user["username"]


def test_get_user(client, sample_user):
    response = client.get(f"/users/{sample_user['id']}")
    assert response.status_code == 200
    assert response.json()["username"] == sample_user["username"]


def test_get_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == 404
