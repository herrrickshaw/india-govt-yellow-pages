#!/usr/bin/env python3
"""Generate outreach materials for urgent government incentive applications.

Creates ready-to-send emails, phone scripts, tracking sheets, and contact lists
for reaching out to officials about closing application deadlines.

Usage:
    python3 scripts/generate_outreach_materials.py [--format csv|excel|email]
"""
import csv
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
URGENT_CONTACTS_FILE = DATA_DIR / "urgent_outreach_contacts.csv"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "reports" / "outreach"


def load_urgent_contacts() -> list:
    """Load urgent contacts from CSV."""
    if not URGENT_CONTACTS_FILE.exists():
        print(f"❌ File not found: {URGENT_CONTACTS_FILE}")
        return []

    contacts = []
    with URGENT_CONTACTS_FILE.open(encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)

    return contacts


def generate_email_drafts(contacts: list) -> dict:
    """Generate draft emails organized by program and priority."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    emails_by_program = defaultdict(list)
    for contact in contacts:
        program = contact.get('policy', '').strip()
        if program:
            emails_by_program[program].append(contact)

    # Generate individual email files
    email_files = {}
    for program, program_contacts in emails_by_program.items():
        priority = int(program_contacts[0].get('priority', '99'))
        days_left = program_contacts[0].get('days_remaining', '0')
        deadline = program_contacts[0].get('deadline_date', 'N/A')

        safe_name = program.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').lower()
        filename = f"email_priority_{priority:02d}_{safe_name}.txt"
        filepath = OUTPUT_DIR / filename

        email_content = f"""URGENT OUTREACH EMAIL - PRIORITY {priority}
Program: {program}
Days Remaining: {days_left}
Application Deadline: {deadline}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIMARY CONTACT (PROGRAM DIRECTOR):
"""
        # Find EOI contact (Program Director)
        eoi_contact = None
        for c in program_contacts:
            if 'EOI' in c.get('contact_type', ''):
                eoi_contact = c
                break

        if eoi_contact:
            email_content += f"""
Name: {eoi_contact.get('contact_name', 'N/A')}
Title: {eoi_contact.get('designation', 'N/A')}
Email: {eoi_contact.get('email', 'N/A')}
Phone: {eoi_contact.get('phones', 'N/A')}
Organization: {eoi_contact.get('organization', 'N/A')}

EMAIL DRAFT:
────────────────────────────────────────────────────────────────────────

Subject: {program} Application Support - Deadline {deadline} ({days_left} days)

Dear {eoi_contact.get('contact_name', 'Sir/Madam').split()[0]},

We are reaching out regarding the {program} program, which has an imminent
application deadline of {deadline} ({days_left} days remaining).

We would like to discuss:
• Clarification on current application requirements
• Technical support for pending submissions
• Possible extension pathways if urgent

Could we schedule a brief call this week? We can coordinate around your
schedule at your convenience.

Contact: [YOUR NAME]
Phone: [YOUR PHONE]
Email: [YOUR EMAIL]

Regards,
[YOUR ORGANIZATION]

────────────────────────────────────────────────────────────────────────
"""

        # Add secondary contacts
        email_content += f"""
SECONDARY CONTACTS (ESCALATION):
"""
        for i, contact in enumerate(program_contacts, 1):
            if 'EOI' not in contact.get('contact_type', ''):
                email_content += f"""
{i}. {contact.get('contact_name', 'N/A')} ({contact.get('designation', 'N/A')})
   Email: {contact.get('email', 'N/A')}
   Phone: {contact.get('phones', 'N/A')}
   When: {contact.get('outreach_channel', 'Email')} | Follow-up: {contact.get('follow_up_days', '7')} days
"""

        email_content += f"""

BEST TIME TO CONTACT:
10:00-11:30 AM IST or 2:00-3:30 PM IST (avoid 11:30 AM-2 PM and after 4 PM)

CALL SCRIPT (if calling):
────────────────────────────────────────────────────────────────────────
"Namaste [NAME], thank you for taking the call. I'm [YOUR NAME] from
[ORGANIZATION]. I'm calling regarding the {program} scheme with {days_left}
days left before the application deadline. We have companies interested and
would like to ensure smooth processing. Could you point us to the right
coordinator or notify them of incoming submissions?"

TRACKING:
✓ Date Sent: ___________
✓ Response: ___________
✓ Next Step: ___________
✓ Follow-up Date: ___________

"""

        with filepath.open('w', encoding='utf-8') as f:
            f.write(email_content)

        email_files[program] = str(filepath)

    return email_files


def generate_excel_tracking_sheet(contacts: list) -> str:
    """Generate a CSV tracking sheet for email follow-ups."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / "outreach_tracking_sheet.csv"

    with filepath.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "Priority",
            "Program",
            "Days Remaining",
            "Deadline",
            "Contact Name",
            "Title",
            "Email",
            "Phone",
            "Contact Type",
            "Outreach Channel",
            "Date Sent",
            "Response Received",
            "Response Date",
            "Follow-up Needed",
            "Follow-up Date",
            "Status",
            "Notes",
        ])

        # Data rows
        for contact in contacts:
            writer.writerow([
                contact.get('priority', ''),
                contact.get('policy', ''),
                contact.get('days_remaining', ''),
                contact.get('deadline_date', ''),
                contact.get('contact_name', ''),
                contact.get('designation', ''),
                contact.get('email', ''),
                contact.get('phones', ''),
                contact.get('contact_type', ''),
                contact.get('outreach_channel', ''),
                '',  # Date Sent
                '',  # Response Received (YES/NO)
                '',  # Response Date
                contact.get('follow_up_days', ''),  # Follow-up after N days
                '',  # Follow-up Date
                '🔴 TODO',  # Status
                '',  # Notes
            ])

    print(f"✓ Tracking sheet: {filepath}")
    return str(filepath)


def generate_contact_summary(contacts: list) -> str:
    """Generate a quick reference contact summary."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / "contact_summary.txt"

    # Group by program
    by_program = defaultdict(list)
    for c in contacts:
        by_program[c.get('policy', '')].append(c)

    content = """╔════════════════════════════════════════════════════════════════════════════╗
║              URGENT OUTREACH CONTACTS - QUICK REFERENCE                   ║
╚════════════════════════════════════════════════════════════════════════════╝

"""

    for program in sorted(by_program.keys()):
        contacts_list = by_program[program]
        priority = contacts_list[0].get('priority', '99')
        days = contacts_list[0].get('days_remaining', '0')
        deadline = contacts_list[0].get('deadline_date', 'N/A')

        urgency = "🔴 CRITICAL" if int(days) <= 30 else "🟡 HIGH" if int(
            days) <= 90 else "🟢 NORMAL"

        content += f"""
{urgency} PRIORITY {priority}: {program.upper()}
{"─" * 76}
Deadline: {deadline} ({days} days remaining)

"""

        for contact in contacts_list:
            contact_type = "📱 PROGRAM LEAD" if "Program Director" in contact.get(
                'contact_type', '') else "👤 MINISTRY" if "Senior Ministry" in contact.get(
                'contact_type', '') else "🔧 TECHNICAL"

            content += f"""  {contact_type}
  Name: {contact.get('contact_name', 'N/A')}
  Title: {contact.get('designation', 'N/A')}
"""

            if contact.get('email'):
                content += f"  Email: {contact.get('email', 'N/A')}\n"
            if contact.get('phones'):
                content += f"  Phone: {contact.get('phones', 'N/A')}\n"

            content += f"  Channel: {contact.get('outreach_channel', 'Email')} | Follow-up: {contact.get('follow_up_days', '7')} days\n\n"

    with filepath.open('w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Contact summary: {filepath}")
    return str(filepath)


def main():
    """Generate all outreach materials."""
    contacts = load_urgent_contacts()

    if not contacts:
        print("❌ No urgent contacts loaded")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n📧 Generating Outreach Materials")
    print("=" * 80)

    # Generate email drafts
    print("\n1️⃣  Email Drafts by Program Priority:")
    email_files = generate_email_drafts(contacts)
    for program, filepath in email_files.items():
        print(f"   ✓ {program}")

    # Generate tracking sheet
    print("\n2️⃣  Excel Tracking Sheet:")
    tracking_file = generate_excel_tracking_sheet(contacts)

    # Generate contact summary
    print("\n3️⃣  Quick Reference Summary:")
    summary_file = generate_contact_summary(contacts)

    print("\n" + "=" * 80)
    print(f"✅ All materials generated in: {OUTPUT_DIR}")
    print(f"\nNext Steps:")
    print(f"1. Review outreach priority {OUTPUT_DIR}/contact_summary.txt")
    print(f"2. Customize emails in {OUTPUT_DIR}/email_priority_*.txt files")
    print(f"3. Use tracking sheet to log responses: {tracking_file}")
    print(f"4. Follow escalation path if no response in 5 days")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
