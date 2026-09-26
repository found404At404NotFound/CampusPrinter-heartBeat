import os
from sqlalchemy import create_engine, text

DB_URL = os.environ["DB_URL"]

engine = create_engine(
    DB_URL.replace("postgresql://", "postgresql+psycopg2://"),
    pool_pre_ping=True
)

# Origins allowed to call this function from a browser.
# Add every origin your frontend is served from.
ALLOWED_ORIGINS = {
    "https://printer.mangojam.me",
    "https://mangojam.me",
    "http://127.0.0.1:5005",
    "http://localhost:5173",
    "https://doctrine-hunting-hosting-bryant.trycloudflare.com"
}


def _cors_headers(origin: str | None) -> dict:
    """Return CORS headers for the given request Origin, if allowed."""
    if origin and origin in ALLOWED_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true",
            "Vary": "Origin",
        }
    # No match — return empty. Browser will block; that's correct.
    return {}


def main(context):
    # Figure out who's calling
    origin = None
    try:
        # Appwrite exposes headers as a dict on context.req.headers
        origin = context.req.headers.get("origin") or context.req.headers.get("Origin")
    except Exception:
        pass

    cors = _cors_headers(origin)

    # Handle CORS preflight
    if context.req.method == "OPTIONS":
        return context.res.text("", 204, cors)

    try:
        with engine.begin() as conn:
            result = conn.execute(
                text("""
                    SELECT
                        "PRINTER_ID",
                        "PRINTER_NAME",
                        "BLOCK",
                        "PRINTER_LOCATION",
                        "ENDPOINT_URL",
                        "AVAILABLE"
                    FROM printer
                    ORDER BY "PRINTER_ID"
                """)
            )

            printers = [
                {
                    "printer_id": row[0],
                    "printer_name": row[1],
                    "block": row[2],
                    "location": row[3],
                    "endpoint_url": row[4],
                    "available": row[5],
                }
                for row in result.fetchall()
            ]

        return context.res.json(
            {"status": "ok", "printers": printers},
            200,
            cors,
        )

    except Exception as e:
        return context.res.json(
            {"status": "error", "message": str(e)},
            500,
            cors,
        )



