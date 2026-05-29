# Hoja de Ruta — Hermes Agent

**Versión:** 2.0
**Última actualización:** mayo 2026
**Propósito:** guía detallada del proyecto para cualquier desarrollador.

> Basado en: `Hermes_Agent_Hoja_de_Ruta.md` (Drive) y `Hermes_Agent_SPEC_Desarrollador.md`
> Convención: 🔵 Hermes | 🟢 Cliente | 🟢🔵 Conjunto

---

## FASE 0 — Preparación (completada)

### Paso 1. 🟢🔵 Servidor aprovisionado ✅
- Ubuntu 24.04 LTS en 84.247.165.81 (chatbotph user)
- SSH puerto 23456, solo llaves (ED25519)
- UFW: solo 23456 abierto
- fail2ban configurado para sshd en puerto 23456
- docker-ce + docker-compose-plugin instalados
- Security Dashboard en localhost:5000 (SSH tunnel)
- **Para el desarrollador:** el servidor está en Contabo, mismo proveedor que el VPS original

### Paso 2. 🟢 Dominio ✅
- adminbot.info registrado en IONOS
- DNS: registro A apuntando a 84.247.165.81
- API IONOS configurada para cambios DNS programáticos
- **Para el desarrollador:** las credenciales de IONOS están en el Drive del proyecto

### Paso 3. 🟢 Activos digitales ✅
- Cuenta GitHub: Fabig76
- Repositorio: github.com/Fabig76/chatbotph
- Bot Telegram: @Santasofia01_bot (token en .env)
- Dominio: adminbot.info

---

## FASE 1 — MVP: Bot del administrador con consulta de saldo

### Paso 4. 🔵 Estructura del proyecto ✅
**Archivos:** `docker-compose.yml`, `Caddyfile`, `backend/Dockerfile`, `backend/requirements.txt`, `.env.example`

**Servicios Docker:**
- **caddy**: reverse proxy con HTTPS automático (Let's Encrypt). Escucha en 80/443.
- **api**: FastAPI con uvicorn, recarga automática en desarrollo. Puerto interno 8000.
- **worker**: mismo código que api, ejecuta tareas asíncronas (sync Sheets).
- **db**: PostgreSQL 16 con pgvector. Health check cada 5s. Puerto interno 5432.
- **redis**: Redis 7 con persistencia AOF. Health check cada 5s. Puerto interno 6379.

**Red Docker:** `hermes-net` (bridge), todos los servicios se comunican internamente.

**Volúmenes:** `postgres_data`, `redis_data`, `caddy_data`, `caddy_config`, `media_data`

**Para el desarrollador:**
- `docker compose up -d` levanta todo
- Caddy maneja SSL automáticamente
- No expongas puertos innecesarios al host

### Paso 5. 🔵 Modelo de datos ✅
**Archivos:** `backend/app/models/`, `backend/db/migrations/`

**Modelos SQLAlchemy (6 tablas):**

| Tabla | Propósito | Campos clave |
|-------|-----------|-------------|
| `units` | Unidades físicas | `code` (único), `kind` (apartment/house) |
| `residents` | Residentes | `unit_id` (FK), `full_name`, `document_id_hash` (SHA-256), `email`, `phone`, `is_owner` |
| `account_balances` | Saldos por unidad | `unit_id` (único FK), `balance_cop`, `as_of_date` |
| `sheet_sync_runs` | Auditoría de sync | `status`, `rows_total`, `rows_changed` |
| `admin_chats` | Whitelist Telegram | `chat_id` (PK), `role` (admin/portero), `active` |
| `audit_log` | Log append-only | `actor_kind`, `action`, `details_json` (JSONB) |

**Convenciones:**
- Todas las tablas tienen `id UUID PK`, `created_at`, `updated_at`
- Soft-delete con `deleted_at` solo donde se indique
- Identificadores en inglés, strings de usuario en español
- Migraciones con Alembic (async)
- pgvector extension habilitada para futuros embeddings RAG

**Para el desarrollador:**
- `alembic upgrade head` para migrar
- Los modelos están en `backend/app/models/`
- La sesión async se obtiene con `async_session()`

### Paso 6. 🔵 Google Sheets sync ✅ (código listo, falta service account)
**Archivos:** `backend/app/services/google_auth.py`, `backend/app/services/sheets_sync.py`, `backend/app/worker.py`, `scripts/test_sheets.py`

**Flujo de sincronización:**
1. Worker lee Google Sheets cada 1h (residentes) y 30min (saldos)
2. Compara hash de fila para detectar cambios
3. Hace upsert en la base de datos
4. Registra cada corrida en `sheet_sync_runs`

**Requisitos:**
- Service Account JSON en `credentials/google-service-account.json`
- Sheets compartidas con el email de la service account
- Formato esperado de Sheets: fila 1 = headers, datos desde fila 2

**Google Sheets esperadas:**
- **Residentes**: unidad, nombre, documento, email, teléfono, propietario
- **Saldos**: unidad, saldo, fecha_corte

**Seguridad:**
- Documentos de identidad: solo hash SHA-256, nunca en claro
- Service Account con permisos de solo lectura en Sheets

**Para el desarrollador:**
- Crear service account en console.cloud.google.com
- Descargar JSON a `credentials/google-service-account.json`
- Compartir Sheets con el email de la service account
- Probar con: `python scripts/test_sheets.py`

### Paso 7. 🔵 App FastAPI base ✅
**Archivos:** `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/db/base.py`, `backend/app/db/session.py`

**Endpoints:**

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/health` | GET | Health check con verificación de DB |
| `/telegram/webhook` | POST | Webhook del bot de Telegram |
| `/telegram/webhook/info` | GET | Estado del webhook |

**Configuración (Pydantic Settings):**
- Lee de variables de entorno + archivo `.env`
- Tipos validados: `list[str]` para CORS, `int` para chat_ids
- Valores por defecto seguros

**Para el desarrollador:**
- `uvicorn app.main:app --reload` para desarrollo
- Las settings se inyectan como singleton
- Usar `get_db()` como dependency en endpoints

### Paso 8. 🔵 Bot Telegram ✅
**Archivos:** `backend/app/services/telegram_bot.py`, `backend/app/api/telegram.py`, `backend/app/models/admin_chat.py`

**Comandos:**

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/start` | Bienvenida + comandos | `/start` |
| `/saldo <código>` | Consulta saldo de unidad | `/saldo T1-301` |
| `/help` | Ayuda | `/help` |

**Flujo de /saldo:**
1. Verifica whitelist (`admin_chats`)
2. Busca unidad por código (ILIKE)
3. Busca saldo en `account_balances`
4. Responde con: código, saldo formateado (COP), fecha de corte, última actualización
5. Si saldo != 0, muestra advertencia

**Seguridad:**
- Solo chat_ids en `admin_chats.active = true` pueden usar el bot
- Sin datos personales en las respuestas
- Formato de pesos colombianos ($ 1.234.567)

**Para el desarrollador:**
- Usar @BotFather para crear el bot y obtener token
- Configurar webhook: `https://adminbot.info/telegram/webhook`
- Agregar chat_id a `admin_chats` para autorizar

### Paso 9. 🔵 SSL + Dominio ✅
- Caddy con Let's Encrypt automático
- HTTP redirige a HTTPS (308 Permanent Redirect)
- adminbot.info resuelve a 84.247.165.81

**Para el desarrollador:**
- No tocar los certificados manualmente — Caddy los gestiona
- Los certificados se almacenan en el volumen `caddy_data`

### Paso 10. ⏳ Google Service Account
**Pendiente:** crear service account en GCP y compartir Sheet

**Pasos:**
1. Ir a https://console.cloud.google.com/apis/credentials
2. Crear proyecto "Hermes Agent"
3. Crear cuenta de servicio "hermes-agent-sync"
4. Generar clave JSON → guardar en `credentials/google-service-account.json`
5. Compartir Sheet con email de la service account

### Paso 11. ⏳ Pruebas de aceptación
**Pendiente:** agregar chat_id del administrador y probar /saldo en vivo

**Criterios de aceptación:**
- El saldo responde en menos de 2 segundos
- Los cambios en Sheets se reflejan en menos de 30 minutos
- HTTPS funciona correctamente
- `docker compose up -d` levanta todo desde cero

---

## Orquestación con Hermes Agent

Este proyecto se desarrolla con **Hermes Agent** como orquestador:

| Componente | Rol |
|------------|-----|
| **Hermes** | Planificación, delegación, code review |
| **Engram** | Memoria persistente entre sesiones (MCP, 19 tools) |
| **Code Review MCP** | Pre-commit review automático (skill) |
| **Git/GitHub** | Control de versiones |

**Flujo de trabajo:**
1. Hermes planifica y divide en tareas
2. Hermes implementa (con subagentes vía delegate_task)
3. Antes del commit: static security scan + subagente revisor independiente
4. Si pasa → commit con prefijo `[hermes-review]`
5. Engram guarda cada decisión y progreso para futuras sesiones

**Para el desarrollador:** si retomas el proyecto sin Hermes, los commits `[hermes-review]` indican que el código pasó por revisión automatizada.
