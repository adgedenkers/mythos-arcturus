#!/usr/bin/env python3
"""
Mythos SMS - Send texts via AT&T email-to-SMS gateway

Usage:
    sms "Hey dinner is ready"
    sms "Test" --to both
    sms "Long message here" --to seraphe --mms
"""

import smtplib, argparse, sys, os, json, logging
from email.message import EmailMessage
from datetime import datetime, timezone

CONTACTS = {
    "seraphe": {"name": "Seraphe", "number": "6073162604", "sms": "txt.att.net", "mms": "mms.att.net"},
    "kataurel": {"name": "Ka'tuar'el", "number": "6072260710", "sms": "txt.att.net", "mms": "mms.att.net"},
}

FROM_ADDR = os.environ.get("MYTHOS_SMS_FROM", "arcturus@mythos.local")
SMTP_HOST = os.environ.get("MYTHOS_SMTP_HOST", "localhost")
SMTP_PORT = int(os.environ.get("MYTHOS_SMTP_PORT", "25"))
LOG_FILE = "/opt/mythos/sms/logs/sms.log"
logger = logging.getLogger("mythos-sms")

def send_sms(message, to="seraphe", use_mms=False):
    results = []
    targets = list(CONTACTS.keys()) if to == "both" else [to.lower()]
    for target in targets:
        if target not in CONTACTS:
            results.append({"to": target, "status": "error", "error": f"Unknown: {target}"})
            continue
        c = CONTACTS[target]
        gw = c["mms"] if use_mms else c["sms"]
        dest = f"{c['number']}@{gw}"
        msg = EmailMessage()
        msg.set_content(message)
        msg["To"] = dest
        msg["From"] = FROM_ADDR
        try:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            server.send_message(msg)
            server.quit()
            results.append({"to": c["name"], "gateway": dest, "status": "sent"})
        except ConnectionRefusedError:
            results.append({"to": c["name"], "status": "error", "error": "postfix not running"})
        except Exception as e:
            results.append({"to": c["name"], "status": "error", "error": str(e)})
    result = {"ts": datetime.now(timezone.utc).isoformat(), "msg": message, "results": results}
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(result) + "\n")
    except: pass
    return result

def main():
    parser = argparse.ArgumentParser(description="Send SMS from Arcturus")
    parser.add_argument("message", help="Message text")
    parser.add_argument("--to", "-t", default="seraphe", choices=["seraphe", "kataurel", "both"])
    parser.add_argument("--mms", "-m", action="store_true")
    args = parser.parse_args()
    result = send_sms(args.message, to=args.to, use_mms=args.mms)
    for r in result["results"]:
        if r["status"] == "sent": print(f"✓ Sent to {r['to']} via {r['gateway']}")
        else: print(f"✗ Failed: {r['to']}: {r['error']}", file=sys.stderr)
    sys.exit(0 if all(r["status"] == "sent" for r in result["results"]) else 1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
