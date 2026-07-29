#!/usr/bin/env python3
"""Generate dashboard/index.html — a self-contained, offline dashboard over the
yellow-pages CSVs. Vanilla HTML/JS with embedded JSON; no external assets.

Views: stat tiles, Officials (searchable), Organizations (searchable),
Open Policies -> contacts, PIB activity (6y per-year inline bars).
"""
import csv
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
OUT = Path(__file__).resolve().parent.parent / "dashboard" / "index.html"


def rows(name):
    p = DATA / name
    if not p.exists():
        return []
    with p.open() as f:
        return list(csv.DictReader(f))


def main():
    orgs = rows("organizations_index.csv")
    officials = rows("officials.csv")
    contacts = rows("org_contacts.csv")
    policies = rows("policy_contacts.csv")
    pib = rows("pib_ministry_contacts.csv")

    # PIB: collapse to one row per ministry (contacts repeat per row)
    pib_min, pib_contacts = {}, {}
    year_cols = [c for c in (pib[0].keys() if pib else []) if c.startswith("releases_2")]
    for r in pib:
        m = r["ministry"]
        pib_min.setdefault(m, r)
        if r.get("contact_name"):
            pib_contacts.setdefault(m, []).append(
                f'{r["contact_name"]} ({r["designation"]})')

    payload = {
        "stats": {
            "orgs": len({(o["name"], o["state"]) for o in orgs}),
            "withDetail": len({o["igod_org_id"] for o in orgs if o["igod_org_id"]}),
            "officials": len(officials),
            "emails": sum(1 for o in officials if o.get("email")),
            "states": len({o["state"] for o in orgs if o["state"]}),
            "openPolicies": len({p["instrument"] for p in policies}),
        },
        "officials": [[o["name"], o["designation"], o["org_name"], o["state"] or "Centre",
                       o["phones"], o["email"]] for o in officials],
        "orgs": [[o["name"], o["branch"], o["state"], o["category"], o["website"]]
                 for o in orgs],
        "orgContacts": [[c["org_name"], c["address"], c["phone"], c["email"], c["website"]]
                        for c in contacts],
        "policies": [[p["instrument"], p["offering_entity"], p["tier"], p["status"],
                      p["contact_name"], p["designation"], p["email"], p["source_url"]]
                     for p in policies],
        "pibYears": [c.replace("releases_", "") for c in year_cols],
        "pib": [[m, int(r.get("releases_6y_total") or 0)]
                + [int(r.get(c) or 0) for c in year_cols]
                + [int(r.get("releases_90d") or 0),
                   "; ".join(pib_contacts.get(m, [])[:3])]
                for m, r in sorted(pib_min.items(),
                                   key=lambda kv: -int(kv[1].get("releases_6y_total") or 0))],
    }

    html = HTML.replace("__DATA__", json.dumps(payload, ensure_ascii=False))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    print(f"wrote {OUT} ({OUT.stat().st_size/1e6:.1f} MB)")


HTML = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>India Government Yellow Pages</title>
<style>
:root{--bg:#fafafa;--surface:#fff;--ink:#1a1a2e;--ink2:#555;--muted:#888;
 --line:#e4e4e8;--accent:#2f6b9a;--accent-soft:#dbe9f4;--chip:#eef2f6}
@media(prefers-color-scheme:dark){:root{--bg:#111318;--surface:#1a1d24;--ink:#e8e8ec;
 --ink2:#b5b5bd;--muted:#7c7c86;--line:#2a2d36;--accent:#6aa5d4;--accent-soft:#24405a;--chip:#232733}}
*{box-sizing:border-box;margin:0}
body{font:14px/1.5 -apple-system,system-ui,sans-serif;background:var(--bg);color:var(--ink);padding:24px}
h1{font-size:20px;margin-bottom:4px}
.sub{color:var(--muted);margin-bottom:20px;font-size:13px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:20px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.tile b{display:block;font-size:24px;font-weight:650}
.tile span{color:var(--ink2);font-size:12px}
nav{display:flex;gap:6px;margin-bottom:14px;flex-wrap:wrap}
nav button{border:1px solid var(--line);background:var(--surface);color:var(--ink2);
 padding:7px 14px;border-radius:8px;cursor:pointer;font-size:13px}
nav button.on{background:var(--accent);border-color:var(--accent);color:#fff}
.bar-ctl{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap}
input,select{padding:8px 10px;border:1px solid var(--line);border-radius:8px;
 background:var(--surface);color:var(--ink);font-size:13px;min-width:220px}
.wrap{background:var(--surface);border:1px solid var(--line);border-radius:10px;overflow:auto;max-height:72vh}
table{border-collapse:collapse;width:100%;font-size:13px}
th{position:sticky;top:0;background:var(--surface);text-align:left;padding:9px 12px;
 border-bottom:2px solid var(--line);color:var(--ink2);font-weight:600;white-space:nowrap}
td{padding:8px 12px;border-bottom:1px solid var(--line);vertical-align:top}
tr:hover td{background:var(--chip)}
.n{color:var(--muted);font-size:12px;margin:8px 2px}
a{color:var(--accent);text-decoration:none}
.chip{background:var(--chip);border-radius:6px;padding:1px 7px;font-size:12px;white-space:nowrap}
.bcell{min-width:70px}.bwrap{display:flex;align-items:center;gap:6px}
.b{height:8px;border-radius:4px;background:var(--accent);min-width:2px}
.bv{font-size:11px;color:var(--ink2)}
</style></head><body>
<h1>India Government Yellow Pages</h1>
<div class="sub">Union ministries · state departments · who's-who contacts — scraped from igod.gov.in (NIC) · policies from digital-twin-for-ipa · press activity from PIB index</div>
<div class="tiles" id="tiles"></div>
<nav id="nav"></nav>
<div class="bar-ctl"><input id="q" placeholder="Search…"><select id="f1"></select></div>
<div class="n" id="count"></div><div class="wrap"><table id="tbl"></table></div>
<script>
const D=__DATA__;
const VIEWS={
 officials:{cols:["Name","Designation","Organization","State","Phones","Email"],rows:D.officials,
   filter:3,link:null,email:5},
 organizations:{cols:["Name","Branch","State","Category","Website"],rows:D.orgs,filter:1,link:4},
 "org contacts":{cols:["Organization","Address","Phone","Email","Website"],rows:D.orgContacts,
   filter:null,link:4,email:3},
 "open policies":{cols:["Instrument","Ministry/Entity","Tier","Status","Contact","Designation","Email","Source"],
   rows:D.policies,filter:2,link:7,email:6},
 "pib activity":{cols:["Ministry","6y total",...D.pibYears,"90d","Top contacts"],rows:D.pib,
   filter:null,bars:true}
};
let view="officials";
const $=id=>document.getElementById(id);
function tiles(){const s=D.stats;$("tiles").innerHTML=[
 [s.orgs,"organizations indexed"],[s.withDetail,"with igod detail pages"],
 [s.officials,"officials listed"],[s.emails,"official emails"],
 [s.states,"states / UTs"],[s.openPolicies,"open policy instruments"]]
 .map(([v,l])=>`<div class="tile"><b>${(+v).toLocaleString("en-IN")}</b><span>${l}</span></div>`).join("")}
function nav(){$("nav").innerHTML=Object.keys(VIEWS).map(k=>
 `<button class="${k===view?"on":""}" onclick="setView('${k}')">${k}</button>`).join("")}
function setView(k){view=k;$("q").value="";buildFilter();nav();render()}
function buildFilter(){const v=VIEWS[view],f=$("f1");
 if(v.filter==null){f.style.display="none";return}
 f.style.display="";const vals=[...new Set(v.rows.map(r=>r[v.filter]).filter(Boolean))].sort();
 f.innerHTML=`<option value="">All (${v.cols[v.filter]})</option>`+vals.map(x=>`<option>${x}</option>`).join("")}
function render(){const v=VIEWS[view],q=$("q").value.toLowerCase(),fv=$("f1").value;
 let rs=v.rows.filter(r=>(!fv||r[v.filter]===fv)&&(!q||r.some(c=>String(c).toLowerCase().includes(q))));
 const total=rs.length;rs=rs.slice(0,800);
 const max=v.bars?Math.max(1,...v.rows.map(r=>Math.max(...r.slice(2,2+D.pibYears.length)))):0;
 $("count").textContent=`${total.toLocaleString("en-IN")} rows${total>800?" (showing first 800)":""}`;
 $("tbl").innerHTML="<tr>"+v.cols.map(c=>`<th>${c}</th>`).join("")+"</tr>"+
  rs.map(r=>"<tr>"+r.map((c,i)=>{
   if(v.bars&&i>=2&&i<2+D.pibYears.length)
    return `<td class="bcell"><div class="bwrap"><div class="b" style="width:${Math.round(60*c/max)}px"></div><span class="bv">${c}</span></div></td>`;
   if(v.link===i&&c)return `<td><a href="${c.startsWith("http")?c:"https://"+c}" target="_blank" rel="noopener">${c.replace(/^https?:\/\//,"").slice(0,40)}</a></td>`;
   if(v.email===i&&c)return `<td><a href="mailto:${c}">${c}</a></td>`;
   if(i===1&&view==="organizations")return `<td><span class="chip">${{ug:"Union",sg:"State",apx:"Apex",jud:"Judiciary",leg:"Legislature",int:"Intl"}[c]||c}</span></td>`;
   return `<td>${c||""}</td>`}).join("")+"</tr>").join("");}
$("q").addEventListener("input",render);$("f1").addEventListener("change",render);
tiles();nav();buildFilter();render();
</script></body></html>
"""

if __name__ == "__main__":
    main()
