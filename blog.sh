#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PY="$ROOT/.venv/bin/python"

if [[ ! -x "$PY" ]]; then
  echo "Primera vez:"
  echo "  python3 -m venv .venv"
  echo "  .venv/bin/pip install -r requirements-blog.txt"
  exit 1
fi

cmd="${1:-ayuda}"
shift || true

case "$cmd" in
  new)
    "$PY" tools/blog.py new "$@"
    ;;
  build|ver)
    "$PY" tools/blog.py build
    ;;
  linkedin)
    "$PY" tools/blog.py linkedin
    ;;
  ayuda|help|-h|--help)
    cat <<'EOF'
Publicar un tutorial y mandarlo a LinkedIn

  ./blog.sh new "Título" --tags "Django,AppSec" --excerpt "Una frase."
      Sale en cuanto hagas git push.

  ./blog.sh new "Título" --at "2026-10-20 09:00" --tags "AppSec"
      Queda programado. Actions lo publica a esa hora (Bogotá) y lo comparte.

  ./blog.sh new "Título" --no-linkedin
      Solo el sitio, sin LinkedIn.

  Edita content/posts/*.md y luego:

  git add content/posts
  git commit -m "blog: título"
  git push

  ./blog.sh build     vista local del HTML
  ./blog.sh linkedin  cómo conectar la API (una vez)

EOF
    ;;
  *)
    echo "Comando no reconocido: $cmd"
    echo "Usa: ./blog.sh ayuda"
    exit 1
    ;;
esac
