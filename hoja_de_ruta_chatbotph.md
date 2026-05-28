# Hoja de Ruta — ChatbotPH

**Versión:** 1.0
**Fecha:** mayo 2026
**Propósito:** guía paso a paso del proyecto, usando Hermes + Engram + GitHub.

**Convención:**
- 🔵 Pasos que ejecuta Hermes (yo)
- 🟢 Pasos que ejecutas tú
- 🟢🔵 Pasos conjuntos

---

## FASE 0 — Preparación (casi lista)

### Paso 1. 🟢🔵 Servidor y dominio ✅
- ✅ Servidor Ubuntu 24.04 en 84.247.165.81
- ✅ SSH puerto 23456, solo llaves
- ✅ Usuario chatbotph con sudo
- ✅ UFW + fail2ban
- ✅ Docker + Docker Compose instalados
- ✅ Repo clonado: /home/chatbotph/chatbotph/
- ✅ Security Dashboard en :5000 (solo SSH tunnel)
- ✅ DNS adminbot.info → 84.247.165.81 (propagándose)

### Paso 2. 🟢🔵 SSL y dominio
- ⏳ Cuando el DNS se propague, configurar SSL (Let's Encrypt o Cloudflare)
- ⏳ Nginx como reverse proxy

### Paso 3. 🟢 Activos digitales
- ✅ Dominio adminbot.info (Ionos)
- ⏳ API keys de OpenRouter para Hermes 4 70B
- ⏳ API key de IONOS DNS (ya la tienes)

---

## FASE 1 — MVP: Chatbot PH público

> Objetivo: tener un chatbot web público que responda preguntas sobre Ley 675/2001 con RAG.

### Paso 4. 🔵 Estructura del proyecto
- Crear docker-compose.yml con: web (Next.js), api (FastAPI), db (PostgreSQL+pgvector), redis, nginx
- Estructura de carpetas según SPEC
- Commit y push a GitHub

### Paso 5. 🔵 Modelo de datos
- Tablas: documents, chunks (con vector embedding), sessions, messages, feedback
- Migraciones con Alembic
- Guardar decisión en Engram

### Paso 6. 🔵 Pipeline de ingesta jurídica
- Scripts para cargar Ley 675, decretos, sentencias
- Chunking por artículos con metadatos
- Embeddings con BGE-M3
- Almacenar en pgvector

### Paso 7. 🔵 API de chat con RAG
- Endpoint POST /api/chat
- Clasificador de dominio (¿es PH?)
- Recuperación híbrida (vector + BM25)
- Re-ranker
- Generador Hermes 4 70B vía OpenRouter
- Verificador de citas
- Rate limiting por IP

### Paso 8. 🔵 Frontend web
- Next.js + Tailwind, estilo ChatGPT minimalista
- Sin registro, límite por IP
- Botón de feedback
- Aviso legal y disclaimer visibles

### Paso 9. 🟢🔵 Dominio y HTTPS
- Una vez propagado el DNS:
  - Configurar Nginx + Let's Encrypt (SSL)
  - O Cloudflare proxy + SSL
- https://adminbot.info funcionando

### Paso 10. 🟢🔵 Pruebas de aceptación Fase 1
- Pregunta sobre Ley 675 responde con cita al artículo
- Pregunta fuera de PH es rechazada
- Límite de consultas por IP funciona
- HTTPS funciona
- docker compose up -d levanta todo

---

## FASE 2 — Hardening legal y corpus completo

### Paso 11. 🔵 Carga completa del corpus
- Ley 675/2001 completa
- Ley 2079/2021 (modificaciones)
- Decreto 1060/2009
- Decreto 1077/2015
- 30+ sentencias clave de Corte Constitucional
- 100+ conceptos Minvivienda, SIC, DIAN

### Paso 12. 🔵 Refinar RAG
- Ajustar chunking jurídico
- Optimizar recuperación
- Pruebas con 100 preguntas curadas
- Tasa de "no sé" < 15%

### Paso 13. 🟢🔵 Aspectos legales
- EIPD documentado
- Aviso de privacidad público
- Términos y condiciones
- Disclaimer visible en cada respuesta
- Registro RNBD si aplica

### Paso 14. 🟢🔵 Pruebas de aceptación Fase 2
- Beta cerrada con 10 administradores reales
- Feedback recogido
- Tasa de alucinación < 5%
- Latencia p95 < 10 segundos

---

## FASE 3 — Registro y funciones avanzadas

### Paso 15. 🔵 Registro de usuarios
- Login opcional (email + OTP)
- Historial de conversaciones por usuario
- Más consultas para registrados

### Paso 16. 🔵 Mejoras al chat
- Memoria de conversación
- Descarga PDF de respuestas
- Preguntas frecuentes curadas

### Paso 17. 🟢🔵 Lanzamiento público
- LinkedIn + grupos de administradores
- Contenido en redes
- Medición de tráfico

---

## Cómo usar esta lista

1. Cada paso se completa antes de pasar al siguiente
2. Cada paso terminado → commit a GitHub + guardar en Engram
3. Si surge una idea nueva → va a "Fase 4" o posterior
4. No saltar pasos — la Fase 1 existe para validar la arquitectura antes de lo visible

---

## Checklist

- [ ] **Fase 0** — Pasos 1 a 3 (Preparación) → 70% completo
- [ ] **Fase 1** — Pasos 4 a 10 (MVP chatbot público)
- [ ] **Fase 2** — Pasos 11 a 14 (Hardening legal + corpus)
- [ ] **Fase 3** — Pasos 15 a 17 (Registro y lanzamiento)
