from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from typing import Optional, List
import requests

API_KEY = "mysecretkey"  # Change this to a secure value
DATA_PATH = "data/emotions_data.json"

app = FastAPI(title="EmotiVision Content Personalization API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_emotion_history():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "sessions" in data:
                    # Support for old format
                    return data["sessions"]
            except Exception:
                return []
    return []

@app.middleware("http")
async def check_api_key(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        key = request.headers.get("x-api-key")
        if key != API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Invalid API key"})
    return await call_next(request)

@app.get("/api/latest_emotion")
def latest_emotion():
    history = load_emotion_history()
    if not history:
        raise HTTPException(status_code=404, detail="No emotion data found")
    latest = history[-1]
    return {"emotion": latest.get("emotion"), "confidence": latest.get("confidence"), "age": latest.get("age"), "timestamp": latest.get("timestamp")}

@app.get("/api/emotion_trend")
def emotion_trend():
    history = load_emotion_history()
    if not history:
        raise HTTPException(status_code=404, detail="No emotion data found")
    trend = {}
    for entry in history:
        emo = entry.get("emotion")
        if emo:
            trend[emo] = trend.get(emo, 0) + 1
    return {"trend": trend}

@app.get("/api/age_distribution")
def age_distribution():
    history = load_emotion_history()
    if not history:
        raise HTTPException(status_code=404, detail="No emotion data found")
    ages = {}
    for entry in history:
        age = entry.get("age")
        if age:
            ages[age] = ages.get(age, 0) + 1
    return {"age_distribution": ages}

@app.post("/api/push_event")
def push_event(event: dict = Body(...)):
    # Append event to data/emotions_data.json
    history = load_emotion_history()
    history.append(event)
    with open(DATA_PATH, "w") as f:
        json.dump(history, f, indent=2)
    return {"status": "success", "event": event}

@app.get("/api/events")
def get_events(date: Optional[str] = None, user: Optional[str] = None) -> List[dict]:
    history = load_emotion_history()
    if date:
        history = [e for e in history if e.get("timestamp", "").startswith(date)]
    if user:
        history = [e for e in history if e.get("username") == user]
    return history

@app.post("/api/webhook_test")
def webhook_test(webhook_url: str = Body(...), event: dict = Body(...)):
    try:
        resp = requests.post(webhook_url, json=event, timeout=5)
        return {"status": "sent", "response_code": resp.status_code}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# To run: uvicorn api:app --reload 