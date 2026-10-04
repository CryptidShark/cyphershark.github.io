---
title: "WSL2 como laboratorio DevOps: un entorno Linux reproducible sobre Windows"
slug: wsl2-laboratorio-devops
publish_at: "2026-10-04T01:15:00-05:00"
status: published
tags:
  - WSL2
  - DevOps
  - Docker
  - Linux
excerpt: "Windows como host, Linux como entorno de trabajo y Docker como infraestructura: cómo montar un laboratorio DevOps reproducible en WSL2, con Compose, scripts y Git."
linkedin: true
linkedin_text: ""
---

**Windows como host. Linux como entorno de trabajo. Docker como infraestructura. Scripts como automatización.**

Durante mucho tiempo, trabajar con Linux desde Windows significaba elegir entre una máquina virtual, dual boot o aceptar las diferencias entre ambos entornos.

Hoy existe una alternativa práctica para desarrollo: **WSL2**. Instalar Ubuntu dentro de WSL, sin embargo, no es lo mismo que construir un entorno de desarrollo.

El objetivo de este artículo es otro:

> Un entorno Linux reproducible donde se pueda desarrollar, ejecutar servicios, automatizar tareas y administrar contenedores, sin convertir Windows en una colección de instalaciones independientes.

La arquitectura final:

```text
┌─────────────────────────────────────────────┐
│                 Windows 11                  │
│                                             │
│  VS Code / Terminal / herramientas Windows  │
│                    │                        │
│                    ▼                        │
│             ┌──────────────┐                │
│             │     WSL2     │                │
│             │    Ubuntu    │                │
│             └──────┬───────┘                │
│                    │                        │
│             Linux filesystem                │
│                    │                        │
│                    ▼                        │
│             ┌──────────────┐                │
│             │    Docker    │                │
│             │   Compose    │                │
│             └──────┬───────┘                │
│                    │                        │
│       ┌────────────┼────────────┐           │
│       ▼            ▼            ▼           │
│    Django      PostgreSQL     Redis         │
│                                             │
└─────────────────────────────────────────────┘
```

Cada capa tiene una responsabilidad concreta.

## 1. Por qué esta arquitectura

WSL2 utiliza un kernel Linux real. Las distribuciones se integran con Windows. Microsoft recomienda comprobar la versión con:

```powershell
wsl --version
```

Las instalaciones nuevas con `wsl --install` usan WSL2 por defecto.

Docker Desktop puede usar el backend WSL2 y dejar los comandos `docker` disponibles desde la distribución Linux.

Eso evita una disposición poco práctica:

```text
Windows
 ├── Python Windows
 ├── PostgreSQL Windows
 ├── Redis Windows
 ├── Node Windows
 ├── Docker Windows
 └── herramientas Linux separadas
```

En su lugar:

```text
Windows
   │
   └── WSL2
        │
        └── Linux
             │
             └── Docker
                  ├── PostgreSQL
                  ├── Redis
                  └── aplicaciones
```

Windows queda como anfitrión. Linux es el entorno de trabajo.

## 2. Comprobar el estado de WSL

Antes de instalar nada, conviene saber qué hay. Desde PowerShell:

```powershell
wsl --status
wsl --version
wsl -l -v
```

El último comando muestra las distribuciones y si usan WSL1 o WSL2. Una salida típica:

```text
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

Si aparece WSL1:

```powershell
wsl --set-version Ubuntu 2
```

## 3. Mantener WSL actualizado

WSL es software independiente:

```powershell
wsl --update
wsl --shutdown
wsl --status
```

Microsoft recomienda actualizarlo para soporte moderno, incluido systemd.

## 4. systemd

WSL moderno puede usar **systemd** y herramientas habituales:

```bash
systemctl
journalctl
```

En Ubuntu instalado con `wsl --install`, systemd puede venir habilitado. En otras distros se activa en `/etc/wsl.conf`.

Comprobación:

```bash
ps -p 1 -o comm=
```

Si responde `systemd`, es el PID 1.

Para habilitarlo:

```bash
sudo nano /etc/wsl.conf
```

```ini
[boot]
systemd=true
```

Desde PowerShell:

```powershell
wsl --shutdown
```

Volver a entrar:

```powershell
wsl
```

```bash
systemctl status
```

Microsoft documenta esta configuración y el reinicio con `wsl.exe --shutdown`.

## 5. `wsl.conf` frente a `.wslconfig`

### `/etc/wsl.conf`

Pertenece a una distribución concreta (`Ubuntu` → `/etc/wsl.conf`). Puede controlar systemd, usuario predeterminado, interoperabilidad, automontaje y red.

### `%UserProfile%\.wslconfig`

Es global para WSL2 (`C:\Users\<usuario>\.wslconfig`). Afecta a la máquina virtual de WSL2.

Microsoft distingue ambos niveles. Así se evita cambiar WSL entero cuando solo hace falta ajustar Ubuntu.

## 6. Preparar Ubuntu

Dentro de Ubuntu:

```bash
sudo apt update
sudo apt upgrade -y
```

Herramientas básicas:

```bash
sudo apt install -y \
    git \
    curl \
    wget \
    unzip \
    zip \
    jq \
    tree \
    htop \
    ca-certificates
```

```bash
git --version
curl --version
jq --version
tree --version
```

Queda una base Linux limpia.

## 7. Dónde guardar el código

Hay una diferencia de rendimiento importante. No conviene usar `/mnt/c/Users/<usuario>/...` como directorio principal de proyectos Linux.

Para stacks con muchas operaciones de archivos (Node, Python, Docker), el código vive mejor en el filesystem Linux:

```bash
mkdir -p ~/workspace/projects
cd ~/workspace/projects
```

```text
~/workspace/
└── projects/
    ├── proyecto-01/
    ├── proyecto-02/
    └── laboratorio/
```

Desde Windows se puede abrir esa carpeta con `explorer.exe .`. WSL permite el acceso, pero el flujo intenso de archivos rinde mejor dentro de Linux.

## 8. Docker: una sola capa de infraestructura

Con Docker Desktop e integración WSL2 no hace falta otro daemon Docker solo para los contenedores del laboratorio.

Tras habilitar la distribución en Docker Desktop:

```bash
docker version
docker compose version
docker run --rm hello-world
```

Si aparece el mensaje de bienvenida, WSL2 y Docker se comunican.

## 9. Primera regla del entorno

> **La infraestructura de los proyectos vive en Docker.**

PostgreSQL no tiene que instalarse en Ubuntu. En lugar de servicios sueltos en el sistema:

```text
Ubuntu
 │
 └── Docker
      ├── PostgreSQL
      ├── Redis
      └── aplicación
```

Así se pueden destruir y reconstruir servicios sin ensuciar el sistema operativo.

## 10. Primer laboratorio

```bash
cd ~/workspace/projects
mkdir dev-lab
cd dev-lab
nano compose.yaml
```

```yaml
services:

  postgres:
    image: postgres:18
    restart: unless-stopped
    environment:
      POSTGRES_DB: devdb
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpassword
    volumes:
      - postgres_data:/var/lib/postgresql
    ports:
      - "5432:5432"

  redis:
    image: redis:8
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

volumes:
  postgres_data:
  redis_data:
```

Las versiones de imagen forman parte de la infraestructura. En proyectos reales conviene fijarlas; las etiquetas flotantes hay que revisarlas.

## 11. Levantar la infraestructura

```bash
docker compose up -d
docker compose ps
```

Debería verse algo así:

```text
NAME              STATUS
dev-lab-postgres  running
dev-lab-redis     running
```

PostgreSQL y Redis corren sin instalarse en Ubuntu.

## 12. Logs sin entrar al contenedor

```bash
docker compose logs
docker compose logs -f
docker compose logs -f postgres
docker compose logs -f redis
```

Útil cuando algo falla.

## 13. No tratar los contenedores como cajas negras

```bash
docker compose ps
docker stats
docker network ls
docker volume ls
docker system df
```

No se trata de memorizar comandos, sino de poder responder: qué está en ejecución, dónde están los datos y qué recursos usan.

## 14. Persistencia

`docker compose down` elimina contenedores. Los volúmenes siguen.

Por eso importan `postgres_data` y `redis_data`. Comprobación: `docker volume ls`.

Para borrar también los datos:

```bash
docker compose down -v
```

Ese comando elimina los volúmenes definidos por Compose. No debe ir en scripts destructivos sin confirmación.

```text
docker compose down
        └── elimina contenedores

docker compose down -v
        ├── elimina contenedores
        └── elimina volúmenes
```

## 15. Automatización: diagnóstico

```bash
mkdir -p scripts
nano scripts/status.sh
```

```bash
#!/usr/bin/env bash

set -euo pipefail

echo "=== WSL ==="
uname -a

echo
echo "=== Docker ==="
docker version --format 'Client: {{.Client.Version}}'
docker version --format 'Server: {{.Server.Version}}'

echo
echo "=== Containers ==="
docker compose ps

echo
echo "=== Disk ==="
df -h /

echo
echo "=== Memory ==="
free -h
```

```bash
chmod +x scripts/status.sh
./scripts/status.sh
```

## 16. Makefile como interfaz del proyecto

```makefile
up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

status:
	docker compose ps

restart:
	docker compose restart

clean:
	docker compose down -v

shell:
	bash
```

`make up` equivale a `docker compose up -d`. La ventaja no es ahorrar caracteres: es una **interfaz estable** para el proyecto.

## 17. Bootstrap

```bash
nano scripts/bootstrap.sh
```

```bash
#!/usr/bin/env bash

set -euo pipefail

echo "[1/4] Actualizando paquetes..."
sudo apt update

echo "[2/4] Instalando herramientas..."
sudo apt install -y \
    git \
    curl \
    wget \
    jq \
    tree \
    htop \
    ca-certificates

echo "[3/4] Comprobando Docker..."

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker no está disponible."
    echo "Instala Docker Desktop y habilita la integración WSL2."
    exit 1
fi

echo "[4/4] Comprobando Compose..."
docker compose version

echo
echo "Entorno preparado correctamente."
```

```bash
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

El repositorio pasa a incluir instrucciones ejecutables para reconstruir el entorno.

## 18. Git: infraestructura versionada

```bash
git init
nano .gitignore
```

```gitignore
.env
.env.*
!.env.example

__pycache__/
*.py[cod]

.venv/
venv/

node_modules/

*.log

.vscode/
.idea/

.DS_Store
```

```bash
git add .
git commit -m "Initial development environment"
```

> **La infraestructura también es código.**

El flujo deseable:

```text
Git → clone → bootstrap → Docker Compose → entorno reproducible
```

En lugar de “creo que mi máquina estaba configurada así”.

## 19. Variables de entorno

No conviene dejar contraseñas reales en `compose.yaml`.

```env
POSTGRES_DB=devdb
POSTGRES_USER=devuser
POSTGRES_PASSWORD=change-me
```

```bash
cp .env.example .env
```

`.gitignore` evita subir `.env`. Se comparte `.env.example`, no los secretos.

## 20. Una comprobación útil

```bash
docker compose ps
docker compose config
docker compose logs --tail=50
git status
```

- Docker: ¿la infraestructura está en pie?
- Compose config: ¿la configuración es válida?
- Logs: ¿hay errores?
- Git: ¿hay cambios sin versionar?

## 21. Administrar WSL desde Windows

```powershell
wsl -l -v
wsl --list --all
wsl --shutdown
wsl -d Ubuntu
wsl -d Ubuntu -- uname -a
```

Windows puede ser el punto de entrada; Linux ejecuta las tareas.

```text
PowerShell → WSL → Bash → Docker
```

## 22. Automatización híbrida

```powershell
wsl -d Ubuntu -- bash -lc "cd ~/workspace/projects/dev-lab && ./scripts/status.sh"
```

Sirve para tareas programadas, scripts administrativos, CI local, mantenimiento, copias y comprobación de servicios.

## 23. Cómo queda el proyecto

```text
dev-lab/
├── compose.yaml
├── Makefile
├── .env.example
├── .gitignore
└── scripts/
    ├── bootstrap.sh
    └── status.sh
```

Conceptual:

```text
Windows → WSL2 / Ubuntu → Docker → PostgreSQL / Redis / aplicación → volúmenes
```

Git controla lo que debe ser reproducible.

## 24. Qué no automatizaría

Evitaría, sin confirmación:

- `docker compose down -v`
- `sudo apt upgrade -y` en cada arranque
- `git reset --hard` como rutina

Una automatización razonable es repetible, predecible, auditable y reversible cuando se puede. Si un script puede borrar datos, que lo haga de forma explícita.

## 25. Diagnóstico rápido

Orden fijo cuando algo falle.

**WSL**

```powershell
wsl --status
wsl -l -v
```

**Linux**

```bash
uname -a
systemctl status
```

**Docker**

```bash
docker version
docker compose version
```

**Contenedores y logs**

```bash
docker compose ps
docker compose logs --tail=100
```

**Recursos y red**

```bash
docker stats
df -h
free -h
docker network ls
```

Así se evita ir lanzando comandos al azar.

## 26. El objetivo

No basta con “Ubuntu instalado en Windows”. El destino es:

```text
Código
  ├── Git
  ├── configuración
  ├── scripts
  └── infraestructura → Docker → servicios reproducibles
```

La máquina deja de ser una configuración manual y pasa a ser una **descripción ejecutable del entorno**. Ese cambio importa más que memorizar cincuenta comandos.

## 27. Checklist

Cuando preparo un proyecto Linux/DevOps, quiero poder responder que sí:

- ¿Uso WSL2 y está actualizado?
- ¿systemd está disponible cuando lo necesito?
- ¿El código vive en el filesystem Linux?
- ¿Docker funciona desde WSL?
- ¿Los servicios están en Compose y los datos en volúmenes?
- ¿Las credenciales están fuera del repositorio y hay `.env.example`?
- ¿Hay automatización de tareas repetitivas y un mecanismo de diagnóstico?
- ¿La infraestructura está versionada y puedo reconstruir el entorno sin recordar cada paso?

Si es así, ya no se trata solo de usar Linux desde Windows: es un entorno de desarrollo reproducible.

## Conclusión

WSL2 puede ser más que una terminal Linux en Windows:

```text
Windows → WSL2 → Linux → Docker → servicios → automatización → Git → entorno reproducible
```

La idea central:

> **Instalar menos cosas directamente. Declarar más cosas como código. Automatizar lo repetitivo. Versionar la infraestructura.**

Ahí WSL deja de ser solo compatibilidad y funciona como un laboratorio DevOps.

### Referencias técnicas

- Microsoft: instalación y administración de WSL.
- Microsoft: `wsl.conf` y `.wslconfig`.
- Microsoft: systemd en WSL.
- Docker: backend WSL2 de Docker Desktop.
