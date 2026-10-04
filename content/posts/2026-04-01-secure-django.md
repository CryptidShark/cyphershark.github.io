---
title: "Pentesting web avanzado: 5 pasos para encontrar fallos críticos que los scanners automáticos nunca detectan"
slug: secure-django
publish_at: "2026-04-01T09:00:00-05:00"
status: published
tags:
  - Pentesting
  - AppSec
  - Técnicas avanzadas
excerpt: "AppSec, lógica de negocio, APIs y OWASP. Técnicas manuales para detectar vulnerabilidades reales más allá de los scanners."
linkedin: false
linkedin_text: ""
---

Los scanners automáticos (Burp Suite Active Scan, Nessus, Nikto) son útiles para hallazgos ruidosos pero superficiales. Las vulnerabilidades que realmente ponen en riesgo un negocio suelen estar ocultas en **lógica de negocio, validaciones inconsistentes y fallos de configuración humana**. Aquí te muestro 5 pasos con técnicas que he usado en auditorías reales.

## 1. Mapeo de funcionalidades ocultas y parámetros olvidados

Los desarrolladores a menudo dejan endpoints de depuración, parámetros legacy o rutas no indexadas. Un scanner no los encuentra si no están enlazados desde el HTML.

### Acción clave

- Fuzzear rutas con listas como `raft-medium-directories.txt` o `common.txt` (ffuf, gobuster).
- Revisar **JavaScripts empaquetados** en busca de rutas internas. Ejemplo: usar `grep -roh "https?://[^\"]*" *.js`.
- **Dato poco conocido:** muchas APIs exponen un `/swagger`, `/openapi.json` o `/v3/api-docs` sin autenticación. Busca esos endpoints.

## 2. Validación de control de acceso horizontal y vertical (IDOR + Privilege Escalation)

Los IDOR (Insecure Direct Object References) siguen siendo la joya del pentesting manual. Pero lo que pocos hacen es combinarlos con cambios de método HTTP.

### Pasos concretos

- Interceptar peticiones con IDs numéricos o UUID y probar variaciones (id=1→2, UUID incremental).
- **Payload poco conocido:** si el ID está en JSON: `{"user_id": 123}`, probar `{"user_id": {"$ne": null}}` (inyección NoSQL en APIs).
- Cambiar `GET /profile/123` a `POST /profile/123` con cuerpo vacío. A veces el método no está bien restringido.
- Probar cabeceras como `X-Original-URL: /admin` o `X-Rewrite-URL: /admin` para saltar reglas de autenticación.

## 3. Ataque a flujos de negocio (Business Logic Abuse)

Aquí los scanners son ciegos. Se trata de violar la lógica esperada: descuentos acumulables, puntos de fidelización, procesos de checkout.

### Técnicas clave

- En carritos de compra: agregar un producto, cambiar la cantidad a valor negativo, o repetir la misma solicitud de cupón varias veces.
- **Ejemplo real:** una plataforma de gift cards permitía canjear la misma tarjeta dos veces si se enviaban dos peticiones en paralelo (race condition). Usa Turbo Intruder de PortSwigger.
- Revisar parámetros de precio ocultos en HTML: a veces el precio está en un campo `value="199.99"` pero el backend no lo valida.

## 4. Explotación de cabeceras HTTP mal configuradas y cache poisoning

Pocos pentesters explotan a fondo cabeceras como `X-Forwarded-Host`, `X-Forwarded-Scheme` o `X-Original-URL` para manipular cachés o redirigir a sitios maliciosos.

### Pruebas manuales

- Envía `X-Forwarded-Host: evil.com` y observa si los enlaces generados por la app usan ese valor (redirección abierta en caché).
- Si la app usa `X-Forwarded-For` para whitelist de IPs, prueba `X-Forwarded-For: 127.0.0.1` o `X-Real-IP: 127.0.0.1`.
- **Dato poco conocido:** algunos proxies internos confían en `X-Original-URL` para reescribir rutas. Un atacante puede acceder a `/admin` enviando `X-Original-URL: /admin` en una petición a una ruta pública.

## 5. Bypass de rate limiting y WAF con técnicas de ofuscación

Los rate limits basados en IP se saltan fácilmente con listas de proxies o rotación de IP. Pero también hay trucos de ofuscación para evitar WAFs en login/registro.

### Métodos prácticos

- Agregar parámetros aleatorios: `/login?nocache=123456789` para que el WAF no agrupe las peticiones.
- Cambiar el caso de caracteres en JSON: `{"userName": "admin"}` vs `{"username": "admin"}`.
- En GraphQL, usar alias múltiples para ejecutar muchas consultas en una sola petición:

```
{
  a: user(id:1){ email },
  b: user(id:2){ email },
  c: user(id:3){ email }
}
```

- **Payload para WAFs de SQLi:** usar comentarios anidados `/*!50000 UNION/*!/*!/*!/*! SELECT*/`.

## Conclusión: el valor del pentesting manual

Los scanners encuentran el 30% de las vulnerabilidades. El 70% restante —fallos de lógica, negocio y configuración— solo se descubren con pensamiento crítico y conocimiento profundo del framework subyacente. Empresas que entienden esto invierten en auditorías combinadas.

Si necesitas ayuda para auditar tu aplicación o capacitar a tu equipo en estas técnicas, [contáctame](../contact.html).
