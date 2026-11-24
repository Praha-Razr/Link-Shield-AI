# LINKSHIELD AI

> **Rajasthan Police Cyber Security Hackathon 2026**  
> **Problem Statement PS01:** *Scam Message & Phishing Link Detection with Fake Loan / Investment App and Fraudulent Website Analysis*  
> **Tagline:** *Detect. Explain. Investigate. Protect.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![FastAPI: 0.165](https://img.shields.io/badge/FastAPI-0.165-teal.svg)](https://fastapi.tiangolo.com/)
[![React: 18.3](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://reactjs.org/)
[![Vite: 5.4](https://img.shields.io/badge/Vite-5.4-purple.svg)](https://vitejs.dev/)
[![Tailwind: 3.4](https://img.shields.io/badge/TailwindCSS-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![National Cyber Helpline: 1930](https://img.shields.io/badge/Helpline-1930-rose.svg)](https://cybercrime.gov.in/)

---

## 🛡️ Executive Summary

**LINKSHIELD AI** is a production-grade cybercrime intelligence and triage platform built specifically for the **Rajasthan Police Cyber Crime Branch** and Indian citizens. It bridges the critical operational gap between citizen-reported phishing messages and complex syndicate investigations:

1. **For Citizens (Citizen Mode):** Intuitive "Check something" interface for SMS, WhatsApp, Telegram, suspicious links, and investment/loan portals. Provides instant risk ratings, plain-language explanations in English and Hindi, and direct safety instructions (including one-click connection to the National Cyber Crime Helpline `1930`).
2. **For Cyber Officers (Officer Mode):** Comprehensive cyber intelligence workstation featuring multi-factor explainable risk scoring, SSRF-immune static DOM analysis, campaign relationship graphing (clustering syndicates by shared domains, UPI IDs, bank accounts, and phone numbers), threat heat-lists, evidence-grounded AI assistant interrogation, and 1-click official PDF dossiers.

---

## 🌐 Deployed Version (Live Cloud Demo)

LinkShield AI is configured for cloud deployment with the frontend on Vercel and the backend on Render.

* **Live Web Portal (Vercel):** `https://your-app.vercel.app` *(Placeholder - update with your deployed URL)*
* **Backend API & Health Check (Render):** `https://your-backend.onrender.com/api/health` *(Placeholder - update with your deployed URL)*
* **Deployment Guide:** See [DEPLOYMENT.md](file:///c:/My_Files/LinkShield/DEPLOYMENT.md) for full step-by-step setup and environment configuration.

> **Evaluation Credentials (Demo Only, Synthetic Data):**
> * **Officer Workstation:** Username `officer_sharma` / Password `Officer@Shield2026`
> * **Citizen Portal:** Username `citizen_demo` / Password `Citizen@Shield2026` *(or click "Sign Up" to create a new citizen account)*
> 
> *Note: These credentials access an isolated, synthetic evaluation dataset. Citizen and Officer operational interfaces and permissions are strictly enforced on the server.*

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Client ["Client Presentation Layer (Vite + React 18 + Tailwind v3.4)"]
        UI_Citizen["Citizen Portal (Check SMS, Links, Websites)"]
        UI_Officer["Officer Workstation (Graph, Heat-list, Dossiers, Assistant)"]
        RoleState["Role Context (localStorage: Citizen / Officer)"]
        ReactFlow["Scam Campaign Radar (@xyflow/react)"]
    end

    subgraph API_Gateway ["Application Server (FastAPI + Uvicorn)"]
        Router["REST Router (/api/*)"]
        RateLimit["Safety & Payload Size Limits (2MB)"]
        CORS["CORS Policy (Origin: localhost:5173)"]
    end

    subgraph Core_Engines ["LinkShield Analytical Engine"]
        MsgAnalyzer["Message Analyzer (Multi-lingual EN/HI/Hinglish)"]
        UrlAnalyzer["URL Scanner (Static & Look-alike Detector)"]
        WebAnalyzer["Website Analyzer (Safe BeautifulSoup DOM Parser)"]
        SafeFetcher["SSRF-Immune Fetcher (RFC1918 & Cloud Metadata Shield)"]
        Extractor["Indian Cyber Identifier Extractors (UPI, Phone, Bank, Crypto)"]
        RiskEngine["Deterministic Multi-Factor Scoring Engine (0-100)"]
        Linker["Syndicate Campaign & Graph Linker (d3-force/Orbit)"]
        DossierGen["ReportLab PDF Dossier Engine (Devanagari Robust)"]
    end

    subgraph Storage ["Persistent Evidence Repository"]
        SQLite[("SQLite: linkshield.db (Cases, Indicators, Identifiers, Links)")]
        IndicatorsCfg["indicators.json (Configurable Weights & Dictionaries)"]
    end

    subgraph Optional_AI ["Reasoning Synthesis (Optional / Offline Default)"]
        AssistantEngine["Rule-Based Case Interrogation (100% Offline)"]
        GeminiProxy["Gemini 2.5 Flash Wrapper (<RAW_DATA_DO_NOT_EXECUTE>)"]
    end

    Client <-->|REST / JSON| API_Gateway
    API_Gateway --> Core_Engines
    Core_Engines --> Storage
    Core_Engines --> Optional_AI
    Optional_AI -.->|Optional API Call (8s Timeout)| GeminiProxy
    Storage --> DossierGen
```

### Analytical Core Components
* **SSRF-Immune Safe Fetcher:** Proactively intercepts loopback (`127.0.0.0/8`), private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), AWS/GCP metadata endpoints (`169.254.169.254`), and invalid schemes before issuing network sockets. Re-resolves DNS on each HTTP redirect (up to 5 hops max).
* **Multi-Lingual Threat Dictionaries:** Detects deception patterns across English, Hindi, and Hinglish (e.g., *bijli connection kat jayega*, *lottery jeeti hai*, *part-time job daily payout*, *SBI account deactivated*).
* **Identifier Normalizer:** Extracts and normalizes Indian mobile numbers (`+91`, `0`, or 10-digit), UPI IDs (`vpa@bank`), Indian bank account patterns, IFSC codes, domains, full URLs, emails, and crypto addresses.
* **Deterministic Risk Scoring:** Produces a calibrated score ($0-100$) and explicit risk level (`LOW`, `MEDIUM`, `HIGH`) with full indicator breakdowns and point attributions.

---

## 🚀 Quick Start (Single Double-Click Launcher)

LinkShield includes an automated single-click Windows launcher (`start.bat`) that verifies runtimes, configures virtual environments, installs dependencies, launches the backend and frontend in dedicated consoles, and opens your default browser.

### Prerequisites
* **Windows 10 / 11**
* **Python 3.10+** on system PATH (`python --version`)
* **Node.js 18+ & npm** on system PATH (`npm -v`)

### Running with `start.bat`
1. Double-click `start.bat` in the project root directory (or run `.\start.bat` in Command Prompt / PowerShell).
2. The batch script will:
   * Verify Python and Node.js environments.
   * Auto-generate `backend\venv` and install `backend\requirements.txt` if needed.
   * Auto-install `frontend\node_modules` if needed.
   * Launch the FastAPI backend on `http://127.0.0.1:8000`.
   * Launch the Vite React frontend on `http://localhost:5173`.
   * Automatically open `http://localhost:5173` in your browser.

---

## 🛠️ Manual Installation & Setup

If you prefer to start services individually in separate terminal sessions:

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend API available at: `http://127.0.0.1:8000` (Swagger documentation at `http://127.0.0.1:8000/docs`).*

### 2. Frontend Setup
```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install node packages
npm install

# Start Vite development server
npm run dev
```
*Frontend Web UI available at: `http://localhost:5173`.*

---

## 📂 Demo Data & Official Dataset Import

### 1. Loading Synthetic Demo Data
LinkShield ships with 44 synthetic cases representing authentic cybercrime modus operandi across Rajasthan (investment frauds, electricity bill disconnection scams, fake KYC deactivations, task-based Telegram frauds, loan apps, and genuine bank transaction alerts):

* **Via UI:** Click the **"Load Demo Data"** button in the top right of the Threat Intelligence Dashboard (`/`).
* **Via Standalone Script:**
  ```bash
  python load_demo.py
  ```
* **Via API:**
  ```bash
  curl -X POST http://127.0.0.1:8000/api/demo/load -H "Content-Type: application/json" -d "{}"
  ```
*To clear demo data at any time, click **"Clear Demo"** on the dashboard or run `POST /api/demo/clear`.*

### 2. Importing the Official Rajasthan Police Dataset (`r4c_dataset.csv`)
LinkShield provides an ingestion bridge for external complaint callsets and official R4C incident records:

* **Via CLI Script:**
  ```bash
  backend\venv\Scripts\python.exe backend/import_r4c.py path/to/r4c_dataset.csv
  ```
* **Via REST API (Multipart Form Upload):**
  ```bash
  curl -X POST http://127.0.0.1:8000/api/cases/import -F "file=@path/to/r4c_dataset.csv"
  ```
All imported rows are ingested as verified real investigations (`is_demo=False`), extracted for operational identifiers, scored via the multi-factor risk engine, and integrated into the Scam Intelligence Graph.

---

## 🤖 Google Gemini AI Integration & Forensic Grounding

LinkShield AI features a state-of-the-art hybrid architecture combining a **deterministic, 100% offline rule-based engine** with an **evidence-grounded Google Gemini model** (`gemini-3-flash-preview`).

### 1. Configuration (`backend/.env`)
```env
# Optional: Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3-flash-preview
GEMINI_ASSISTANT_TIMEOUT=20.0
GEMINI_ANALYSIS_TIMEOUT=10.0
AI_ASSIST_ANALYSIS=true

# Privacy Safeguard: Mask phone, UPI, email, and bank account for non-demo cases (is_demo=false)
# Set to true only with departmental authorization to transmit live citizen identifiers
ALLOW_EXTERNAL_AI_FOR_REAL_CASES=false

# Optional: Google Safe Browsing Lookup API Key (v4)
GOOGLE_SAFE_BROWSING_KEY=
```
*Note: If `GEMINI_API_KEY` is omitted or unconfigured, LinkShield operates entirely in offline mode with zero degradation of core forensic capabilities.*

### 2. Conversational Assistant with Native SQLite Tools (Officer Only)
The Cyber Safety Assistant (`/assistant`) uses Gemini function calling grounded directly in SQLite:
* **Tool Calling Capabilities:**
  * `get_stats()`: Retrieve live dataset and threat distribution statistics.
  * `search_cases(query, risk, category, input_type, limit)`: Filter cases by keyword, risk level, or attack category.
  * `get_case(case_id)`: Inspect full forensic dossier for a specific investigation.
  * `cases_for_identifier(value)`: Find all cases linked to a phone number, UPI handle, or domain.
  * `top_identifiers(identifier_type, limit)`: Identify highest-frequency recidivist scam vectors.
  * `shared_identifiers(min_cases, limit)`: Trace multi-case cross-linkages for syndicate discovery.
* **Agent Execution Loop:** Multi-step autonomous loop (up to 5 tool calls per turn) to resolve compound questions.
* **Multi-Turn Context:** Preserves the last 6 turns of conversation history for natural follow-up interrogation.
* **Citation Verification Guard:** Post-response validator cross-references every cited Case ID against `linkshield.db`. Any hallucinated or unverified IDs are strictly rejected.
* **Status Monitoring:** `GET /api/assistant/status` provides live connectivity diagnostics (`ok` / `error` / `not_configured`) and displays connection status in the UI with sanitized error descriptions.

### 3. AI Second Opinion Analyzer
For message, URL, and website evaluations, an AI second opinion evaluates deceptive intent in parallel:
* **Structured Output:** Strictly typed JSON schema returning `{scam_likelihood, category, impersonated_brand, reasons, confidence}`.
* **Calibrated Scoring Escalation:**
  * If rule-based score is LOW (<30), but Gemini evaluates MEDIUM or HIGH (confidence $\ge 0.7$): adds **+25 points** (or **+10 points** if indicators already fired).
  * **Safety Caps:** AI escalation alone is capped at 49 (cannot push a LOW case into HIGH).
  * **Non-Destructive:** AI can **never lower** a rule-based score or risk level.
  * **Official Domain Shield:** Verified brand domains (e.g., `sbi.co.in`, `incometax.gov.in`) and allowlisted domains can never be escalated.
* **Content Hash Caching:** SHA-256 caching eliminates redundant API latency for duplicate inputs.

### 4. Privacy & Data Protection Safeguards
* **Automated Data Masking:** For user-submitted cases (`is_demo=False`), phone numbers (`+91 XXXXX 1234`), UPI handles (`u***@bank`), and bank account numbers (`XXXXXXXX1234`) are masked before transmission to external AI.
* **Controlled De-anonymization:** Unmasked external transmission requires explicit administrative configuration (`ALLOW_EXTERNAL_AI_FOR_REAL_CASES=true`).

### 5. Real Domain Age via RDAP & Safe Browsing
* **Public RDAP Querying:** Automatically queries `https://rdap.org/domain/<domain>` (5-second timeout, cached in-memory) with zero API keys required.
* **Threat Indicators:**
  * Domain registered $< 30$ days ago: `Newly Registered Domain (<30 days, registered YYYY-MM-DD)` (+15 pts).
  * Domain registered $< 90$ days ago: `Recently Registered Domain (<90 days)` (+10 pts).
* **Safe Browsing Integration:** Optionally validates URLs against Google Safe Browsing API v4, flagging confirmed malware/social engineering threats (+40 pts).

---

## 🌐 REST API Endpoints

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **System** | `GET` | `/api/health` | Healthcheck and active database status |
| **Analysis** | `POST` | `/api/analyze/message` | Analyzes SMS/WhatsApp/Telegram text + nested URLs |
| **Analysis** | `POST` | `/api/analyze/url` | Static inspection + SSRF-safe link probe |
| **Analysis** | `POST` | `/api/analyze/website` | Static DOM inspection of URL or uploaded HTML |
| **Cases** | `GET` | `/api/cases` | Paginated case list with risk/type filters & search |
| **Cases** | `GET` | `/api/cases/{case_id}` | Detailed case dossier with indicators & identifiers |
| **Cases** | `POST` | `/api/cases/{case_id}/notes` | Saves official investigator notes to case record |
| **Cases** | `POST` | `/api/cases/import` | Ingests external CSV/JSON callsets (e.g. R4C) |
| **Intelligence** | `GET` | `/api/intelligence/graph` | Multi-case campaign relationship graph nodes & edges |
| **Intelligence** | `GET` | `/api/intelligence/heatlist` | Frequency-ranked surveillance registry of identifiers |
| **Intelligence** | `GET` | `/api/dashboard/stats` | Aggregate threat metrics and category distributions |
| **Assistant** | `POST` | `/api/assistant/ask` | Evidence-grounded case interrogation (offline + Gemini) |
| **Reports** | `GET` | `/api/reports/{case_id}/pdf` | Generates official PDF investigation dossier |
| **Demo** | `POST` | `/api/demo/load` | Seeds 44 synthetic demo cases |
| **Demo** | `POST` | `/api/demo/clear` | Clears all synthetic demo cases idempotently |

---

## ⏱️ 3-Minute Evaluation Demo Script

Follow this step-by-step walkthrough to evaluate LinkShield AI:

### Step 1: Citizen Scans a Fraudulent Electricity SMS (1 min)
1. Open `http://localhost:5173` and toggle the top-bar role to **Citizen**.
2. Navigate to **"Check a Message"** (`/analyze/message`).
3. Click the sample prompt: *"Dear customer your electricity power will be disconnected tonight at 9:30 PM..."*.
4. Click **"Analyse Message"**.
5. **Observe:**
   * Risk Level immediately flagged as **HIGH (Score: 85/100)** with red visual warning.
   * Detected indicators: `Electricity Disconnection Scam Threat`, `Urgent Deadline / Fear Pressure`, `Suspicious Payment Request`.
   * Clear advice in English and Hindi advising the citizen not to call the number or pay.
   * Emergency action button to dial Cyber Helpline `1930`.

### Step 2: Officer Evaluates Syndicate Campaign Graph (1 min)
1. Sign in as **Officer** (e.g. `officer_sharma` / `Officer@Shield2026`).
2. Navigate to **"Scam Graph"** (`/intelligence/graph`).
3. View the **Campaign Intelligence Radar**.
4. In the left **Detected Syndicates** drawer, click on `#1 SYNDICATE: demo-scam.test (15 linked cases)`.
5. **Observe:**
   * The radar focuses cleanly on the primary anchor hub (`demo-scam.test`).
   * Connected technical assets (associated phone numbers, UPI IDs, secondary URLs) orbit the hub in an organized celestial layout.
   * Linked high-risk cases appear along the outer perimeter with clear dashed vectors.
   * Clicking the central hub opens the **Infrastructure Asset Drawer** showing 15 linked complaints and first/last observed timestamps.

### Step 3: Drill-down into Threat Surveillance Heat-list (30 sec)
1. Navigate to **"Threat Heat-list"** (`/intelligence/heatlist`).
2. Switch between **Domains**, **Phones**, and **UPI IDs** tabs.
3. Observe frequency ranking bars indicating multi-case recidivism.
4. Click **"Inspect Cases"** on any entity to view all linked complaint dossiers.

### Step 4: Interrogate Cases with Cyber Cop Assistant (30 sec)
1. Navigate to **"Cyber Cop Assistant"** (`/assistant`).
2. Click the suggestion chip: **"Why was case DEMO-011 classified as high risk?"**.
3. **Observe:**
   * Instant, 100% deterministic answer citing verified case indicators and points.
   * Clickable Case ID pill appears at the bottom.
   * Click the pill to jump directly into the full investigative case drawer in Case Management!
4. Return to Assistant and test an unknown query: *"Tell me about the suspect in case 99999"*.
   * Assistant strictly outputs: *"No supporting records found in the database."* (zero fabrication).

### Step 5: Export Official Investigation PDF Dossier (15 sec)
1. In **Case Management** (`/cases`), open any case (e.g. `DEMO-011` or `LS-0001`).
2. Add an investigator note: *"Assigned to Cyber Cell Investigation Unit. Bank freeze request initiated."* and click **Save Notes**.
3. Click **"Download PDF Dossier"**.
4. Open the generated PDF: observe LINKSHIELD AI header, watermark, metadata summary, risk assessment matrix, extracted identifiers table, and officer notes.

---

## 🔐 Authentication & Role-Based Access Control (RBAC)

LINKSHIELD AI implements secure, role-based access control with real user authentication:

* **Authentication Architecture:**
  * **Password Hashing:** Passwords hashed with `bcrypt` (work factor 12).
  * **Session Management:** Signed JSON Web Tokens (JWT) using `HS256` with 2-hour expiration, transported via `Authorization: Bearer <token>` in `sessionStorage` and HttpOnly/SameSite cookies.
  * **Account Lockout Protection:** 5 consecutive failed login attempts trigger an automated 5-minute lockout to defend against brute-force attacks.
  * **Server-Enforced RBAC:** Access control is strictly enforced on every FastAPI endpoint via dependency injection (`require_officer`, `require_citizen_or_officer`). Roles cannot be escalated from the client side.
  * **Citizen Data Isolation:** Citizen analysis endpoints enforce strict isolation; `similarity_matches` are cleared (`[]`) for citizens so no other users' case IDs or data are disclosed.
  * **Aggregate Scam Awareness:** Citizen dashboard queries aggregate metrics and category trends (`GET /api/public/awareness`), never exposing individual phone numbers, UPI IDs, emails, domains, or case records.

* **Default Seed Accounts (`backend/seed_users.py`) — Demo Only, Synthetic Data:**
  * **Officer Account:** `officer_sharma` / `Officer@Shield2026` *(Demo only, synthetic data)*
  * **Admin Account:** `admin_cyber` / `Admin@Shield2026` *(Demo only, synthetic data)*
  * **Citizen Account:** `citizen_demo` / `Citizen@Shield2026` *(Demo only, synthetic data — Citizens can also self-register directly via the portal)*
  > **Note:** These credentials operate on purely synthetic test datasets. Citizen and Officer operational interfaces and permissions are strictly enforced on the server.

---

## 🔒 Security Measures & Safe Execution Guarantee

* **Zero Execution of Untrusted Scripts:** LinkShield utilizes pure static BeautifulSoup parsing for HTML and static regex/AST analyzers. Untrusted JavaScript, iframes, and active browser engines are completely disabled.
* **SSRF Shield:** Validates IP addresses against RFC 1918, link-local, loopback, and broadcast ranges prior to socket initialization. Redirect chains are re-inspected on every hop.
* **Deterministic Fallback:** The investigation assistant requires no internet connection and cannot hallucinate non-existent cases.
* **Sanitized PDF Export:** All user inputs are strictly escaped using XML/HTML entity escaping before ReportLab flowable construction to prevent layout injection.

---

## ⚠️ Production Limitations & Enterprise Roadmap

* **Current Limitations:**
  * **MFA / Hardware Keys:** Multi-factor authentication (TOTP / FIDO2 WebAuthn) is recommended for production police network deployment.
  * **Distributed Session Revocation:** Token revocation currently relies on JWT expiry and cookie deletion; enterprise deployment would use a Redis token blacklist for instant cross-cluster revocation.
  * **Dynamic JavaScript SPAs:** Live website scanning relies on static HTML snapshots; single-page apps (SPAs) that render exclusively via heavy client-side JavaScript execution will only have their static HTML pre-render evaluated.
  * **OCR / Image Extraction:** Image and OCR analysis (e.g., reading bank transfer screenshots) requires an external Tesseract or Vision pipeline not currently included in core PS01 text/URL scope.
* **Future Scope:**
  * Direct integration with the National Cybercrime Reporting Portal (NCRP) API for automated XML/JSON complaint ingestion.
  * Automated freeze request dispatch via Indian Financial Cyber Fraud Reporting and Management System (CFCFRMS).
  * On-device fine-tuned IndicBERT model for localized Rajasthani dialect scam detection.

---

## ⚖️ License & Disclaimer

Built for the **Rajasthan Police Cyber Security Hackathon 2026** under the MIT License.  
*Disclaimer: Demo cases included in this package are synthetically generated for evaluation and demonstration purposes. Operational findings require verification by authorized law enforcement personnel prior to executive or legal action.*
