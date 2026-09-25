import os
from sqlalchemy import create_engine, text

DB_URL = os.environ["DB_URL"]

engine = create_engine(DB_URL, pool_pre_ping=True)


def main(context):
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
                    "available": row[5]
                }
                for row in result.fetchall()
            ]

        return context.res.json({
            "status": "ok",
            "printers": printers
        })

    except Exception as e:
        return context.res.json({
            "status": "error",
            "message": str(e)
        }, 500)
