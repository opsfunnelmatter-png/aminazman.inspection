import os, sys, json, time, random, smtplib, imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "schedule_config.json")
TARGETS_FILE = os.path.join(BASE_DIR, "profiles", "basyir", "batch3_targets.json")

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
        # FAIL-SAFE CRITICAL GUARD: Never assume unsent on error!
        # If network error occurs, assume it was sent to prevent ANY risk of duplicate spam!
        print(f"     [SAFETY LOCK] Skipping {target_email} due to check error to prevent duplicate email!")
        return True

def main():
    now_utc = datetime.now(timezone.utc)
    MYT = timezone(timedelta(hours=8))
    now_myt = datetime.now(MYT)
    today_str = now_myt.strftime("%Y-%m-%d")
    day_name = now_myt.strftime("%A")

    print(f"\n=======================================================")
    print(f"   TIMEZONE-AWARE CLOUD SCHEDULER ENGINE (10:00 AM LOCAL)")
    print(f"   Current UTC Time : {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"   Current MYT Time : {now_myt.strftime('%Y-%m-%d %H:%M:%S %Z')} ({day_name})")
    print(f"=======================================================")

    if not os.path.exists(CONFIG_FILE):
        print(f"ABORT: Config not found at {CONFIG_FILE}")
        return

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        sched = json.load(f)

    if not sched.get("active", False):
        print("Schedule is INACTIVE in config. Exiting.")
        return

    if day_name not in sched.get("scheduled_days", []):
        print(f"Today ({day_name}) is not in scheduled_days. Exiting.")
        return

    # Load targets
    if not os.path.exists(TARGETS_FILE):
        print(f"ABORT: Targets file not found at {TARGETS_FILE}")
        return

    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        targets = json.load(f)

    profile_name = sched.get("profile", "basyir").lower()
    p_dir = os.path.join(BASE_DIR, "profiles", profile_name)
    prof_cfg_file = os.path.join(p_dir, "config.json")
    ledger_file = os.path.join(p_dir, "sent_ledger.json")

    with open(prof_cfg_file, "r", encoding="utf-8") as f:
        prof_cfg = json.load(f)

    if os.path.exists(ledger_file):
        with open(ledger_file, "r", encoding="utf-8") as f:
            ledger = json.load(f)
    else:
        ledger = []

    cv_path = os.path.join(p_dir, "cv", prof_cfg.get("cv_filename", ""))
    ledger_set = set(e.strip().lower() for e in ledger)

    print(f"Sender: {prof_cfg['name']} <{prof_cfg['email']}>")
    print(f"Total Batch 2 Targets: {len(targets)}")
    print(f"Already in Ledger: {len(ledger_set)}\n")

    # Evaluate who is eligible for 10:00 AM local dispatch in this sweep window
    ready_to_send = []
    waiting_queue = []

    for t in targets:
        em = t["email"].strip().lower()
        if em in ledger_set:
            continue
            
        utc_off = t.get("utc_offset", 8)
        # Calculate recipient's current local hour and minute
        recip_time = now_utc + timedelta(hours=utc_off)
        recip_hour = recip_time.hour
        recip_min = recip_time.minute
        
        # 10:00 AM Local delivery window rule:
        # Eligible if recipient local time is >= 10:00 AM (and during working day < 18:00)
        if recip_hour >= 10 and recip_hour < 18:
            ready_to_send.append((t, recip_time))
        else:
            waiting_queue.append((t, recip_time))

    print(f"--- SWEEP EVALUATION ---")
    print(f"• Ready for Dispatch NOW (Local Time >= 10:00 AM) : {len(ready_to_send)} targets")
    print(f"• Waiting for 10:00 AM in their Timezone       : {len(waiting_queue)} targets")

    for t, rt in waiting_queue:
        print(f"  [WAITING] {t['company']} ({t['region']}) — Current Local: {rt.strftime('%I:%M %p')}")

    if not ready_to_send:
        print("\nNo targets currently in the 10:00 AM window for this sweep. Safe exit.")
        return

    print("\n--- EXECUTING DISPATCH FOR RECIPIENTS AT 10:00 AM LOCAL ---")
    sent_count = 0

    for idx, (target, recip_time) in enumerate(ready_to_send, 1):
        target_email = target["email"].strip()
        comp = target.get("company", "Company")
        pic = target.get("pic", "Recruitment Team")
        region = target.get("region", "Global")

        print(f"\n[{idx}/{len(ready_to_send)}] Target: {comp} ({pic}) <{target_email}>")
        print(f"     Recipient Local Time: {recip_time.strftime('%I:%M %p')} ({region})")

        # Live Google Sent Mail check
        if check_live_sent_mail(prof_cfg["email"], prof_cfg["app_password"], target_email):
            print("     -> SKIPPED (Already in live Google Sent Mail)")
            ledger.append(target_email.lower())
            with open(ledger_file, "w", encoding="utf-8") as f:
                json.dump(list(set(ledger)), f, indent=2)
            continue

        greeting = f"Hi {pic.split()[0]}," if pic and pic.lower() not in ["none", "all", "recruitment team", "hr team", "crewing team", "operations team", "general desk", "crewing desk", "recruitment desk", "asia pacific crewing desk", "singapore recruitment desk", "sea talent acquisition team", "sijin unis / regional desk", "inspection & marine survey desk", "offshore crewing desk", "operations & crewing desk", "hr & crewing department", "offshore recruitment desk", "crewing operations desk", "regional energy recruiter", "commercial & personnel desk"] else "Dear Hiring & Crewing Team,"

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

        msg = MIMEMultipart()
        msg["From"] = f"{prof_cfg['name']} <{prof_cfg['email']}>"
        msg["To"] = target_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with open(cv_path, "rb") as cv_f:
            cv_bytes = cv_f.read()
            if len(cv_bytes) < 500000:
                raise ValueError(f"FATAL: CV attachment at {cv_path} is corrupted or empty ({len(cv_bytes)} bytes)!")
            part = MIMEApplication(cv_bytes, Name=os.path.basename(cv_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(cv_path)}"'
            msg.attach(part)

        # STRICT VERIFICATION: Ensure both text body and PDF attachment exist in MIME message
        if len(msg.get_payload()) < 2:
            raise ValueError(f"FATAL: MIME structure missing attachment! Aborting send to {target_email}!")

        try:
            print(f"     Sending email via {prof_cfg['email']}...")
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
            server.starttls()
            server.login(prof_cfg["email"], prof_cfg["app_password"])
            server.sendmail(prof_cfg["email"], target_email, msg.as_string())
            server.quit()
            print(f"     SUCCESS: Delivered to {target_email} at {recip_time.strftime('%I:%M %p')} recipient local time!")
            sent_count += 1

            ledger.append(target_email.lower())
            with open(ledger_file, "w", encoding="utf-8") as f:
                json.dump(list(set(ledger)), f, indent=2)

            if idx < len(ready_to_send):
                delay = random.randint(60, 110)
                print(f"     Waiting {delay}s safety delay before next send...")
                time.sleep(delay)
        except Exception as e:
            print(f"     FAILED to send to {target_email}: {e}")

    print(f"\n=======================================================")
    print(f"   SWEEP FINISHED: {sent_count} EMAILS DELIVERED AT 10:00 AM LOCAL")
    print(f"=======================================================\n")

if __name__ == "__main__":
    main()
