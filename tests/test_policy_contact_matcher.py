"""Window status, filtering and seniority ranking in
scripts/policy_contact_matcher.py, on synthetic contacts."""
from datetime import datetime

import policy_contact_matcher as pcm

D = datetime


def test_window_status_three_states_and_boundaries():
    s, e = D(2026, 1, 10), D(2026, 1, 20)
    assert pcm.get_window_status(s, e, D(2026, 1, 1)) == ("OPENING_SOON", 9)
    assert pcm.get_window_status(s, e, D(2026, 1, 10)) == ("ACTIVE", 10)
    assert pcm.get_window_status(s, e, D(2026, 1, 20)) == ("ACTIVE", 0)
    assert pcm.get_window_status(s, e, D(2026, 1, 25)) == ("CLOSED", 5)


def _windows():
    now = datetime.now()
    from datetime import timedelta as td
    return {
        "Open Scheme": (now - td(days=5), now + td(days=5)),
        "Soon Scheme": (now + td(days=10), now + td(days=40)),
        "Far Scheme": (now + td(days=90), now + td(days=120)),
        "Shut Scheme": (now - td(days=40), now - td(days=10)),
    }


CONTACTS = [{"instrument": n} for n in
            ["Open Scheme", "Soon Scheme", "Far Scheme", "Shut Scheme", "Unknown Scheme", ""]]


def test_filter_active_only():
    out = pcm.filter_by_active_windows(CONTACTS, _windows(), active_only=True)
    assert [c["instrument"] for c in out] == ["Open Scheme"]
    assert out[0]["window_status"] == "ACTIVE"


def test_filter_including_upcoming_and_no_data():
    out = pcm.filter_by_active_windows(CONTACTS, _windows(), active_only=False, days_ahead=30)
    got = {c["instrument"]: c["window_status"] for c in out}
    assert got == {"Open Scheme": "ACTIVE", "Soon Scheme": "OPENING_SOON", "Unknown Scheme": "NO_DATA"}


def test_group_and_open_policies():
    cs = [{"instrument": "A", "status": "Open"}, {"instrument": "B", "status": "closed"},
          {"instrument": "A", "status": "OPEN till March"}, {"instrument": " ", "status": "open"}]
    assert sorted(pcm.group_by_policy(cs)) == ["A", "B"]
    assert pcm.get_open_policies(cs) == ["A"]


def test_seniority_specific_titles_are_not_swallowed_by_generic_ones():
    # Documented order: Minister > Secretary > Minister of State >
    # Additional Secretary > Joint Secretary > Director > others.
    cs = [{"designation": d} for d in
          ["Director", "Joint Secretary", "Additional Secretary", "Minister of State",
           "Secretary", "Union Minister", "Consultant"]]
    got = [c["designation"] for c in pcm.rank_contacts_by_seniority(cs)]
    assert got == ["Union Minister", "Secretary", "Minister of State", "Additional Secretary",
                   "Joint Secretary", "Director", "Consultant"]


def test_window_status_is_inclusive_of_the_end_date_during_the_day():
    # application_end_date is a calendar day: an application window that ends on
    # 20 Jan must still be ACTIVE at 15:00 on 20 Jan (and 9 days away on 1 Jan at noon)
    s, e = D(2026, 1, 10), D(2026, 1, 20)
    assert pcm.get_window_status(s, e, D(2026, 1, 20, 15, 0)) == ("ACTIVE", 0)
    assert pcm.get_window_status(s, e, D(2026, 1, 10, 9, 30)) == ("ACTIVE", 10)
    assert pcm.get_window_status(s, e, D(2026, 1, 1, 12, 0)) == ("OPENING_SOON", 9)
    assert pcm.get_window_status(s, e, D(2026, 1, 21, 0, 30)) == ("CLOSED", 1)
