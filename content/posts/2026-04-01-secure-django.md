---
title: "Pentesting web avanzado: 5 pasos para fallos que el scanner no ve"
slug: secure-django
publish_at: "2026-04-01T09:00:00-05:00"
status: published
tags:
  - AppSec
  - Pentesting
  - OWASP
excerpt: "Cómo priorizar acceso, lógica de negocio y configuración cuando el scan automático ya dijo que todo está limpio."
linkedin: false
linkedin_text: ""
---

Este texto es una guía de **auditoría autorizada**. Sirve para equipos que ya tienen alcance, entorno de pruebas y un dueño del riesgo. No es un recetario para atacar sistemas ajenos.

Los scanners (Burp Active Scan, Nessus, Nikto y similares) son buenos para ruido conocido: cabeceras flojas, software viejo, XSS obvio. Las pérdidas de dinero suelen estar en otro sitio: **objetos mal protegidos, reglas de negocio rotas y proxies que confían de más**.

Abajo va el orden en el que yo reviso una app web cuando el informe automático llegó “verde”.

## 1. Inventario de lo que el HTML no enseña

Un crawler solo sigue enlaces. Lo peligroso a menudo vive en JS empaquetado, rutas legacy y docs de API olvidadas.

Qué revisar, con permiso y en el entorno acordado:

- Directorios y rutas que el front ya no muestra.
- Bundles JS: URLs internas, feature flags, clientes de API.
- Contratos abiertos: `/openapi.json`, `/swagger`, `/v3/api-docs`.

**Por qué el scanner falla:** no adivina un endpoint que nadie linkea.

**Qué arreglar:** inventario de rutas, auth en la documentación interna, y apagar lo que ya no se usa.

## 2. Control de acceso, no solo “el login funciona”

IDOR y subida de privilegios siguen pagando incidentes. El patrón es simple: el usuario autenticado puede leer o mutar el objeto de otro.

Señales:

- IDs en path, query o JSON sin comprobar pertenencia en servidor.
- El mismo recurso acepta un verbo HTTP que nadie pensó (un `GET` endurecido y un `POST` flojo).
- Confiar en cabeceras de rewrite (`X-Original-URL` y primas) para decidir si algo es admin.

**Remediación:** autorización por objeto en el backend, tests de “usuario A no toca recurso de B”, y negar por defecto cualquier cabecera de proxy que no hayáis puesto vosotros.

## 3. Lógica de negocio

Aquí el scanner es ciego. Cupones, saldos, gift cards, checkout y puntos de fidelización no tienen firma en OWASP ZAP.

Preguntas útiles:

- ¿Puedo aplicar dos veces el mismo descuento si envío las peticiones juntas?
- ¿El precio viaja en el cliente y el servidor lo cree?
- ¿Un valor negativo o un estado “cancelado” rompe el flujo a mi favor?

**Remediación:** invariantes en servidor, idempotencia en canjes, y pruebas de carrera en los flujos que mueven dinero.

## 4. Proxies, caché y cabeceras de confianza

`X-Forwarded-Host`, `X-Forwarded-For`, `X-Original-URL` y primas son útiles detrás de un edge que controláis. Si la app las cree en crudo, alguien las va a rellenar.

Efectos típicos: enlaces mal generados, cache poisoning, bypass de “solo red interna”.

**Remediación:** el reverse proxy pisa esas cabeceras; la app no las usa para auth ni para construir URLs públicas si no están firmadas por infra.

## 5. Rate limit y WAF como capa, no como diseño

Limitar por IP es un parche. Ofuscación de JSON, aliases de GraphQL y cache-busters existen porque el control está en el borde, no en el dominio.

Un WAF bien tunado reduce basura. No sustituye:

- lockout o backoff en login,
- cuota por cuenta, no solo por IP,
- validación estricta del schema.

## Cómo usarlo en un equipo

1. Alcance por escrito.
2. Recorrer flujos de negocio con dos usuarios de verdad.
3. Anotar impacto (datos, dinero, reputación), no el nombre de la CVE.
4. Parchear en código y config; volver a probar el mismo caso.

Los porcentajes de “el scanner pilla el 30%” son marketing. Lo medible es: **cuántos de vuestros flujos de dinero y de identidad tienen test de autorización**.

Si quieres una revisión con alcance y entregable accionable, [escribe](../contact.html).
