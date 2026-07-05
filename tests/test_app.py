import pytest
from app import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"NeforOS" in response.data


def test_apps_endpoint_returns_catalog(client):
    response = client.get("/api/apps")
    assert response.status_code == 200
    payload = response.get_json()
    assert "apps" in payload
    assert any(item["name"] == "Phone" for item in payload["apps"])


def test_system_status_endpoint_returns_device_info(client):
    response = client.get("/api/system/status")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["device"] == "Nefor One"
    assert payload["bootComplete"] is True
    assert 0 <= payload["battery"] <= 100


def test_store_purchase_updates_inventory(client):
    response = client.post("/api/store/purchase", json={"appId": "instagram"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["purchased"] is True
    assert payload["installed"] is True


def test_browser_search_returns_results(client):
    response = client.get("/api/browser/search?q=python")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert len(payload["results"]) >= 1
    assert "title" in payload["results"][0]
    assert "url" in payload["results"][0]


def test_messages_contacts_endpoint_returns_permission_state(client):
    response = client.get("/api/messages/contacts")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["permission"] in {"pending", "granted", "denied"}
    assert isinstance(payload["contacts"], list)


def test_app_launch_endpoint_sets_active_app(client):
    response = client.post("/api/apps/launch", json={"appId": "messages"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["activeApp"] == "messages"
    assert payload["status"] == "opened"
    assert payload["screen"]["type"] == "messages"


def test_system_status_includes_navigation_state(client):
    response = client.get("/api/system/status")
    assert response.status_code == 200
    payload = response.get_json()
    assert "navigationMode" in payload
    assert payload["navigationMode"] in {"home", "app"}


def test_messages_thread_endpoint_returns_conversation(client):
    response = client.get("/api/messages/thread?contactId=1")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["contactId"] == 1
    assert len(payload["messages"]) >= 1


def test_call_flow_endpoint_can_start_and_end_call(client):
    start_response = client.post("/api/calls/start", json={"peer": "Ayla", "mode": "video"})
    assert start_response.status_code == 200
    start_payload = start_response.get_json()
    assert start_payload["active"] is True

    end_response = client.post("/api/calls/end")
    assert end_response.status_code == 200
    end_payload = end_response.get_json()
    assert end_payload["active"] is False


def test_messages_contacts_permission_flow_creates_contacts(client):
    response = client.post(
        "/api/messages/contacts/permission",
        json={"grant": True, "contacts": [{"name": "Ece", "phone": "+90 555 123 45 67"}]},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["permission"] == "granted"

    contacts_response = client.get("/api/messages/contacts")
    assert contacts_response.status_code == 200
    contacts_payload = contacts_response.get_json()
    assert contacts_payload["permission"] == "granted"
    assert any(contact["name"] == "Ece" for contact in contacts_payload["contacts"])


def test_gallery_endpoint_returns_real_media_items(client):
    response = client.get("/api/gallery?query=technology")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["query"] == "technology"
    assert len(payload["items"]) >= 1
    assert "title" in payload["items"][0]
    assert "imageUrl" in payload["items"][0]


def test_gallery_upload_favorite_and_album_flow(client):
    upload_response = client.post(
        "/api/gallery/upload",
        data={"title": "Night City", "description": "Uploaded from the shell", "imageUrl": "https://example.com/shot.jpg"},
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 200
    upload_payload = upload_response.get_json()
    assert upload_payload["status"] == "uploaded"
    item_id = upload_payload["item"]["id"]

    favorite_response = client.post(f"/api/gallery/{item_id}/favorite")
    assert favorite_response.status_code == 200
    favorite_payload = favorite_response.get_json()
    assert favorite_payload["favorited"] is True

    album_response = client.post("/api/gallery/albums", json={"name": "Travel"})
    assert album_response.status_code == 200
    album_payload = album_response.get_json()
    assert album_payload["name"] == "Travel"


def test_weather_endpoint_returns_data(client):
    response = client.get("/api/weather?city=Istanbul")
    assert response.status_code == 200
    payload = response.get_json()
    assert "temperature" in payload
    assert "city" in payload
