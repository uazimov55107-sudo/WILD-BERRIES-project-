import json
import os
import threading
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
LOG_FILE = BASE / "events.jsonl"

class RateLimiter:
    def __init__(self, limit=5, window=60):
        self.limit = limit
        self.window = window
        self.attempts = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key):
        now = time.monotonic()
        with self.lock:
            queue = self.attempts[key]
            while queue and now - queue[0] >= self.window:
                queue.popleft()
            if len(queue) >= self.limit:
                return False
            queue.append(now)
            return True

class SecurityAgent:
    ALLOWED_EVENTS = {
        "LOGIN_SUCCESS", "LOGIN_FAILED", "LOGIN_RATE_LIMITED",
        "ACCESS_DENIED", "SUSPICIOUS_REQUEST", "APP_SECURITY_CHECK"
    }

    def __init__(self):
        self.login_limiter = RateLimiter()

    def allow_login_attempt(self, identifier):
        return self.login_limiter.allow(identifier)

    def record_event(self, code, severity="INFO"):
        if code not in self.ALLOWED_EVENTS:
            raise ValueError("Noma'lum xavfsizlik hodisasi")
        if severity not in {"INFO", "WARNING", "CRITICAL"}:
            raise ValueError("Noto'g'ri severity")

        event = {
            "id": str(uuid.uuid4()),
            "time": datetime.now(timezone.utc).isoformat(),
            "event": code,
            "severity": severity
        }

        BASE.mkdir(parents=True, exist_ok=True)
        fd = os.open(LOG_FILE, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as log:
            log.write(json.dumps(event) + "\n")
        return event
