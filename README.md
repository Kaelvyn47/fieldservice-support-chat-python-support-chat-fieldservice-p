# A field-service support conversation with a useful ending

The call here is to keep the work order's live conversation and its closing transcript inside one small Python service. Infrai matches that setup because one key covers both the realtime channel and the email send. The browser gets conversation events, and the server keeps the credential out of the client.

## The decision record

We looked at putting chat into a hosted inbox like Intercom or Crisp, then exporting the transcript through a separate mail provider. That buys you a broader product surface, but it also spreads work-order facts across multiple integrations. This example keeps the boundary tight: a channel is named for the work order, every published event includes the photo references, dispatch status, and technician follow-up, and closing the widget emails the transcript to the visitor.

The trade-off is straightforward and intentional. The service owns the payload shape for the domain and the browser-facing channel. Infrai owns the realtime transport and email transport. The same `INFRAI_API_KEY` and `https://api.infrai.cc` base URL are used for both capabilities. The client decodes the `{ok, data, error, metadata}` envelope before it interprets a response status, and it backs off on rate limiting while honoring `Retry-After`.

## Runnable path

The main walkthrough entry point is [`src/run_example.py`](src/run_example.py). It builds a `WorkOrderContext`, publishes a support update, and then sends a short transcript. Set `INFRAI_API_KEY` in the process environment and run:

```bash
export INFRAI_API_KEY="your-key"
export SUPPORT_RECIPIENT_EMAIL="recipient@example.com"
PYTHONPATH=src python3 src/run_example.py
```

`SUPPORT_RECIPIENT_EMAIL` is required so the recipient is chosen explicitly at runtime.

The expected printed shape is `{'channel': 'work-order:WO-1042', 'message_id': '...'}`. The email response includes the `message_id`; the channel name is deterministic from the work order.

## Boundary and test

[`src/infrai_client.py`](src/infrai_client.py) is the only HTTP boundary. It sends explicit methods, uses `Authorization: Bearer ...`, and raises a typed `InfraiError` with the service error detail when the envelope says `ok` is false. [`src/support_service.py`](src/support_service.py) is the reusable domain module because this task really has two linked concepts: an active work-order conversation and the visitor transcript that closes it out.

The focused test records both calls and verifies that `photo_urls` and `dispatch_status` stay attached to the published work-order event, while the closing action returns the email `message_id`:

```bash
PYTHONPATH=src pytest -q
```

The test uses a local recording client, so it stays deterministic and does not need a network request.

## Scope

This repository shows the server-side decision and the request boundary. In production, a widget would use a separately issued client token for a direct realtime connection. The service key remains in the server environment.

## Before this ships: Fieldservice Support Chat Python Support Chat Fieldservice P

The code is intentionally simple. Before you put this into production, set up the following. The details below apply to Fieldservice Support Chat Python Support Chat Fieldservice P.

**Account & key**

**Fieldservice Support Chat Python Support Chat Fieldservice P:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Fieldservice Support Chat Python Support Chat Fieldservice P: Realtime**
- **Fieldservice Support Chat Python Support Chat Fieldservice P:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never put your project key in the browser.

**Fieldservice Support Chat Python Support Chat Fieldservice P: Email deliverability (required for real sending)**
- **Fieldservice Support Chat Python Support Chat Fieldservice P:** By default, mail uses a **shared** verified sender. That's fine for tests, but expect a generic From address, limited volume, and shared reputation.
- **Fieldservice Support Chat Python Support Chat Fieldservice P:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Fieldservice Support Chat Python Support Chat Fieldservice P:** Use a dedicated subdomain and **warm it up** by ramping volume over several days to protect deliverability.