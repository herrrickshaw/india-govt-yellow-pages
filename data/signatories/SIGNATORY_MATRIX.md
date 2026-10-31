# Who signed what — officers ↔ orders / notifications matrix

_Built 2026-10-31 by `scripts/signatory_matrix.py`. Scope: ministries with a who's-who roster in `data/ministry_officials.csv` (12 ministries/departments)._

## Funnel

| Stage | Count |
|---|---|
| Candidate order/notification/circular/OM/gazette PDFs in the document index | 1809 |
| PDFs fetched | 1784 |
| PDFs with machine-readable text | 1719 |
| PDFs with a detectable signature block | 592 |
| Signatures matched to a roster officer | 247 documents / 46 officers |
| Signatures not matched (person not in any roster, or moved) | 358 |

## Per ministry

| Ministry | candidates | fetched | signature found | matched docs | officers linked |
|---|---|---|---|---|---|
| Civil Aviation (MoCA) | 5 | 4 | 2 | 0 | 0 |
| Coal | 4 | 4 | 3 | 1 | 1 |
| Department of Animal Husbandry and Dairying (DoAHD) | 649 | 648 | 251 | 93 | 17 |
| Department of Atomic Energy | 6 | 6 | 0 | 0 | 0 |
| Department of Chemicals and Petro-Chemicals (DoCP) | 4 | 4 | 1 | 0 | 0 |
| Department of Consumer Affairs (DoCA) | 150 | 145 | 93 | 60 | 6 |
| Department of Ex-Servicemen Welfare (DESW) | 8 | 3 | 2 | 0 | 0 |
| Department of Land Resources (DLR) | 160 | 160 | 51 | 2 | 1 |
| Department of Revenue (DoR) | 9 | 9 | 3 | 1 | 1 |
| Food Processing Industries (MoFPI) | 2 | 1 | 0 | 0 | 0 |
| New and Renewable Energy (MNRE) | 638 | 638 | 163 | 85 | 18 |
| Ports, Shipping and Waterways (MoPSW) | 174 | 162 | 23 | 5 | 2 |

## Officer × topic matrix (documents signed)

Full pivot: `officer_topic_pivot.csv`; long form with example titles and URLs: `officer_topic_matrix.csv`; one row per signed document: `officer_documents.csv`.

| Officer | Designation (roster) | Ministry | Acts / commencement / legislation | Advisory / public notice / caution | Budget / sanction / release of funds / grants | Committees / meetings / minutes / constitution of | Customs / tariff / duty / GST | HR: appointment / transfer / posting / promotion | HR: leave / pay / allowances / service rules | Legal metrology / consumer protection rules | Licensing / approvals / standards / enlistment | Office administration / housekeeping | Other / unclassified | Procurement / tenders / GeM | RTI / appellate authority / CPIO | Recruitment rules / RRs | Scheme guidelines / implementation | Statutory rules / gazette notifications (G.S.R. / S.O.) | Training / capacity building / workshops | Vigilance / disciplinary / court matters | TOTAL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sh. Anupam Mishra | Additional Secretary | Department of Consumer Affairs (DoCA) | 6 |  |  |  |  | 7 | 2 | 30 | 1 |  |  |  |  | 4 |  | 39 |  |  | 89 |
| Shri Pankaj Kumar Sinha | Under Secretary (Admin l/Cash Section) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  | 1 | 25 | 8 |  | 4 | 4 | 10 |  |  | 1 | 1 | 1 |  | 1 | 56 |
| Sanjay Gorelal Karndhar | Scientist E | New and Renewable Energy (MNRE) |  | 4 |  | 2 | 1 |  |  |  | 30 |  |  |  |  |  | 7 |  |  |  | 44 |
| Rishikesh Vaishnav | Scientist-C | New and Renewable Energy (MNRE) |  | 4 |  |  |  |  |  |  | 3 |  | 2 |  |  |  | 11 |  |  |  | 20 |
| Smt. Nidhi Khare | Secretary (CA) | Department of Consumer Affairs (DoCA) | 2 |  |  |  |  |  |  | 6 |  |  |  |  |  |  |  | 6 |  |  | 14 |
| Shri Vikas Kumar Vikrosy | Under Secretary (General & AQCS) | Department of Animal Husbandry and Dairying (DoAHD) |  |  | 1 |  |  | 7 | 2 |  | 1 | 1 | 2 |  |  |  |  |  |  |  | 14 |
| Shri Rama Shankar Sinha | Additional Secretary (LH) | Department of Animal Husbandry and Dairying (DoAHD) | 1 |  |  |  |  | 5 |  |  |  |  |  |  |  | 5 |  | 1 |  |  | 12 |
| Smt. Anamika Nigam | Under Secretary (NLM) | Department of Animal Husbandry and Dairying (DoAHD) |  |  | 1 |  |  | 3 | 2 |  |  |  | 1 |  |  | 1 |  | 2 | 1 |  | 11 |
| Dr. Muthukumarasamy B. | Joint Secretary (NLM/SD) | Department of Animal Husbandry and Dairying (DoAHD) | 1 |  |  | 2 |  |  |  |  |  |  | 2 |  |  |  |  | 5 |  |  | 10 |
| Vikram Dhaka | Scientist D | New and Renewable Energy (MNRE) |  | 1 |  |  |  |  |  |  |  |  | 4 |  |  |  | 1 |  |  |  | 6 |
| Shri Victor Bilung | Under Secretary (Parl./Legal) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  | 2 | 1 |  |  |  |  |  | 3 |  |  |  |  |  | 6 |
| Sh. Ashutosh Agarwal | Director (Legal Metrology) | Department of Consumer Affairs (DoCA) |  | 2 |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  | 2 |  |  | 6 |
| Jeevan Kumar Jethani | Scientist F | New and Renewable Energy (MNRE) |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  | 4 |  |  |  | 5 |
| Rajesh Kulhari | Joint Secretary | New and Renewable Energy (MNRE) |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 3 | 2 |  |  | 5 |
| Dr. Gagan Garg | Joint Commissioner (RGM) | Department of Animal Husbandry and Dairying (DoAHD) |  | 1 |  |  |  |  |  |  | 2 |  | 1 |  |  |  |  |  |  | 1 | 5 |
| Shobhit Srivastava | Scientist E | New and Renewable Energy (MNRE) |  |  |  | 1 |  |  |  |  |  |  | 1 |  |  |  | 2 |  |  |  | 4 |
| Mohd. Azmal Mansoori | Scientist C | New and Renewable Energy (MNRE) |  |  |  |  | 1 |  |  |  |  |  | 1 | 1 |  |  | 1 |  |  |  | 4 |
| Sujit Pillai | Scientist F | New and Renewable Energy (MNRE) |  |  |  |  |  |  |  |  | 1 |  | 3 |  |  |  |  |  |  |  | 4 |
| J. Rajesh Kumar | Economic Advisor | New and Renewable Energy (MNRE) |  |  |  | 2 |  |  |  |  |  |  |  |  |  |  |  | 2 |  |  | 4 |
| Shri Sanjay Kumar | Under Secretary (C&DD) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  | 2 |  |  |  |  |  |  |  | 2 |  |  |  |  | 4 |
| Dr. Sujit K. Dutta | Joint Commissioner (NLM) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  |  |  |  |  |  |  | 4 |  |  |  |  |  |  | 4 |
| Pillarisetty Venkata Tarun Saketh | Scientist C | New and Renewable Energy (MNRE) |  |  |  |  |  |  | 1 |  |  |  |  |  |  |  | 2 |  |  |  | 3 |
| Sachin Meena | Scientist-C | New and Renewable Energy (MNRE) |  |  |  |  | 1 |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  | 3 |
| Sh. Baldev Singh | Under Secretary (BIS) | Department of Consumer Affairs (DoCA) |  |  |  |  |  |  |  |  | 2 |  |  | 1 |  |  |  |  |  |  | 3 |
| Sh. Sandeep Gupta | JS (PHRD, Establishment, Coord. & Parl) | Ports, Shipping and Waterways (MoPSW) |  |  |  |  |  | 2 |  |  |  |  |  |  |  | 1 |  |  |  |  | 3 |
| Shri S. Kamal Garg | Under Secretary (GC/PC) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  |  |  |  |  |  |  |  | 3 |  |  |  |  |  | 3 |
| Shri C. Sen | Joint Commissioner/GM (DMS) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  | 1 |  |  |  |  |  | 2 |  |  |  |  |  |  | 3 |
| Sanjay Kumar Shahi | Scientist E | New and Renewable Energy (MNRE) |  |  |  |  |  |  |  |  |  |  | 2 |  |  |  |  |  |  |  | 2 |
| Anubhav Uppal | Scientist D | New and Renewable Energy (MNRE) |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  | 1 |  |  |  | 2 |
| Aravindh Madhavankutty Ambika | Scientist D | New and Renewable Energy (MNRE) |  | 1 |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  | 2 |
| Shri Girnish Kumar | Under Secretary | Department of Land Resources (DLR) |  |  |  |  |  |  |  |  |  |  | 2 |  |  |  |  |  |  |  | 2 |
| Dr. Naveena. B.Maheswarappa | Animal Husbandry Commissioner | Department of Animal Husbandry and Dairying (DoAHD) |  | 1 |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |  |  | 2 |
| Pankaj Saxena | Scientist G | New and Renewable Energy (MNRE) |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  | 2 |
| Shri Sanjib Bhattacharya | Deputy Secretary (Admin l/ Admin ll/Cash Section) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  | 2 |
| Shri Bhuwan Chandra Mishra | HOD & Sr. Director (IT) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  | 1 |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  | 2 |
| Tarun Singh | Scientist E | New and Renewable Energy (MNRE) |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  | 1 |
| Dr. Rajendra Gulabrao Bambal | Joint Commissioner (Cattle) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  | 1 |
| Ms. Puja Rustagi | Director(Trade/IC/Dairy) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  |  |  |  |  |  | 1 |  |  |  |  |  |  |  | 1 |
| Shri Rajiv Mani | Secretary | Department of Legal Affairs | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 1 |
| Shri Ajith Kumar K | Deputy Commissioner (DD) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  | 1 |

## Contact person by topic

For each ministry and topic, the roster officers who signed the most documents on it (name, roster designation, email).

### Coal

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation | **Shri Sanoj Kumar Jha** — Add. Secretary — sanoj.jha@nic.in (1) |
| Statutory rules / gazette notifications (G.S.R. / S.O.) | **Smt. Rupinder Brar** — Add. Secretary — rup.brar@nic.in (1) |

### Department of Animal Husbandry and Dairying (DoAHD)

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation | **Dr. Muthukumarasamy B.** — Joint Secretary (NLM/SD) — js-nlm@dahd.nic.in (1); **Shri Rama Shankar Sinha** — Additional Secretary (LH) — jslh-dadf@nic.in (1) |
| Advisory / public notice / caution | **Dr. Gagan Garg** — Joint Commissioner (RGM) — gagan.garg@nic.in (1); **Dr. Naveena. B.Maheswarappa** — Animal Husbandry Commissioner — ahc-dahd@nic.in (1) |
| Budget / sanction / release of funds / grants | **Shri Vikas Kumar Vikrosy** — Under Secretary (General & AQCS) — vk.vikrosy@gov.in (1); **Smt. Anamika Nigam** — Under Secretary (NLM) — anamika.edu@nic.in (1) |
| Committees / meetings / minutes / constitution of | **Dr. Muthukumarasamy B.** — Joint Secretary (NLM/SD) — js-nlm@dahd.nic.in (2); **Shri Bhuwan Chandra Mishra** — HOD & Sr. Director (IT) — bcmishra@nic.in (1) |
| Customs / tariff / duty / GST | **Shri Ajith Kumar K** — Deputy Commissioner (DD) — ajith.kk@gov.in (1); **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (1) |
| HR: appointment / transfer / posting / promotion | **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (25); **Shri Vikas Kumar Vikrosy** — Under Secretary (General & AQCS) — vk.vikrosy@gov.in (7); **Shri Rama Shankar Sinha** — Additional Secretary (LH) — jslh-dadf@nic.in (5); **Smt. Anamika Nigam** — Under Secretary (NLM) — anamika.edu@nic.in (3) |
| HR: leave / pay / allowances / service rules | **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (8); **Shri Vikas Kumar Vikrosy** — Under Secretary (General & AQCS) — vk.vikrosy@gov.in (2); **Smt. Anamika Nigam** — Under Secretary (NLM) — anamika.edu@nic.in (2); **Shri Sanjib Bhattacharya** — Deputy Secretary (Admin l/ Admin ll/Cash Section) — sanjeeb.b@nic.in (1) |
| Licensing / approvals / standards / enlistment | **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (4); **Dr. Gagan Garg** — Joint Commissioner (RGM) — gagan.garg@nic.in (2); **Shri Vikas Kumar Vikrosy** — Under Secretary (General & AQCS) — vk.vikrosy@gov.in (1) |
| Office administration / housekeeping | **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (4); **Dr. Naveena. B.Maheswarappa** — Animal Husbandry Commissioner — ahc-dahd@nic.in (1); **Shri Vikas Kumar Vikrosy** — Under Secretary (General & AQCS) — vk.vikrosy@gov.in (1) |
| Other / unclassified | **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (10); **Dr. Muthukumarasamy B.** — Joint Secretary (NLM/SD) — js-nlm@dahd.nic.in (2); **Shri Vikas Kumar Vikrosy** — Under Secretary (General & AQCS) — vk.vikrosy@gov.in (2); **Dr. Gagan Garg** — Joint Commissioner (RGM) — gagan.garg@nic.in (1) |
| Procurement / tenders / GeM | **Dr. Sujit K. Dutta** — Joint Commissioner (NLM) — sk.dutta@nic.in (4); **Shri C. Sen** — Joint Commissioner/GM (DMS) — chinmoyjit.sen@gov.in (2) |
| RTI / appellate authority / CPIO | **Shri S. Kamal Garg** — Under Secretary (GC/PC) — gargsk.edu@nic.in (3); **Shri Victor Bilung** — Under Secretary (Parl./Legal) — victor.bilung38@nic.in (3) |
| Recruitment rules / RRs | **Shri Rama Shankar Sinha** — Additional Secretary (LH) — jslh-dadf@nic.in (5); **Shri Sanjay Kumar** — Under Secretary (C&DD) — sanjay.kmr70@nic.in (2); **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (1); **Smt. Anamika Nigam** — Under Secretary (NLM) — anamika.edu@nic.in (1) |
| Scheme guidelines / implementation | **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (1) |
| Statutory rules / gazette notifications (G.S.R. / S.O.) | **Dr. Muthukumarasamy B.** — Joint Secretary (NLM/SD) — js-nlm@dahd.nic.in (5); **Smt. Anamika Nigam** — Under Secretary (NLM) — anamika.edu@nic.in (2); **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (1); **Shri Rama Shankar Sinha** — Additional Secretary (LH) — jslh-dadf@nic.in (1) |
| Training / capacity building / workshops | **Smt. Anamika Nigam** — Under Secretary (NLM) — anamika.edu@nic.in (1) |
| Vigilance / disciplinary / court matters | **Dr. Gagan Garg** — Joint Commissioner (RGM) — gagan.garg@nic.in (1); **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (1) |

### Department of Consumer Affairs (DoCA)

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation | **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (6); **Smt. Nidhi Khare** — Secretary (CA) — Secy-ca@nic.in (2) |
| Advisory / public notice / caution | **Sh. Ashutosh Agarwal** — Director (Legal Metrology) — ashutosh.agarwal13@nic.in, dirwm-ca@nic.in (2) |
| HR: appointment / transfer / posting / promotion | **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (7) |
| HR: leave / pay / allowances / service rules | **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (2) |
| Legal metrology / consumer protection rules | **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (30); **Smt. Nidhi Khare** — Secretary (CA) — Secy-ca@nic.in (6); **Sh. Ashutosh Agarwal** — Director (Legal Metrology) — ashutosh.agarwal13@nic.in, dirwm-ca@nic.in (1) |
| Licensing / approvals / standards / enlistment | **Sh. Baldev Singh** — Under Secretary (BIS) — usbis-ca@gov.in (2); **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (1) |
| Office administration / housekeeping | **Sh. Ashutosh Agarwal** — Director (Legal Metrology) — ashutosh.agarwal13@nic.in, dirwm-ca@nic.in (1) |
| Procurement / tenders / GeM | **Sh. Bal Krishna Thakur** — Under Secretary (Establishment and General Administration) — usestt-ca@nic.in (1); **Sh. Baldev Singh** — Under Secretary (BIS) — usbis-ca@gov.in (1) |
| Recruitment rules / RRs | **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (4) |
| Statutory rules / gazette notifications (G.S.R. / S.O.) | **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (39); **Smt. Nidhi Khare** — Secretary (CA) — Secy-ca@nic.in (6); **Sh. Ashutosh Agarwal** — Director (Legal Metrology) — ashutosh.agarwal13@nic.in, dirwm-ca@nic.in (2) |

### Department of Land Resources (DLR)

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified | **Shri Girnish Kumar** — Under Secretary — girnish.kumar@nic.in (2) |

### Department of Legal Affairs

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation | **Shri Rajiv Mani** — Secretary — secylaw-dla@nic.in (1) |

### Department of Revenue (DoR)

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified | **Nimit Dhalia** — Assistant Director — nimit.dhalia2057@gov.in (1) |

### Managing Director, Solar Energy Corporation of India, M/o New & Renewable Energy, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

### New and Renewable Energy (MNRE)

| Topic | Contact officers (docs signed) |
|---|---|
| Advisory / public notice / caution | **Rishikesh Vaishnav** — Scientist-C — rishikesh.mnre@gov.in (4); **Sanjay Gorelal Karndhar** — Scientist E — karndhar.sg@nic.in (4); **Aravindh Madhavankutty Ambika** — Scientist D — aravindh.mnre@gov.in (1); **Jeevan Kumar Jethani** — Scientist F — jethani.jk@nic.in (1) |
| Committees / meetings / minutes / constitution of | **J. Rajesh Kumar** — Economic Advisor — jrajesh.kumar@nic.in (2); **Sanjay Gorelal Karndhar** — Scientist E — karndhar.sg@nic.in (2); **Pankaj Saxena** — Scientist G — spankaj@nic.in (1); **Shobhit Srivastava** — Scientist E — shobhit.srivastava@nic.in (1) |
| Customs / tariff / duty / GST | **Mohd. Azmal Mansoori** — Scientist C — azmal.mnre@gov.in (1); **Sachin Meena** — Scientist-C — sachin.mnre@gov.in (1); **Sanjay Gorelal Karndhar** — Scientist E — karndhar.sg@nic.in (1) |
| HR: leave / pay / allowances / service rules | **Pillarisetty Venkata Tarun Saketh** — Scientist C — tarunsaketh.mnre@gov.in (1) |
| Licensing / approvals / standards / enlistment | **Sanjay Gorelal Karndhar** — Scientist E — karndhar.sg@nic.in (30); **Rishikesh Vaishnav** — Scientist-C — rishikesh.mnre@gov.in (3); **Sujit Pillai** — Scientist F — sujit.pillai@gov.in (1) |
| Other / unclassified | **Vikram Dhaka** — Scientist D — vikram.mnre@gov.in (4); **Sujit Pillai** — Scientist F — sujit.pillai@gov.in (3); **Rishikesh Vaishnav** — Scientist-C — rishikesh.mnre@gov.in (2); **Sanjay Kumar Shahi** — Scientist E — sk.shahi@nic.in (2) |
| Procurement / tenders / GeM | **Anubhav Uppal** — Scientist D — anubhav.mnre@gov.in (1); **Aravindh Madhavankutty Ambika** — Scientist D — aravindh.mnre@gov.in (1); **Mohd. Azmal Mansoori** — Scientist C — azmal.mnre@gov.in (1) |
| Scheme guidelines / implementation | **Rishikesh Vaishnav** — Scientist-C — rishikesh.mnre@gov.in (11); **Sanjay Gorelal Karndhar** — Scientist E — karndhar.sg@nic.in (7); **Jeevan Kumar Jethani** — Scientist F — jethani.jk@nic.in (4); **Rajesh Kulhari** — Joint Secretary — rkjs.mnre@gov.in (3) |
| Statutory rules / gazette notifications (G.S.R. / S.O.) | **J. Rajesh Kumar** — Economic Advisor — jrajesh.kumar@nic.in (2); **Rajesh Kulhari** — Joint Secretary — rkjs.mnre@gov.in (2); **Pankaj Saxena** — Scientist G — spankaj@nic.in (1) |

### Ports, Shipping and Waterways (MoPSW)

| Topic | Contact officers (docs signed) |
|---|---|
| HR: appointment / transfer / posting / promotion | **Sh. Sandeep Gupta** — JS (PHRD, Establishment, Coord. & Parl) — jsadmin-psw@gov.in jscord-psw@gov.in (2) |
| HR: leave / pay / allowances / service rules |  |
| Recruitment rules / RRs | **Sh. Sandeep Gupta** — JS (PHRD, Establishment, Coord. & Parl) — jsadmin-psw@gov.in jscord-psw@gov.in (1) |

## Signatories missing from the rosters (roster gaps)

People who sign orders for a ministry but are not on its who's-who page / igod / civil lists — candidates to add to the yellow pages.

| Ministry | Signatory (as printed) | Signed as | Documents | Latest |
|---|---|---|---|---|
| Department of Land Resources (DLR) | Th. Lianboi | Under SecretarY (Admn / Under Secretary (Admn. | 21 | 2026-03-16 |
| Department of Animal Husbandry and Dairying (DoAHD) | Rohit Tewari | Secretary to the Government of India / Under Secretary to the Government of India | 13 | 2025-07-15 |
| Department of Animal Husbandry and Dairying (DoAHD) | Dharm Prakash | Under Secretary (RTI / Under Secretary (RTT | 10 | 2025-07-15 |
| Department of Land Resources (DLR) | Rajeev Bahal | Under Secretary to the Government of India | 10 | 2022-03-17 |
| Department of Animal Husbandry and Dairying (DoAHD) | UPAMANYU BASU | Jt. Secy | 9 | 2025-06-30 |
| Department of Animal Husbandry and Dairying (DoAHD) | Deepak Sethi | Under Secretary / Under Secretary to the Government of India | 8 | 2025-06-27 |
| Department of Animal Husbandry and Dairying (DoAHD) | GIRJA NAND SINGH | Joint Secretary to the Government of India / Jt. Secy | 8 | 2026-03-27 |
| Department of Consumer Affairs (DoCA) | AMIT MEHTA | Jt. Secy | 8 |  |
| Department of Animal Husbandry and Dairying (DoAHD) | S. C. Srivastav | Deputy Secretary to the Government of India / Deputy Secretary to the Govt. of India | 7 | 2025-10-19 |
| New and Renewable Energy (MNRE) | GHANSHYAM PRASAD | Joint Secretary to the Govt. of India / Jt. Secy | 7 | 2022-12-01 |
| New and Renewable Energy (MNRE) | Rahul Rawat | Scientist 'C' / Scientist - C | 7 | 2024-08-23 |
| New and Renewable Energy (MNRE) | Rohit Thakwani | Scientist C / Scientist ‘C’ | 7 | 2023-02-15 |
| Department of Animal Husbandry and Dairying (DoAHD) | SAGAR MEHRA | Jt. Secy | 6 | 2021-12-17 |
| Department of Consumer Affairs (DoCA) | D. K. SONKER | Deputy Director (NTH / Director | 6 |  |
| New and Renewable Energy (MNRE) | PIYUSH SINGH | Joint Secretary to the Government of India / Jt. Secy | 5 | 2023-05-23 |
| Ports, Shipping and Waterways (MoPSW) | MUMBAI PORT TRUST | Officer (im full (5 SRE NPL Et ae / Officer (in fail a oe es ee | 5 |  |
| Department of Animal Husbandry and Dairying (DoAHD) | Bhushan Tyagi | Deputy Commissioner (RGM) - / Joint Commissioner | 4 | 2025-06-27 |
| Department of Animal Husbandry and Dairying (DoAHD) | KPJ Gerald | Deputy Secretary to Govt of India / Deputy Secretary to the Govt of India | 4 | 2020-06-04 |
| Department of Animal Husbandry and Dairying (DoAHD) | Madhusudanan V. K | Under Secretary (RTI / Under Secretary to the Government of India | 4 | 2025-06-27 |
| Department of Consumer Affairs (DoCA) | P. V. RAMA SASTRY | Jt. Secy / Secy | 4 |  |
| Department of Consumer Affairs (DoCA) | RAKESH KACKER | Addl. Secy / Spl. Secy | 4 |  |
| Department of Animal Husbandry and Dairying (DoAHD) | K. GURUMURTHY | Jt. Secy | 3 | 2026-07-10 |
| New and Renewable Energy (MNRE) | AJAY JAIN | PRINCIPAL SECRETARY TO GOVERNMENT | 3 | 2019-01-03 |
| New and Renewable Energy (MNRE) | Sanjay G. Kamdhar | Scientist-E | 3 | 2023-08-23 |
| Ports, Shipping and Waterways (MoPSW) | LUCAS L. KAMSUAN | Jt. Secy | 3 |  |
| Department of Animal Husbandry and Dairying (DoAHD) | C. L.Gautam | Under Secretary to the Government of India / Under Secretary to the Govt. of India | 2 | 2025-06-30 |
| Department of Animal Husbandry and Dairying (DoAHD) | DHARMENDRA DEO | Secy | 2 | 2026-06-05 |
| Department of Animal Husbandry and Dairying (DoAHD) | K. P. J. Gerald | Deputy Secretary to the Government of India | 2 | 2020-05-28 |
| Department of Animal Husbandry and Dairying (DoAHD) | LALIT GROVER | Under Secretary to the Govt. of India / Under Secy | 2 | 2026-04-16 |
| Department of Animal Husbandry and Dairying (DoAHD) | Narender Kumar | Under Secretary to the Government of India | 2 | 2021-01-13 |
| Department of Animal Husbandry and Dairying (DoAHD) | O. P. CHAUDHARY | Joint Secretary to the Government of India / Jt. Secy | 2 | 2026-06-05 |
| Department of Animal Husbandry and Dairying (DoAHD) | Pankaj Sinha | Under Secretary to the Government of India | 2 | 2025-06-30 |
| Department of Animal Husbandry and Dairying (DoAHD) | Personal Files | Secretary, AHD. | 2 | 2025-06-27 |
| Department of Animal Husbandry and Dairying (DoAHD) | R. P. Sinha | Under Secretary (RTI / Under Secretary to the Government of India | 2 | 2025-06-27 |
| Department of Animal Husbandry and Dairying (DoAHD) | RACHNA SHAH | Secy | 2 | 2026-10-23 |
| Department of Animal Husbandry and Dairying (DoAHD) | RAJBIR SINGH RANA | Jt. Secy / it. Secy | 2 | 2026-10-16 |
| Department of Animal Husbandry and Dairying (DoAHD) | RAJIV MANI | Secretary to the Govt. of India. | 2 | 2026-07-10 |
| Department of Animal Husbandry and Dairying (DoAHD) | RAVI S. PRASAD | Jt. Secy | 2 | 2026-06-05 |
| Department of Consumer Affairs (DoCA) | Consumer Disputes | Joint Registrar, | 2 |  |
| Department of Consumer Affairs (DoCA) | Disputes Redressal | Jt. Secy. | 2 |  |
| Department of Consumer Affairs (DoCA) | RAJIV AGARWAL | Secy | 2 |  |
| Department of Ex-Servicemen Welfare (DESW) | PRAVIN AGRAWAL | Jt. Secy | 2 | 2026-10 |
| Department of Land Resources (DLR) | Sushil Kumar Daila | Director (WM / Director(WM | 2 | 2023-01-24 |
| Department of Land Resources (DLR) | Th Lianbol | Under Secretary to the Government of:ndia / under sec「 eta:γ to the Government ofIndia | 2 | 2022-08-29 |
| New and Renewable Energy (MNRE) | ANKUR GUPTA | Principal Secretary to Government Haryana, / Principal Secretary to Govt. Haryana, | 2 | 2018-03-09 |
| New and Renewable Energy (MNRE) | DILIP NIGAM | Adviser (NSM / Director | 2 | 2017-06-19 |
| New and Renewable Energy (MNRE) | Divisional Heads | Officer, MNRE, New Delhi. | 2 | 2022-10-13 |
| New and Renewable Energy (MNRE) | Empowered Committee | Secretary of the GNCTD. / Secretary, J&K Chairman | 2 | 2025-10-08 |
| New and Renewable Energy (MNRE) | JK Jethani | Scientist ‘F’ | 2 | 2024-11-28 |
| New and Renewable Energy (MNRE) | Monitoring Framework | Secretary, MNRE and other | 2 | 2024-07-04 |
| New and Renewable Energy (MNRE) | Regulatory Commissions | Secretary, MNRE, CGO Complex, New Delhi | 2 | 2023-04-10 |
| New and Renewable Energy (MNRE) | Suman Kumar | Under Secretary to the Govt. of India | 2 | 2025-09-08 |
| New and Renewable Energy (MNRE) | Ye Jha | Deputy Secretary to Govt. of India | 2 | 2025-02-13 |
| Ports, Shipping and Waterways (MoPSW) | Dashrath Prasad | Director | 2 |  |

## Caveats

- A signature block is read heuristically from the last two pages of each PDF: a name line (often in parentheses) followed by a designation line. Scanned PDFs and Hindi-only signature blocks are not read (counted above).
- Matching is by name similarity with a bonus for the same ministry and a matching designation; `confidence` is `high` (near-exact name, same ministry), `medium`, or `low (name only, other ministry)`. Rosters are a snapshot (who's-who pages, igod, DoPT civil lists), so an officer who signed in 2022 may have moved since.
- 'Contact person for a topic' means *signed documents on that topic*, not a published point of contact. Topics are keyword buckets over subject line + title + site category; a document can fall in two buckets.
- Rows with `match_status=unmatched` in `notification_signatories.csv` are real signatories who are not in any roster — a useful list of people to add to the yellow pages.