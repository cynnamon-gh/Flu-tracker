import os
import re

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

import db

app = Flask(__name__)
db.init_databases()

SYMPTOM_MAP = {
    "A": "cough",
    "B": "fever",
    "C": "congestion",
    "D": "sore throat",
    "E": "other",
}


@app.route("/sms", methods=["POST"])
def incoming_sms():
    phone = request.form["From"]
    body = request.form["Body"].strip()
    state_info = db.get_state(phone)
    state = state_info["state"]
    ctx = state_info["context"]
    pid = state_info["participant_id"]

    reply = _handle_message(phone, body, state, ctx, pid)

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)


def _handle_message(phone, body, state, ctx, pid):
    text = body.upper()

    # -- New user or someone texting SIGNUP --
    if state == "NEW" or text == "SIGNUP":
        existing = db.get_participant_by_phone(phone)
        if existing:
            return ("You're already signed up! "
                    "You'll get a weekly check-in text. Reply STOP anytime to opt out.")
        db.set_state(phone, "SIGNUP_UV")
        return ("Welcome to the Cold & Flu Tracker! "
                "Quick signup (4 questions).\n\n"
                "Do you regularly spend time in a space with a far-UV lamp? "
                "Reply YES or NO")

    # -- Signup flow --
    if state == "SIGNUP_UV":
        if text in ("YES", "Y"):
            db.set_state(phone, "SIGNUP_UV_HOURS", context={"uv": True})
            return ("How many hours per week do you spend in a space with a far-UV lamp? "
                    "Reply with a number (e.g. 8, 20, 40)")
        elif text in ("NO", "N"):
            db.set_state(phone, "SIGNUP_ZIP", context={"uv": False, "uv_hours": None})
            return "What's your zip code?"
        else:
            return "Please reply YES or NO - do you regularly spend time in a space with a far-UV lamp?"

    if state == "SIGNUP_UV_HOURS":
        hours = _parse_number(body)
        if hours is None or hours < 0:
            return "Please reply with a number of hours per week (e.g. 8, 20, 40)"
        ctx["uv_hours"] = hours
        db.set_state(phone, "SIGNUP_ZIP", context=ctx)
        return "What's your zip code?"

    if state == "SIGNUP_ZIP":
        zip_code = re.sub(r"\s+", "", body)
        if not re.match(r"^\d{5}(-\d{4})?$", zip_code):
            return "Please reply with a 5-digit US zip code (e.g. 90210)"
        ctx["zip"] = zip_code[:5]
        db.set_state(phone, "SIGNUP_HOUSEHOLD", context=ctx)
        return ("How many people regularly share your home or workspace? "
                "Reply with a number")

    if state == "SIGNUP_HOUSEHOLD":
        size = _parse_number(body)
        if size is None or size < 1:
            return "Please reply with a number (e.g. 1, 4, 12)"
        pid = db.create_participant(
            phone_number=phone,
            uv_exposure=ctx.get("uv", False),
            uv_hours=ctx.get("uv_hours"),
            zip_code=ctx.get("zip"),
            household_size=int(size),
        )
        db.set_state(phone, "IDLE", participant_id=pid)
        return ("You're all set! You'll get a weekly text asking how you're feeling. "
                "Reply STOP anytime to opt out. Thanks for participating!")

    # -- Weekly check-in flow --
    if state == "WEEKLY_SICK":
        if text in ("YES", "Y"):
            db.set_state(phone, "WEEKLY_SEVERITY", participant_id=pid, context={"sick": True})
            return "Sorry to hear that! How severe on a scale of 1-5? (1=barely noticeable, 5=knocked out)"
        elif text in ("NO", "N"):
            db.record_response(pid, sick=False)
            db.set_state(phone, "IDLE", participant_id=pid)
            return "Glad to hear it! Talk to you next week."
        else:
            return "Were you sick this past week? Reply YES or NO"

    if state == "WEEKLY_SEVERITY":
        severity = _parse_number(body)
        if severity is None or severity < 1 or severity > 5:
            return "Please reply with a number 1-5 (1=barely noticeable, 5=knocked out)"
        ctx["severity"] = int(severity)
        db.set_state(phone, "WEEKLY_SYMPTOMS", participant_id=pid, context=ctx)
        return ("What symptoms? Reply with the letters that apply:\n"
                "A) Cough\nB) Fever\nC) Congestion\nD) Sore throat\nE) Other\n\n"
                "e.g. reply AC for cough and congestion")

    if state == "WEEKLY_SYMPTOMS":
        letters = set(re.findall(r"[A-Ea-e]", body.upper()))
        if not letters:
            return ("Please reply with letters A-E for your symptoms:\n"
                    "A) Cough  B) Fever  C) Congestion  D) Sore throat  E) Other")
        symptoms = ",".join(sorted(SYMPTOM_MAP[l] for l in letters))
        db.record_response(pid, sick=True, severity=ctx.get("severity"), symptoms=symptoms)
        db.set_state(phone, "IDLE", participant_id=pid)
        return "Got it, hope you feel better soon! Talk to you next week."

    # -- IDLE or unknown state --
    if text == "STOP":
        if pid:
            # Twilio handles STOP automatically, but we also mark inactive
            from db import _connect, IDENTITY_DB
            with _connect(IDENTITY_DB) as conn:
                conn.execute("UPDATE participants SET active = 0 WHERE id = ?", (pid,))
            db.set_state(phone, "IDLE", participant_id=pid)
        return ""  # Twilio handles the actual STOP response

    if text == "STATUS":
        participant = db.get_participant_by_phone(phone)
        if participant:
            uv = "Yes" if participant["uv_exposure"] else "No"
            return f"You're active in the study. UV exposure: {uv}. Reply STOP to opt out."
        return "You're not currently signed up. Reply SIGNUP to join!"

    # Default for IDLE users who text something random
    participant = db.get_participant_by_phone(phone)
    if participant:
        return "Thanks for your message! You'll get your weekly check-in automatically. Reply STATUS to see your info."
    return "Hi! Reply SIGNUP to join the Cold & Flu Tracker study."


def _parse_number(text):
    try:
        return float(text.strip())
    except ValueError:
        return None


if __name__ == "__main__":
    app.run(debug=True, port=5000)
