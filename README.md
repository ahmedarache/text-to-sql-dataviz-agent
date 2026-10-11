# 📊 Enterprise Text-to-SQL & Automated DataViz Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![n8n Self-Hosted](https://img.shields.io/badge/n8n-Self--Hosted-orange.svg)](https://n8n.io/)
[![Database: Neon PostgreSQL](https://img.shields.io/badge/Database-Neon_PostgreSQL-00e599.svg)](https://neon.tech/)

An autonomous, event-driven analytics assistant that translates plain English/French natural language questions into secure PostgreSQL queries and auto-renders interactive charts. Built with **n8n**, **Groq/OpenAI LLMs**, **Neon PostgreSQL**, **JavaScript AST Safety Guardrails**, and **Streamlit**.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Frontend ["Streamlit Dashboard"]
        UI[Chat Interface & Auto-Viz]
    end

    subgraph n8n ["n8n Workflow (Production)"]
        Webhook[Webhook Trigger] --> Schema[Schema Fetcher]
        Schema --> AI[AI Agent LLM]
        AI --> Validator[JS AST & Safety Validator]
        Validator -->|Safe SQL Only| PG[PostgreSQL Execution]
        PG --> Respond[Respond to Webhook]
    end

    subgraph Database ["Neon PostgreSQL"]
        Neon[(Neon DB: customers & orders)]
    end

    UI -->|HTTP POST JSON| Webhook
    AI -.->|Inspects DB Schema| Neon
    PG -->|Executes Query| Neon
    Respond -->|JSON Data Payload| UI


## 🛠️ Core Stack & Implementation Details

### 1. Database Layer (Neon PostgreSQL)
Hosted on serverless Neon PostgreSQL with structured relational tables (`customers` and `orders`). Relational keys and column data types are configured to allow dynamic schema extraction.

### 2. Orchestration Layer (n8n Self-Hosted)
Handles event-driven routing between chat UI requests, metadata generation, LLM prompting, safety parsing, and database query execution.

* **Webhook Trigger:** Exposes production `/webhook/` endpoint accepting incoming chat requests.
* **Schema Fetcher:** Dynamically queries `information_schema` to inject live table structures, types, and foreign key relationships directly into the LLM system prompt.
* **AI Agent Node:** Translates natural language into structured PostgreSQL queries using high-performance chat models (Groq / OpenAI).

### 3. Security Guardrail (JS AST/Safety Validator)
A custom n8n Code Node (JavaScript) operating on a zero-trust model:
* Strips markdown code fences (` ```sql `) and normalizes whitespace.
* Performs tokenization and uppercase normalization.
* Scans against a strict array of blocked modification/destruction keywords: `DROP`, `DELETE`, `TRUNCATE`, `ALTER`, `INSERT`, `UPDATE`, `CREATE`, `GRANT`, `REVOKE`.
* Returns a structured payload: `{"is_safe": boolean, "sql": string}`. Non-SELECT queries are blocked before hitting the database.

### 4. Frontend Dashboard (Streamlit)
* Connected via `requests.post()` calls to the n8n production webhook endpoint.
* Unpacks payload fields (`is_safe`, `sql`, and result rows).
* **Collapsible Developer View:** Displays validated SQL statements for auditability.
* **Automated DataViz Heuristic:** Evaluates DataFrame schemas to auto-select rendering styles:
  * **Time-Series Line Charts:** Triggered when datetime and numerical columns coexist.
  * **Categorical Bar Charts:** Triggered for categorical aggregations.
  * **Interactive Data Tables:** Rendered via Pandas dataframes for raw listings.
