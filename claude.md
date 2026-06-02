# 📌 Project: Receipt Processing MVP (Cloud-Only)

---

## 🎯 Goal

Build a cloud-only MVP system that:

1. Receives receipt images via Telegram bot
2. Processes the image in a cloud backend (Render)
3. Extracts structured data using Gemini Vision
4. Stores data in Neon PostgreSQL
5. Sends parsed receipt back to Telegram

---

## 🌐 Architecture (STRICT)

Telegram Bot
    ↓
FastAPI Backend (Render)
    ↓
Gemini Vision Parser (image → structured JSON)
    ↓
Neon PostgreSQL (persistent storage)
    ↓
Telegram Response

---

## ⚠️ Mandatory Constraints (MUST FOLLOW)

### 1. Cloud-only execution
- Do NOT design anything dependent on local execution
- Everything must run in deployed backend (Render)

---

### 2. No local filesystem persistence
- Do NOT save images or data to disk
- Use in-memory processing only
- Filesystem is ephemeral → data will be lost after restart

---

### 3. Minimal MVP ONLY
- Do NOT introduce extra features
- Do NOT optimize prematurely
- Do NOT design for scale yet

---

### 4. Separation of Concerns (STRICT)

Modules must be independent:

- Telegram: communication only
- Parser: extract structured data from image only
- DB: insert + query only
- Response: format and send message only

NO mixing responsibilities

---

### 5. Stateless backend
- Backend must NOT store state
- Only database is persistent

---

### 6. Free-tier friendly design
- Avoid heavy processing
- Avoid long-running tasks
- Keep response fast and simple

---

## 🧱 Required Modules

Backend must be structured in modules:

1. telegram_handler → webhook + message parsing
2. image_service → fetch image from Telegram
3. parser_service → image → structured JSON (Gemini Vision)
4. db_service → Neon DB interaction
5. response_service → send result back to Telegram

---

## 📦 Data Format (STRICT JSON)

Every receipt must follow:
{
"store_name": "",
"total_amount": "",
"date": "",
"items": [
{
"name": "",
"price": ""
}
]
}

---

## 🧪 Logging (MANDATORY)

Each module must log:

- input received
- output generated
- errors

Purpose: debugging + cloud tracing

---

## 🔁 Claude Workflow Rules (VERY IMPORTANT)

### 1. ALWAYS plan first

Before coding:
- explain approach
- list files to be created/modified
- identify risks

WAIT for approval.

---

### 2. One module at a time

DO NOT:
- implement multiple modules together
- jump ahead in plan

---

### 3. No assumptions

If requirements unclear:
- ASK before implementing

---

### 4. Small iterations only

Each step should:
- implement minimal functionality
- be testable independently

---

### 5. Preserve working code

DO NOT:
- rewrite existing modules unnecessarily
- break previous functionality

---

## 🚫 Forbidden Actions

- NO full system generation
- NO combining parsing + DB in one function
- NO local file storage
- NO background jobs (free tier incompatible)
- NO Docker optimization yet
- NO caching layer
- NO authentication system

---

## ✅ Expected Development Flow

1. Telegram Webhook
2. Image Retrieval
3. Vision Parser (Gemini)
4. Database Integration
5. Telegram Response
6. End-to-End flow

---

## 💡 Coding Style

- Prefer simple functions over classes
- Use clear naming
- Avoid abstraction unless necessary
- Readability > cleverness

---

## 📣 Communication Style

- Be concise
- Avoid long explanations
- Focus on task at hand
- Do not generate unnecessary code

---

## ✅ Definition of Done

Each module is complete when:

- Works independently
- Can be tested via API call
- Logs expected output
- Does not depend on other modules unnecessarily