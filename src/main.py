import os
from datetime import datetime, timezone
from urllib.parse import urlparse

from sqlalchemy import create_engine, text

DB_URL = os.environ["DB_URL"]
HEARTBEAT_SECRET = os.environ["HEARTBEAT_SECRET"]

engine = create_engine(DB_URL, pool_pre_ping=True)


def main(context):
    try:
        body = context.req.body_json

        printer_id = body.get("printer_id")
        tunnel_url = body.get("tunnel_url")
        secret = body.get("secret")

        if not printer_id:
            return context.res.json(
                {"status": "error", "message": "printer_id missing"}, 400
            )

        if not tunnel_url:
            return context.res.json(
                {"status": "error", "message": "tunnel_url missing"}, 400
            )

        if secret != HEARTBEAT_SECRET:
            return context.res.json(
                {"status": "error", "message": "Unauthorized"}, 401
            )

        # Validate Cloudflare Quick Tunnel URL
        parsed = urlparse(tunnel_url)

        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or not parsed.hostname.endswith(".trycloudflare.com")
        ):
            return context.res.json(
                {"status": "error", "message": "Invalid tunnel URL"}, 400
            )

        now = datetime.now(timezone.utc)

        with engine.begin() as conn:
            result = conn.execute(
                text("""
                    UPDATE printer
                    SET
                        "LAST_PING" = :last_ping,
                        "ENDPOINT_URL" = :tunnel_url
                    WHERE "PRINTER_ID" = :printer_id
                    RETURNING "PRINTER_ID"
                """),
                {
                    "last_ping": now,
                    "tunnel_url": tunnel_url,
                    "printer_id": printer_id
                }
            )

            if result.fetchone() is None:
                return context.res.json(
                    {"status": "error", "message": "Unknown printer"}, 404
                )

        return context.res.json({
            "status": "ok",
            "printer_id": printer_id,
            "tunnel_url": tunnel_url,
            "last_ping": now.isoformat()
        })

    except Exception as e:
        return context.res.json(
            {"status": "error", "message": str(e)}, 500
        )
