"""Parsing logic of scripts/ministry_whoswho.py on synthetic HTML only
(fictional names, example.gov.in addresses). No network."""
import ministry_whoswho as mw


def test_deob_variants():
    assert mw.deob("asha.example[at]nic[dot]in") == "asha.example@nic.in"
    assert mw.deob("asha [at] example [dot] gov [dot] in") == "asha@example.gov.in"
    assert mw.deob("js-test[at]gov[in]") == "js-test@gov.in"
    assert mw.deob("") == ""
    assert mw.deob(None) == ""


def test_who_re_matches_url_spellings():
    for u in ["/about-us/whos-who", "/who-s-who", "/whoswho", "/who-is-who", "/Who%27s%20Who"]:
        assert mw.WHO_RE.search(u), u
    assert not mw.WHO_RE.search("/about-us/contact")


TABLE = """
<table><caption>Policy Division</caption>
<thead><tr><th>S.No.</th><th>Name of the Officer</th><th>Designation</th>
<th>Room No.</th><th>Telephone</th><th>E-mail</th></tr></thead>
<tbody>
<tr><td>1</td><td>Asha  Example</td><td>Joint Secretary</td><td>101-A</td>
    <td>011-0000000</td><td>asha.ex[at]example[dot]gov[dot]in</td></tr>
<tr><td>2</td><td>Vacant</td><td>Director</td><td></td><td>-</td><td></td></tr>
<tr><td>3</td><td>Ravi Testcase</td><td>Under Secretary</td><td>5</td><td>-</td>
    <td>see ravi.t@example.gov.in</td></tr>
</tbody></table>
<table><tr><th>Item</th><th>Value</th></tr><tr><td>a</td><td>b</td></tr></table>
"""


def test_parse_tables_maps_columns_and_skips_vacant():
    rows = mw.parse_tables(TABLE, "https://example.gov.in/whos-who")
    assert [r["name"] for r in rows] == ["Asha Example", "Ravi Testcase"]
    first = rows[0]
    assert first["designation"] == "Joint Secretary"
    assert first["room"] == "101-A"
    assert first["phones"] == "011-0000000"
    assert first["email"] == "asha.ex@example.gov.in"
    assert first["division"] == "Policy Division"
    assert first["source_url"] == "https://example.gov.in/whos-who"


def test_parse_tables_dash_phone_dropped_and_email_recovered_from_row():
    rows = mw.parse_tables(TABLE, "u")
    assert rows[1]["phones"] == ""
    assert rows[1]["email"] == "ravi.t@example.gov.in"


def test_parse_tables_requires_name_and_designation_columns():
    html = "<table><tr><th>Name</th><th>Phone</th></tr><tr><td>Asha Example</td><td>1</td></tr></table>"
    assert mw.parse_tables(html, "u") == []
    assert mw.parse_tables("", "u") == []
