import os, sys, json, time, random, smtplib, imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "schedule_config.json")
CONTACTS_FILE = os.path.join(BASE_DIR, "contacts_data.json")

# Current Malaysia Time (UTC+8)
MYT = timezone(timedelta(hours=8))
now_myt = datetime.now(MYT)
today_str = now_myt.strftime("%Y-%m-%d")
day_name = now_myt.strftime("%A")

def check_live_sent_mail(user, app_pass, target_email):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=15)
        mail.login(user, app_pass)
        mail.select('"[Gmail]/Sent Mail"')
        status, messages = mail.search(None, f'TO "{target_email.strip().lower()}"')
        has_sent = bool(messages and messages[0].split())
        mail.logout()
        return has_sent
    except Exception as e:
        print(f"     [IMAP Warning] Live check error for {target_email}: {e}")
        return False

def main():
    print(f"\n=======================================================")
    print(f"   CLOUD OUTREACH SCHEDULER ENGINE (SWEEP RUNNER)")
    print(f"   Server Time (MYT): {now_myt.strftime('%Y-%m-%d %H:%M:%S %Z')} ({day_name})")
    print(f"=======================================================")

    if not os.path.exists(CONFIG_FILE):
        print(f"ABORT: Config file not found at {CONFIG_FILE}")
        return

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        sched = json.load(f)

    # 1. Check if schedule is active
    if not sched.get("active", False):
        print("Schedule is currently INACTIVE in config. Exiting.")
        return

    # 2. Check scheduled day
    if day_name not in sched.get("scheduled_days", []):
        print(f"Today ({day_name}) is not in scheduled_days {sched.get('scheduled_days')}. Exiting.")
        return

    # 3. Check if already dispatched today (IDEMPOTENCY GUARD)
    if sched.get("last_run_date") == today_str:
        print(f"Today's batch for {today_str} has ALREADY been executed and completed. Exiting safely.")
        return

    # 4. Load target profile
    profile_name = sched.get("profile", "basyir").lower()
    p_dir = os.path.join(BASE_DIR, "profiles", profile_name)
    prof_cfg_file = os.path.join(p_dir, "config.json")
    ledger_file = os.path.join(p_dir, "sent_ledger.json")

    if not os.path.exists(prof_cfg_file):
        print(f"ABORT: Profile config not found at {prof_cfg_file}")
        return

    with open(prof_cfg_file, "r", encoding="utf-8") as f:
        prof_cfg = json.load(f)

    if os.path.exists(ledger_file):
        with open(ledger_file, "r", encoding="utf-8") as f:
            ledger = json.load(f)
    else:
        ledger = []

    cv_path = os.path.join(p_dir, "cv", prof_cfg.get("cv_filename", ""))
    if not os.path.exists(cv_path):
        print(f"ABORT: CV not found at {cv_path}")
        return

    ledger_set = set(e.strip().lower() for e in ledger)

    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        contacts = json.load(f)

    # Filter unsent eligible contacts
    eligible = []
    for c in contacts:
        e = c.get("email", "").strip().lower()
        if not e or any(ex in e or ex in c.get("company", "").lower() for ex in ["mcsoil", "vantris", "alam-maritim"]):
            continue
        if e in ledger_set:
            continue
        eligible.append(c)

    batch_limit = sched.get("batch_size", 15)
    to_send = eligible[:batch_limit]

    print(f"Target Profile: {prof_cfg['name']} ({prof_cfg['email']})")
    print(f"Eligible Unsent Available: {len(eligible)} contacts")
    print(f"Batch Limit Today: {batch_limit} emails\n")

    if not to_send:
        print("No eligible contacts remaining in queue. Exiting.")
        return

    sent_count = 0
    for idx, contact in enumerate(to_send, 1):
        target_email = contact["email"].strip()
        comp = contact.get("company", "Company")
        pic = contact.get("pic_name", "Recruitment Team")

        print(f"[{idx}/{len(to_send)}] Target: {comp} ({pic}) <{target_email}>")

        # Live Google Sent Mail check
        if check_live_sent_mail(prof_cfg["email"], prof_cfg["app_password"], target_email):
            print("     -> SKIPPED (Found in live Google Sent Mail)")
            ledger.append(target_email.lower())
            with open(ledger_file, "w", encoding="utf-8") as f:
                json.dump(list(set(ledger)), f, indent=2)
            continue

        greeting = f"Hi {pic.split()[0]}," if pic and pic.lower() not in ["none", "all", "recruitment team", "hr team", "crewing team", "operations team", "general desk", "crewing desk", "recruitment desk"] else "Dear Hiring & Crewing Team,"

        if profile_name == "basyir":
            subject = f"Senior CSWIP 3.4U Subsea Inspection Coordinator / Inspection Engineer - {prof_cfg['name']} (Freelance / Ad-Hoc Mobilizations)"
            body = f"""{greeting}

I am writing to express my strong interest in joining {comp} for upcoming offshore campaigns, freelancing roles, and ad-hoc mobilizations as a Senior CSWIP 3.4U Subsea Inspection Coordinator / Inspection Engineer. I am 100% available for immediate worldwide freelance mobilization.

Key Qualifications & Proven Track Record:
• CSWIP 3.4U Certification: Underwater Inspection Controller Grade 3.4U (Cert #671180 — Valid to 14th October 2030).
• Academic Background: B.Eng (Hons) in Electrical & Electronic Engineering, International Islamic University Malaysia (IIUM).
• 11+ Years Subsea & Offshore Experience: Over 11+ years of dedicated subsea inspection experience as CSWIP 3.4U Inspection Coordinator, Inspection Engineer, and Lead Report Coordinator across diving and ROV subsea inspection campaigns, UWILD surveys, deepwater structures (XMT, manifolds, PLET, jumpers), pipeline integrity, FMD, and decommissioning surveys.
• Major Operator Campaign History: PTT / Chevron Thailand (DP2 Mermaid Sapphire & DP2 MMA Pride), Subsea 7 / North Oil Company Qatar (DP2DSV Swordfish), Sarawak Shell (F23 & Malikai TTR), PETRONAS Carigali (Tangga Barat TBCP), PTTEP (Block H & K Deepwater, Kikeh SPAR UWILD), Mubadala (Pegaga ICPP), and Murphy Oil (Kikeh).
• Software Mastery: VisualSoft Suite 10.3 (Certified), Digital EdgeDVR, AutoCAD 2D/3D, MS Project, and comprehensive CSWIP 3.4U QA/QC client deliverables.
• Valid Mandatory Offshore Clearances: OPITO FOET with CA-EBS (Valid to May 2027), Comprehensive Offshore Medical (OEUK, PETRONAS MPM, Shell, ExxonMobil, STCW 2010 ILO, QatarEnergy LNG & PTTEP approved — Valid to 2nd June 2028), International Passport (Valid to 28th July 2027), and Malaysian Seaman Book.

Attached is my comprehensive CV (PDF format). Full certified certificate packages and editable formats are available immediately upon request.

Thank you for your time and consideration. I look forward to discussing potential campaign requirements with {comp}.

Best regards,

{prof_cfg['name'].upper()}
Senior CSWIP 3.4U Subsea Inspection Coordinator / Inspection Engineer
Mobile / WhatsApp: {prof_cfg['phone']}
Email: {prof_cfg['email']}
Location: {prof_cfg['location']}
"""
        else: # amin
            subject = f"CSWIP 3.4U Subsea Inspection Engineer / Data Recorder - {prof_cfg['name']} (Freelance / Contract / Permanent)"
            body = f"""{greeting}

I am writing to express my strong interest in joining {comp} for upcoming offshore campaigns, ad-hoc freelancing mobilizations, contract, or permanent positions as a CSWIP 3.4U Subsea Inspection Engineer / Data Recorder. I am 100% open for freelancing, contract, or permanent roles and willing to relocate worldwide.

With over 280+ offshore days across 10+ subsea campaigns (including PETRONAS, PTTEP, CHOC, Fugro Upper Zakum, ADNOC, and RINA Class surveys), I possess extensive hands-on expertise in subsea data acquisition, pipeline tracking (TSS 440/350 & MBES), Flooded Member Detection (Cobalt-60 & Impact Subsea FMD), and digital inspection suites (Sirrihatt, EdgeDVR, IDAMS).

Key Qualifications & Active Offshore Clearances:
• CSWIP 3.4U Subsea Inspection Engineer (Cert #542968 - Valid to 2028)
• B.Eng (Hons) Petroleum Engineering, Universiti Teknologi Malaysia (UTM)
• OPITO BOSIET with CA-EBS & EBS, PETRONAS & OEUK Offshore Medicals (Valid to May 2027)
• ADNOC Offshore HSE Induction (Valid to Nov 2026) & Malaysian Seaman Card/Book
• Digital Suites: Sirrihatt, Digital EdgeDVR, IDAMS WinCairs, VOYIS Live Discovery/VSLAM, Agisoft 3D Photogrammetry, OBS Studio

Attached is my latest CV (PDF format). Full supporting certificate packages and editable formats are available immediately upon request.

I am 100% available for immediate worldwide offshore mobilization, open for freelancing / contract / permanent roles, and willing to relocate. I look forward to hearing from you soon regarding opportunities with {comp}.

Best regards,

{prof_cfg['name'].upper()}
CSWIP 3.4U Subsea Inspection Engineer / Data Recorder
Mobile / WhatsApp: {prof_cfg['phone']}
Email: {prof_cfg['email']}
Location: {prof_cfg['location']}
"""

        msg = MIMEMultipart()
        msg["From"] = f"{prof_cfg['name']} <{prof_cfg['email']}>"
        msg["To"] = target_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with open(cv_path, "rb") as cv_f:
            part = MIMEApplication(cv_f.read(), Name=os.path.basename(cv_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(cv_path)}"'
            msg.attach(part)

        try:
            print(f"     Sending email via {prof_cfg['email']}...")
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
            server.starttls()
            server.login(prof_cfg["email"], prof_cfg["app_password"])
            server.sendmail(prof_cfg["email"], target_email, msg.as_string())
            server.quit()
            print(f"     SUCCESS: Email delivered to {target_email}!")
            sent_count += 1

            ledger.append(target_email.lower())
            with open(ledger_file, "w", encoding="utf-8") as f:
                json.dump(list(set(ledger)), f, indent=2)

            if idx < len(to_send):
                delay = random.randint(60, 110)
                print(f"     Waiting {delay}s safety delay before next email...")
                time.sleep(delay)
        except Exception as e:
            print(f"     FAILED to send to {target_email}: {e}")

    # Mark last_run_date to today
    sched["last_run_date"] = today_str
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(sched, f, indent=2)

    print(f"\n=======================================================")
    print(f"   SWEEP DISPATCH FINISHED: {sent_count} EMAILS DELIVERED")
    print(f"   Marked last_run_date: {today_str}")
    print(f"=======================================================\n")

if __name__ == "__main__":
    main()
