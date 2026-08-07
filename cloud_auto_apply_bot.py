import json
import smtplib
import time
import random
import os
import openpyxl
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

# ==========================================
# DUAL SENDER ACCOUNTS CONFIGURATION
# ==========================================
GMAIL_PASS_1 = os.environ.get('GMAIL_APP_PASS_1', 'sznpitgpdmhpkvee')
GMAIL_PASS_2 = os.environ.get('GMAIL_APP_PASS_2', 'djggjmmezbjxofbi')

ACCOUNTS = [
    {"email": "amin87.azman@gmail.com", "pass": GMAIL_PASS_1},
    {"email": "aminazman.inspection@gmail.com", "pass": GMAIL_PASS_2}
]

BATCH_LIMIT = 25           # 25 emails total per cloud session
MIN_DELAY_SECONDS = 30     # Fast mode for cloud runner (30s)
MAX_DELAY_SECONDS = 90     # Fast mode for cloud runner (90s)

JSON_FILE = "contacts_data.json"
EXCEL_FILE = "Master_Subsea_Contacts_v2.xlsx"
CV_PDF_PATH = "CV_Muhammad_Amin_Azman_3.4U_Inspection_Engineer.pdf"
ZIP_DOCS_PATH = r"c:\Users\amin8\Desktop\AG Projects\AG-Offshore\All_Certificates_Amin_Azman.zip"
PROJECT_DIR = os.getcwd()

def generate_email_content(contact, sender_email):
    company = contact.get("company", "Subsea Team")
    pic_name = contact.get("pic_name", "")
    email = contact.get("email", "").lower()
    location = contact.get("location", "").lower()
    remark = str(contact.get("remark", "")).lower()
    
    salutation = f"Hi {pic_name}," if pic_name else f"Hi {company} Recruitment Team,"
    
    is_uk = any(uk_tag in email or uk_tag in location or uk_tag in remark or uk_tag in company.lower() 
               for uk_tag in [".uk", "uk", "aberdeen", "scotland", "north sea", "ukcs", "united kingdom"])
    
    subject = f"[AVAILABLE IMMEDIATELY] CSWIP 3.4U Engineer | CA-EBS / Petronas / ADNOC Ready | Amin Azman"
    
    uk_clause = ""
    if is_uk:
        uk_clause = "\n• North Sea / UKCS Readiness: Certified CSWIP 3.4U Inspection Engineer with valid OPITO CA-EBS (5750), OEUK Medical, and Seaman's Book. Available for vessel-based North Sea/UKCS campaigns outside 12nm via Letter of Guarantee (LOG) / Seafarer Transit status."

    body = f"""{salutation}

I am a Certified CSWIP 3.4U Subsea Inspection Engineer open for long-term contract positions, offshore campaigns, or ad-hoc freelance mobilizations (3–5 days readiness).

• Certs: CSWIP 3.4U (Cert: 542968), OPITO FOET w/ CA-EBS, OEUK Medical, Petronas OSP, ADNOC Induction & Medical Clear, Seafarers' SID & Passport{uk_clause}
• Tech: Voyis 3D Laser & VSLAM, TSS 440/350 Pipe Tracker, MBES Bathymetry, Gamma FMD, Sirrihatt / IDAMS / EdgeDVR

Full Documentation & Verified Credentials:
🔗 Interactive CV & Project History: https://ag-offshore.vercel.app/certificates.html
📁 All Certificates & Document Pack (Google Drive): https://tinyurl.com/29sg45dw

(Print-ready CV PDF attached for your convenience)

Best regards,

Muhammad Amin bin Azman
CSWIP 3.4U Subsea Inspection Engineer
📞 Mobile / WhatsApp: +60 12-506 5516
✉️ Email: {sender_email}
🔗 LinkedIn: https://www.linkedin.com/in/aminazman-inspection
🌐 Profile & Credentials: https://ag-offshore.vercel.app
"""
    return subject, body

def push_to_vercel():
    try:
        subprocess.run(["git", "add", "contacts_data.json", "Master_Subsea_Contacts_v2.xlsx"], cwd=PROJECT_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "Real-time dual account CRM status update"], cwd=PROJECT_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("     Synced live status to Vercel CRM!")
    except Exception as e:
        print(f"     Git sync error: {e}")

def send_via_smtp(sender_acc, target_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = f"Muhammad Amin Azman <{sender_acc['email']}>"
    msg["To"] = target_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach ONLY 1 Single Print-ready CV PDF (No ZIP attachments to pass enterprise firewalls)
    if os.path.exists(CV_PDF_PATH):
        with open(CV_PDF_PATH, "rb") as cv_f:
            part = MIMEApplication(cv_f.read(), Name=os.path.basename(CV_PDF_PATH))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(CV_PDF_PATH)}"'
            msg.attach(part)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_acc["email"], sender_acc["pass"])
    server.sendmail(sender_acc["email"], target_email, msg.as_string())
    server.quit()

def run_dual_account_campaign():
    print("=== DUAL-ACCOUNT SAFE AUTO-APPLY CAMPAIGN INITIALIZED ===")
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        contacts = json.load(f)

    # Filter unsent contacts (excluding Alam Maritim & Bounced)
    unsent_contacts = [
        c for c in contacts 
        if str(c.get("sent")).upper() not in ["TRUE", "TRUE (SIMULATED)", "BOUNCED", "REDIRECTED"] 
        and c.get("email") 
        and "alam-maritim" not in c.get("email", "").lower() 
        and "alam maritim" not in c.get("company", "").lower()
    ]

    print(f"Total Active Database Contacts: {len(contacts)}")
    print(f"Unsent Active Contacts Available: {len(unsent_contacts)}")
    print(f"Batch Limit Set To: {BATCH_LIMIT} emails tonight\n")

    if not unsent_contacts:
        print("All active contacts have already been emailed!")
        return

    batch_to_send = unsent_contacts[:BATCH_LIMIT]
    sent_count = 0

    for idx, contact in enumerate(batch_to_send, 1):
        target_email = contact["email"].strip()
        company = contact.get("company", "Company").encode('ascii', 'ignore').decode('ascii')
        
        # Alternate between ACCOUNTS (Round Robin)
        sender_acc = ACCOUNTS[(idx - 1) % len(ACCOUNTS)]
        
        subject, body = generate_email_content(contact, sender_acc["email"])
        safe_subject = subject.encode('ascii', 'ignore').decode('ascii')

        print(f"[{idx}/{len(batch_to_send)}] Processing: {company} <{target_email}>")
        print(f"     Sender Account: {sender_acc['email']}")
        print(f"     Subject: {safe_subject}")

        try:
            send_via_smtp(sender_acc, target_email, subject, body)
            print(f"     SUCCESS: Email sent to {target_email} via {sender_acc['email']}")
            
            contact["sent"] = "TRUE"
            contact["sent_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            contact["status"] = "SENT / PENDING"
            contact["sender_email"] = sender_acc["email"]
            sent_count += 1

            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(contacts, f, indent=2)
            
            push_to_vercel()

            # Randomized long delay (12 to 25 mins)
            if idx < len(batch_to_send):
                delay = random.randint(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                print(f"     Sleeping for {delay} seconds (~{delay//60} mins) before next send...\n")
                time.sleep(delay)

        except Exception as e:
            print(f"     FAILED to send to {target_email}: {e}")

    # Sync Excel
    print("\nSynchronizing campaign status to Master Excel v2...")
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws = wb["Master Contacts"]
        for row in range(2, ws.max_row + 1):
            cell_email = str(ws.cell(row=row, column=6).value or '').strip().lower()
            for c in contacts:
                if c.get("email") and c["email"].strip().lower() == cell_email and c.get("sent_date"):
                    ws.cell(row=row, column=1, value=c["status"])
                    ws.cell(row=row, column=11, value=f"TRUE ({c['sent_date']})")
                    break
        wb.save(EXCEL_FILE)
        print("Master Excel v2 updated successfully!")
    except Exception as e:
        print(f"Excel sync error: {e}")

    print(f"\n=== DUAL-ACCOUNT BATCH COMPLETE: Processed {sent_count} emails ===")

if __name__ == "__main__":
    run_dual_account_campaign()
