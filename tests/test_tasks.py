def test_create_task(client, sample_user):
    response = client.post(f"/tasks/?owner_id={sample_user['id']}", json={
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "priority": 3,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["priority"] == 3
    assert data["completed"] is False
    assert data["owner_id"] == sample_user["id"]


def test_create_task_invalid_owner(client):
    response = client.post("/tasks/?owner_id=999", json={
        "title": "Orphan task",
    })
    assert response.status_code == 404


def test_list_tasks(client, sample_task, sample_user):
    client.post(f"/tasks/?owner_id={sample_user['id']}", json={
        "title": "Second task",
        "priority": 1,
    })
    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert data["items"][0]["title"] == "Second task"


def test_list_tasks_filter_completed(client, sample_user):
    client.post(f"/tasks/?owner_id={sample_user['id']}", json={"title": "Done task"})
    response = client.get("/tasks/?completed=false")
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert item["completed"] is False


def test_get_task(client, sample_task):
    response = client.get(f"/tasks/{sample_task['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == sample_task["title"]


def test_get_task_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_update_task(client, sample_task):
    response = client.patch(f"/tasks/{sample_task['id']}", json={
        "title": "Updated title",
        "completed": True,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["completed"] is True


def test_update_task_not_found(client):
    response = client.patch("/tasks/999", json={"title": "Nope"})
    assert response.status_code == 404


def test_delete_task(client, sample_task):
    response = client.delete(f"/tasks/{sample_task['id']}")
    assert response.status_code == 204

    response = client.get(f"/tasks/{sample_task['id']}")
    assert response.status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404
