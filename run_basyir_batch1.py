import os, sys, json, time, random, smtplib, imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles", "basyir")
TARGETS_FILE = os.path.join(PROFILES_DIR, "batch1_targets.json")
CONFIG_FILE = os.path.join(PROFILES_DIR, "config.json")
LEDGER_FILE = os.path.join(PROFILES_DIR, "sent_ledger.json")

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

def run():
    print(f"\n=======================================================")
    print(f"   BASYIR BATCH 1 CLOUD DISPATCHER (MONDAY MORNING 8:30 AM)")
    print(f"=======================================================")
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        targets = json.load(f)
        
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            ledger = json.load(f)
    else:
        ledger = []
        
    cv_path = os.path.join(PROFILES_DIR, "cv", config.get("cv_filename", ""))
    if not os.path.exists(cv_path):
        print(f"ERROR: CV PDF not found at {cv_path}")
        return

    ledger_set = set(e.strip().lower() for e in ledger)
    
    print(f"Sender: {config['name']} <{config['email']}>")
    print(f"Total Targets in Batch 1: {len(targets)}")
    print(f"CV Attachment: {os.path.basename(cv_path)}")
    print("=======================================================\n")
    
    sent_count = 0
    for idx, target in enumerate(targets, 1):
        target_email = target["email"].strip()
        comp = target.get("company", "Company")
        pic = target.get("pic", "Recruitment Team")
        
        print(f"[{idx}/{len(targets)}] Target: {comp} ({pic}) <{target_email}>")
        
        # 1. Check local ledger
        if target_email.lower() in ledger_set:
            print("     -> SKIPPED (Already in local ledger)")
            continue
            
        # 2. Check live Google Sent Mail
        if check_live_sent_mail(config["email"], config["app_password"], target_email):
            print("     -> SKIPPED (Already in live Google Sent Mail history)")
            ledger.append(target_email.lower())
            with open(LEDGER_FILE, "w", encoding="utf-8") as f:
                json.dump(list(set(ledger)), f, indent=2)
            continue
            
        # 3. Build Email
        greeting = f"Hi {pic.split()[0]}," if pic and pic.lower() not in ["none", "all", "recruitment team", "hr team", "crewing team", "operations team", "general desk", "crewing desk", "recruitment desk"] else "Dear Hiring & Crewing Team,"
        
        subject = f"Senior CSWIP 3.4U Subsea Inspection Coordinator / Inspection Engineer - {config['name']} (Freelance / Ad-Hoc Mobilizations)"
        
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

{config['name'].upper()}
Senior CSWIP 3.4U Subsea Inspection Coordinator / Inspection Engineer
Mobile / WhatsApp: {config['phone']}
Email: {config['email']}
Location: {config['location']}
"""
        
        msg = MIMEMultipart()
        msg["From"] = f"{config['name']} <{config['email']}>"
        msg["To"] = target_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        with open(cv_path, "rb") as cv_f:
            part = MIMEApplication(cv_f.read(), Name=os.path.basename(cv_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(cv_path)}"'
            msg.attach(part)
            
        try:
            print(f"     Sending email via {config['email']}...")
            server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
            server.starttls()
            server.login(config["email"], config["app_password"])
            server.sendmail(config["email"], target_email, msg.as_string())
            server.quit()
            print(f"     SUCCESS: Email delivered to {target_email}!")
            sent_count += 1
            
            ledger.append(target_email.lower())
            with open(LEDGER_FILE, "w", encoding="utf-8") as f:
                json.dump(list(set(ledger)), f, indent=2)
                
            if idx < len(targets):
                delay = random.randint(60, 110)
                print(f"     Waiting {delay}s safety delay before next email...")
                time.sleep(delay)
        except Exception as e:
            print(f"     FAILED to send to {target_email}: {e}")
            
    print(f"\n=======================================================")
    print(f"   BATCH 1 DISPATCH COMPLETED: {sent_count} EMAILS SENT")
    print(f"=======================================================\n")

if __name__ == "__main__":
    run()
