---
title: Attack Surface Dashboard
date: 2026-01-22
description: AI-powered multi-tenant vulnerability management platform — aggregates 13+ scan formats, runs autonomous agentic scans, and turns raw output into prioritised, exploitable findings with one-click reports.
tags: tools, ai, vulnerability-management, automation, python, fastapi, red-team
repo: https://github.com/antonytuff/attack-surface-dashboard
---

## Overview

**Attack Surface Dashboard** is a self-hosted, AI-augmented vulnerability management platform built for penetration testers and security teams. It ingests output from a broad range of scanners, normalises it into a finding model, and then layers AI analysis, deduplication, and reporting on top — all behind a multi-tenant web UI with role-based access.

Designed to replace the spreadsheet-driven post-engagement workflow with something that feels like a proper SOC-grade product, just lighter and runnable on a single host.

[**View on GitHub →**](https://github.com/antonytuff/attack-surface-dashboard)

---

## What it does

### Scan ingestion (13 parsers)
Nmap · Burp Suite · OWASP ZAP · Nessus · Nuclei · Shodan · and more — drop in any supported export and the parser stack normalises it into the unified `Finding` model with deduplication and severity mapping.

### Live scanning (38 integrations + MCP)
Run scans directly from the UI against 38 built-in scanner integrations, plus arbitrary external tooling via the **MCP (Model Context Protocol)** server interface — letting Claude/LLM-driven agents call shell tools as first-class actions.

### AI engine
- **10 specialist agents** for triage, exploitability assessment, and remediation suggestions
- Automatic priority scoring based on severity, asset value, and exploitability
- **Ghost Scan** — an autonomous chat terminal that runs an LLM decision loop with 66 chat tools to perform recon, enumeration, and follow-up scans without human intervention

### Workflow management
- 8-stage finding lifecycle (`new → triaged → confirmed → in-remediation → … → closed`)
- Assignment, due dates, overdue tracking, **MTTR** metrics, bulk operations
- Evidence attachments, tags, comments, manual finding creation
- **Audit log** for every user action (IP, timestamp, action) with a terminal-style admin view

### Reporting
One-click multi-format export: **PDF · DOCX · HTML · XLSX · CSV** with embedded severity charts via ReportLab.

### Multi-tenant + auth
- Client isolation with role-based access; a single user can belong to multiple clients
- Account lockout, configurable password complexity, API-key auth for CI/CD pipelines
- Per-user email notifications via SMTP

---

## Dashboard views

| | Page | Purpose |
|---|---|---|
| 1 | **Dashboard** | Overview stats, severity distribution, top vulns |
| 2 | **Attack Surface** | D3.js mind-map of targets, ports, technologies |
| 3 | **Clients** | Client organisation CRUD (admin) |
| 4 | **Scans** | Upload and manage scan files |
| 5 | **Vuln Scanner** | Live scanning with 38 integrations + MCP |
| 6 | **Findings** | Filter, assign, manage findings with overdue badges |
| 7 | **Analysis** | Run AI analysis and clustering |
| 8 | **AI Agents** | Multi-agent pipeline monitor with real-time progress |
| 9 | **Ghost Scan** | Full-page AI chat terminal — autonomous scanning |
| 10 | **Reports** | Generate / download PDF · DOCX · HTML · XLSX · CSV |
| 11 | **Users** | User management with lockout status (admin) |
| 12 | **Live Ops** | Real-time scan monitoring (WebSocket) |
| 13 | **Audit Logs** | Hacker-themed terminal-style audit trail (admin) |
| 14 | **Settings** | 8 tabs — API Keys · Scanner · AI · MCP · Tools · Security · Webhooks · Email |

---

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI (Python 3.10+) |
| ORM | SQLAlchemy + Alembic migrations |
| Database | SQLite (single-binary deployment) |
| Realtime | WebSockets |
| Reports | ReportLab |
| Frontend | Server-rendered HTML/CSS/JS, D3.js for graph viz |
| AI | Multi-agent LLM pipeline + MCP for tool calls |
| Deploy | Docker / `docker compose up -d` |

---

## Quickstart

```bash
git clone https://github.com/antonytuff/attack-surface-dashboard.git
cd attack-surface-dashboard

# Option A — native
pip install -r requirements.txt
python run.py

# Option B — docker
cp .env.example .env
docker compose up -d

# verify
curl http://localhost:8000/health
```

Default login: `admin` / `admin123`. Then point any supported scanner at the target and import the result file from **Scans → Upload**.

---

## Why it exists

Existing vulnerability-management tools are either enterprise-priced (Tenable, Rapid7) or shallow CSV viewers. This project compresses what a small pentest team actually needs — *parse → analyse → assign → report* — into a single Docker container, with an AI layer that turns raw scanner output into prioritised findings instead of a 4-figure-line CSV. Useful for:

- Internal red teams that want a persistent finding store across engagements
- Boutique pentest shops needing automated client deliverables
- Researchers experimenting with agentic offensive AI workflows
