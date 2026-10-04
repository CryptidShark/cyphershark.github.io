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
from urllib.parse import quote
from zoneinfo import ZoneInfo

import markdown
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
POSTS_DIR = ROOT / "content" / "posts"
STATE_PATH = ROOT / "content" / "state.json"
BLOG_DIR = ROOT / "blog"
BLOG_INDEX = ROOT / "blog.html"
INDEX_PATH = ROOT / "index.html"
SITEMAP_PATH = ROOT / "sitemap.xml"
SITE_TZ = ZoneInfo("America/Bogota")
DEFAULT_SITE_URL = "https://cyphershark.github.io"
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
FONTS = (
    "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
    "&family=IBM+Plex+Sans:wght@400;500;600;700"
    "&family=IBM+Plex+Serif:ital,wght@0,500;0,600;1,400&display=swap"
)

ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{title}} | CryptidShark</title>
  <meta name="description" content="{{description}}">
  <meta name="author" content="Anthony Renzo A.">
  <meta name="theme-color" content="#0b0d11">
  <link rel="canonical" href="{{url}}">
  <meta property="og:site_name" content="CryptidShark">
  <meta property="og:locale" content="es_ES">
  <meta property="og:title" content="{{title}}">
  <meta property="og:description" content="{{description}}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{{url}}">
  <meta property="og:image" content="{{image}}">
  <meta property="og:image:secure_url" content="{{image}}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{{title}}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{{title}}">
  <meta name="twitter:description" content="{{description}}">
  <meta name="twitter:image" content="{{image}}">
  <link rel="icon" href="../assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{{fonts}}" rel="stylesheet">
  <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
  <a class="skip-link" href="#contenido">Saltar al contenido</a>
  <header class="navbar">
    <div class="navbar-inner">
      <a class="brand" href="../index.html">
        <img src="../assets/img/favicon.svg" alt="">
        CryptidShark
      </a>
      <input id="nav-toggle" class="nav-toggle" type="checkbox" aria-hidden="true" tabindex="-1">
      <label class="nav-burger" for="nav-toggle" aria-label="Abrir menú"><span></span></label>
      <nav aria-label="Principal">
        <a href="../index.html">Inicio</a>
        <a href="../about.html">Sobre mí</a>
        <a href="../portfolio.html">Portafolio</a>
        <a class="is-active" href="../blog.html" aria-current="page">Blog</a>
        <a href="../cv.html">CV</a>
        <a href="../contact.html">Contacto</a>
      </nav>
    </div>
  </header>

  <main id="contenido" class="article-shell">
    <a class="back-link" href="../blog.html">← Todos los artículos</a>
    <article>
      <p class="eyebrow">{{tags}}</p>
      <h1>{{title}}</h1>
      <p class="article-meta"><time datetime="{{date_iso}}">{{date_label}}</time> · {{reading_time}} min de lectura</p>
      {{share}}
      {{toc}}
      <div class="article-body">
        {{body}}
      </div>
      {{share}}
    </article>
    <aside class="page-cta">
      <strong>¿Necesitas una revisión o apoyo similar?</strong>
      <p class="section-intro">Auditorías y desarrollo con alcance acordado.</p>
      <a class="btn primary" href="../contact.html">Contactar</a>
    </aside>
  </main>

  <footer class="footer">
    <div class="footer-inner">
      <p>© {{year}} CryptidShark — Backend & Security Engineering</p>
      <p><a href="../blog.html">Blog</a></p>
    </div>
  </footer>
  <script src="../assets/js/share.js" defer></script>
</body>
</html>
"""

BLOG_INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog | CryptidShark</title>
  <meta name="description" content="Tutoriales de backend, AppSec y automatización. Publicación programada desde el repo.">
  <meta name="theme-color" content="#0b0d11">
  <link rel="canonical" href="{{site_url}}/blog.html">
  <meta property="og:site_name" content="CryptidShark">
  <meta property="og:locale" content="es_ES">
  <meta property="og:title" content="Blog | CryptidShark">
  <meta property="og:description" content="Tutoriales de backend, AppSec y automatización.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{{site_url}}/blog.html">
  <meta property="og:image" content="{{image}}">
  <meta property="og:image:secure_url" content="{{image}}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="{{image}}">
  <link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{{fonts}}" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
  <a class="skip-link" href="#contenido">Saltar al contenido</a>
  <header class="navbar">
    <div class="navbar-inner">
      <a class="brand" href="index.html">
        <img src="assets/img/favicon.svg" alt="">
        CryptidShark
      </a>
      <input id="nav-toggle" class="nav-toggle" type="checkbox" aria-hidden="true" tabindex="-1">
      <label class="nav-burger" for="nav-toggle" aria-label="Abrir menú"><span></span></label>
      <nav aria-label="Principal">
        <a href="index.html">Inicio</a>
        <a href="about.html">Sobre mí</a>
        <a href="portfolio.html">Portafolio</a>
        <a class="is-active" href="blog.html" aria-current="page">Blog</a>
        <a href="cv.html">CV</a>
        <a href="contact.html">Contacto</a>
      </nav>
    </div>
  </header>

  <main id="contenido">
    <section class="hero">
      <div class="wrap">
        <p class="eyebrow">Blog técnico</p>
        <h1>Tutoriales de backend, AppSec y automatización.</h1>
        <p class="subtitle">
          Artículos técnicos con pasos aplicables a sistemas reales:
          Django, Python, seguridad web y operación.
        </p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        <h2>Artículos</h2>
        <p class="section-intro">{{categories}}</p>
        <div class="post-list">
          {{cards}}
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="footer-inner">
      <p>© {{year}} CryptidShark — Backend & Security Engineering</p>
      <p><a href="contact.html">Contacto</a></p>
    </div>
  </footer>
</body>
</html>
"""


def fill(template: str, **kwargs: str) -> str:
    out = template
    for key, value in kwargs.items():
        out = out.replace("{{" + key + "}}", str(value))
    return out


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
    words = len(re.findall(r"\w+", body, flags=re.UNICODE))
    return max(1, round(words / 200))


def load_posts() -> list[dict]:
    posts = []
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(POSTS_DIR.glob("*.md")):
        if path.name.startswith("_"):
            continue
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
            excerpt = re.sub(r"\s+", " ", re.sub(r"[#*`>_]", "", body)).strip()[:180]
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
    return post["status"] in {"scheduled", "published"} and post["publish_at"] <= now


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"live": [], "linkedin": []}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render_markdown(markdown_text: str) -> tuple[str, str]:
    converter = markdown.Markdown(extensions=["fenced_code", "tables", "sane_lists", "toc"])
    body = converter.convert(markdown_text)
    toc = converter.toc if getattr(converter, "toc", "") and "<li>" in converter.toc else ""
    if toc:
        toc = f'<nav class="toc" aria-label="Índice"><p>En esta página</p>{toc}</nav>'
    return body, toc


def post_card(post: dict, featured: bool = False, href_prefix: str = "blog/") -> str:
    klass = "post-card post-card--featured" if featured else "post-card"
    chips = "".join(f"<li>{html.escape(tag)}</li>" for tag in post["tags"])
    chips_html = f'<ul class="chips">{chips}</ul>' if chips else ""
    return (
        f'<a class="{klass}" href="{href_prefix}{html.escape(post["slug"])}.html">'
        f'<div class="post-card-meta">'
        f'<time datetime="{post["publish_at"].date().isoformat()}">{html.escape(format_date_es(post["publish_at"]))}</time>'
        f'<span>{reading_minutes(post["body"])} min</span>'
        f"</div>"
        f"<h3>{html.escape(post['title'])}</h3>"
        f'<p class="excerpt">{html.escape(post["excerpt"])}</p>'
        f"{chips_html}"
        "</a>"
    )


def share_bar(url: str, title: str, excerpt: str = "") -> str:
    q_url = quote(url, safe="")
    q_title = quote(title, safe="")
    linkedin = html.escape(f"https://www.linkedin.com/sharing/share-offsite/?url={q_url}")
    twitter = html.escape(f"https://x.com/intent/tweet?url={q_url}&text={q_title}")
    facebook = html.escape(f"https://www.facebook.com/sharer/sharer.php?u={q_url}")
    copied = html.escape(url)
    return (
        '<div class="share">'
        '<p class="share-label">Compartir</p>'
        '<ul class="share-list">'
        f'<li><a class="share-btn" href="{linkedin}" target="_blank" rel="noopener noreferrer">LinkedIn</a></li>'
        f'<li><a class="share-btn" href="{twitter}" target="_blank" rel="noopener noreferrer">X</a></li>'
        f'<li><a class="share-btn" href="{facebook}" target="_blank" rel="noopener noreferrer">Facebook</a></li>'
        f'<li><button type="button" class="share-btn" data-copy="{copied}" title="Instagram no admite vista previa de enlaces. Se copia la URL para pegarla en la app.">Instagram</button></li>'
        "</ul>"
        "</div>"
    )


def write_article(post: dict, site_url: str) -> None:
    from og_image import write_og_image

    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    url = f"{site_url.rstrip('/')}/blog/{post['slug']}.html"
    image = f"{site_url.rstrip('/')}/assets/img/og/{post['slug']}.png"
    write_og_image(post["slug"], post["title"])
    body, toc = render_markdown(post["body"])
    html_doc = fill(
        ARTICLE_TEMPLATE,
        title=html.escape(post["title"]),
        description=html.escape(post["excerpt"]),
        url=html.escape(url),
        image=html.escape(image),
        fonts=FONTS,
        tags=html.escape(" · ".join(post["tags"]) or "Tutorial"),
        date_iso=post["publish_at"].date().isoformat(),
        date_label=html.escape(format_date_es(post["publish_at"])),
        reading_time=str(reading_minutes(post["body"])),
        toc=toc,
        body=body,
        share=share_bar(url, post["title"], post["excerpt"]),
        year=str(datetime.now(SITE_TZ).year),
    )
    (BLOG_DIR / f"{post['slug']}.html").write_text(html_doc, encoding="utf-8")


def write_index(live_posts: list[dict], site_url: str) -> None:
    if live_posts:
        cards = "\n          ".join(
            post_card(post, featured=(index == 0)) for index, post in enumerate(live_posts)
        )
        categories = " · ".join(dict.fromkeys(tag for post in live_posts for tag in post["tags"])) or "Tutoriales"
    else:
        cards = '<p class="section-intro">Aún no hay tutoriales en vivo. El próximo aparece aquí solo, a la hora programada.</p>'
        categories = "Backend · Django · Python · AppSec"
    BLOG_INDEX.write_text(
        fill(
            BLOG_INDEX_TEMPLATE,
            cards=cards,
            categories=html.escape(categories),
            year=str(datetime.now(SITE_TZ).year),
            fonts=FONTS,
            site_url=html.escape(site_url.rstrip("/")),
            image=html.escape(f"{site_url.rstrip('/')}/assets/img/og/default.png"),
        ),
        encoding="utf-8",
    )


def update_home(live_posts: list[dict]) -> None:
    if not INDEX_PATH.exists():
        return
    source = INDEX_PATH.read_text(encoding="utf-8")
    start = "<!-- BLOG_LATEST:START -->"
    end = "<!-- BLOG_LATEST:END -->"
    if start not in source or end not in source:
        return
    if live_posts:
        inner = '<div class="post-list">\n          ' + "\n          ".join(
            post_card(post, featured=(index == 0)) for index, post in enumerate(live_posts[:3])
        ) + "\n        </div>"
    else:
        inner = '<p class="section-intro">El primer tutorial aparecerá aquí al publicarse.</p>'
    before, rest = source.split(start, 1)
    _, after = rest.split(end, 1)
    INDEX_PATH.write_text(f"{before}{start}\n        {inner}\n        {end}{after}", encoding="utf-8")


def write_sitemap(live_posts: list[dict], site_url: str) -> None:
    base = site_url.rstrip("/")
    pages = ["/", "/about.html", "/portfolio.html", "/blog.html", "/cv.html", "/contact.html"]
    urls = pages + [f"/blog/{post['slug']}.html" for post in live_posts]
    items = "\n".join(
        f"  <url><loc>{html.escape(base + path if path != '/' else base + '/')}</loc></url>"
        for path in urls
    )
    SITEMAP_PATH.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{items}\n"
        "</urlset>\n",
        encoding="utf-8",
    )


def cmd_new(args: argparse.Namespace) -> None:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    if getattr(args, "now", False) or not args.at:
        publish_at = datetime.now(SITE_TZ)
    else:
        publish_at = parse_dt(args.at)
    slug = args.slug or slugify(args.title)
    filename = f"{publish_at.strftime('%Y-%m-%d')}-{slug}.md"
    path = POSTS_DIR / filename
    if path.exists():
        raise SystemExit(f"Ya existe {path}")
    status = "scheduled" if publish_at > datetime.now(SITE_TZ) else "published"
    tags = [item.strip() for item in (args.tags or "Tutorial").split(",") if item.strip()]
    share = not getattr(args, "no_linkedin", False)
    doc = {
        "title": args.title,
        "slug": slug,
        "publish_at": publish_at.isoformat(timespec="minutes"),
        "status": status,
        "tags": tags,
        "excerpt": args.excerpt or "",
        "linkedin": share,
        "linkedin_text": "",
    }
    front = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False).strip()
    path.write_text(
        f"---\n{front}\n---\n\n"
        "Párrafo de contexto: para quién es esto y qué problema cierra.\n\n"
        "## Qué vas a dejar hecho\n\n"
        "## Pasos\n\n"
        "1. \n\n"
        "## Cómo comprobarlo\n\n"
        "## Cierre\n",
        encoding="utf-8",
    )
    print(f"Creado {path.relative_to(ROOT)}")
    print(f"Estado: {status} | Publicación: {publish_at.isoformat()}")
    print(f"LinkedIn: {'sí, al publicarse' if share else 'no'}")
    print("1) Edita ese archivo.")
    print("2) Opcional: python tools/blog.py build")
    print("3) git add content/posts && git commit -m \"blog: título\" && git push")
    print("   GitHub Actions publica el HTML y, con secrets, lo comparte en LinkedIn.")


def cmd_build(args: argparse.Namespace) -> list[dict]:
    from og_image import write_default_og

    write_default_og()
    now = datetime.now(SITE_TZ)
    site_url = args.site_url.rstrip("/")
    posts = load_posts()
    live = [post for post in posts if is_live(post, now)]
    scheduled = [post for post in posts if post["status"] != "draft" and post["publish_at"] > now]
    drafts = [post for post in posts if post["status"] == "draft"]

    for post in live:
        write_article(post, site_url)
    write_index(live, site_url)
    update_home(live)
    write_sitemap(live, site_url)

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
            if not post["linkedin"] or post["slug"] in already_shared:
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


def cmd_linkedin(_args: argparse.Namespace) -> None:
    print(
        """Una sola vez:

1. App en https://www.linkedin.com/developers/
   Productos: Sign In with LinkedIn using OpenID Connect + Share on LinkedIn
   Redirect: https://www.linkedin.com/developers/tools/oauth/redirect

2. export LINKEDIN_CLIENT_ID=... LINKEDIN_CLIENT_SECRET=...
   python tools/linkedin_auth.py url
   Autoriza, copia el code de la URL.

3. python tools/linkedin_auth.py token PEGA_EL_CODE

4. GitHub → Settings → Secrets → Actions:
   LINKEDIN_ACCESS_TOKEN
   LINKEDIN_AUTHOR_URN
   (opcional) SITE_URL=https://cyphershark.github.io

5. Settings → Actions → General → Read and write permissions

Cada post nuevo trae linkedin: true. Al hacer git push, el workflow
publica el artículo y lo comparte. El token dura ~60 días; si deja
de publicarse, repite los pasos 2–4.
"""
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Blog de tutoriales para GitHub Pages")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL, help="URL pública del sitio")
    sub = parser.add_subparsers(dest="command", required=True)

    new_p = sub.add_parser("new", help="Crear un tutorial en Markdown")
    new_p.add_argument("title", help="Título del tutorial")
    new_p.add_argument("--at", help="Fecha/hora de publicación, ej. 2026-10-20 09:00")
    new_p.add_argument("--now", action="store_true", help="Publicable en cuanto hagas push")
    new_p.add_argument("--slug", help="Slug de la URL")
    new_p.add_argument("--tags", help="Tags separados por coma")
    new_p.add_argument("--excerpt", help="Resumen corto")
    new_p.add_argument("--no-linkedin", action="store_true", help="No compartir en LinkedIn")
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

    li_p = sub.add_parser("linkedin", help="Cómo conectar LinkedIn (una sola vez)")
    li_p.set_defaults(func=cmd_linkedin)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
