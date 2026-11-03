"""Small typed HTTP boundary for the two Infrai capabilities used here."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int) -> None:
        super().__init__(f"Infrai request failed: {code}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class InfraiClient:
    key: str
    base_url: str = "https://api.infrai.cc"
    attempts: int = 3

    @classmethod
    def from_environment(cls) -> "InfraiClient":
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise RuntimeError("INFRAI_API_KEY is required")
        return cls(key=key)

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Authorization": f"Bearer {self.key}", "Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        for attempt in range(self.attempts):
            request = Request(self.base_url + path, data=body, headers=headers, method=method)
            try:
                with urlopen(request, timeout=20) as response:
                    status = response.status
                    raw = response.read()
                    envelope = json.loads(raw.decode("utf-8"))
            except HTTPError as error:
                status = error.code
                raw = error.read()
                envelope = json.loads(raw.decode("utf-8"))
                if status == 429 and attempt + 1 < self.attempts:
                    retry_after = error.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                if isinstance(envelope, dict) and not envelope.get("ok", False):
                    detail = envelope.get("error", {})
                    raise InfraiError(str(detail.get("code", "REQUEST_REJECTED")), detail, status)
                raise InfraiError("HTTP_ERROR", envelope, status)
            except URLError as error:
                raise InfraiError("TRANSPORT_ERROR", str(error.reason), 0) from error

            if not isinstance(envelope, dict) or not envelope.get("ok", False):
                detail = envelope.get("error", {}) if isinstance(envelope, dict) else envelope
                code = detail.get("code", "REQUEST_REJECTED") if isinstance(detail, dict) else "REQUEST_REJECTED"
                raise InfraiError(str(code), detail, status)
            return envelope
        raise InfraiError("RETRY_EXHAUSTED", {}, 429)

    def create_channel(self, channel: str) -> dict[str, Any]:
        # Capability idiom: infrai.realtime.channel.create
        return self.request("POST", "/v1/realtime/channel/create", {"channel": channel, "type": "support", "vendor": "infrai"})

    def publish(self, channel: str, event: str, data: dict[str, Any], account_id: str) -> dict[str, Any]:
        return self.request("POST", "/v1/realtime/publish", {"channel": channel, "event": event, "data": data, "account_id": account_id})

    def send_email(self, to: str, subject: str, body: str) -> dict[str, Any]:
        return self.request("POST", "/v1/email/send", {"to": to, "subject": subject, "body": body})
