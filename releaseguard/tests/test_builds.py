def test_empty_build_list(client):
    response = client.get("/builds")

    assert response.status_code == 200
    assert response.json() == []

def test_get_build(client):
    response = client.post("/builds", json={"name": "build-01", "version": "01", "description": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "build-01"
    assert response.json()["version"] == "01"
    assert response.json()["description"] == "test"

    response = client.get("/builds")
    assert response.status_code == 200
    builds = response.json()
    assert len(builds) == 1
    assert builds[0]["name"] == "build-01"
    assert builds[0]["version"] == "01"
    assert builds[0]["description"] == "test"
