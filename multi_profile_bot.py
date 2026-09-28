import os, sys, json, time, random, argparse, smtplib, imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
CONTACTS_FILE = os.path.join(BASE_DIR, "contacts_data.json")

def load_profile(profile_name):
    p_dir = os.path.join(PROFILES_DIR, profile_name.lower())
    cfg_file = os.path.join(p_dir, "config.json")
    ledger_file = os.path.join(p_dir, "sent_ledger.json")
    
    if not os.path.exists(cfg_file):
        raise FileNotFoundError(f"Profile config not found for '{profile_name}' at {cfg_file}")
        
    with open(cfg_file, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    if os.path.exists(ledger_file):
        with open(ledger_file, "r", encoding="utf-8") as f:
            ledger = json.load(f)
    else:
        ledger = []
        
    cv_path = os.path.join(p_dir, "cv", config.get("cv_filename", ""))
    return config, ledger, ledger_file, cv_path

def check_live_sent_mail(user, app_pass, target_email):
    """Query live Gmail server to verify if email was EVER sent to target in history."""
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

def generate_email_content(profile_config, contact):
    pic = contact.get("pic_name", "").strip()
    company = contact.get("company", "Your Company").strip()
    
    greeting = f"Hi {pic.split()[0]}," if pic and pic.lower() not in ["none", "all", "recruitment team", "hr team", "crewing team", "general desk"] else "Dear Hiring & Crewing Team,"
    
    if profile_config["profile_id"] == "basyir":
        subject = f"Senior CSWIP 3.4U Subsea Inspection Coordinator / Inspection Engineer - {profile_config['name']} (Freelance / Ad-Hoc Mobilizations)"
        body = f"""{greeting}

I am writing to express my strong interest in joining {company} for upcoming offshore campaigns, freelancing roles, and ad-hoc mobilizations as a Senior CSWIP 3.4U Subsea Inspection Coordinator / Inspection Engineer. I am 100% available for immediate worldwide freelance mobilization.

Key Qualifications & Proven Track Record:
• CSWIP 3.4U Certification: Underwater Inspection Controller Grade 3.4U (Cert #671180 — Valid to 14th October 2030).
• Academic Background: B.Eng (Hons) in Electrical & Electronic Engineering, International Islamic University Malaysia (IIUM).
• 11+ Years Subsea & Offshore Experience: Over 11+ years of dedicated subsea inspection experience as CSWIP 3.4U Inspection Coordinator, Inspection Engineer, and Lead Report Coordinator across diving and ROV subsea inspection campaigns, UWILD surveys, deepwater structures (XMT, manifolds, PLET, jumpers), pipeline integrity, FMD, and decommissioning surveys.
• Major Operator Campaign History: PTT / Chevron Thailand (DP2 Mermaid Sapphire & DP2 MMA Pride), Subsea 7 / North Oil Company Qatar (DP2DSV Swordfish), Sarawak Shell (F23 & Malikai TTR), PETRONAS Carigali (Tangga Barat TBCP), PTTEP (Block H & K Deepwater, Kikeh SPAR UWILD), Mubadala (Pegaga ICPP), and Murphy Oil (Kikeh).
• Software Mastery: VisualSoft Suite 10.3 (Certified), Digital EdgeDVR, AutoCAD 2D/3D, MS Project, and comprehensive CSWIP 3.4U QA/QC client deliverables.
• Valid Mandatory Offshore Clearances: OPITO FOET with CA-EBS (Valid to May 2027), Comprehensive Offshore Medical (OEUK, PETRONAS MPM, Shell, ExxonMobil, STCW 2010 ILO, QatarEnergy LNG & PTTEP approved — Valid to 2nd June 2028), International Passport (Valid to 28th July 2027), and Malaysian Seaman Book.

Attached is my comprehensive CV (PDF format). Full certified certificate packages and editable formats are available immediately upon request.

Thank you for your time and consideration. I look forward to discussing potential campaign requirements with {company}.

Best regards,

{profile_config['name'].upper()}
Senior CSWIP 3.4U Subsea Inspection Coordinator / Inspection Engineer
Mobile / WhatsApp: {profile_config['phone']}
Email: {profile_config['email']}
Location: Kota Damansara, Selangor / Kuala Lumpur, Malaysia (Point of Hire / Nearest Airport: KLIA / KUL | 100% Available for Freelance / Ad-Hoc Mobilizations)
"""
    else: # amin
        subject = f"CSWIP 3.4U Subsea Inspection Engineer / Data Recorder - {profile_config['name']} (Freelance / Contract / Permanent)"
        body = f"""{greeting}

I am writing to express my strong interest in joining {company} for upcoming offshore campaigns, ad-hoc freelancing mobilizations, contract, or permanent positions as a CSWIP 3.4U Subsea Inspection Engineer / Data Recorder. I am 100% open for freelancing, contract, or permanent roles and willing to relocate worldwide.

With over 280+ offshore days across 10+ subsea campaigns (including PETRONAS, PTTEP, CHOC, Fugro Upper Zakum, ADNOC, and RINA Class surveys), I possess extensive hands-on expertise in subsea data acquisition, pipeline tracking (TSS 440/350 & MBES), Flooded Member Detection (Cobalt-60 & Impact Subsea FMD), and digital inspection suites (Sirrihatt, EdgeDVR, IDAMS).

Key Qualifications & Active Offshore Clearances:
• CSWIP 3.4U Subsea Inspection Engineer (Cert #542968 - Valid to 2028)
• B.Eng (Hons) Petroleum Engineering, Universiti Teknologi Malaysia (UTM)
• OPITO BOSIET with CA-EBS & EBS, PETRONAS & OEUK Offshore Medicals (Valid to May 2027)
• ADNOC Offshore HSE Induction (Valid to Nov 2026) & Malaysian Seaman Card/Book
• Digital Suites: Sirrihatt, Digital EdgeDVR, IDAMS WinCairs, VOYIS Live Discovery/VSLAM, Agisoft 3D Photogrammetry, OBS Studio

Attached is my latest CV (PDF format). Full supporting certificate packages and editable formats are available immediately upon request.

I am 100% available for immediate worldwide offshore mobilization, open for freelancing / contract / permanent roles, and willing to relocate. I look forward to hearing from you soon regarding opportunities with {company}.

Best regards,

{profile_config['name'].upper()}
CSWIP 3.4U Subsea Inspection Engineer / Data Recorder
Mobile / WhatsApp: {profile_config['phone']}
Email: {profile_config['email']}
Location: {profile_config['location']}
"""
    return subject, body

def send_profile_email(profile_config, target_email, subject, body, cv_path):
    msg = MIMEMultipart()
    msg["From"] = f"{profile_config['name']} <{profile_config['email']}>"
    msg["To"] = target_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if os.path.exists(cv_path):
        with open(cv_path, "rb") as cv_f:
            part = MIMEApplication(cv_f.read(), Name=os.path.basename(cv_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(cv_path)}"'
            msg.attach(part)
    else:
        raise FileNotFoundError(f"CV PDF not found at {cv_path}")

    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
    server.starttls()
    server.login(profile_config["email"], profile_config["app_password"])
    server.sendmail(profile_config["email"], target_email, msg.as_string())
    server.quit()

def run_campaign(profile_name, batch_size=10, dry_run=False):
    config, ledger, ledger_file, cv_path = load_profile(profile_name)
    
    print(f"\n=======================================================")
    print(f"   MULTI-PROFILE OUTREACH ENGINE: {config['name'].upper()}")
    print(f"=======================================================")
    print(f"• Sender Email     : {config['email']}")
    print(f"• Profile ID       : {config['profile_id']}")
    print(f"• Target CV File   : {cv_path}")
    print(f"• CV Exists        : {'YES (Ready)' if os.path.exists(cv_path) else 'NO (Missing!)'}")
    print(f"• Previous Sent Log: {len(ledger)} contacts in ledger")
    print(f"• Batch Size Target: {batch_size} emails")
    print(f"• Mode             : {'DRY RUN (Simulation)' if dry_run else 'LIVE OUTREACH'}")
    print("=======================================================\n")
    
    if not os.path.exists(cv_path):
        print(f"ABORT: Cannot run campaign without valid CV PDF at {cv_path}")
        return

    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        contacts = json.load(f)

    ledger_set = set(e.strip().lower() for e in ledger)
    
    # Filter available contacts
    eligible_contacts = []
    for c in contacts:
        e = c.get("email", "").strip().lower()
        if not e or any(ex in e or ex in c.get("company", "").lower() for ex in ["mcsoil", "vantris", "alam-maritim"]):
            continue
        if e in ledger_set:
            continue
        eligible_contacts.append(c)

    print(f"Total Master Contacts : {len(contacts)}")
    print(f"Eligible Unsent Queue : {len(eligible_contacts)} contacts available for {config['name']}")
    
    if not eligible_contacts:
        print(f"All contacts have already been emailed for {config['name']}!")
        return

    to_process = eligible_contacts[:batch_size]
    sent_count = 0

    for idx, contact in enumerate(to_process, 1):
        target_email = contact["email"].strip()
        company = contact.get("company", "Company")
        pic = contact.get("pic_name", "Recruitment")
        
        print(f"\n[{idx}/{len(to_process)}] Processing: {company} ({pic}) <{target_email}>")
        
        # Pre-flight Live IMAP Check
        if not dry_run:
            if check_live_sent_mail(config["email"], config["app_password"], target_email):
                print(f"     -> SKIPPED: Already found in live Gmail Sent Mail history!")
                ledger.append(target_email.lower())
                with open(ledger_file, "w", encoding="utf-8") as f:
                    json.dump(list(set(ledger)), f, indent=2)
                continue
                
        subject, body = generate_email_content(config, contact)
        
        if dry_run:
            print(f"     [SIMULATION] Would send Subject: '{subject[:60]}...'")
            print(f"     [SIMULATION] Attaching: {os.path.basename(cv_path)}")
        else:
            try:
                print(f"     Sending email via {config['email']}...")
                send_profile_email(config, target_email, subject, body, cv_path)
                print(f"     SUCCESS: Email delivered to {target_email}!")
                sent_count += 1
                
                # Update ledger immediately
                ledger.append(target_email.lower())
                with open(ledger_file, "w", encoding="utf-8") as f:
                    json.dump(list(set(ledger)), f, indent=2)
                    
                # Delay between sends
                if idx < len(to_process):
                    delay = random.randint(60, 110)
                    print(f"     Waiting {delay}s safety delay before next email...")
                    time.sleep(delay)
            except Exception as err:
                print(f"     FAILED to send to {target_email}: {err}")

    print(f"\n=======================================================")
    print(f"   CAMPAIGN BATCH COMPLETED FOR {config['name'].upper()}")
    print(f"   Successfully Sent: {sent_count} emails")
    print(f"   Total in Profile Ledger: {len(ledger)} / {len(contacts)}")
    print(f"=======================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Profile Subsea Outreach Engine")
    parser.add_argument("--profile", type=str, required=True, choices=["amin", "basyir"], help="Profile to send for (amin/basyir)")
    parser.add_argument("--batch", type=int, default=10, help="Batch limit (default 10)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run simulation")
    args = parser.parse_args()
    
    run_campaign(args.profile, args.batch, args.dry_run)
