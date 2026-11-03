"""Field-service support workflow: live conversation first, transcript second."""

from __future__ import annotations

from dataclasses import dataclass

from infrai_client import InfraiClient


@dataclass(frozen=True)
class WorkOrderContext:
    work_order_id: str
    customer_email: str
    photo_urls: tuple[str, ...]
    dispatch_status: str
    technician_follow_up: str


@dataclass(frozen=True)
class TranscriptResult:
    channel: str
    message_id: str


def publish_support_update(client: InfraiClient, context: WorkOrderContext, message: str, account_id: str) -> str:
    """Put the operational facts beside the human message so every listener sees one state."""
    channel = f"work-order:{context.work_order_id}"
    client.create_channel(channel)
    client.publish(
        channel,
        "support.message",
        {
            "message": message,
            "work_order_id": context.work_order_id,
            "photo_urls": list(context.photo_urls),
            "dispatch_status": context.dispatch_status,
            "technician_follow_up": context.technician_follow_up,
        },
        account_id,
    )
    return channel


def email_transcript(client: InfraiClient, context: WorkOrderContext, transcript: str) -> TranscriptResult:
    """Send the same conversation to the visitor when the widget closes."""
    result = client.send_email(
        context.customer_email,
        f"Support transcript for work order {context.work_order_id}",
        transcript,
    )
    data = result.get("data", {})
    return TranscriptResult(channel=f"work-order:{context.work_order_id}", message_id=str(data["message_id"]))
