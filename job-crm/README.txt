==========================================================================
                      JOB APPLICATION CRM — AMIN AZMAN
==========================================================================

This folder contains a lightweight Python-based CRM system to automate,
track, and personalize your subsea crew applications.

--------------------------------------------------------------------------
1. FOLDER STRUCTURE
--------------------------------------------------------------------------
job-crm/
│
├── config.py                 # Configuration settings (Gmail, PDF attachments, etc.)
├── 01_setup_database.py      # Imports Excel data to SQLite database
├── 02_send_emails.py         # Sends personalized emails one-by-one with random delays
├── 03_update_status.py       # Interactive terminal utility to search & update statuses
├── 04_dashboard.py           # Real-time stats screen
├── 05_find_contacts.py       # Generates crewing contact search links
│
├── cv_attachments/           # Put your CV PDF file inside this folder!
│
├── crm.db                    # SQLite Database (automatically created)
├── email_log.txt             # Chronological log of emails successfully sent
└── README.txt                # This file

--------------------------------------------------------------------------
2. GETTING STARTED (STEP-BY-STEP)
--------------------------------------------------------------------------
STEP 1: Create the "cv_attachments" folder (automatically created by run) and
        place your latest CV PDF file inside it.
        
STEP 2: Open terminal in this folder and run:
        python 01_setup_database.py
        
        This will read your Excel file and build "crm.db".

STEP 3: Configure your Gmail App Password inside "config.py" on line 6:
        GMAIL_APP_PASSWORD = "znjkeaawhwwfwyrm"

STEP 4: Run the dashboard to check your queue status:
        python 04_dashboard.py

--------------------------------------------------------------------------
3. RUNNING CORES
--------------------------------------------------------------------------
* SENDS PENDING EMAILS (DEFAULT LIMIT = 5 TO PREVENT SPAM):
  python 02_send_emails.py
  
  Want to send more? Use the limit override argument:
  python 02_send_emails.py --limit 10
  
  Want to send all pending emails at once?
  python 02_send_emails.py --no-limit

* UPDATE STATUS & ADD NEW CONTACTS INTERACTIVELY:
  python 03_update_status.py
  
  Use this CLI to update statuses (like 'Replied-NCA' or 'Replied-Interested')
  when companies reply, or insert new crewing emails discovered online.

* RUN STRATEGIC SEARCH LINKS GENERATOR:
  python 05_find_contacts.py
  
  This generates "contact_search_links.txt". You can open it, click the pre-formed
  LinkedIn and Google Search links to discover names/emails of crewing staff,
  and then use 03_update_status.py to add them to your database.

--------------------------------------------------------------------------
4. ANTI-SPAM RECOMMENDATIONS
--------------------------------------------------------------------------
- The sending script is configured with a random delay of 45 to 120 seconds
  between emails to simulate normal user behavior.
- We recommend sending a maximum of 50 emails per day to keep your Gmail
  account in good standing.
==========================================================================
