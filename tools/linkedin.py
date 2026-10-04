#!/usr/bin/env python3
"""Share a published tutorial on LinkedIn (personal profile)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

UGC_URL = "https://api.linkedin.com/v2/ugcPosts"


class LinkedInConfigError(RuntimeError):
    pass


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise LinkedInConfigError(
            f"Falta {name}. Añádelo como secret de GitHub o variable de entorno."
        )
    return value


def _commentary(post: dict, url: str) -> str:
    if post.get("linkedin_text"):
        text = post["linkedin_text"]
    else:
        tags = " ".join(f"#{tag.replace(' ', '')}" for tag in post.get("tags") or [])
        text = (
            f"{post['title']}\n\n"
            f"{post.get('excerpt') or ''}\n\n"
            f"Tutorial completo: {url}\n"
            f"{tags}"
        ).strip()
    return text[:2900]


def share_post(post: dict, url: str) -> None:
    token = _required_env("LINKEDIN_ACCESS_TOKEN")
    author = _required_env("LINKEDIN_AUTHOR_URN")
    payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": _commentary(post, url)},
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "originalUrl": url,
                        "title": {"text": post["title"][:200]},
                        "description": {"text": (post.get("excerpt") or "")[:256]},
                    }
                ],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    request = urllib.request.Request(
        UGC_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            print(f"LinkedIn OK ({response.status}): {body[:300]}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LinkedIn {exc.code}: {detail}") from exc
