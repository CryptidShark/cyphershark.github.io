#!/usr/bin/env python3
"""Create, build and publish tutorial posts for this GitHub Pages site."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
POSTS_DIR = ROOT / "content" / "posts"
STATE_PATH = ROOT / "content" / "state.json"
BLOG_DIR = ROOT / "blog"
BLOG_INDEX = ROOT / "blog.html"
SITE_TZ = ZoneInfo("America/Bogota")
MONTHS_ES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)

ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | CryptidShark</title>
  <meta name="description" content="{description}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
  <header class="navbar">
    <div class="brand">CryptidShark 🦈</div>
    <nav>
      <a href="../index.html">Home</a>
      <a href="../about.html">About</a>
      <a href="../portfolio.html">Portfolio</a>
      <a href="../blog.html">Blog</a>
      <a href="../cv.html">CV</a>
      <a href="../contact.html">Contact</a>
    </nav>
  </header>

  <main class="page article">
    <article>
      <p class="eyebrow">{tags}</p>
      <h1>{title}</h1>
      <p class="article-meta"><strong>Publicado:</strong> {date_label} | <strong>Lectura:</strong> {reading_time} min</p>
      {body}
    </article>
  </main>

  <footer class="footer">
    <p>© {year} CryptidShark — Backend & Security Engineering</p>
  </footer>
</body>
</html>
"""

BLOG_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog | CryptidShark</title>
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
  <header class="navbar">
    <div class="brand">CryptidShark 🦈</div>
    <nav>
      <a href="index.html">Home</a>
      <a href="about.html">About</a>
      <a href="portfolio.html">Portfolio</a>
      <a href="blog.html">Blog</a>
      <a href="cv.html">CV</a>
      <a href="contact.html">Contact</a>
    </nav>
  </header>

  <main class="page">
    <section class="hero">
      <p class="eyebrow">Blog técnico</p>
      <h1>Ingeniería backend, automatización y ciberseguridad aplicada.</h1>
      <p class="subtitle">
        Tutoriales y actualizaciones técnicas: arquitectura web, hardening,
        debugging avanzado, automatización con Python y seguridad en entornos reales.
      </p>
    </section>

    <section class="expertise">
      <h2>Artículos</h2>
      <div class="grid">
        {cards}
      </div>
    </section>

    <section class="preview">
      <h2>Categorías</h2>
      <p>{categories}</p>
    </section>
  </main>

  <footer class="footer">
    <p>© {year} CryptidShark — Backend & Security Engineering</p>
  </footer>
</body>
</html>
"""


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "post"


def parse_dt(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip().replace("Z", "+00:00")
        if "T" not in text and " " in text:
            text = text.replace(" ", "T", 1)
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            dt = datetime.strptime(text[:10], "%Y-%m-%d")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=SITE_TZ)
    return dt.astimezone(SITE_TZ)


def format_date_es(dt: datetime) -> str:
    return f"{dt.day} de {MONTHS_ES[dt.month - 1]} {dt.year}"


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = yaml.safe_load(parts[1]) or {}
    return meta, parts[2].lstrip("\n")


def reading_minutes(body: str) -> int:
    words = len(re.findall(r"\w+", body))
    return max(1, round(words / 200))


def load_posts() -> list[dict]:
    posts = []
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(POSTS_DIR.glob("*.md")):
        meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
        title = str(meta.get("title") or path.stem)
        slug = str(meta.get("slug") or slugify(title))
        publish_at = parse_dt(meta.get("publish_at") or meta.get("date") or datetime.now(SITE_TZ))
        status = str(meta.get("status") or "published").lower()
        tags = meta.get("tags") or []
        if isinstance(tags, str):
            tags = [item.strip() for item in tags.split(",") if item.strip()]
        excerpt = str(meta.get("excerpt") or "").strip()
        if not excerpt:
            excerpt = re.sub(r"\s+", " ", re.sub(r"[#*`]", "", body)).strip()[:180]
        posts.append(
            {
                "path": path,
                "title": title,
                "slug": slug,
                "publish_at": publish_at,
                "status": status,
                "tags": tags,
                "excerpt": excerpt,
                "linkedin": bool(meta.get("linkedin", True)),
                "linkedin_text": str(meta.get("linkedin_text") or "").strip(),
                "body": body,
            }
        )
    posts.sort(key=lambda item: item["publish_at"], reverse=True)
    return posts


def is_live(post: dict, now: datetime) -> bool:
    if post["status"] == "draft":
        return False
    if post["status"] in {"scheduled", "published"}:
        return post["publish_at"] <= now
    return False


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"live": [], "linkedin": []}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render_body(markdown_text: str) -> str:
    return markdown.markdown(
        markdown_text,
        extensions=["fenced_code", "tables", "nl2br", "sane_lists"],
    )


def write_article(post: dict, site_url: str) -> None:
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    url = f"{site_url.rstrip('/')}/blog/{post['slug']}.html"
    html_doc = ARTICLE_TEMPLATE.format(
        title=html.escape(post["title"]),
        description=html.escape(post["excerpt"]),
        url=html.escape(url),
        tags=html.escape(" • ".join(post["tags"]) or "Tutorial"),
        date_label=html.escape(format_date_es(post["publish_at"])),
        reading_time=reading_minutes(post["body"]),
        body=render_body(post["body"]),
        year=datetime.now(SITE_TZ).year,
    )
    (BLOG_DIR / f"{post['slug']}.html").write_text(html_doc, encoding="utf-8")


def write_index(live_posts: list[dict]) -> None:
    if live_posts:
        cards = "\n        ".join(
            (
                f'<a class="card blog-card" href="blog/{html.escape(post["slug"])}.html">'
                f"<strong>{html.escape(post['title'])}</strong><br><br>"
                f"{html.escape(post['excerpt'])}"
                "</a>"
            )
            for post in live_posts
        )
        categories = " • ".join(dict.fromkeys(tag for post in live_posts for tag in post["tags"])) or "Tutoriales"
    else:
        cards = '<p class="subtitle">Aún no hay tutoriales publicados. El próximo artículo aparecerá aquí automáticamente.</p>'
        categories = "Backend • Django • Python • AppSec • Debugging • OWASP • Automation"
    BLOG_INDEX.write_text(
        BLOG_INDEX_TEMPLATE.format(
            cards=cards,
            categories=html.escape(categories),
            year=datetime.now(SITE_TZ).year,
        ),
        encoding="utf-8",
    )


def cmd_new(args: argparse.Namespace) -> None:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    publish_at = parse_dt(args.at) if args.at else datetime.now(SITE_TZ)
    slug = args.slug or slugify(args.title)
    filename = f"{publish_at.strftime('%Y-%m-%d')}-{slug}.md"
    path = POSTS_DIR / filename
    if path.exists():
        raise SystemExit(f"Ya existe {path}")
    status = "scheduled" if publish_at > datetime.now(SITE_TZ) else "published"
    tags = [item.strip() for item in (args.tags or "Tutorial").split(",") if item.strip()]
    doc = {
        "title": args.title,
        "slug": slug,
        "publish_at": publish_at.isoformat(timespec="minutes"),
        "status": status,
        "tags": tags,
        "excerpt": args.excerpt or "",
        "linkedin": True,
        "linkedin_text": "",
    }
    front = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False).strip()
    path.write_text(
        f"---\n{front}\n---\n\n"
        f"Escribe aquí tu tutorial.\n\n"
        f"## Qué vas a construir\n\n"
        f"## Pasos\n\n"
        f"1. \n\n"
        f"## Conclusión\n",
        encoding="utf-8",
    )
    print(f"Creado {path.relative_to(ROOT)}")
    print(f"Estado: {status} | Publicación: {publish_at.isoformat()}")


def cmd_build(args: argparse.Namespace) -> list[dict]:
    now = datetime.now(SITE_TZ)
    site_url = args.site_url.rstrip("/")
    posts = load_posts()
    live = [post for post in posts if is_live(post, now)]
    scheduled = [post for post in posts if post["status"] != "draft" and post["publish_at"] > now]
    drafts = [post for post in posts if post["status"] == "draft"]

    for post in live:
        write_article(post, site_url)
    write_index(live)

    print(f"Publicados ahora: {len(live)}")
    for post in live:
        print(f"  - {post['slug']} ({post['publish_at'].isoformat()})")
    if scheduled:
        print("Programados:")
        for post in scheduled:
            print(f"  - {post['slug']} → {post['publish_at'].isoformat()}")
    if drafts:
        print(f"Borradores ignorados: {len(drafts)}")
    return live


def cmd_publish(args: argparse.Namespace) -> None:
    from linkedin import LinkedInConfigError, share_post

    live = cmd_build(args)
    state = load_state()
    previously_live = set(state.get("live") or [])
    already_shared = set(state.get("linkedin") or [])
    newly_live = [post for post in live if post["slug"] not in previously_live]
    site_url = args.site_url.rstrip("/")

    try:
        for post in live:
            if not post["linkedin"]:
                continue
            if post["slug"] in already_shared:
                continue
            if post["slug"] not in previously_live or args.share_existing:
                url = f"{site_url}/blog/{post['slug']}.html"
                share_post(post, url)
                already_shared.add(post["slug"])
                state["linkedin"] = sorted(already_shared)
                save_state(state)
                print(f"LinkedIn: compartido {post['slug']}")
    except LinkedInConfigError as exc:
        print(f"LinkedIn omitido: {exc}")

    state["live"] = [post["slug"] for post in live]
    state["linkedin"] = sorted(already_shared)
    save_state(state)
    if newly_live:
        print("Nuevos en el sitio:")
        for post in newly_live:
            print(f"  - {post['slug']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Blog de tutoriales para GitHub Pages")
    parser.add_argument(
        "--site-url",
        default="https://cyphershark.github.io",
        help="URL pública del sitio",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    new_p = sub.add_parser("new", help="Crear un tutorial en Markdown")
    new_p.add_argument("title", help="Título del tutorial")
    new_p.add_argument("--at", help="Fecha/hora de publicación, ej. 2026-10-20 09:00")
    new_p.add_argument("--slug", help="Slug de la URL")
    new_p.add_argument("--tags", help="Tags separados por coma")
    new_p.add_argument("--excerpt", help="Resumen corto")
    new_p.set_defaults(func=cmd_new)

    build_p = sub.add_parser("build", help="Generar HTML de los posts ya vencidos")
    build_p.set_defaults(func=cmd_build)

    publish_p = sub.add_parser("publish", help="Generar HTML y compartir en LinkedIn")
    publish_p.add_argument(
        "--share-existing",
        action="store_true",
        help="También compartir posts ya publicados que aún no se enviaron a LinkedIn",
    )
    publish_p.set_defaults(func=cmd_publish)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
