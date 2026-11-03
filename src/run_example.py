from infrai_client import InfraiClient
from support_service import WorkOrderContext, email_transcript, publish_support_update
import os


def main() -> None:
    recipient = os.environ.get("SUPPORT_RECIPIENT_EMAIL")
    if not recipient:
        raise RuntimeError("SUPPORT_RECIPIENT_EMAIL is required")
    context = WorkOrderContext(
        work_order_id="WO-1042",
        customer_email=recipient,
        photo_urls=("https://example.com/photos/panel.jpg",),
        dispatch_status="technician_assigned",
        technician_follow_up="Call the customer after the replacement part arrives.",
    )
    client = InfraiClient.from_environment()
    channel = publish_support_update(client, context, "I attached the panel photo for the technician.", "field-service-demo")
    result = email_transcript(client, context, "Visitor: I attached the panel photo for the technician.")
    print({"channel": channel, "message_id": result.message_id})


if __name__ == "__main__":
    main()
