# CryptidShark — sitio y blog

Sitio estático en GitHub Pages, con tutoriales en Markdown, publicación programada y envío automático a LinkedIn.

## Cómo publicar un tutorial

Desde la raíz del repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-blog.txt

python tools/blog.py new "Cómo endurecer una API Django" --at "2026-10-20 09:00" --tags "Django,AppSec"
```

Eso crea un archivo en `content/posts/`. Edítalo, súbelo a GitHub y listo.

- Si `--at` es **en el futuro**, el post queda `scheduled`. GitHub Actions lo publica cuando llegue la hora (zona `America/Bogota`, UTC-5).
- Si `--at` es ahora o lo omites, se genera el HTML en cuanto corras `build` o se dispare el workflow.
- `status: draft` nunca se publica.
- `linkedin: true` (por defecto en posts nuevos) comparte el artículo en tu perfil cuando pasa a estar en vivo.

Generar el sitio en local:

```bash
python tools/blog.py build
```

El listado vive en `blog.html` y cada artículo en `blog/<slug>.html`.

## LinkedIn automático

LinkedIn no deja programar el post “en su app” desde este repo: el workflow publica el HTML **y luego** llama a la API. Necesitas una app en [LinkedIn Developers](https://www.linkedin.com/developers/).

1. Crea una app y agrégale los productos **Sign In with LinkedIn using OpenID Connect** y **Share on LinkedIn**.
2. En Auth, añade esta Redirect URL: `https://www.linkedin.com/developers/tools/oauth/redirect`
3. Genera el token:

```bash
export LINKEDIN_CLIENT_ID="..."
export LINKEDIN_CLIENT_SECRET="..."
python tools/linkedin_auth.py url
# autoriza, copia el code de la URL
python tools/linkedin_auth.py token PEGA_EL_CODE
```

4. En el repo de GitHub: **Settings → Secrets and variables → Actions**, crea:
   - `LINKEDIN_ACCESS_TOKEN`
   - `LINKEDIN_AUTHOR_URN` (sale del script, forma `urn:li:person:...`)
   - opcional: `SITE_URL` (`https://cyphershark.github.io`)

El workflow `.github/workflows/publish-blog.yml` corre cada hora y también al subir archivos en `content/posts/`.

Los tokens personales de LinkedIn caducan (suele ser ~60 días). Cuando dejen de publicarse, vuelve a ejecutar `linkedin_auth.py`.

El artículo que ya estaba en el sitio tiene `linkedin: false` para no republicarlo en LinkedIn. En tutoriales nuevos déjalo en `true`.

## Frontmatter

```yaml
title: Título del tutorial
slug: url-corta
publish_at: "2026-10-20T09:00:00-05:00"
status: scheduled   # draft | scheduled | published
tags: [Django, AppSec]
excerpt: Resumen corto para la tarjeta y LinkedIn
linkedin: true
linkedin_text: "Texto opcional del post en LinkedIn"
```
