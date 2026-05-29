# Hermes Agent

**Asistente digital para la administración de propiedad horizontal (conjuntos residenciales en Colombia).**

Sistema que centraliza la comunicación entre administradores, portería y residentes, automatizando tareas repetitivas como consulta de saldos, reservas de zonas comunes, trasteos, generación de paz y salvos con QR, y gestión de correo.

## Stack Tecnológico

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| Backend | Python 3.12 + FastAPI | API REST asíncrona |
| Frontend | PWA (Next.js / HTML+Alpine.js) | Interfaz de residentes |
| Base de datos | PostgreSQL 16 + pgvector | Datos + embeddings RAG |
| Cache/Colas | Redis 7 | Rate limiting, tareas async |
| Proxy/TLS | Caddy 2 | HTTPS automático, reverse proxy |
| Bot | python-telegram-bot v21+ | Canal administrador/portería |
| IA | Claude API (Anthropic) | RAG sobre reglamentos, clasificación de correo |
| Google APIs | Sheets, Gmail, Calendar | Sincronización, correo, agenda |
| Infra | Docker Compose + Ubuntu 24.04 LTS | Despliegue reproducible |

## Arquitectura

```
┌─ Usuarios ─────────────────────────────────────────────────┐
│  Administrador (Telegram)  │  Portería (Telegram)          │
│  Residentes (PWA web)      │  Notarías (página pública QR)  │
└────────────────────────────┴────────────────────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │    Caddy       │  ← HTTPS + reverse proxy
                   │  (puerto 443)  │
                   └───────┬────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        /api/*        /telegram/*    /verify/*
      (FastAPI)    (Bot Webhook)   (QR público)
              │
      ┌───────┴───────┐
      │               │
      ▼               ▼
  PostgreSQL       Redis
  + pgvector       (cache + colas)
```

## Fases del Proyecto

### FASE 0 — Preparación (✅ Completada)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 1 | Servidor Ubuntu 24.04 en Contabo / dedicado | ✅ |
| 2 | SSH puerto 23456, solo llaves, UFW, fail2ban | ✅ |
| 3 | Docker + Docker Compose instalados | ✅ |
| 4 | DNS adminbot.info → servidor | ✅ |
| 5 | Security Dashboard en localhost:5000 | ✅ |

### FASE 1 — MVP: Bot del administrador con consulta de saldo (Parcial)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 6 | docker-compose.yml con 5 servicios (caddy, api, worker, db pgvector, redis) | ✅ |
| 7 | Modelo de datos: Units, Residents, AccountBalances, SheetSyncRuns, AuditLog, AdminChats + Alembic | ✅ |
| 8 | Google Sheets sync: servicio de auth + sync de residentes y saldos | ✅ Código listo |
| 9 | Bot Telegram @Santasofia01_bot con /start, /saldo, /help | ✅ |
| 10 | SSL/HTTPS con Caddy + Let's Encrypt | ✅ |
| 11 | Google Service Account JSON | ⏳ Pendiente |
| 12 | Pruebas de aceptación con usuario real | ⏳ Pendiente |

### FASE 2 — PWA del residente y chat del reglamento
### FASE 3 — Reservas, trasteos y portería
### FASE 4 — Paz y salvo con QR
### FASE 5 — Gestión de correo Gmail

## Estructura del Repositorio

```
hermes-agent/
├── backend/
│   ├── app/
│   │   ├── api/               # Endpoints FastAPI
│   │   │   ├── health.py      # GET /health — health check
│   │   │   └── telegram.py    # POST /telegram/webhook — webhook del bot
│   │   ├── core/
│   │   │   └── config.py      # Settings con Pydantic v2
│   │   ├── db/
│   │   │   ├── base.py        # Base SQLAlchemy + TimestampMixin
│   │   │   └── session.py     # Async engine + session factory
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── unit.py        # Units — unidades físicas del conjunto
│   │   │   ├── resident.py    # Residents — residentes (hash de documento)
│   │   │   ├── account_balance.py  # Saldos por unidad
│   │   │   ├── sheet_sync_run.py   # Auditoría de sincronización
│   │   │   ├── audit_log.py        # Log de cambios sensibles
│   │   │   └── admin_chat.py       # Whitelist de chats autorizados
│   │   ├── services/
│   │   │   ├── google_auth.py # Google Service Account auth
│   │   │   ├── sheets_sync.py # Sincronización Sheets → DB
│   │   │   └── telegram_bot.py # Handlers del bot (/start, /saldo)
│   │   ├── worker.py          # Tareas asíncronas (sync cada 1h/30min)
│   │   └── main.py            # FastAPI app + lifespan
│   ├── db/migrations/
│   │   ├── env.py             # Alembic async config
│   │   └── 001_initial.py     # Migración inicial (6 tablas + pgvector)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic.ini
├── credentials/               # Service account JSON (gitignored)
├── scripts/
│   └── test_sheets.py         # Script para probar conexión Google Sheets
├── docker-compose.yml         # Orquestación de servicios
├── Caddyfile                  # Reverse proxy + TLS
├── .env.example               # Variables de entorno (plantilla)
└── hoja_de_ruta_chatbotph.md  # Guía detallada del proyecto
```

## Despliegue

```bash
# 1. Clonar
git clone git@github.com:Fabig76/chatbotph.git
cd chatbotph

# 2. Configurar entorno
cp .env.example .env
# Editar .env con credenciales reales

# 3. Iniciar servicios
docker compose up -d

# 4. Ejecutar migraciones
docker compose exec api alembic upgrade head

# 5. Salud del sistema
curl https://adminbot.info/api/health
```

## Variables de Entorno

Ver `.env.example` para la lista completa. Las principales:

| Variable | Descripción |
|----------|-------------|
| `POSTGRES_PASSWORD` | Contraseña de la base de datos |
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Ruta al JSON de service account |
| `ANTHROPIC_API_KEY` | API key de Claude (para RAG) |
| `CORS_ORIGINS_RAW` | Orígenes CORS permitidos |

## Modelo de Datos

### units
Unidades físicas del conjunto (apartamentos, casas). Contiene `code` único (ej: "Torre 1 - Apto 301").

### residents
Residentes, réplica operativa desde Google Sheets. El documento de identidad **nunca se almacena en claro** — solo su hash SHA-256 y los últimos 4 dígitos.

### account_balances
Caché de saldos por unidad sincronizada desde Sheets. Incluye fecha de corte del contador para control de vigencia (máx 15 días).

### admin_chats
Whitelist de chat_ids de Telegram autorizados para usar el bot. Soporta roles: `admin` y `portero`.

### audit_log
Registro append-only de cambios sensibles (aprobaciones, emisiones de paz y salvo, etc.).

### sheet_sync_runs
Auditoría de cada corrida de sincronización con Google Sheets.

## Bot de Telegram

**Usuario:** @Santasofia01_bot

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida y comandos disponibles |
| `/saldo <código>` | Consulta el saldo de una unidad (ej: `/saldo T1-301`) |
| `/help` | Ayuda |

## Seguridad

- **Documentos de identidad**: solo hash SHA-256, nunca en claro
- **Cifrado en reposo**: PostgreSQL datos sensibles
- **HTTPS**: Caddy con Let's Encrypt automático
- **Firewall**: UFW, solo puerto 23456 (SSH) y 80/443 (web)
- **Autenticación SSH**: solo con llaves, root deshabilitado
- **Whitelist Telegram**: solo chat_ids autorizados pueden usar el bot
- **Aprobación obligatoria**: ninguna acción sensible sin confirmación del admin
- **Rate limiting**: por IP para el chat público (cuando esté disponible)

## Desarrollado con

- **Orquestación**: Hermes Agent
- **Control de versiones**: Git + GitHub
- **Code Review**: Hermes Agent Code Review MCP (pre-commit, static scan, subagente revisor independiente)
- **Memoria persistente**: Engram (MCP con 19 herramientas)
