"""Org-name normalisation, seniority and open-status logic in
scripts/link_policy_contacts.py (synthetic inputs only)."""
import link_policy_contacts as lpc


def test_norm_drops_filler_and_applies_aliases():
    assert lpc.norm("Ministry of Power, Govt. of India") == "ministry of power"
    assert lpc.norm("MeitY") == "ministry of electronics and information technology"
    assert lpc.norm("Law & Justice") == "ministry of law and justice"
    assert lpc.norm(None) == ""


def test_rank_of_orders_specific_titles_correctly():
    order = ["Cabinet Minister", "Minister of State", "Minister", "Secretary",
             "Additional Secretary", "Joint Secretary", "Director General", "Director",
             "Deputy Secretary", "Under Secretary"]
    ranks = [lpc.rank_of(d) for d in order]
    assert ranks == sorted(ranks) and len(set(ranks)) == len(ranks), ranks
    assert lpc.rank_of("Consultant") == len(lpc.RANK)


def test_is_open():
    assert lpc.is_open({"status": "Active, applications open"})
    assert not lpc.is_open({"status": "Lapsed"})
    assert lpc.is_open({"status": "closed for new entrants but operative"})
    assert lpc.is_open({"status": "", "verified_on_site": True})
    assert not lpc.is_open({})


def test_match_org_exact_containment_fuzzy_none():
    by_org = {"ministry of power": [], "ministry of new and renewable energy": [], "ministry of steel": []}
    assert lpc.match_org("Ministry of Power", by_org) == "ministry of power"
    assert lpc.match_org("Steel", by_org) == "ministry of steel"
    assert lpc.match_org("Ministry of Steal", by_org) == "ministry of steel"
    assert lpc.match_org("Department of Space", by_org) is None
