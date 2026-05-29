# Hoja de Ruta — Hermes Agent

**Versión:** 1.0
**Fecha:** mayo 2026
**Propósito:** guía paso a paso del proyecto. Seguir el orden exacto.

**Basado en:** Hermes_Agent_Hoja_de_Ruta.md (Drive)
**Convención:**
- 🔵 Hermes
- 🟢 Tú
- 🟢🔵 Conjunto

---

## FASE 0 — Preparación ✅ Completada

- ✅ Servidor Ubuntu 24.04 (84.247.165.81:23456)
- ✅ SSH solo llave, UFW, fail2ban
- ✅ Docker + Docker Compose
- ✅ Repo GitHub Fabig76/chatbotph
- ✅ DNS adminbot.info → 84.247.165.81
- ✅ Security Dashboard (localhost:5000)
- ⏳ Respaldos automáticos (pendiente)

## FASE 1 — MVP: Bot del administrador con consulta de saldo

### Paso 8. 🔵 Aprovisionar el servidor ✅
### Paso 9. 🔵 Configurar dominio y HTTPS (⏳ SSL pendiente)
### Paso 10. 🔵 Crear repositorio y estructura base 🔜 **SIGUIENTE**
- [ ] docker-compose.yml (caddy, api, db, redis)
- [ ] Estructura carpetas (backend/, frontend/, corpus/, scripts/, docs/)
- [ ] .env.example con variables

### Paso 11. 🔵 Modelo de datos base
- [ ] Tablas: units, residents, account_balances, sheet_sync_runs, audit_log
- [ ] Migraciones Alembic

### Paso 12. 🔵 Conectar Google Sheets
- [ ] Cuenta de servicio Google
- [ ] Job de sincronización cada 30-60 min

### Paso 13. 🔵 Bot Telegram administrador
- [ ] BotFather + webhook
- [ ] Comando /saldo <unidad>

### Paso 14. 🟢🔵 Pruebas de aceptación Fase 1

---

## FASE 2 — PWA del residente y chat del reglamento
## FASE 3 — Reservas, trasteos y portería
## FASE 4 — Paz y salvo con QR
## FASE 5 — Gestión de correo
## FASE 6 — Cierre, documentación y entrega
