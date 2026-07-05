import os
import random
import threading
import time
from typing import Any, Dict, List

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

SYSTEM_STATE = {
    "battery": 92,
    "batteryCharging": False,
    "storageUsed": 78,
    "storageTotal": 512,
    "network": "5G",
    "bootComplete": True,
    "installedApps": {"phone": True, "messages": True, "camera": True, "browser": True, "settings": True},
    "purchasedApps": {"phone": True, "messages": True, "camera": True, "browser": True, "settings": True},
    "activeApp": "home",
    "appStack": ["home"],
    "navigationMode": "home",
    "contactPermission": "pending",
    "cameraPreview": False,
    "callDialog": None,
    "lastUpdated": time.time(),
}

APP_CATALOG = [
    {
        "id": "phone",
        "name": "Phone",
        "category": "Communication",
        "icon": "◉",
        "accent": "#2f80ed",
        "description": "Reliable voice and video calling",
        "price": 0,
        "installed": True,
    },
    {
        "id": "messages",
        "name": "Messages",
        "category": "Communication",
        "icon": "✉",
        "accent": "#27ae60",
        "description": "Secure and fast messaging",
        "price": 0,
        "installed": True,
    },
    {
        "id": "camera",
        "name": "Camera",
        "category": "Media",
        "icon": "📷",
        "accent": "#f2994a",
        "description": "High quality photo and video",
        "price": 0,
        "installed": True,
    },
    {
        "id": "browser",
        "name": "Browser",
        "category": "Productivity",
        "icon": "🌐",
        "accent": "#9b51e0",
        "description": "Fast secure web browsing",
        "price": 0,
        "installed": True,
    },
    {
        "id": "settings",
        "name": "Settings",
        "category": "System",
        "icon": "⚙",
        "accent": "#4f4f4f",
        "description": "Complete device control",
        "price": 0,
        "installed": True,
    },
    {
        "id": "instagram",
        "name": "Instagram",
        "category": "Social",
        "icon": "📸",
        "accent": "#d946ef",
        "description": "Real social feed experience",
        "price": 4.99,
        "installed": False,
    },
    {
        "id": "whatsapp",
        "name": "WhatsApp",
        "category": "Communication",
        "icon": "💬",
        "accent": "#22c55e",
        "description": "Encrypted conversations and calls",
        "price": 5.99,
        "installed": False,
    },
    {
        "id": "netflix",
        "name": "Netflix",
        "category": "Entertainment",
        "icon": "🎬",
        "accent": "#ef4444",
        "description": "Premium streaming library",
        "price": 9.99,
        "installed": False,
    },
]

MESSAGES_CONTACTS = []
MESSAGE_THREADS: Dict[int, List[Dict[str, Any]]] = {
    1: [
        {"id": 101, "from": "Ayla", "text": "The launch review is ready.", "time": "09:15"},
        {"id": 102, "from": "Me", "text": "Great, I am preparing the final build.", "time": "09:16"},
    ]
}
APP_STREAMS = {
    "instagram": {
        "name": "Instagram",
        "status": "streaming",
        "buffer": 42,
        "items": ["New story from Maya", "Fresh reels from the design team"],
    },
    "whatsapp": {
        "name": "WhatsApp",
        "status": "syncing",
        "buffer": 31,
        "items": ["Encrypted sync complete", "Voice note received from Ece"],
    },
    "netflix": {
        "name": "Netflix",
        "status": "buffering",
        "buffer": 58,
        "items": ["Episode 4 is ready", "4K stream prepared"],
    },
}

CALL_STATE = {"active": False, "peer": None, "mode": "voice"}

GALLERY_ITEMS = [
    {
        "id": 1,
        "title": "Aurora skyline",
        "description": "Captured from the rooftop studio during golden hour.",
        "imageUrl": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80",
        "source": "unsplash",
        "likes": 128,
        "favorite": False,
    },
    {
        "id": 2,
        "title": "Neon city lights",
        "description": "A cinematic frame exploring motion and urban glow.",
        "imageUrl": "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?auto=format&fit=crop&w=900&q=80",
        "source": "unsplash",
        "likes": 94,
        "favorite": True,
    },
    {
        "id": 3,
        "title": "Studio portrait",
        "description": "Editorial light setup with a premium matte finish.",
        "imageUrl": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80",
        "source": "unsplash",
        "likes": 176,
        "favorite": False,
    },
]
GALLERY_ALBUMS = []


def simulate_battery() -> None:
    while True:
        time.sleep(60)
        if not SYSTEM_STATE["batteryCharging"]:
            SYSTEM_STATE["battery"] = max(0, SYSTEM_STATE["battery"] - 1)
        SYSTEM_STATE["lastUpdated"] = time.time()


threading.Thread(target=simulate_battery, daemon=True).start()


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/api/apps")
def get_apps():
    apps = []
    for item in APP_CATALOG:
        apps.append(
            {
                **item,
                "installed": SYSTEM_STATE["installedApps"].get(item["id"], False) or item.get("installed", False),
                "purchased": SYSTEM_STATE["purchasedApps"].get(item["id"], False),
            }
        )
    return jsonify({"apps": apps})


@app.get("/api/system/status")
def system_status():
    return jsonify(
        {
            "device": "Nefor One",
            "os": "NeforOS 1.0",
            "kernel": "Linux 6.6",
            "battery": SYSTEM_STATE["battery"],
            "batteryCharging": SYSTEM_STATE["batteryCharging"],
            "storageUsed": SYSTEM_STATE["storageUsed"],
            "storageTotal": SYSTEM_STATE["storageTotal"],
            "network": SYSTEM_STATE["network"],
            "bootComplete": True,
            "installedApps": sorted(SYSTEM_STATE["installedApps"].keys()),
            "navigationMode": SYSTEM_STATE["navigationMode"],
            "lastUpdated": SYSTEM_STATE["lastUpdated"],
        }
    )


@app.get("/api/weather")
def weather():
    city = request.args.get("city", "Istanbul")
    weather_data = fetch_weather(city)
    return jsonify(weather_data)


@app.get("/api/quote")
def quote():
    quote_data = fetch_quote()
    return jsonify(quote_data)


@app.get("/api/browser/search")
def browser_search():
    query = request.args.get("q", "")
    results = search_web(query)
    return jsonify({"status": "ok", "query": query, "results": results})


@app.get("/api/messages/contacts")
def messages_contacts():
    return jsonify({"permission": SYSTEM_STATE["contactPermission"], "contacts": MESSAGES_CONTACTS})


@app.post("/api/messages/contacts/permission")
def contact_permission():
    payload = request.get_json(silent=True) or {}
    granted = bool(payload.get("grant", False))
    SYSTEM_STATE["contactPermission"] = "granted" if granted else "denied"
    if granted:
        contacts = payload.get("contacts", []) or []
        for contact in contacts:
            if not any(item["name"] == contact.get("name") for item in MESSAGES_CONTACTS):
                MESSAGES_CONTACTS.append(
                    {
                        "id": len(MESSAGES_CONTACTS) + 1,
                        "name": contact.get("name", "Unknown"),
                        "phone": contact.get("phone", ""),
                        "status": "Online",
                        "lastSeen": "Just now",
                        "unread": 0,
                    }
                )
    return jsonify({"permission": SYSTEM_STATE["contactPermission"], "contacts": MESSAGES_CONTACTS})


@app.get("/api/messages/thread")
def messages_thread():
    contact_id = int(request.args.get("contactId", 1))
    messages = MESSAGE_THREADS.get(contact_id, [])
    return jsonify({"contactId": contact_id, "messages": messages})


@app.post("/api/messages/thread")
def post_message():
    payload = request.get_json(silent=True) or {}
    contact_id = int(payload.get("contactId", 1))
    message_text = payload.get("text", "")
    if not message_text:
        return jsonify({"status": "error", "message": "Empty message"}), 400
    thread = MESSAGE_THREADS.setdefault(contact_id, [])
    thread.append({"id": int(time.time()), "from": "Me", "text": message_text, "time": "now"})
    return jsonify({"status": "sent", "contactId": contact_id, "messages": thread})


@app.get("/api/app/stream")
def app_stream():
    app_id = request.args.get("appId", "instagram")
    stream = APP_STREAMS.get(app_id, {"name": app_id, "status": "idle", "buffer": 0, "items": []})
    return jsonify({"appId": app_id, **stream})


@app.get("/api/gallery")
def gallery():
    query = request.args.get("query", "latest").strip() or "latest"
    items = []
    for item in GALLERY_ITEMS:
        items.append(
            {
                **item,
                "title": f"{item['title']} · {query.title()}",
                "query": query,
            }
        )
    return jsonify({"status": "ok", "query": query, "items": items, "albums": GALLERY_ALBUMS})


@app.post("/api/gallery/upload")
def gallery_upload():
    title = request.form.get("title", "Untitled")
    description = request.form.get("description", "")
    image_url = request.form.get("imageUrl", "") or request.form.get("image_url", "")
    item = {
        "id": int(time.time()),
        "title": title,
        "description": description,
        "imageUrl": image_url or "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=900&q=80",
        "source": "user",
        "likes": 0,
        "favorite": False,
    }
    GALLERY_ITEMS.insert(0, item)
    return jsonify({"status": "uploaded", "item": item})


@app.post("/api/gallery/<int:item_id>/favorite")
def gallery_favorite(item_id: int):
    for item in GALLERY_ITEMS:
        if item["id"] == item_id:
            item["favorite"] = not item.get("favorite", False)
            item["likes"] = item.get("likes", 0) + (1 if item["favorite"] else -1)
            return jsonify({"status": "ok", "favorited": item["favorite"], "item": item})
    return jsonify({"status": "error", "message": "Item not found"}), 404


@app.post("/api/gallery/albums")
def gallery_albums():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "New Album").strip()
    if not name:
        return jsonify({"status": "error", "message": "Album name is required"}), 400
    album = {"id": len(GALLERY_ALBUMS) + 1, "name": name, "count": 0}
    GALLERY_ALBUMS.append(album)
    return jsonify({"status": "created", **album})


@app.get("/api/camera/status")
def camera_status():
    return jsonify(
        {
            "status": "ready",
            "mode": "ultra",
            "stabilization": "active",
            "zoom": "5x",
            "nightMode": True,
            "preview": SYSTEM_STATE["cameraPreview"],
        }
    )


@app.post("/api/camera/preview")
def camera_preview():
    SYSTEM_STATE["cameraPreview"] = True
    return jsonify({"status": "previewing", "preview": True})


@app.post("/api/camera/stop")
def camera_stop():
    SYSTEM_STATE["cameraPreview"] = False
    return jsonify({"status": "stopped", "preview": False})


@app.get("/api/calls/state")
def calls_state():
    return jsonify(CALL_STATE)


@app.post("/api/calls/start")
def start_call():
    payload = request.get_json(silent=True) or {}
    CALL_STATE["active"] = True
    CALL_STATE["peer"] = payload.get("peer", "Unknown")
    CALL_STATE["mode"] = payload.get("mode", "voice")
    SYSTEM_STATE["callDialog"] = {"peer": CALL_STATE["peer"], "mode": CALL_STATE["mode"]}
    return jsonify(CALL_STATE)


@app.post("/api/calls/end")
def end_call():
    CALL_STATE["active"] = False
    CALL_STATE["peer"] = None
    CALL_STATE["mode"] = "voice"
    SYSTEM_STATE["callDialog"] = None
    return jsonify(CALL_STATE)


@app.post("/api/apps/launch")
def launch_app():
    payload = request.get_json(silent=True) or {}
    app_id = payload.get("appId", "home")
    if app_id != "home":
        SYSTEM_STATE["activeApp"] = app_id
        SYSTEM_STATE["navigationMode"] = "app"
        if app_id not in SYSTEM_STATE["appStack"]:
            SYSTEM_STATE["appStack"].append(app_id)
        if app_id in APP_STREAMS:
            SYSTEM_STATE["storageUsed"] = min(SYSTEM_STATE["storageTotal"], SYSTEM_STATE["storageUsed"] + 2)
    else:
        SYSTEM_STATE["activeApp"] = "home"
        SYSTEM_STATE["appStack"] = ["home"]
        SYSTEM_STATE["navigationMode"] = "home"

    screen = {
        "type": app_id,
        "title": app_id.capitalize() if app_id != "home" else "Home",
        "content": f"{app_id.capitalize()} screen is now active.",
    }
    if app_id == "messages":
        screen = {
            "type": "messages",
            "title": "Messages",
            "content": "Your secure conversations and contacts are ready.",
        }
    elif app_id == "browser":
        screen = {
            "type": "browser",
            "title": "Browser",
            "content": "Search and discover information with premium results.",
        }
    elif app_id == "camera":
        screen = {
            "type": "camera",
            "title": "Camera",
            "content": "Ultra camera mode is ready for capture.",
        }
    elif app_id == "instagram":
        screen = {
            "type": "instagram",
            "title": "Instagram",
            "content": "Live social feed stream is active.",
        }
    elif app_id == "whatsapp":
        screen = {
            "type": "whatsapp",
            "title": "WhatsApp",
            "content": "Encrypted messages and calls are synced.",
        }
    elif app_id == "netflix":
        screen = {
            "type": "netflix",
            "title": "Netflix",
            "content": "Streaming service is buffering the next episode.",
        }

    return jsonify({"status": "opened", "activeApp": SYSTEM_STATE["activeApp"], "stack": SYSTEM_STATE["appStack"], "screen": screen})


@app.post("/api/store/purchase")
def purchase_app():
    payload = request.get_json(silent=True) or {}
    app_id = payload.get("appId")
    item = next((entry for entry in APP_CATALOG if entry["id"] == app_id), None)
    if not item:
        return jsonify({"purchased": False, "installed": False, "error": "App not found"}), 404
    SYSTEM_STATE["purchasedApps"][app_id] = True
    SYSTEM_STATE["installedApps"][app_id] = True
    return jsonify({"purchased": True, "installed": True, "appId": app_id, "price": item["price"]})


@app.post("/api/system/charge")
def charge_device():
    SYSTEM_STATE["batteryCharging"] = True
    SYSTEM_STATE["battery"] = min(100, SYSTEM_STATE["battery"] + 10)
    return jsonify({"battery": SYSTEM_STATE["battery"], "charging": True})


@app.post("/api/system/home")
def go_home():
    SYSTEM_STATE["activeApp"] = "home"
    SYSTEM_STATE["appStack"] = ["home"]
    SYSTEM_STATE["navigationMode"] = "home"
    return jsonify({"status": "home", "activeApp": SYSTEM_STATE["activeApp"]})


def search_web(query: str) -> List[Dict[str, Any]]:
    if not query:
        return []

    api_key = os.getenv("AIzaSyApVV7SgZsGR-h7CDc1cHbOBTUCtbkd_cc", "").strip()
    search_engine_id = os.getenv("GOOGLE_CX", "").strip()

    if api_key and search_engine_id:
        try:
            response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": api_key, "cx": search_engine_id, "q": query, "num": 5},
                timeout=8,
            )
            response.raise_for_status()
            payload = response.json()
            items = payload.get("items", [])
            if items:
                return [
                    {
                        "title": item.get("title", "Result"),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "google-custom-search",
                    }
                    for item in items[:5]
                ]
        except Exception:
            pass

    return [
        {
            "title": f"{query} — Research overview",
            "url": f"https://www.google.com/search?q={query}",
            "snippet": f"Live Google search is configured when GOOGLE_API_KEY and GOOGLE_CX are provided.",
            "source": "fallback",
        },
        {
            "title": f"Latest updates for {query}",
            "url": f"https://www.google.com/search?q={query}",
            "snippet": "Fallback result for local prototype until real Google credentials are supplied.",
            "source": "fallback",
        },
    ]


def fetch_weather(city: str) -> Dict[str, Any]:
    try:
        geo_resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=5,
        )
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()
        if not geo_data.get("results"):
            raise ValueError("No geocoding results")

        place = geo_data["results"][0]
        forecast_resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,weather_code",
                "timezone": "auto",
            },
            timeout=5,
        )
        forecast_resp.raise_for_status()
        forecast_data = forecast_resp.json()
        current = forecast_data.get("current", {})
        return {
            "city": place.get("name", city),
            "country": place.get("country", "Unknown"),
            "temperature": current.get("temperature_2m", 21),
            "weatherCode": current.get("weather_code", 0),
            "status": "ok",
        }
    except Exception:
        return {
            "city": city,
            "country": "Local",
            "temperature": 22,
            "weatherCode": 1,
            "status": "fallback",
        }


def fetch_quote() -> Dict[str, Any]:
    try:
        resp = requests.get("https://api.quotable.io/random", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return {"content": data.get("content", "Design with intention."), "author": data.get("author", "NeforOS")}
    except Exception:
        return {"content": "Precision beats noise.", "author": "NeforOS"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
