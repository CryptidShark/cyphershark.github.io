#!/usr/bin/env python3
"""Get a LinkedIn token and person URN for automatic sharing."""

from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
DEFAULT_REDIRECT = "https://www.linkedin.com/developers/tools/oauth/redirect"
SCOPES = "openid profile w_member_social"


def cmd_url(args: argparse.Namespace) -> None:
    client_id = args.client_id or os.environ.get("LINKEDIN_CLIENT_ID", "")
    if not client_id:
        raise SystemExit("Pasa --client-id o LINKEDIN_CLIENT_ID")
    query = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": args.redirect_uri,
            "scope": SCOPES,
            "state": "blog",
        }
    )
    print("1. Abre esta URL, autoriza y copia el ?code= de la redirección:")
    print(f"{AUTH_URL}?{query}")


def cmd_token(args: argparse.Namespace) -> None:
    client_id = args.client_id or os.environ.get("LINKEDIN_CLIENT_ID", "")
    client_secret = args.client_secret or os.environ.get("LINKEDIN_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise SystemExit("Necesitas client id y secret de la app de LinkedIn.")
    data = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": args.code,
            "redirect_uri": args.redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        token_payload = json.loads(response.read().decode("utf-8"))
    access_token = token_payload["access_token"]
    me_req = urllib.request.Request(
        USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    with urllib.request.urlopen(me_req, timeout=30) as response:
        profile = json.loads(response.read().decode("utf-8"))
    person_id = profile.get("sub")
    print("Guarda estos valores como secrets del repositorio:")
    print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
    print(f"LINKEDIN_AUTHOR_URN=urn:li:person:{person_id}")
    if "expires_in" in token_payload:
        days = int(token_payload["expires_in"]) // 86400
        print(f"El token caduca en ~{days} días. Vuelve a ejecutar este script para renovarlo.")


def main() -> None:
    parser = argparse.ArgumentParser(description="OAuth de LinkedIn para el blog")
    parser.add_argument("--client-id")
    parser.add_argument("--client-secret")
    parser.add_argument("--redirect-uri", default=DEFAULT_REDIRECT)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("url").set_defaults(func=cmd_url)
    token_p = sub.add_parser("token")
    token_p.add_argument("code", help="Código ?code= de la redirección OAuth")
    token_p.set_defaults(func=cmd_token)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
