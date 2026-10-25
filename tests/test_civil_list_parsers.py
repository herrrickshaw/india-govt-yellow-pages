"""DoPT IAS row parser and IPS PDF layout helpers, on synthetic fixtures
(fictional officer, made-up identifiers). No network, no real PDF."""
import dopt_civil_list as dopt
import ips_civil_list as ips

ROW = ('<div><img src="data:image/png;base64,AAAA"><h3>उदाहरण</h3>'
       '<a href="/Home/ER?id=1&amp;x=2"><b>Name:</b> Asha Example</a>'
       '<p>DOB: 01/01/1970</p><b>Identity No.:</b> XX0000'
       '<b>Allotment Year:</b> 1999 <b>Source of Recruitment:</b> RR'
       '<b>Qualification(Subject):</b> M.A. <i>(Testing)</i></p>'
       '<b>Pay Scale:</b> Level 15 <b>Remarks:</b> none <b>&</b> Example State'
       '<b>Posting:-</b><ul><li>Secretary, Example Dept Posting W.E.F.: 02/03/2024</li></ul></div>')


def test_dopt_parse_row():
    r = dopt.parse_row(ROW, "XX", 7)
    assert r["name_en"] == "Asha Example"
    assert r["name_hi"] == "उदाहरण"
    assert r["identity_no"] == "XX0000"
    assert r["allotment_year"] == "1999"
    assert r["source_of_recruitment"] == "RR"
    assert r["qualification"] == "M.A. (Testing)"
    assert r["pay_scale"] == "Level 15"
    assert r["domicile_state"] == "Example State"
    assert r["current_posting"] == "Secretary, Example Dept"
    assert r["posting_wef"] == "02/03/2024"
    assert r["er_sheet_url"] == "/Home/ER?id=1&x=2"
    assert r["dob"] == "01/01/1970"
    assert (r["cadre_code"], r["sr_no"]) == ("XX", 7)


def test_dopt_parse_row_empty():
    r = dopt.parse_row("", "XX", 1)
    assert r["name_en"] == "" and r["dob"] == ""


def W(text, x0, top):
    return {"text": text, "x0": x0, "top": top}


def test_cluster_rows_by_top_tolerance():
    bands = ips.cluster_rows([W("a", 0, 10), W("b", 5, 12.5), W("c", 0, 20)])
    assert [[w["text"] for w in ws] for _, ws in bands] == [["a", "b"], ["c"]]


def test_column_bounds_and_assignment():
    words = [W(f"({i})", 100 * i, 50) for i in range(1, 7)]
    bounds = ips.page_column_bounds(words)
    assert bounds == [100, 200, 300, 400, 500, 600]
    assert ips.assign_column(99, bounds) == 0
    assert ips.assign_column(250, bounds) == 1
    assert ips.assign_column(700, bounds) == 5
    assert ips.page_column_bounds(words[:5]) is None


def test_flush_record_splits_cells():
    rec = {
        1: [[W("उदाहरण", 0, 0)], [W("Asha", 0, 1), W("Example", 30, 1)], [W("B.Sc.", 0, 2)]],
        2: [[W("RR", 0, 0)], [W("1234567", 0, 1)], [W("Example", 0, 2), W("State", 40, 2)]],
        3: [[W("01/01/1970", 0, 0)], [W("01/09/1995", 0, 1)]],
        4: [[W("DGP", 0, 0), W("Level", 30, 0), W("17", 60, 0), W("05/06/2023", 90, 0)]],
        5: [[W("Medal", 0, 0)]],
    }
    r = ips.flush_record(rec, "Example State", "1995", 3)
    assert r["name_en"] == "Asha Example" and r["name_hi"] == "उदाहरण"
    assert r["qualification"] == "B.Sc."
    assert (r["source_of_recruitment"], r["officer_code"], r["domicile_state"]) == ("RR", "1234567", "Example State")
    assert (r["dob"], r["appointment_date"]) == ("01/01/1970", "01/09/1995")
    assert r["pay_scale"] == "Level 17"
    assert r["posting_wef"] == "05/06/2023"
    assert r["current_posting"] == "DGP"
    assert r["awards"] == "Medal"
