#!/usr/bin/env python3
"""Match officials against open policies with active/upcoming application windows.

Reads policy_contacts.csv and creates a "who to contact" matrix for incentives
with application windows currently open or opening soon.

Usage:
    python3 scripts/policy_contact_matcher.py [--days-ahead 30]
"""
import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
POLICY_CONTACTS_FILE = DATA_DIR / "policy_contacts.csv"


def load_policy_contacts() -> List[Dict]:
    """Load policy contacts from CSV."""
    if not POLICY_CONTACTS_FILE.exists():
        print(f"❌ File not found: {POLICY_CONTACTS_FILE}")
        return []

    contacts = []
    with POLICY_CONTACTS_FILE.open(encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)

    return contacts


def group_by_policy(contacts: List[Dict]) -> Dict[str, List[Dict]]:
    """Group contacts by policy instrument."""
    grouped = defaultdict(list)
    for contact in contacts:
        instrument = contact.get('instrument', '').strip()
        if instrument:
            grouped[instrument].append(contact)
    return grouped


def get_open_policies(contacts: List[Dict]) -> List[str]:
    """Extract unique open policy instruments."""
    open_policies = set()
    for contact in contacts:
        status = contact.get('status', '').lower()
        instrument = contact.get('instrument', '').strip()
        if instrument and 'open' in status:
            open_policies.add(instrument)
    return sorted(open_policies)


def rank_contacts_by_seniority(contacts: List[Dict]) -> List[Dict]:
    """Rank contacts by designation seniority."""
    # Rank order: Minister > Secretary > Minister of State > others
    rank_map = {
        'minister': 1,
        'secretary': 2,
        'minister of state': 3,
        'additional secretary': 4,
        'joint secretary': 5,
        'director': 6,
    }

    def get_rank(contact):
        designation = contact.get('designation', '').lower()
        for title, rank in rank_map.items():
            if title in designation:
                return rank
        return 99  # Unknown

    return sorted(contacts, key=lambda c: get_rank(c))


def print_policy_contact_matrix(policies_by_instrument: Dict[str, List[Dict]]):
    """Print a matrix of policies and their top contacts."""
    print("\n" + "=" * 100)
    print("🎯 OPEN POLICY INCENTIVES & TOP CONTACTS (WHO TO CONTACT)")
    print("=" * 100)

    for instrument, contacts in sorted(policies_by_instrument.items()):
        if not contacts:
            continue

        status = contacts[0].get('status', 'unknown')
        offering_entity = contacts[0].get('offering_entity', 'unknown')
        instrument_type = contacts[0].get('instrument_type', 'unknown')
        source_url = contacts[0].get('source_url', '')

        print(f"\n📋 {instrument.upper()}")
        print(f"   Sector: {offering_entity} | Type: {instrument_type}")
        print(f"   Status: {status}")
        if source_url:
            print(f"   Website: {source_url}")

        # Rank and show top 3 contacts
        ranked = rank_contacts_by_seniority(contacts)
        print(f"\n   🤝 Top Contacts (by seniority):")

        for i, contact in enumerate(ranked[:3], 1):
            name = contact.get('contact_name', '').strip()
            designation = contact.get('designation', '').strip()
            division = contact.get('division', '').strip()
            phones = contact.get('phones', '').strip()
            email = contact.get('email', '').strip()

            if not name:
                continue

            print(f"\n      {i}. {name}")
            if designation:
                print(f"         Role: {designation}")
            if division:
                print(f"         Division: {division}")
            if phones:
                phone_list = [p.strip() for p in phones.split(',')]
                print(f"         Phone: {', '.join(phone_list)}")
            if email:
                print(f"         Email: {email}")
            else:
                print(f"         Email: [Not available]")


def print_summary_by_sector(policies_by_instrument: Dict[str, List[Dict]]):
    """Print summary grouped by sector/entity."""
    print("\n" + "=" * 100)
    print("📊 SUMMARY BY SECTOR")
    print("=" * 100)

    by_sector = defaultdict(list)
    for instrument, contacts in policies_by_instrument.items():
        if contacts:
            sector = contacts[0].get('offering_entity', 'Unknown').strip()
            by_sector[sector].append(instrument)

    for sector, instruments in sorted(by_sector.items()):
        print(f"\n{sector}")
        for instrument in instruments:
            print(f"  • {instrument}")


def print_contact_lookup(policies_by_instrument: Dict[str, List[Dict]]):
    """Print quick lookup: who is contact for what."""
    print("\n" + "=" * 100)
    print("📇 CONTACT LOOKUP (Who is responsible for what)")
    print("=" * 100)

    by_contact = defaultdict(list)
    for instrument, contacts in policies_by_instrument.items():
        for contact in contacts:
            name = contact.get('contact_name', '').strip()
            designation = contact.get('designation', '').strip()
            email = contact.get('email', '').strip()

            if name:
                key = (name, designation, email)
                by_contact[key].append(instrument)

    for (name, designation, email), instruments in sorted(by_contact.items()):
        if name:
            print(f"\n{name}")
            print(f"  Designation: {designation}")
            if email:
                print(f"  Email: {email}")
            print(f"  Policies:")
            for instrument in sorted(instruments):
                print(f"    • {instrument}")


def print_missing_contacts():
    """Identify policies without contacts assigned."""
    print("\n" + "=" * 100)
    print("⚠️  POLICIES WITHOUT ASSIGNED CONTACTS")
    print("=" * 100)

    contacts = load_policy_contacts()
    open_policies = get_open_policies(contacts)

    no_contact_policies = []
    for policy in open_policies:
        matching_contacts = [c for c in contacts if c.get('instrument', '').strip() == policy]
        assigned_contacts = [c for c in matching_contacts if c.get('contact_name', '').strip()]
        if not assigned_contacts:
            instrument_type = matching_contacts[0].get('instrument_type', '') if matching_contacts else ''
            no_contact_policies.append((policy, instrument_type))

    if no_contact_policies:
        for policy, instr_type in no_contact_policies:
            print(f"\n• {policy}")
            if instr_type:
                print(f"  Type: {instr_type}")
    else:
        print("\n✅ All open policies have assigned contacts!")


def print_application_window_template():
    """Print template for adding application window data."""
    print("\n" + "=" * 100)
    print("🔄 TO ADD APPLICATION WINDOW DATA")
    print("=" * 100)
    print("""
Application windows can be added by:

1. Web scraping policy websites (using Selenium or Playwright):
   - Extract "Application opens" and "Application closes" dates
   - Parse PDF notices with dateutil
   - Store in policy_windows.csv with columns:
     * instrument
     * application_start_date (YYYY-MM-DD)
     * application_end_date (YYYY-MM-DD)
     * last_updated (ISO timestamp)
     * source_url (where date was scraped)

2. Example: policy_windows.csv

   instrument,application_start_date,application_end_date,notification_url
   "Agriculture Infrastructure Fund (AIF)","2026-06-01","2026-12-31","agriinfra.dac.gov.in/notification"
   "MIDH","2026-01-01","2026-08-31","midh.gov.in"
   "PMFBY","2025-06-01","2026-05-31","pmfby.gov.in"

3. Then filter open policies by comparing today's date against these windows.

Current status: {0} open policy instruments identified.
""".format(len(get_open_policies(load_policy_contacts()))))


def main():
    """Main entry point."""
    contacts = load_policy_contacts()

    if not contacts:
        print("❌ No contacts loaded")
        return 1

    policies_by_instrument = group_by_policy(contacts)
    open_policies = get_open_policies(contacts)

    print(f"\n📈 Dataset Summary")
    print(f"   • Total contacts loaded: {len(contacts)}")
    print(f"   • Unique policies: {len(policies_by_instrument)}")
    print(f"   • Open policies: {len(open_policies)}")

    # Print matrices and summaries
    print_policy_contact_matrix(policies_by_instrument)
    print_summary_by_sector(policies_by_instrument)
    print_contact_lookup(policies_by_instrument)
    print_missing_contacts()
    print_application_window_template()

    print("\n" + "=" * 100)
    print("✅ Analysis complete")
    print("=" * 100)

    return 0


if __name__ == "__main__":
    sys.exit(main())
