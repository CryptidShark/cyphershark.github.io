# CryptidShark

Sitio estático (GitHub Pages) con tutoriales en Markdown, publicación a una hora fija y aviso opcional en LinkedIn.

## Publicar un tutorial nuevo

1. En la raíz del repo, una sola vez:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-blog.txt
```

2. Crear el archivo (la hora es `America/Bogota`, UTC-5):

```bash
python tools/blog.py new "Título del tutorial" \
  --at "2026-10-20 09:00" \
  --tags "Django,AppSec" \
  --excerpt "Una frase que explique el problema y el resultado."
```

Si omites `--at`, se considera publicable ahora.

3. Edita `content/posts/AAAA-MM-DD-....md`. Frontmatter útil:

```yaml
status: scheduled    # draft | scheduled | published
linkedin: true       # false si no quieres el post en LinkedIn
linkedin_text: ""    # texto custom; si va vacío se arma solo
```

4. Vista local:

```bash
python tools/blog.py build
python3 -m http.server 8765
```

Abre `http://127.0.0.1:8765/blog.html`. Un post futuro **no** aparece hasta su hora.

5. Sube el Markdown (y el resto del sitio) a GitHub. El workflow corre al hacer push de `content/posts/` y **cada hora**. Genera `blog/`, actualiza el listado del home y, si hay secrets, publica en LinkedIn.

6. LinkedIn, una vez: app con *Sign In with LinkedIn* + *Share on LinkedIn*, redirect `https://www.linkedin.com/developers/tools/oauth/redirect`, luego:

```bash
python tools/linkedin_auth.py url
python tools/linkedin_auth.py token PEGA_EL_CODE
```

Secrets del repo: `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN`, opcional `SITE_URL`. En Actions, permiso de escritura al GITHUB_TOKEN. El token caduca ~60 días.

El artículo `secure-django` tiene `linkedin: false` a propósito.
