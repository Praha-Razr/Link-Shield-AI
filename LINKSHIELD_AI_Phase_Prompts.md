# LINKSHIELD AI: Phase-by-Phase Prompts for Antigravity

**How to use this file**

1. Paste **GLOBAL RULES** as your first message in Antigravity (once).
2. Paste **Phase 1**. Wait until the agent says it has stopped.
3. Do the **checkpoint checks** yourself. Only if they pass, paste the next phase.
4. If something fails, paste the **FIX PROMPT** at the bottom instead of moving on.

**Deadline plan:** Phase 1 + 2 today (22 Nov), Phase 3 on 23 Nov, Phase 4 + submission on 24 Nov (submit well before the day ends).

---

# GLOBAL RULES (paste first, once)

```
You are an expert full-stack developer, cybersecurity engineer and UI/UX designer.
We are building LINKSHIELD AI for the Rajasthan Police Cyber Security Hackathon 2026,
Problem Statement PS01: "Scam Message & Phishing Link Detection with Fake Loan /
Investment App and Fraudulent Website Analysis".

Tagline: Detect. Explain. Investigate. Protect.

WHAT IT IS
A real, working web app (NOT a static mockup, NOT fake numbers). It analyses suspicious
messages, URLs and websites; extracts identifiers (domains, URLs, phone numbers, UPI IDs,
emails, bank-account-like numbers, crypto wallets); gives an explainable risk level; links
cases that share identifiers; and produces investigation-ready PDF reports.

TECH STACK (use exactly this unless the workspace already has something compatible)
- Backend: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, SQLite, BeautifulSoup, ReportLab, rapidfuzz
- Frontend: React + Vite + JavaScript, Tailwind CSS (pin v3.4.x), React Router, Recharts,
  React Flow (package name: @xyflow/react), Lucide icons
- Pin all dependency versions in requirements.txt and package.json.

WORKING RULES (very important)
1. We work in 4 PHASES. Complete ONLY the phase I give you, then STOP.
2. After finishing a phase, STOP and give me a report with:
   (a) what was built, (b) exact commands to run it on Windows, (c) tests you ran and the
   real results, (d) known issues / limitations. Then WAIT for my approval.
3. Never claim a feature works unless you actually ran and tested it.
4. No hardcoded statistics. Every number shown comes from the database.
5. No placeholder or "coming soon" pages inside the phase scope.
6. Every analysis result must include a list of indicators, each with: name, points,
   and a plain-language explanation of WHY it was flagged.
7. A single keyword is never proof of fraud. Say "indicates" / "consistent with", not "is a scammer".
   Repeated identifiers are NOT proof someone is criminal; label them "frequently reported".
8. External data that is unavailable (WHOIS, domain age, reputation) must show "Not available".
   Never invent it.

SECURITY RULES
- Validate all input (length limits, types). Escape/sanitise anything rendered in HTML.
- Never execute website scripts or downloaded files. Static analysis only.
- URL fetching: allow only http/https; resolve DNS and BLOCK private, loopback, link-local
  and reserved IPs (SSRF protection); follow redirects MANUALLY (max 5 hops) and re-validate
  every hop; 5-second timeouts; response size cap (e.g. 2 MB).
- File uploads: allow only .html/.htm/.txt, max 1 MB, never executed.
- Never access private accounts. Never auto-block or take down anything.
- All demo data is synthetic. Use only reserved domains (.test, .example, .invalid), and
  obviously placeholder phone numbers (90000 00001 to 90000 00030). No real personal data.

PROJECT FOLDER STRUCTURE
linkshield-ai/
  backend/   (FastAPI app)
  frontend/  (React app)
  data/      (synthetic demo dataset JSON)
  README.md
  start.bat  (Windows: starts backend + frontend)

Confirm you understand these rules in 5 lines or fewer, inspect the current workspace,
and WAIT for Phase 1.
```

---

# PHASE 1: Backend, Risk Engine, Extractors, Demo Data (no UI yet)

```
PHASE 1: BACKEND ONLY. Do not build the frontend yet. STOP when done.

Build the complete FastAPI backend inside /backend, with SQLite persistence.

1. DATABASE (SQLAlchemy models)
- cases: id (string like "LS-0001" / demo: "DEMO-001"), subject, input_type
  (message|url|website), raw_content, content_sha256, created_at, risk_score, risk_level
  (LOW|MEDIUM|HIGH), category, status, is_demo (bool), language (en|hi|hinglish|other),
  investigator_notes (text)
- indicators: id, case_id, name, points, explanation
- identifiers: id, type (domain|url|phone|upi|email|bank_account|crypto_wallet), value
  (normalised), unique on (type, value)
- case_identifiers: case_id, identifier_id (the link table that powers relationships)
- similarity_links: case_id_a, case_id_b, similarity (0-1) for near-duplicate content
- Evidence: store raw content + SHA-256 hash + UTC timestamp for each case.

2. EXTRACTORS (backend/app/extractors.py)
Extract with regex + validation, normalise values (lowercase domains, strip spaces in phones):
- URLs, domains (use urllib / a public-suffix approach, fallback to simple parsing)
- Indian phone numbers (+91 / 10 digits starting 6-9, allow spaces/hyphens)
- UPI IDs (name@handle, ensure not confused with emails: emails have a dot in the domain part)
- Emails
- Bank-account-like numbers (9-18 digits, only when near words like account/a/c/IFSC) and IFSC codes
- Crypto wallets (BTC bech32/legacy, ETH 0x + 40 hex, TRON T + 33 chars)
- Suspicious phrases found (return the exact matched phrases)

3. RISK ENGINE (backend/app/risk/engine.py + config in backend/app/risk/indicators.json)
Configurable indicator list, each with: id, points, regex/keywords, explanation, languages.
Starting scores (adjustable in the JSON):
- Urgency / threatening language: +15
- Fake KYC / account-block impersonation: +20
- Bank / government / courier impersonation: +15
- Electricity-bill disconnection scam: +15
- Parcel-delivery fee scam: +15
- Fake job offer (registration fee, work-from-home guaranteed income): +15
- Suspicious payment instruction (pay to UPI/personal account): +15
- Look-alike domain (brand names like sbi, hdfc, icici, paytm, indiapost, amazon + extra tokens
  or edit-distance match with rapidfuzz): +25
- Suspicious URL pattern (IP address host, punycode xn--, many hyphens, excessive subdomains,
  shorteners, suspicious TLD, '@' in URL, keywords like login/verify/kyc/update): +15
- Known synthetic blacklist match (table of demo blacklist domains): +35
- Guaranteed-return investment claims: +20
- Ponzi / double-your-money language: +20
- Referral-chain / MLM language: +15
- Illegal betting promotion language: +20
- Fake loan advertisement (instant loan, no documents, pre-approved): +15
- Suspicious payment request on website (UPI/bank/crypto asked to deposit): +15
Rules:
- Total capped at 100. LOW 0-24, MEDIUM 25-49, HIGH 50-100. Thresholds in config.
- Support English, Hindi (Devanagari) and Hinglish keywords for every message indicator,
  e.g. "khata band", "turant", "KYC update karein", "aapka account block", "बैंक खाता बंद".
- Genuine messages (e.g., normal OTP/bank credit alert/parcel update from a known sender
  without links or payment requests) must score LOW. Include a small "benign context" reducer
  concept only if it is explainable and shown as a negative-point indicator.
- Return: score, level, category, indicators[] (name, points, explanation), safety_recommendations[].

4. ANALYSERS
- message_analyser: text in, extract identifiers, run indicators, also analyse each URL found
  with the URL analyser (no network needed for static checks).
- url_analyser: static checks always (structure, keywords, IP host, punycode, look-alike,
  subdomains, HTTPS scheme). Optional live checks (redirect chain, HTTPS availability) ONLY via
  the safe fetcher in security.py. If a live check cannot run or is blocked, report
  "Not available" with the reason. Domain age: "Not available" unless a reliable source is
  configured (add a config hook, do not invent data). Blacklist: use the synthetic demo blacklist.
- website_analyser: accepts a URL (via safe fetcher) OR uploaded HTML text. Parse with
  BeautifulSoup (remove scripts, never execute). Detect indicators, extract identifiers from
  visible text, links and attributes (tel:, mailto:, href), save an evidence excerpt.
- Similarity: on every new case, compare with existing cases using rapidfuzz (token_set_ratio
  or similar). If >= 0.85, create a similarity_link and add an indicator "Near-duplicate of
  case X" (0 points, informational).

5. LINKER
After saving a case, its identifiers are stored through the identifiers + case_identifiers
tables. Provide helper queries: cases for an identifier, identifiers shared by multiple cases,
top identifiers by distinct case count, graph nodes/edges built ONLY from real shared data.

6. API ENDPOINTS (all working, Pydantic schemas, CORS enabled for localhost:5173)
POST /api/analyze/message
POST /api/analyze/url
POST /api/analyze/website   (JSON with url OR multipart HTML upload)
GET  /api/dashboard/stats
GET  /api/cases              (search q, risk, category, date_from, date_to, input_type, pagination)
GET  /api/cases/{case_id}
PATCH /api/cases/{case_id}/notes
GET  /api/intelligence/graph
GET  /api/intelligence/heatlist (filter by type, date range, include_demo flag)
POST /api/demo/load          (idempotent: no duplicates on repeated clicks)
POST /api/demo/clear         (deletes ONLY is_demo records, requires {"confirm": true})
GET  /api/reports/{case_id}/pdf  (create a stub that returns 501 for now; real PDF is Phase 3)
POST /api/import             (CSV/JSON import of external sample data, e.g. the official R4C
                              dataset; validate fields, mark is_demo=false)
GET  /api/health

7. SYNTHETIC DEMO DATASET (data/demo_dataset.json)
Create 44 records, each with: case_id, category, input_type, submitted_content,
expected_classification (scam|genuine), expected_risk_level, relevant_indicators,
expected_identifiers.
- 10 genuine messages (parcel updates, bank credit alerts, job interview updates, service notices)
- 10 suspicious messages (fake KYC, electricity bill, parcel fee, fake job, bank impersonation,
  payment threats). Include 3 in Hindi/Hinglish.
- 10 suspicious URLs (fake login, look-alike domains, payment links, fake loan, investment links)
- 10 website samples as HTML strings (2 genuine financial-info pages, 3 fake investment,
  2 Ponzi-style, 1 MLM referral, 2 illegal betting)
- 4 extra "link" records that deliberately reuse identifiers so the graph is rich. Example:
  demo-scam.test appears in a message, a URL and a website; one placeholder phone number
  (90000 00001) appears in 3 cases; one UPI (demo.pay@demoupi) appears in a message and a website.
- Genuine samples must NOT share identifiers with scam samples.
- Every record is_demo = true and clearly marked DEMO DATA.
Loading the dataset must run each record through the REAL analysis pipeline (not copy
pre-written scores), so the engine is actually exercised.

8. TESTS (pytest, backend/tests)
- Extractors: phones, UPI vs email, URLs, wallets, IFSC.
- Risk engine: all 10 genuine messages score LOW; all 10 suspicious messages score MEDIUM or
  HIGH; the 10 suspicious URLs MEDIUM/HIGH; report accuracy vs expected_risk_level.
- Security: SSRF tests (127.0.0.1, 10.x.x.x, 169.254.x.x, localhost, redirect to private IP,
  non-http schemes) must all be blocked.
- Demo load twice => no duplicates. Demo clear => only demo records removed.
- Linker: shared identifiers produce correct edges; no fake edges.

9. RUN AND VERIFY
Install deps, start uvicorn, open /docs (Swagger), call every endpoint with real examples,
load demo data and show results. Fix all errors and check logs.

CHECKPOINT: STOP after this. Report: files created, run commands (Windows), pytest results
including the genuine-vs-scam accuracy table, 5 sample API outputs, and known issues.
WAIT for my approval before Phase 2.
```

### Checkpoint 1: what YOU check
- [ ] `http://localhost:8000/docs` opens and endpoints are listed
- [ ] `POST /api/demo/load` works, and clicking it twice does not duplicate
- [ ] `GET /api/dashboard/stats` shows real counts
- [ ] A genuine message returns LOW; a fake KYC message returns HIGH with reasons
- [ ] `GET /api/intelligence/graph` returns nodes/edges from shared identifiers
- [ ] A Hindi/Hinglish scam message is flagged
- [ ] pytest passes and the SSRF tests pass

---

# PHASE 2: Frontend Foundation + Core Pages

```
PHASE 2: FRONTEND CORE. Backend from Phase 1 already works; do not rewrite it (only small
fixes if a real integration bug appears; tell me exactly what you changed). STOP when done.

Build /frontend with React + Vite + Tailwind (v3.4 pinned) + React Router + Recharts +
Lucide icons. Connect everything to the REAL backend API (base URL in .env, default
http://localhost:8000). No mock data.

DESIGN
- Dark navy sidebar, white/light-grey content background, electric blue + cyan accents.
- Clean modern cards and tables, responsive, subtle animations, professional typography.
- Create a shield-inspired LINKSHIELD AI logo as an inline SVG component (shield + link/check
  motif) and the tagline "Detect. Explain. Investigate. Protect." under it in the sidebar.
- Do not clutter. It should look like a real cybercrime investigation product.
- Reusable components: RiskBadge (LOW green / MEDIUM amber / HIGH red), IndicatorList,
  IdentifierChips (colour-coded by type), StatCard, DemoBadge ("DEMO DATA"), EmptyState,
  LoadingSpinner, ErrorBanner.

ROLE TOGGLE
Top-bar toggle "Citizen / Officer" (no login, stored in localStorage).
- Citizen view: simple "Check something" screens (Message, URL), plain-language results.
- Officer view: full sidebar with all pages.

PAGES IN THIS PHASE
1. Dashboard: cards for total cases, High/Medium/Low counts, suspicious domains, repeated
   phone numbers, total identifiers; charts: risk distribution, daily reported cases, scam
   category distribution, frequently reported identifiers; recent investigations table.
   Buttons: LOAD DEMO DATA, CLEAR DEMO DATA (confirmation modal). Empty state when no data.
2. Message Analyser: large textarea, ANALYSE button, validation (not empty, max length),
   results: risk score gauge, level, category, indicators with explanations, extracted
   identifiers, recommended safety actions, link to the saved case. Also show a clear
   "Do not click this link" warning banner for HIGH risk.
3. URL Scanner: input + SCAN button, validation, shows structural findings, "Not available"
   for unavailable external data (domain age, blacklist if not configured, redirect info),
   risk level with reasons.
4. Case Management: table (Case ID, Subject, Date, Input type, Risk level, Score,
   identifiers, status), search, risk/category/date/input-type filters, pagination,
   case detail drawer/page with: full indicators, identifiers, evidence hash + timestamp,
   investigator notes (editable, saved to backend), related cases (shared identifiers and
   near-duplicates) with clickable navigation, DEMO DATA badge.

Sidebar items for pages not built yet (Website Analyser, Graph, Heat-list, Reports,
Assistant) must NOT appear yet. Add them in later phases.

TESTING (run for real)
- Start backend + frontend. Load demo data from the button.
- Analyse one genuine and one suspicious message; scan one URL; open a case; save a note;
  search for an identifier; apply filters; clear demo data (with confirmation) and reload it.
- Check browser console: no errors. Check backend logs: no exceptions.
- Test narrow (mobile) width.

CHECKPOINT: STOP. Report: what was built, Windows run commands, test results, screenshots
description of each page, console/log status, known issues. WAIT for approval before Phase 3.
```

### Checkpoint 2: what YOU check
- [ ] Dashboard numbers change after LOAD / CLEAR demo data
- [ ] Message Analyser: genuine message = LOW, scam = HIGH with explanations
- [ ] URL Scanner shows "Not available" instead of invented data
- [ ] Case search by a phone number / UPI ID finds the right cases
- [ ] Notes you type are still there after a page refresh
- [ ] No red errors in the browser console

---

# PHASE 3: Website Analyser, Graph, Heat-list, PDF Reports

```
PHASE 3: INTELLIGENCE + REPORTS. Phases 1-2 work already. STOP when done.

1. WEBSITE ANALYSER PAGE
- Two inputs: website URL (fetched ONLY through the safe fetcher) OR upload a saved HTML
  file (.html/.htm/.txt, max 1 MB).
- Static analysis only; never run scripts.
- Show: risk level and score, detected indicators with explanations (guaranteed returns, Ponzi
  language, MLM/referral chain, fake loan, betting, suspicious payment requests), extracted
  identifiers (phones, UPI IDs, emails, domains, URLs, bank-account-like numbers, crypto
  wallets), a SAFE evidence excerpt (escaped text, no raw HTML rendering), content hash.
- Saved as a case.

2. SCAM INTELLIGENCE GRAPH PAGE (React Flow via @xyflow/react)
- Nodes: cases and identifiers (domains, phones, UPI IDs, emails, URLs), colour-coded by type
  with a legend. Edges come ONLY from real case_identifiers rows. By default show identifiers
  that appear in 2 or more cases (plus their cases), with a toggle to show all.
- Click a node: side panel with the identifier value, type, number of distinct cases, list of
  connected cases (click opens the case), first/last seen.
- Filters: identifier type, include/exclude demo data, search box that focuses a node.
- Layout: auto-layout so the graph is readable (use a simple force or layered layout).
- Empty state when there is no linked data.

3. THREAT HEAT-LIST PAGE
- Ranked tables for Domains, Phone numbers, UPI IDs, Emails: value, number of DISTINCT cases,
  first seen, last seen, highest risk level seen, DEMO badge.
- Search, sort (frequency, last seen), date filter, bar charts (Recharts).
- Wording: "frequently reported". Add a note: "Repeated reporting does not by itself prove
  wrongdoing; verify before action."
- Click an identifier to see its cases.

4. PDF REPORTS (ReportLab) + REPORTS PAGE
- Implement GET /api/reports/{case_id}/pdf for real.
- Report contents: LINKSHIELD AI header/branding, case ID, generated date/time (UTC and IST),
  DEMO DATA watermark/label when applicable, input type, evidence hash + capture time,
  original content or safe excerpt (max ~2,000 chars), risk level + score, indicator table
  with explanations, extracted identifiers, related cases (shared identifiers and
  near-duplicates), investigator notes, and the disclaimer: "Automated analysis for
  investigation support. Findings must be verified by a human investigator."
- IMPORTANT: escape/sanitise all user content before putting it into ReportLab Paragraphs
  (special characters like <, >, & must not crash PDF generation). Support Devanagari text if
  possible (embed a Unicode font such as Noto Sans Devanagari if available; otherwise note the
  limitation and fall back safely).
- Reports page: searchable list of cases with "Download PDF" buttons; also add a Download
  button inside the case detail view. Optionally add a "bulk campaign report" for one
  identifier (all cases sharing it).

5. SIDEBAR
Now add Website Analyser, Scam Graph, Threat Heat-list and Reports to the sidebar.

TESTING (run for real)
- Analyse each website type from the demo set: a genuine financial page => LOW; fake
  investment, Ponzi, MLM, betting => MEDIUM/HIGH; check extracted identifiers.
- Upload an HTML sample file; upload a disallowed file type and an oversized file => rejected
  with a clear message.
- Graph: verify at least 3 known shared-identifier links appear and no fake edges exist
  (compare with a direct SQL query).
- Heat-list ranking matches SQL counts.
- Generate PDFs for a message case, a URL case, a website case and a Hindi case; open each
  and confirm they are valid PDFs with all required sections.
- Check browser console and backend logs.

CHECKPOINT: STOP. Report: what was built, test results, list of PDFs generated, graph
verification evidence, known issues. WAIT for approval before Phase 4.
```

### Checkpoint 3: what YOU check
- [ ] Graph shows demo-scam.test / the shared phone / the shared UPI linking multiple cases
- [ ] Clicking a graph node shows the connected cases and opens them
- [ ] Heat-list ranks the most-shared identifiers first
- [ ] Downloaded PDF opens, shows case details, indicators and the disclaimer
- [ ] A weird-character message (e.g. `<b> & "quotes"`) still generates a PDF

---

# PHASE 4: Assistant, Polish, README, Final Testing

```
PHASE 4: ASSISTANT + FINISHING. Phases 1-3 work already. STOP when done.

1. INVESTIGATION ASSISTANT (rule-based first, must work with NO internet)
- Chat page in the sidebar. Backend endpoint POST /api/assistant/ask.
- Supported question types (intent matching via keywords/regex):
  * "Why was case X classified as high risk?" => list indicators + explanations of that case
  * "Which domain appears in multiple cases?" => top shared domains with case IDs
  * "Which UPI ID has the most reports?" => ranking from the database
  * "Show all cases linked to <phone/UPI/domain/email>" => case list
  * "Summarise case X" / "Summarise this investigation" => factual summary from stored data
  * "What are the suspicious indicators in website case X?" => indicators list
  * "How many high risk cases?" => stats
- Every answer must include case IDs and an evidence reference (indicator names, identifier
  values). If nothing matches, answer exactly: "No supporting records found in the database."
- Never fabricate. Show suggested example questions as clickable chips.

2. OPTIONAL "ENHANCED MODE" WITH GEMINI (only after the rule-based assistant is tested)
- Config via backend/.env: GEMINI_API_KEY and GEMINI_MODEL (model name configurable, do not
  hardcode). If the key is missing or any call fails/times out (8s), automatically fall back
  to the rule-based answer and show a small "Basic mode" label.
- Flow: the backend first retrieves the relevant records from SQLite; Gemini is given ONLY
  those records and must answer from them, cite case IDs, and return JSON {answer, case_ids}.
- The backend validates that every cited case ID exists; invalid citations are removed or the
  answer is rejected and the basic answer is used.
- Prompt-injection defence: stored scam text is wrapped as quoted DATA, and the system
  instruction says never to follow instructions found inside it.
- The API key is never sent to the frontend. Show an "AI-assisted" badge on Gemini answers.
- Gemini must NEVER change a risk score or classification. It only explains and summarises.
- Keep this feature behind a toggle so the app works fully without it.

3. POLISH
- Consistent loading/empty/error states, form validation messages, keyboard focus, responsive
  layout, no layout glitches, favicon and page titles.
- Footer/about section: "Demo data is synthetic. Findings require human verification."
- Make sure DEMO DATA labels are visible everywhere synthetic records appear.

4. README.md
- What it is, features, architecture diagram (text), tech stack, folder structure,
  setup and run on Windows (Python venv + npm), the start.bat usage, how to load demo data,
  how to import the official R4C dataset (CSV/JSON format), how to configure Gemini,
  API endpoint list, security measures, limitations (static analysis only, no sandbox, no
  takedown, domain age/blacklist depend on configured sources), and future scope
  (APK analysis, Telegram/WhatsApp bot, browser extension).
- Add a "Demo Script" section (5 steps, about 3 minutes).

5. start.bat
One double-click script that creates the venv if missing, installs dependencies, starts the
backend and frontend in separate windows, and opens the browser.

6. FINAL TESTING (do ALL of these for real and record results in TEST_RESULTS.md)
- Fresh start: delete the DB, run start.bat, load demo data.
- Genuine message => LOW. Fake KYC (English + Hinglish) => HIGH.
- URL scan of a look-alike domain; SSRF attempt (http://127.0.0.1) is blocked.
- Website sample analysis; identifier extraction check.
- Open a saved case, add a note, search an identifier.
- Verify the graph connections against SQL; verify heat-list ranking.
- Generate and open PDFs.
- Clear demo data (confirmation) and reload it; no duplicates.
- Assistant: ask all supported question types; ask something with no data => "No supporting
  records found"; test Enhanced mode with and without the API key.
- Browser console and backend logs clean. Report any remaining issues honestly.

CHECKPOINT: STOP. Deliver: final file list, TEST_RESULTS.md summary, honest list of known
limitations. WAIT for my approval.
```

### Checkpoint 4: what YOU check
- [ ] Double-click `start.bat` on a clean machine/folder and the app starts
- [ ] Assistant answers with case IDs and says "No supporting records found" when appropriate
- [ ] Turn off the internet or remove the Gemini key: the assistant still works in Basic mode
- [ ] README steps work exactly as written

---

# FIX PROMPT (use whenever a checkpoint fails)

```
Checkpoint failed. Do NOT move to the next phase and do NOT rebuild everything.
Problem: <describe exactly what you saw, paste error text / screenshot description>
Steps to reproduce: <what you clicked>
Expected: <what should have happened>

Find the root cause, fix only what is needed, re-run the relevant tests, show the real
results, and STOP.
```

---

# SUBMISSION CHECKLIST (24 Nov, finish before the deadline)

- [ ] All 3 Must-haves work end to end (message/URL risk with reasons; website identifiers; dashboard + search + PDF)
- [ ] Demo data loaded and the graph shows real links
- [ ] 3-minute backup demo video recorded
- [ ] README + TEST_RESULTS.md included
- [ ] No API keys or `.env` file in the submission (include `.env.example` only)
- [ ] Uses only synthetic/provided data
- [ ] Final run from a clean start succeeded
- [ ] Submitted well before the end of the day

## Emergency cut order (if time runs short)
1. Gemini Enhanced mode
2. The Assistant page
3. Polish and animations
4. Citizen/Officer toggle

**Never cut:** the risk engine, identifier extraction, case history, graph, and PDF report.
