import os
from datetime import datetime, timezone

from appwrite.client import Client
from sqlalchemy import create_engine, text


DB_URL = os.environ["DB_URL"]
HEARTBEAT_SECRET = os.environ["HEARTBEAT_SECRET"]


engine = create_engine(
    DB_URL,
    pool_pre_ping=True
)


def main(context):
    try:
        body = context.req.body_json

        printer_id = body.get("printer_id")
        secret = body.get("secret")

        if not printer_id:
            return context.res.json(
                {"status": "error", "message": "printer_id missing"},
                400
            )

        if secret != HEARTBEAT_SECRET:
            return context.res.json(
                {"status": "error", "message": "Unauthorized"},
                401
            )

        now = datetime.now(timezone.utc)

        with engine.begin() as conn:
            result = conn.execute(
                text("""
                    UPDATE printer
                    SET "LAST_PING" = :last_ping
                    WHERE "PRINTER_ID" = :printer_id
                    RETURNING "PRINTER_ID"
                """),
                {
                    "last_ping": now,
                    "printer_id": printer_id
                }
            )

            if result.fetchone() is None:
                return context.res.json(
                    {
                        "status": "error",
                        "message": "Unknown printer"
                    },
                    404
                )

        return context.res.json({
            "status": "ok",
            "printer_id": printer_id,
            "last_ping": now.isoformat()
        })

    except Exception as e:
        return context.res.json({
            "status": "error",
            "message": str(e)
        }, 500)
