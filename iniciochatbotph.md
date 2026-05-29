# ChatbotPH — Documentación del Servidor

## Información General

- **Proyecto:** ChatbotPH — Asistente jurídico de Propiedad Horizontal (Colombia)
- **Dominio:** adminbot.info (Ionos)
- **Repositorio GitHub:** https://github.com/Fabig76/chatbotph
- **Orquestador:** Hermes Agent
- **Memoria persistente:** Engram v1.15.15 (MCP, 19 herramientas)

## Servidor

| Dato | Valor |
|------|-------|
| IP | 84.247.165.81 |
| Hostname | vmi3332458 |
| OS | Ubuntu 24.04.4 LTS |
| RAM | 7.8 GB |
| Disco | 145 GB SSD |
| CPU | (por definir) |
| SSH Port | 23456 |
| Usuario | chatbotph |
| Acceso root | Deshabilitado SSH |

### Acceso SSH

**Desde tu Mac:**
```bash
ssh -p 23456 chatbotph@84.247.165.81
```

**Desde Hermes (VPS Contabo):**
```bash
ssh chatbotph
```

## Seguridad Aplicada

| Medida | Estado |
|--------|--------|
| SSH puerto personalizado | ✅ 23456 |
| Autenticación solo con llaves | ✅ PasswordAuthentication no |
| Root deshabilitado | ✅ PermitRootLogin no |
| UFW Firewall | ✅ Solo puerto 23456 abierto |
| fail2ban | ✅ Configurado para sshd en puerto 23456 |
| Socket systemd SSH desactivado | ✅ Para evitar conflicto de puerto |
| Lynis | ✅ Instalado |
| RKhunter | ✅ Instalado |

### Puertos

| Puerto | Servicio | Acceso |
|--------|----------|--------|
| 23456/tcp | SSH | Público (solo llaves) |
| 5000/tcp | Security Dashboard | Solo localhost (vía SSH tunnel) |

## Security Dashboard

- **URL:** http://127.0.0.1:5000 (solo accesible por SSH tunnel)
- **Acceso:** `ssh -L 5000:localhost:5000 -p 23456 chatbotph@84.247.165.81`
- **Monitoreo:** CPU, RAM, Disco, Fail2ban, Intentos SSH, Alertas, Conexiones externas
- **Escáner:** Botón "Iniciar Escaneo Completo" — ejecuta Lynis + RKhunter
- **Servicio:** systemd — `security-dashboard.service`
- **Ubicación:** `/home/chatbotph/security-dashboard/`

## Ecosistema de Herramientas

### Hermes (VPS Contabo)
- Orquestador principal del proyecto
- Skills disponibles: engram-memory, dispatching-parallel-agents, github-code-review, etc.

### Engram (Memoria Persistente)
- v1.15.15, MCP Server, 19 herramientas
- DB: `~/.engram/engram.db`
- Compartido entre Hermes, OpenCode y Codex

### OpenCode Desktop
- Instalado en `/opt/OpenCode/`
- Repo: anomalyco/opencode

### Kali Lab
- Contenedor Docker en Contabo VPS
- Puerto 7681, login kali/kali
- Herramientas: nmap, recon-ng, sublist3r, whatweb, dnsrecon, sslscan, theHarvester, etc.

## Proyecto ChatbotPH

### Stack Técnico Planeado

```
Frontend: Next.js + Tailwind (tipo ChatGPT)
Backend: FastAPI (Python)
Base datos: PostgreSQL 16 + pgvector
Cache/Cola: Redis
LLM Gateway: Hermes 4 70B vía OpenRouter
Embeddings: BGE-M3 self-host
Proxy: Nginx + Cloudflare
Despliegue: Docker Compose
Documentos: Python workers
```

### Arquitectura RAG

1. Clasificador de dominio (¿es PH?)
2. Recuperación híbrida (vector + BM25)
3. Re-ranker
4. Generador con política cerrada
5. Verificador de citas
6. Post-procesador con disclaimers

### Documentos del Proyecto

Disponibles en Drive:
- `chatbotph_spec_driven_development.md` — Especificación SDD completa
- `chatbotph_arquitectura_final.md` — Arquitectura técnica
- `proyecot bot ph.md` — Propuesta técnica refinada
- `voy a crear un bot para reponder a los administrad.md` — Idea original
- `Hermes_Agent_SPEC_Desarrollador (1).md` — SPEC del agente
- `-Paso-Ques-Quhaceresultadoesperado (1).csv` — Tareas planificadas

### Dominio

- **adminbot.info** — comprado en Ionos
- Pendiente: configuración DNS, SSL, despliegue

## Historial de Configuración

### 2026-05-28
- Creación del repositorio chatbotph en GitHub
- Instalación de OpenCode Desktop
- Configuración de Engram como MCP server

### 2026-05-29
- Configuración del servidor chatbotph (84.247.165.81)
- SSH key generada y configurada
- fail2ban instalado y configurado
- UFW activado
- Security Dashboard instalado en puerto 5000
- Escáner de seguridad con botón manual
- Puerto 5000 cerrado (solo localhost)
- Documentación creada en /chatbotph/iniciochatbotph.md
