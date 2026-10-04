# CryptidShark

Sitio estático (GitHub Pages). Tutoriales en Markdown; al hacer push se publican y, si LinkedIn está conectado, se comparten solos.

## Subir un post (lo habitual)

```bash
./blog.sh new "Cómo endurecer una API Django" \
  --tags "Django,AppSec" \
  --excerpt "Auth en servidor, no en el frontend."
```

Edita el archivo que imprime el comando (`content/posts/...md`).

```bash
git add content/posts
git commit -m "blog: endurecer API Django"
git push
```

Eso es todo. GitHub Actions genera el HTML, actualiza el listado y publica en LinkedIn (`linkedin: true` por defecto).

### Programar fecha

```bash
./blog.sh new "Título" --at "2026-10-20 09:00" --tags "AppSec"
```

Hora `America/Bogota`. El post no aparece en el sitio hasta entonces; LinkedIn sale en el mismo momento.

### Sin LinkedIn

```bash
./blog.sh new "Título" --no-linkedin
```

o en el Markdown: `linkedin: false`.

Vista local: `./blog.sh build` y abre `blog.html`.

## LinkedIn, una sola vez

```bash
./blog.sh linkedin
```

Secrets: `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN`. El token dura ~60 días.

El artículo `secure-django` está en `linkedin: false` a propósito.
