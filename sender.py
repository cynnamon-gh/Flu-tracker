"""
Weekly text sender - run this on a schedule (e.g. Sunday morning via cron/Task Scheduler).

Usage:
    python sender.py
"""
import os

from dotenv import load_dotenv
load_dotenv()

from twilio.rest import Client

import db

db.init_databases()


def send_weekly_texts():
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    from_number = os.environ["TWILIO_PHONE_NUMBER"]
    client = Client(account_sid, auth_token)

    participants = db.get_all_active_participants()
    sent = 0
    errors = 0

    for p in participants:
        phone = p["phone_number"]
        pid = p["id"]
        try:
            client.messages.create(
                body="Hi! Quick weekly check-in: were you sick this past week? Reply YES or NO",
                from_=from_number,
                to=phone,
            )
            db.set_state(phone, "WEEKLY_SICK", participant_id=pid)
            sent += 1
        except Exception as e:
            print(f"Failed to send to participant {pid}: {e}")
            errors += 1

    print(f"Sent {sent} texts, {errors} errors")


if __name__ == "__main__":
    send_weekly_texts()
