from typing import Any

from support_service import WorkOrderContext, email_transcript, publish_support_update


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Any]] = []

    def create_channel(self, channel: str) -> dict[str, Any]:
        self.calls.append(("create_channel", channel))
        return {"ok": True}

    def publish(self, channel: str, event: str, data: dict[str, Any], account_id: str) -> dict[str, Any]:
        self.calls.append(("publish", (channel, event, data, account_id)))
        return {"ok": True}

    def send_email(self, to: str, subject: str, body: str) -> dict[str, Any]:
        self.calls.append(("send_email", (to, subject, body)))
        return {"ok": True, "data": {"message_id": "msg-1042"}}


def test_work_order_facts_follow_the_conversation_to_email() -> None:
    context = WorkOrderContext("WO-1042", "visitor@example.com", ("photo.jpg",), "assigned", "Call after delivery.")
    client = RecordingClient()

    channel = publish_support_update(client, context, "Photo received.", "acct-field-service")
    emailed = email_transcript(client, context, "Photo received.")

    assert channel == "work-order:WO-1042"
    published = client.calls[1][1]
    assert published[2]["photo_urls"] == ["photo.jpg"]
    assert published[2]["dispatch_status"] == "assigned"
    assert emailed.message_id == "msg-1042"
    assert client.calls[2][0] == "send_email"
