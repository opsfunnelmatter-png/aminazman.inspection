# SOP & STRICT SAFETY DIRECTIVES: SUBSEA OFFSHORE EMAIL OUTREACH

## 1. ZERO-DUPLICATE SENT-MAIL PRE-FLIGHT VERIFICATION (HARD RULE)
- Before sending ANY outreach email to any contact, the system/bot MUST connect directly via IMAP to Gmail's `[Gmail]/Sent Mail` across both accounts (`amin87.azman@gmail.com` and `aminazman.inspection@gmail.com`).
- Query: `SEARCH TO "<recipient_email>"`
- If the recipient has ALREADY received an outreach email (CSWIP 3.4U / Subsea Inspection) from EITHER account at ANY time in history:
  - **HARD SKIP IMMEDIATELY**: Do NOT send. Mark `sent: true` in local ledger.
- This rule is independent of JSON or database files; Gmail Sent Mail is the single source of truth.

## 2. NO UNSUPERVISED CLOUD CRON JOBS
- Automated cron runs on cloud VM platforms (such as GitHub Actions cron) where git persistence can fail silently are PERMANENTLY FORBIDDEN.
- All outreach campaigns must be executed with live local logging and verified state updates.

## 3. USER CONFIRMATION BEFORE ANY EXTERNAL ACTION
- Always ask and obtain user confirmation before sending emails or taking external actions.
- If the user asks to modify a sentence for an email that was ALREADY sent, warn the user first and ask for double clarification instead of re-sending blindly.

## 4. CV & CERTIFICATES ATTACHMENT RULES
- CV PDF MUST always be sourced exclusively from:
  `C:\Users\amin8\Desktop\AG Projects\AG-Offshore\02_Offshore_CV_FULL\CV - Muhammad Amin Azman (CSWIP 3.4U Inspection Engineer).pdf`
- Sijil-sijil offshore (Certificates) diambil dari:
  `C:\Users\amin8\Desktop\AG Projects\AG-Offshore\01_Offshore_Certificates_FULL\`
- Valid offshore credentials summary section must always be placed AFTER the signature block.
