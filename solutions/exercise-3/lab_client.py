"""Small reproducible API probe. Every invocation uses a NEW temporary database.
The Flask test client exercises routing, cookies and handlers without a network
server. Browser pages use the persistent instance database instead.
"""
import argparse
import json
from tempfile import TemporaryDirectory
from pathlib import Path
from app import create_app
from db import DEMO_PASSWORD, find_note


def sign_in(client, username):
    client.get("/login")
    with client.session_transaction() as session:
        token = session["csrf_token"]
    result = client.post("/login", data={"username": username, "password": DEMO_PASSWORD, "csrf_token": token})
    assert result.status_code == 302, "Login failed: use a seeded username."
    with client.session_transaction() as session:
        return session["csrf_token"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="editor", choices=["reader","editor","other_editor","admin","anonymous"])
    parser.add_argument("--method", default="GET", choices=["GET","PATCH","POST","DELETE"])
    parser.add_argument("--path", default="/api/notes/2")
    parser.add_argument("--json", dest="payload")
    parser.add_argument("--raw", help="Literal request body, useful for malformed JSON")
    parser.add_argument("--content-type", default="application/json")
    parser.add_argument("--no-csrf", action="store_true")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--fault", action="store_true")
    parser.add_argument("--inspect", type=int, metavar="NOTE_ID", help="Show a synthetic stored row after requests")
    args = parser.parse_args()
    with TemporaryDirectory() as tmp:
        app = create_app({"DATABASE":str(Path(tmp)/"demo.sqlite"), "TESTING":True,
                          "LAB_MODE":args.fault, "SESSION_COOKIE_SECURE":False})
        client = app.test_client()
        token = sign_in(client, args.user) if args.user != "anonymous" else ""
        headers = {} if args.no_csrf else {"X-CSRF-Token":token}
        kwargs = {"headers":headers}
        if args.payload is not None:
            kwargs["json"] = json.loads(args.payload)
        if args.raw is not None:
            kwargs.update(data=args.raw, content_type=args.content_type)
        path = "/api/lab-fault" if args.fault else args.path
        for index in range(args.repeat):
            response = client.open(path, method=args.method, **kwargs)
            print(f"Request {index+1}: HTTP {response.status_code}")
            print(response.get_data(as_text=True))
            for key in ("Content-Type","X-Request-ID","X-Content-Type-Options","Referrer-Policy","Content-Security-Policy","Retry-After","X-RateLimit-Remaining"):
                if key in response.headers:
                    print(f"{key}: {response.headers[key]}")
        if args.inspect is not None:
            with app.app_context():
                row = find_note(args.inspect)
                print("Stored synthetic row:", dict(row) if row else None)


if __name__ == "__main__":
    main()
