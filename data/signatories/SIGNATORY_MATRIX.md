# Who signed what — officers ↔ orders / notifications matrix

_Built 2026-10-31 by `scripts/signatory_matrix.py`. Scope: ministries with a who's-who roster in `data/ministry_officials.csv` (70 ministries/departments)._

## Funnel

| Stage | Count |
|---|---|
| Candidate order/notification/circular/OM/gazette PDFs in the document index | 9488 |
| PDFs fetched | 9288 |
| PDFs with machine-readable text | 9065 |
| PDFs with a detectable signature block | 3022 |
| Signatures matched to a roster officer | 410 documents / 86 officers |
| Signatures not matched (person not in any roster, or moved) | 2639 |

## Per ministry

| Ministry | candidates | fetched | signature found | matched docs | officers linked |
|---|---|---|---|---|---|
| AYUSH (MoA) | 4 | 3 | 0 | 0 | 0 |
| Civil Aviation (MoCA) | 5 | 4 | 2 | 0 | 0 |
| Coal | 4 | 4 | 3 | 1 | 1 |
| Cooperation | 30 | 1 | 0 | 0 | 0 |
| Culture | 11 | 11 | 0 | 0 | 0 |
| Department for Promotion of Industry and Internal Trade (DPIIT) | 250 | 245 | 83 | 11 | 4 |
| Department of Administrative Reforms and Public Grievances (DARPG) | 182 | 172 | 45 | 0 | 0 |
| Department of Agriculture and Farmers Welfare (DoAFW) | 2 | 0 | 0 | 0 | 0 |
| Department of Animal Husbandry and Dairying (DoAHD) | 649 | 648 | 251 | 94 | 18 |
| Department of Atomic Energy | 6 | 6 | 0 | 0 | 0 |
| Department of Chemicals and Petro-Chemicals (DoCP) | 4 | 4 | 1 | 0 | 0 |
| Department of Consumer Affairs (DoCA) | 150 | 145 | 93 | 60 | 6 |
| Department of Drinking Water and Sanitation (DDWS) | 2 | 2 | 0 | 0 | 0 |
| Department of Economic Affairs (DEA) | 12 | 11 | 1 | 0 | 0 |
| Department of Empowerment of Persons with Disabilities (DEPWD) | 4 | 4 | 1 | 0 | 0 |
| Department of Ex-Servicemen Welfare (DESW) | 8 | 3 | 2 | 0 | 0 |
| Department of Expenditure (DoE) | 2 | 1 | 0 | 0 | 0 |
| Department of Fertilizers (DoFz) | 4 | 4 | 0 | 0 | 0 |
| Department of Financial Services (DoFS) | 247 | 244 | 128 | 10 | 4 |
| Department of Fisheries (DoF) | 250 | 249 | 81 | 9 | 1 |
| Department of Health Research (DHR) | 136 | 136 | 33 | 0 | 0 |
| Department of Health and Family Welfare (DoHFW) | 250 | 247 | 63 | 2 | 1 |
| Department of Higher Education (DoHE) | 250 | 250 | 30 | 0 | 0 |
| Department of Justice (DoJ) | 250 | 250 | 208 | 0 | 0 |
| Department of Land Resources (DLR) | 160 | 160 | 51 | 2 | 1 |
| Department of Legal Affairs (DoLA) | 250 | 246 | 184 | 15 | 3 |
| Department of Pension & Pensioner's Welfare (DoPPW) | 14 | 14 | 8 | 0 | 0 |
| Department of Personnel and Training (DoPT) | 250 | 245 | 71 | 1 | 1 |
| Department of Pharmaceuticals (DoPs) | 91 | 90 | 28 | 0 | 0 |
| Department of Public Enterprises (DPE) | 250 | 249 | 62 | 0 | 0 |
| Department of Revenue (DoR) | 9 | 9 | 3 | 1 | 1 |
| Department of Rural Development (DoRD) | 28 | 28 | 2 | 0 | 0 |
| Department of School Education and Literacy (DSEL) | 250 | 246 | 54 | 2 | 2 |
| Department of Science and Technology (DST) | 250 | 248 | 46 | 0 | 0 |
| Department of Scientific and Industrial Research (DSIR) | 161 | 159 | 26 | 0 | 0 |
| Department of Social Justice and Empowerment (DoSJE) | 250 | 223 | 45 | 1 | 1 |
| Department of Space | 250 | 250 | 0 | 0 | 0 |
| Department of Sports (DoS) | 9 | 8 | 1 | 0 | 0 |
| Department of Telecommunications (DoT) | 250 | 250 | 66 | 0 | 0 |
| Development of North Eastern Region (MDONER) | 101 | 96 | 36 | 0 | 0 |
| Earth Sciences (MoES) | 250 | 250 | 46 | 2 | 1 |
| Electronics and Information Technology (MeitY) | 145 | 145 | 70 | 15 | 1 |
| Environment, Forest and Climate Change (MoEFCC) | 250 | 238 | 94 | 16 | 2 |
| External Affairs (MEA) | 228 | 227 | 32 | 1 | 1 |
| Food Processing Industries (MoFPI) | 2 | 1 | 0 | 0 | 0 |
| Heavy Industries (MoHI) | 41 | 40 | 11 | 5 | 1 |
| Home Affairs (MHA) | 5 | 5 | 0 | 0 | 0 |
| Housing and Urban Affairs (MoHUA) | 250 | 249 | 85 | 16 | 6 |
| Information and Broadcasting (MIB) | 39 | 39 | 21 | 0 | 0 |
| Labour and Employment (MoLE) | 250 | 250 | 120 | 12 | 3 |
| Legislative Department (LD) | 250 | 246 | 49 | 5 | 1 |
| Micro, Small & Medium Enterprises (MSME) | 64 | 64 | 15 | 0 | 0 |
| Mines (MoM) | 242 | 242 | 153 | 12 | 2 |
| Minority Affairs (MoMA) | 21 | 20 | 5 | 1 | 1 |
| New and Renewable Energy (MNRE) | 638 | 638 | 161 | 85 | 18 |
| Parliamentary Affairs (MPA) | 147 | 147 | 64 | 8 | 1 |
| Petroleum and Natural Gas (MoPNG) | 1 | 1 | 0 | 0 | 0 |
| Planning (MoP) | 90 | 88 | 16 | 0 | 0 |
| Ports, Shipping and Waterways (MoPSW) | 174 | 162 | 23 | 6 | 3 |
| Power | 250 | 249 | 90 | 10 | 2 |
| Railways (MoR) | 1 | 1 | 0 | 0 | 0 |
| Road Transport and Highways (MoRTH) | 125 | 123 | 54 | 0 | 0 |
| Rural Development (MoRD) | 32 | 29 | 6 | 0 | 0 |
| Skill Development and Entrepreneurship (MSDE) | 20 | 20 | 4 | 0 | 0 |
| Statistics and Programme Implementation (MoSPI) | 77 | 43 | 16 | 0 | 0 |
| Steel (MoS) | 123 | 123 | 70 | 0 | 0 |
| Textiles (MoT) | 209 | 208 | 56 | 3 | 1 |
| Tourism | 250 | 250 | 50 | 2 | 1 |
| Tribal Affairs (MoTA) | 26 | 24 | 3 | 2 | 1 |
| Women and Child Development (MoWCD) | 3 | 1 | 0 | 0 | 0 |

## Officer × topic matrix (documents signed)

Full pivot: `officer_topic_pivot.csv`; long form with example titles and URLs: `officer_topic_matrix.csv`; one row per signed document: `officer_documents.csv`.

| Officer | Designation (roster) | Ministry | Acts / commencement / legislation | Advisory / public notice / caution | Budget / sanction / release of funds / grants | Committees / meetings / minutes / constitution of | Customs / tariff / duty / GST | HR: appointment / transfer / posting / promotion | HR: leave / pay / allowances / service rules | Legal metrology / consumer protection rules | Licensing / approvals / standards / enlistment | Office administration / housekeeping | Other / unclassified | Procurement / tenders / GeM | RTI / appellate authority / CPIO | Recruitment rules / RRs | Scheme guidelines / implementation | Statutory rules / gazette notifications (G.S.R. / S.O.) | Training / capacity building / workshops | Vigilance / disciplinary / court matters | TOTAL |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sh. Anupam Mishra | Additional Secretary | Department of Consumer Affairs (DoCA) | 6 |  |  |  |  | 7 | 2 | 30 | 1 |  |  |  |  | 4 |  | 39 |  |  | 89 |
| Shri Pankaj Kumar Sinha | Under Secretary (Admin l/Cash Section) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  | 1 | 25 | 8 |  | 4 | 4 | 10 |  |  | 1 | 1 | 1 |  | 1 | 56 |
| Sanjay Gorelal Karndhar | Scientist E | New and Renewable Energy (MNRE) |  | 4 |  | 2 | 1 |  |  |  | 30 |  |  |  |  |  | 7 |  |  |  | 44 |
| Rishikesh Vaishnav | Scientist-C | New and Renewable Energy (MNRE) |  | 4 |  |  |  |  |  |  | 3 |  | 2 |  |  |  | 11 |  |  |  | 20 |
| Shri Rajiv Mani | Secretary | Department of Legal Affairs | 9 |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 7 |  |  | 16 |
| Mr. Naresh Pal Gangwar | Secretary(AHD) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 14 |  |  | 14 |
| Shri Vikas Kumar Vikrosy | Under Secretary (General & AQCS) | Department of Animal Husbandry and Dairying (DoAHD) |  |  | 1 |  |  | 7 | 2 |  | 1 | 1 | 2 |  |  |  |  |  |  |  | 14 |
| Smt. Nidhi Khare | Secretary (CA) | Department of Consumer Affairs (DoCA) | 2 |  |  |  |  |  |  | 6 |  |  |  |  |  |  |  | 6 |  |  | 14 |
| Shri Rama Shankar Sinha | Additional Secretary (LH) | Department of Animal Husbandry and Dairying (DoAHD) | 1 |  |  |  |  | 5 |  |  |  |  |  |  |  | 5 |  | 1 |  |  | 12 |
| Shri Vijay Kumar Sharma | Under Secretary | Department of Expenditure (DoE) |  |  |  |  |  | 6 |  |  |  |  |  |  |  |  |  |  |  | 6 | 12 |
| Smt. Anamika Nigam | Under Secretary (NLM) | Department of Animal Husbandry and Dairying (DoAHD) |  |  | 1 |  |  | 3 | 2 |  |  |  | 1 |  |  | 1 |  | 2 | 1 |  | 11 |
| Dr. Muthukumarasamy B. | Joint Secretary (NLM/SD) | Department of Animal Husbandry and Dairying (DoAHD) | 1 |  |  | 2 |  |  |  |  |  |  | 2 |  |  |  |  | 5 |  |  | 10 |
| Shri Mukesh Kumar | Section officer (BIS) | Department of Consumer Affairs (DoCA) |  |  |  |  |  | 6 |  |  |  |  |  | 2 |  |  |  |  |  |  | 8 |
| Shri Victor Bilung | Under Secretary (Parl./Legal) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  | 2 | 1 |  |  |  |  |  | 3 |  |  |  |  |  | 6 |
| Vikram Dhaka | Scientist D | New and Renewable Energy (MNRE) |  | 1 |  |  |  |  |  |  |  |  | 4 |  |  |  | 1 |  |  |  | 6 |
| Sh. Ashutosh Agarwal | Director (Legal Metrology) | Department of Consumer Affairs (DoCA) |  | 2 |  |  |  |  |  | 1 |  | 1 |  |  |  |  |  | 2 |  |  | 6 |
| Jeevan Kumar Jethani | Scientist F | New and Renewable Energy (MNRE) |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  | 4 |  |  |  | 5 |
| Sh. Uttam Kumar Mishra | US (SU) | Ports, Shipping and Waterways (MoPSW) |  |  |  |  |  | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  | 5 |
| Dr. Gagan Garg | Joint Commissioner (RGM) | Department of Animal Husbandry and Dairying (DoAHD) |  | 1 |  |  |  |  |  |  | 2 |  | 1 |  |  |  |  |  |  | 1 | 5 |
| Shri Rajiv Mani | Secretary | Legislative Department | 2 |  |  | 1 |  |  |  |  |  |  | 2 |  |  |  |  |  |  |  | 5 |
| Hanuman Prasad Nishad | SO (Ad.VII) | Department of Revenue (DoR) | 1 |  |  |  |  | 2 |  |  |  |  |  |  | 1 |  |  | 1 |  |  | 5 |
| Rajesh Kulhari | Joint Secretary | New and Renewable Energy (MNRE) |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 3 | 2 |  |  | 5 |
| Mohd. Azmal Mansoori | Scientist C | New and Renewable Energy (MNRE) |  |  |  |  | 1 |  |  |  |  |  | 1 | 1 |  |  | 1 |  |  |  | 4 |
| Shri Manoj Kumar Singh | Co-ordination | Department of Chemicals and Petro-Chemicals (DoCP) |  |  |  |  |  |  |  |  |  |  |  |  | 2 |  |  | 1 |  | 1 | 4 |
| Sh. Amit Kumar | Under Secretary (P&C/O&M/ RTI/ E-GOV) | Department of Consumer Affairs (DoCA) |  |  |  |  |  |  | 2 |  | 2 |  |  |  |  |  |  |  |  |  | 4 |
| Shobhit Srivastava | Scientist E | New and Renewable Energy (MNRE) |  |  |  | 1 |  |  |  |  |  |  | 1 |  |  |  | 2 |  |  |  | 4 |
| Shri Sanjay Kumar | Under Secretary (C&DD) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  | 2 |  |  |  |  |  |  |  | 2 |  |  |  |  | 4 |
| Sujit Pillai | Scientist F | New and Renewable Energy (MNRE) |  |  |  |  |  |  |  |  | 1 |  | 3 |  |  |  |  |  |  |  | 4 |
| Dr. Sujit K. Dutta | Joint Commissioner (NLM) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  |  |  |  |  |  |  | 4 |  |  |  |  |  |  | 4 |
| J. Rajesh Kumar | Economic Advisor | New and Renewable Energy (MNRE) |  |  |  | 2 |  |  |  |  |  |  |  |  |  |  |  | 2 |  |  | 4 |
| Sh. Baldev Singh | Under Secretary (BIS) | Department of Consumer Affairs (DoCA) |  |  |  |  |  |  |  |  | 2 |  |  | 1 |  |  |  |  |  |  | 3 |
| Shri S. Kamal Garg | Under Secretary (GC/PC) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  |  |  |  |  |  |  |  | 3 |  |  |  |  |  | 3 |
| Sachin Meena | Scientist-C | New and Renewable Energy (MNRE) |  |  |  |  | 1 |  |  |  |  |  | 1 |  |  |  | 1 |  |  |  | 3 |
| Shri C. Sen | Joint Commissioner/GM (DMS) | Department of Animal Husbandry and Dairying (DoAHD) |  |  |  |  |  | 1 |  |  |  |  |  | 2 |  |  |  |  |  |  | 3 |
| Shri Kumar Shyamal Parthsarathi | Under Secretary | Panchayati Raj (MoPR) |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 3 |  | 3 |
| Pillarisetty Venkata Tarun Saketh | Scientist C | New and Renewable Energy (MNRE) |  |  |  |  |  |  | 1 |  |  |  |  |  |  |  | 2 |  |  |  | 3 |
| Sh. Sandeep Gupta | JS (PHRD, Establishment, Coord. & Parl) | Ports, Shipping and Waterways (MoPSW) |  |  |  |  |  | 2 |  |  |  |  |  |  |  | 1 |  |  |  |  | 3 |
| Sanjay Kumar Shahi | Scientist E | New and Renewable Energy (MNRE) |  |  |  |  |  |  |  |  |  |  | 2 |  |  |  |  |  |  |  | 2 |
| Sh. Sachin Kumar | SO | Ports, Shipping and Waterways (MoPSW) |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  |  | 1 |  | 2 |
| Pankaj Saxena | Scientist G | New and Renewable Energy (MNRE) |  |  |  | 1 |  |  |  |  |  |  |  |  |  |  |  | 1 |  |  | 2 |

## Contact person by topic

For each ministry and topic, the roster officers who signed the most documents on it (name, roster designation, email).

### Additional Secretary to Govt. of India, Department of School Education and Literacy, Ministry of Education, New Delhi

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Additional Secretary to Govt. of India, Ministry of Housing & Urban Affairs, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| HR: appointment / transfer / posting / promotion |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Additional Secretary, Department of Labour and Employment, M/o Labour & Employment, Govt. of India, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| Office administration / housekeeping |  |
| Other / unclassified |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Additional Secretary, Deptt. Of Drinking Water & Sanitation, M/o Jal Shakti, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Advisory / public notice / caution |  |

### Additional Secretary, Government of India, M/o Mines, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Additional Secretary, M.O.H & Urban Affairs, GOI

| Topic | Contact officers (docs signed) |
|---|---|
| HR: appointment / transfer / posting / promotion |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Additional Secretary, M/o Health and Family Welfare, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

### Additional Secretary, M/o Power, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| HR: leave / pay / allowances / service rules |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Additional Secretary, M/o Women and Child Development, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| HR: appointment / transfer / posting / promotion |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Additional Secretary, Ministry of Heavy Industries

| Topic | Contact officers (docs signed) |
|---|---|
| Scheme guidelines / implementation |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

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
| Statutory rules / gazette notifications (G.S.R. / S.O.) | **Mr. Naresh Pal Gangwar** — Secretary(AHD) — secyahd@nic.in (14); **Dr. Muthukumarasamy B.** — Joint Secretary (NLM/SD) — js-nlm@dahd.nic.in (5); **Smt. Anamika Nigam** — Under Secretary (NLM) — anamika.edu@nic.in (2); **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (1) |
| Training / capacity building / workshops | **Smt. Anamika Nigam** — Under Secretary (NLM) — anamika.edu@nic.in (1) |
| Vigilance / disciplinary / court matters | **Dr. Gagan Garg** — Joint Commissioner (RGM) — gagan.garg@nic.in (1); **Shri Pankaj Kumar Sinha** — Under Secretary (Admin l/Cash Section) — pk.sinha88@gov.in (1) |

### Department of Chemicals and Petro-Chemicals (DoCP)

| Topic | Contact officers (docs signed) |
|---|---|
| RTI / appellate authority / CPIO | **Shri Manoj Kumar Singh** — Co-ordination — mk.singh73@gov.in (2) |
| Statutory rules / gazette notifications (G.S.R. / S.O.) | **Shri Manoj Kumar Singh** — Co-ordination — mk.singh73@gov.in (1) |
| Vigilance / disciplinary / court matters | **Shri Manoj Kumar Singh** — Co-ordination — mk.singh73@gov.in (1) |

### Department of Consumer Affairs (DoCA)

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation | **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (6); **Smt. Nidhi Khare** — Secretary (CA) — Secy-ca@nic.in (2) |
| Advisory / public notice / caution | **Sh. Ashutosh Agarwal** — Director (Legal Metrology) — ashutosh.agarwal13@nic.in, dirwm-ca@nic.in (2) |
| HR: appointment / transfer / posting / promotion | **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (7); **Shri Mukesh Kumar** — Section officer (BIS) — sobis-ca@nic.in (6) |
| HR: leave / pay / allowances / service rules | **Sh. Amit Kumar** — Under Secretary (P&C/O&M/ RTI/ E-GOV) — uspc-ca@gov.in (2); **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (2) |
| Legal metrology / consumer protection rules | **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (30); **Smt. Nidhi Khare** — Secretary (CA) — Secy-ca@nic.in (6); **Sh. Ashutosh Agarwal** — Director (Legal Metrology) — ashutosh.agarwal13@nic.in, dirwm-ca@nic.in (1) |
| Licensing / approvals / standards / enlistment | **Sh. Amit Kumar** — Under Secretary (P&C/O&M/ RTI/ E-GOV) — uspc-ca@gov.in (2); **Sh. Baldev Singh** — Under Secretary (BIS) — usbis-ca@gov.in (2); **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (1) |
| Office administration / housekeeping | **Sh. Ashutosh Agarwal** — Director (Legal Metrology) — ashutosh.agarwal13@nic.in, dirwm-ca@nic.in (1) |
| Procurement / tenders / GeM | **Shri Mukesh Kumar** — Section officer (BIS) — sobis-ca@nic.in (2); **Sh. Bal Krishna Thakur** — Under Secretary (Establishment and General Administration) — usestt-ca@nic.in (1); **Sh. Baldev Singh** — Under Secretary (BIS) — usbis-ca@gov.in (1) |
| Recruitment rules / RRs | **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (4) |
| Statutory rules / gazette notifications (G.S.R. / S.O.) | **Sh. Anupam Mishra** — Additional Secretary — as-ca1@gov.in (39); **Smt. Nidhi Khare** — Secretary (CA) — Secy-ca@nic.in (6); **Sh. Ashutosh Agarwal** — Director (Legal Metrology) — ashutosh.agarwal13@nic.in, dirwm-ca@nic.in (2) |

### Department of Expenditure (DoE)

| Topic | Contact officers (docs signed) |
|---|---|
| Budget / sanction / release of funds / grants | **Shri Prateek Kumar Singh** — Director — prateeks.98@gov.in (1) |
| HR: appointment / transfer / posting / promotion | **Shri Vijay Kumar Sharma** — Under Secretary — vkumar.sharma@nic.in (6) |
| Scheme guidelines / implementation | **Shri Prateek Kumar Singh** — Director — prateeks.98@gov.in (1) |
| Vigilance / disciplinary / court matters | **Shri Vijay Kumar Sharma** — Under Secretary — vkumar.sharma@nic.in (6) |

### Department of Land Resources (DLR)

| Topic | Contact officers (docs signed) |
|---|---|
| HR: appointment / transfer / posting / promotion | **Shri Sami Ahmad Khan** — Deputy Secretary — sa.khan15@gov.in (1) |
| Other / unclassified | **Shri Girnish Kumar** — Under Secretary — girnish.kumar@nic.in (2) |

### Department of Legal Affairs

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation | **Shri Rajiv Mani** — Secretary — secylaw-dla@nic.in (9) |
| Statutory rules / gazette notifications (G.S.R. / S.O.) | **Shri Rajiv Mani** — Secretary — secylaw-dla@nic.in (7) |

### Department of Revenue (DoR)

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation | **Hanuman Prasad Nishad** — SO (Ad.VII) — hp.nishad@nic.in (1) |
| HR: appointment / transfer / posting / promotion | **Hanuman Prasad Nishad** — SO (Ad.VII) — hp.nishad@nic.in (2) |
| Other / unclassified | **Nimit Dhalia** — Assistant Director — nimit.dhalia2057@gov.in (1) |
| RTI / appellate authority / CPIO | **Hanuman Prasad Nishad** — SO (Ad.VII) — hp.nishad@nic.in (1) |
| Statutory rules / gazette notifications (G.S.R. / S.O.) | **Hanuman Prasad Nishad** — SO (Ad.VII) — hp.nishad@nic.in (1) |

### Deputy Secretary, Department of School Education & Literacy, M/o Education, Govt. of India, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| Advisory / public notice / caution |  |

### Deputy Secretary, Ministry of Tourism, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| HR: appointment / transfer / posting / promotion |  |
| Recruitment rules / RRs |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Director, Department of Promotion of Industry & Internal Trade, M/O Commerce and Industry, Govt. of India, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |

### Food Processing Industries (MoFPI)

| Topic | Contact officers (docs signed) |
|---|---|
| HR: appointment / transfer / posting / promotion | **Shri Rakesh Kumar Gupta** — Section Officer — r.kumargupta67@nic.in (1) |
| RTI / appellate authority / CPIO | **Shri Rakesh Kumar Gupta** — Section Officer — r.kumargupta67@nic.in (1) |

### Joint Secretary to GOI, M/o Housing and Urban Affairs, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| HR: appointment / transfer / posting / promotion |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Joint Secretary, D/o Promotion of Industry and Internal Trade, M/o Commerce & Industry, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |
| Scheme guidelines / implementation |  |

### Joint Secretary, D/o Promotion of Industry and Internal Trade, M/o Commerce and Industry, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Other / unclassified |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Joint Secretary, Department for Promotion of Industry & Internal Trade, Ministry of Commerce & Industries, GoI, New Delhi

| Topic | Contact officers (docs signed) |
|---|---|
| Scheme guidelines / implementation |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Joint Secretary, Department of Financial Services, M/o Finance, Govt. of India, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Joint Secretary, Dept. of Fisheries, GoI, M/o Fisheres, Animal Husbandry and Dairying

| Topic | Contact officers (docs signed) |
|---|---|
| Licensing / approvals / standards / enlistment |  |
| Scheme guidelines / implementation |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Joint Secretary, GOI, D/o Financial Services, M/o Finance, New Delhi.

| Topic | Contact officers (docs signed) |
|---|---|
| HR: leave / pay / allowances / service rules |  |
| Scheme guidelines / implementation |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Joint Secretary, M/o Earth Sciences, New Delhi

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| HR: appointment / transfer / posting / promotion |  |
| Recruitment rules / RRs |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Joint Secretary, M/o Electronics and IT, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| Advisory / public notice / caution |  |
| HR: appointment / transfer / posting / promotion |  |
| HR: leave / pay / allowances / service rules |  |
| Other / unclassified |  |
| RTI / appellate authority / CPIO |  |
| Scheme guidelines / implementation |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Joint Secretary, M/o Housing & Urban Affairs, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Joint Secretary, M/o Housing and Urban Affairs, GoI, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| HR: appointment / transfer / posting / promotion |  |
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

### Joint Secretary, M/o Textiles, Govt. of India

| Topic | Contact officers (docs signed) |
|---|---|
| Licensing / approvals / standards / enlistment |  |
| Other / unclassified |  |
| Scheme guidelines / implementation |  |

### Joint Secretary, Ministry of Labour & Employment, Govt. of India, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation |  |
| Budget / sanction / release of funds / grants |  |

### Legislative Department

| Topic | Contact officers (docs signed) |
|---|---|
| Acts / commencement / legislation | **Shri Rajiv Mani** — Secretary — secyoffice-ld@gov.in (2) |
| Committees / meetings / minutes / constitution of | **Shri Rajiv Mani** — Secretary — secyoffice-ld@gov.in (1) |
| Other / unclassified | **Shri Rajiv Mani** — Secretary — secyoffice-ld@gov.in (2) |

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

### Panchayati Raj (MoPR)

| Topic | Contact officers (docs signed) |
|---|---|
| Training / capacity building / workshops | **Shri Kumar Shyamal Parthsarathi** — Under Secretary — shymal.pr@nic.in (3) |

### Ports, Shipping and Waterways (MoPSW)

| Topic | Contact officers (docs signed) |
|---|---|
| Committees / meetings / minutes / constitution of | **Sh. Sachin Kumar** — SO — sofin-psw@gov.in (1) |
| HR: appointment / transfer / posting / promotion | **Sh. Uttam Kumar Mishra** — US (SU) — ussu-psw@gov.in (3); **Sh. Sandeep Gupta** — JS (PHRD, Establishment, Coord. & Parl) — jsadmin-psw@gov.in jscord-psw@gov.in (2) |
| HR: leave / pay / allowances / service rules | **Sh. Uttam Kumar Mishra** — US (SU) — ussu-psw@gov.in (2) |
| Recruitment rules / RRs | **Sh. Sandeep Gupta** — JS (PHRD, Establishment, Coord. & Parl) — jsadmin-psw@gov.in jscord-psw@gov.in (1) |
| Training / capacity building / workshops | **Sh. Sachin Kumar** — SO — sofin-psw@gov.in (1) |

### Registrar General and Census Commissioner, India (RG & CCI), New Delhi

| Topic | Contact officers (docs signed) |
|---|---|
| Office administration / housekeeping |  |

### Secretary, M/o Environment, Forests & Climate Change, Govt. of India, New Delhi (On Central Deputation)

| Topic | Contact officers (docs signed) |
|---|---|
| Statutory rules / gazette notifications (G.S.R. / S.O.) |  |

## Signatories missing from the rosters (roster gaps)

People who sign orders for a ministry but are not on its who's-who page / igod / civil lists — candidates to add to the yellow pages.

| Ministry | Signatory (as printed) | Signed as | Documents | Latest |
|---|---|---|---|---|
| Department of Justice (DoJ) | Prem Chand | Under Secretary (Appointments-! / Under Secretary (Appointments-1 | 114 | 2026-10-13 |
| Department of Legal Affairs (DoLA) | Ramesh Kairamkonda | Officer / Officer (Judicial | 78 | 2026-10-16 |
| Department of Justice (DoJ) | Anant Kumar | Under Secretary (Appointments-II / Under Secretary to the Government of India | 72 | 2026-10-09 |
| Mines (MoM) | VEENA KUMARI DERMAL | Addl. Secy / Joint Secretary | 52 |  |
| Mines (MoM) | DINESH MAHUR | Joint Secretary / Joint Secretary to the Government of India | 33 |  |
| Department of Legal Affairs (DoLA) | Kumar Gaurva | Officer / Officer (Judicial | 32 | 2026-07-02 |
| Steel (MoS) | Parmjeet Singh | Adviser / Advisor | 31 | 2025-04 |
| Department of Legal Affairs (DoLA) | Manindra Choudhary | Adviser / Advisor | 29 | 2026-10-16 |
| Mines (MoM) | KULVEER SINGH YADAV | Jt. Secy | 27 |  |
| Department of Administrative Reforms and Public Grievances (DARPG) | Vandana Nangia | I                             to the Government of India / Under Secretary to the Government of India | 25 | 2024-05-30 |
| Department of Land Resources (DLR) | Th. Lianboi | Under SecretarY (Admn / Under Secretary (Admn. | 21 | 2026-03-16 |
| Road Transport and Highways (MoRTH) | MAHMOOD AHMED | Addl Secy / Addl. Secy | 20 |  |
| Housing and Urban Affairs (MoHUA) | S.K. Gupta | SecretarY (Admin / Secretary (Admn | 19 | 2025-10-31 |
| Department of Telecommunications (DoT) | Bijender Singh | Under Secretary to the Government of India / Under Secretary to the Govt. of India | 18 | 2026-10-21 |
| Department for Promotion of Industry and Internal Trade (DPIIT) | SANDHYA BHULLAR | Jt. Secy | 16 | 2026-09-22 |
| Labour and Employment (MoLE) | TEJASWI S. NAIK | Jt. Secy / Jt.Secy | 16 | 2026-09-17 |
| Textiles (MoT) | RAJEEV SAXENA | Joint Secretary to the Government of India / Jt. Secy | 16 | 2025-01-02 |
| Department for Promotion of Industry and Internal Trade (DPIIT) | Manash Kumar Roy | Under Secretary / Under Secretary to the Govt. of India | 15 | 2026-10-19 |
| Department of Financial Services (DoFS) | Vinod Kumar | Director (Coordination and RTI Cell / Director (Coordination, DA and RT| Cell | 14 | 2026-10 |
| Power | Madhukar Sood | Under Secretary to Government of India / Under Secretary to the Government of India | 14 | 2025-06-28 |
| Department of Animal Husbandry and Dairying (DoAHD) | Rohit Tewari | Secretary to the Government of India / Under Secretary to the Government of India | 13 | 2025-07-15 |
| Department of Justice (DoJ) | Jagann Srinivasan | Joint Secretary to the Governinent of India / Joint Secretary to the Government of India | 13 | 2026-06-01 |
| Department of Justice (DoJ) | Jaganna Srinivasan | Joint Secretary to the Government of India / Joint Secretary to the Government ofIndia | 13 | 2025-08-29 |
| Labour and Employment (MoLE) | MANISH KUMAR GUPTA | Jt. Secy | 13 | 2025-06-26 |
| Department of Fisheries (DoF) | V.Srinivasa Rao | Director (Fisheries / Director (Fisheries) ; | 12 | 2026-07-24 |
| Department of Telecommunications (DoT) | SHASHI KUMAR | Director (DS-II | 12 | 2026-10-08 |
| Labour and Employment (MoLE) | DEEPIKA KACHHAL | Jt. Secy | 12 | 2026-08-25 |
| Department of Justice (DoJ) | Jagannat Srinivasan | Joint Secretary to the Government of India | 11 | 2025-10-14 |
| Department of Telecommunications (DoT) | Sunil Kumar | Under Secretary to the Government of India / Under Secretary to the Govt. of India | 11 | 2026-10-21 |
| Labour and Employment (MoLE) | R. K. GUPTA | Jt. Secy | 11 | 2025-06-26 |
| Legislative Department (LD) | G. NARAYANA RAJU | Secretary to the Govt. of India / Secretary to the Govt. of India. | 11 | 2020-03-18 |
| Parliamentary Affairs (MPA) | Satya Prakash | Additional Secretary / Additional Secretary to the Govt. of India | 11 | 2025-04-15 |
| Department of Animal Husbandry and Dairying (DoAHD) | Dharm Prakash | Under Secretary (RTI / Under Secretary (RTT | 10 | 2025-07-15 |
| Department of Financial Services (DoFS) | Jasmine James | Deputy Secretary (Coord. / Under Secretary (Coordination | 10 | 2026-01 |
| Department of Fisheries (DoF) | Krishan Pal | Under Secrelary to the Govl. o, India / Under Secretary to the Government of India | 10 | 2026-07-15 |
| Department of Higher Education (DoHE) | Purnendu Kishore Banerjee | Joint Secretary to the Government of India / Jt. Secy | 10 | 2026-07-09 |
| Department of Land Resources (DLR) | Rajeev Bahal | Under Secretary to the Government of India | 10 | 2022-03-17 |
| Department of Scientific and Industrial Research (DSIR) | Kuldip Kumar | Under Secretary to the Government of India / Under Secretary to the Govt' of India | 10 | 2025-12-05 |
| Environment, Forest and Climate Change (MoEFCC) | Prem Prakash Maurya | Under Secretary to the Government of India / Under Secretary to the Government of Indla | 10 |  |
| Power | Ajay Shankar | Additional Secretary / Additional Secretary to the Government of India | 10 | 2025-07-01 |
| Power | SRIKANT NAGULAPALLI | Additional Secretary to the Govt. of India / Addl. Secy | 10 | 2025-09-19 |
| Road Transport and Highways (MoRTH) | Shashi Bhooshan Kumar | Under Secretary to the Govt. of India | 10 |  |
| Department of Animal Husbandry and Dairying (DoAHD) | UPAMANYU BASU | Jt. Secy | 9 | 2025-06-30 |
| Department of Financial Services (DoFS) | Abdul Gufran | Under Secretary to Government of India / Under Secretary to the Government of India | 9 | 2026-10 |
| Department of Health Research (DHR) | Tushar Karmarkar | Deputy Secretary / Deputy Secretary, DHR | 9 | 2026-10-08 |
| Department of Legal Affairs (DoLA) | Niranjan Prasad | Officer (Judicial | 9 | 2026-10-05 |
| Development of North Eastern Region (MDONER) | S.D. Meena | Deputy Secretary to the Government of India / Deputy Secretary to the Govt. of India | 9 | 2024-07-29 |
| Earth Sciences (MoES) | Rishi Kumar | DEPUTY SECRETARY (GA / Deputy Secretary | 9 | 2025-07-02 |
| Electronics and Information Technology (MeitY) | AMITESH KUMAR SINHA | Addl. Secy / Jt. Secy | 9 | 2025-11-21 |
| Electronics and Information Technology (MeitY) | Sushil Pal | Joint Secretary to Government of India / Joint Secretary to the Government of India | 9 | 2026-10-06 |
| Labour and Employment (MoLE) | RAJEEV ARORA | Jt. Secy | 9 | 2025-07-05 |
| Parliamentary Affairs (MPA) | Rameshwar Prasad | Under Secretary to the Government of India / Under Secretary to the Govt. Of India | 9 | 2025-08-01 |
| Department of Animal Husbandry and Dairying (DoAHD) | Deepak Sethi | Under Secretary / Under Secretary to the Government of India | 8 | 2025-06-27 |
| Department of Animal Husbandry and Dairying (DoAHD) | GIRJA NAND SINGH | Joint Secretary to the Government of India / Jt. Secy | 8 | 2026-03-27 |
| Department of Consumer Affairs (DoCA) | AMIT MEHTA | Jt. Secy | 8 |  |
| Department of Financial Services (DoFS) | SAURABH MISHRA | Jt. Secy | 8 | 2026-10 |
| Department of Legal Affairs (DoLA) | Kumar Gaurav | Officer (Judicial | 8 | 2026-10-09 |
| Department of Personnel and Training (DoPT) | ARCHANA VARMA | It. Secy / Jt. Secy | 8 | 2014-10-27 |
| Department of Pharmaceuticals (DoPs) | Uma Magesh | Under Secretary to Government of India / Under Secretary to the Government of India | 8 |  |
| Environment, Forest and Climate Change (MoEFCC) | ARUN KUMAR MEHTA | Addl. Secy | 8 | 2018-03 |
| Labour and Employment (MoLE) | MANISH GUPTA | Jt. Secy | 8 | 2025-06-26 |
| Parliamentary Affairs (MPA) | Kiran Kumar | Under Secretary (Admn. / Under Secretary to the Govt. of India | 8 | 2024-07-23 |
| Statistics and Programme Implementation (MoSPI) | Neelam Arora | Under Secretary to the Government of India / Under Secretary to the Govt. of India | 8 | 2026-10-22 |
| Steel (MoS) | RUCHIKA CHAUDHRY GOVIL | Joint Secretary to the Government of India / Jt. Secy | 8 | 2025-04 |
| Department of Animal Husbandry and Dairying (DoAHD) | S. C. Srivastav | Deputy Secretary to the Government of India / Deputy Secretary to the Govt. of India | 7 | 2025-10-19 |
| Department of Financial Services (DoFS) | SANJAY KUMAR MISHRA | Under Secy | 7 |  |
| Department of Financial Services (DoFS) | SHEKHAR AGARW AL | Director | 7 | 2026-01 |
| Department of Health Research (DHR) | GEETA NARAYAN | Jt. Secy | 7 | 2022-05-19 |
| Department of Health and Family Welfare (DoHFW) | Pamposh Pokhriyal | Deputy Director | 7 | 2026-05-12 |
| Department of Legal Affairs (DoLA) | MADHAB CHARAN PRUSTY | Additional Secretary / Addl. Secy | 7 | 2026-07-23 |
| Department of Personnel and Training (DoPT) | Uma Magesh | Under Secretary to Government of India / Under Secretary to the Government of India | 7 | 2026-06-05 |
| Housing and Urban Affairs (MoHUA) | SURYA NARAYAN JHA | Under Secy | 7 | 2026-09-02 |
| New and Renewable Energy (MNRE) | GHANSHYAM PRASAD | Joint Secretary to the Govt. of India / Jt. Secy | 7 | 2022-12-01 |
| New and Renewable Energy (MNRE) | Rahul Rawat | Scientist 'C' / Scientist - C | 7 | 2024-08-23 |
| New and Renewable Energy (MNRE) | Rohit Thakwani | Scientist C / Scientist ‘C’ | 7 | 2023-02-15 |
| Tourism | R K Bhati | . Director General / Asstt. Director General | 7 | 2024-01-30 |
| Department for Promotion of Industry and Internal Trade (DPIIT) | ABHISHEK DUTT | Under S ec r eto ry / Under Secretary | 6 | 2026-09-03 |
| Department of Animal Husbandry and Dairying (DoAHD) | SAGAR MEHRA | Jt. Secy | 6 | 2021-12-17 |
| Department of Consumer Affairs (DoCA) | D. K. SONKER | Deputy Director (NTH / Director | 6 |  |
| Department of Legal Affairs (DoLA) | Devanshu Kumar | Under Secretary / Under Secretary to the Govt. of India | 6 | 2026-01-23 |
| Department of Personnel and Training (DoPT) | JISHNU BARUA | Jt. Secy | 6 | 2016-06-20 |
| Department of School Education and Literacy (DSEL) | ANITA KARWAL | Addl. Secy / Jt. Secy | 6 | 2025-12-31 |
| Department of School Education and Literacy (DSEL) | Maneesh Garg | Director, Samagra Shiksha Department of School Education & Literacy, Govt. of India / Joint Secretary, Samagra Shiksha | 6 | 2025-12-31 |
| Environment, Forest and Climate Change (MoEFCC) | NARESH PAL GANGWAR | Jt. Secy | 6 | 2021-11 |
| Environment, Forest and Climate Change (MoEFCC) | SURJIT SINGH | Jt. Secy | 6 | 2018-03 |
| Labour and Employment (MoLE) | G. NARAYANA RAJU | Secretary to the Govt. of India. | 6 | 2025-07-05 |
| Parliamentary Affairs (MPA) | Sharad Dwivedi | Under Secretary (Admn. / Under Secretary to the Govt. of India | 6 | 2025-08-01 |
| Planning (MoP) | Harinder Singh | Under Secretary (RT! / Under Secretary (RTD | 6 | 2026-06 |
| Power | Satinder Kaur | Under Secretary to the Government of India | 6 | 2025-06-28 |
| Steel (MoS) | ABHIJIT NARENDRA | Joint Secretary to the Government of India / Jt. Secy | 6 | 2026-06 |
| Steel (MoS) | Addl. Industrial | Adviser | 6 | 2025-04 |
| Tourism | RAJESH KUMAR | Under Secretary to the Government of India / Under Secy | 6 | 2025-08-07 |
| Department of Financial Services (DoFS) | Mohamed Ashraf J.S | Deputy Secretary / Deputy Secretary (Coord. | 5 | 2026-10 |
| Department of Fisheries (DoF) | Umesh Shankar Prasad | Under Secrelary to the Govt. of India / Under Secretary to the Government of India | 5 | 2023-07-01 |
| Department of Pharmaceuticals (DoPs) | NAVDEEP RINWA | Jt. Secy | 5 |  |
| Department of Public Enterprises (DPE) | Samsul Haque | Under Secretary | 5 | 2025-07-11 |
| Department of School Education and Literacy (DSEL) | Gajraj Singh | Deputy Director (OL / Deputy Director (Ol | 5 | 2016-05-19 |
| Department of School Education and Literacy (DSEL) | RINA RAY | Addl. Secy | 5 | 2017-03-02 |
| Department of Science and Technology (DST) | ANJU BHALLA | Joint Secretary / Joint Secretary (Admn. | 5 | 2020-11-25 |
| Development of North Eastern Region (MDONER) | Vikramaditya Singh Dev | officer | 5 | 2026-08-27 |
| Electronics and Information Technology (MeitY) | Notan Roy | Scientist / Scientist 'E', Cyber Laws, MeitY | 5 | 2026-04-24 |
| Housing and Urban Affairs (MoHUA) | Sunil Kumar | Deputy Secretary to the Govt. of India / Under Secretary to the Govt. of India | 5 | 2025-12-16 |
| Labour and Employment (MoLE) | KALPANA RAJSINGHOT | Jt. Secy | 5 | 2025-07-04 |
| Legislative Department (LD) | SUBHASH C. JAIN | Secy. to the Govt. of India. / Secy.to the Govt. of India. | 5 | 2025-10-30 |
| Mines (MoM) | VIVEK KUMAR BAJPAI | Joint Secretary to the Government of India / Jt. Secy | 5 |  |
| New and Renewable Energy (MNRE) | PIYUSH SINGH | Joint Secretary to the Government of India / Jt. Secy | 5 | 2023-05-23 |
| Parliamentary Affairs (MPA) | Mukesh Kumar | Deputy Secretary / Deputy Secretary (Admn. | 5 | 2026-07-22 |
| Ports, Shipping and Waterways (MoPSW) | MUMBAI PORT TRUST | Officer (im full (5 SRE NPL Et ae / Officer (in fail a oe es ee | 5 |  |
| Power | Hausuanthang Guite | Under Secretary to the Government of India / Under Secretary to the Govt. of India | 5 | 2025-06-28 |
| Statistics and Programme Implementation (MoSPI) | Mukesh Kumar | Under Secretary to the Government of India / Under Secretary to the Govt. of India | 5 | 2026-06-16 |
| Steel (MoS) | RASIKA CHAUBE | Additional Secretary to the Government of India / Addl. Secy | 5 | 2025-04 |
| Steel (MoS) | SUNIL BARTHWAL | Jt. Secy / Secy | 5 | 2025-04 |
| Tourism | RK Bhati | . Director General | 5 | 2023-10-09 |
| Department of Animal Husbandry and Dairying (DoAHD) | Bhushan Tyagi | Deputy Commissioner (RGM) - / Joint Commissioner | 4 | 2025-06-27 |
| Department of Animal Husbandry and Dairying (DoAHD) | KPJ Gerald | Deputy Secretary to Govt of India / Deputy Secretary to the Govt of India | 4 | 2020-06-04 |
| Department of Animal Husbandry and Dairying (DoAHD) | Madhusudanan V. K | Under Secretary (RTI / Under Secretary to the Government of India | 4 | 2025-06-27 |
| Department of Consumer Affairs (DoCA) | P. V. RAMA SASTRY | Jt. Secy / Secy | 4 |  |
| Department of Consumer Affairs (DoCA) | RAKESH KACKER | Addl. Secy / Spl. Secy | 4 |  |
| Department of Financial Services (DoFS) | Sanjay Kumar | Deputy Secretary / Deputy Secretary to the Government of India | 4 | 2026-01 |
| Department of Financial Services (DoFS) | Subhashchandra Amin | Under Secretary to the Go'rt. of India / Under Secretary to the Govt. of India | 4 |  |
| Department of Legal Affairs (DoLA) | C. Dabaria | Adviser (Judicial | 4 | 2026-08-20 |
| Department of Legal Affairs (DoLA) | Krishna Mohan Arya | Adviser / Advisor | 4 | 2026-02-16 |
| Department of Legal Affairs (DoLA) | Lakka Muneswara Rao | Officer (Judicial | 4 | 2026-05-27 |
| Department of Legal Affairs (DoLA) | Legal Affairs | Registrar, Supreme Court of India, New Delhi. | 4 | 2025-12-15 |
| Department of Legal Affairs (DoLA) | PRAVEEN SRIVASTAVA | Addl Secy / Addl. Secy | 4 | 2026-10-08 |
| Department of Legal Affairs (DoLA) | R. K. Srivastava | Joint Secretary & Legal Adviser | 4 | 2026-08-20 |
| Department of Legal Affairs (DoLA) | Radhe Shyam Singh | Under Secretary, Notary Cell | 4 | 2025-12-23 |
| Department of Legal Affairs (DoLA) | Shweta Kamboj | Under Secretary to Govt. of India / Under Secretary to the Gort. ofIndia | 4 | 2026-06-09 |
| Department of Public Enterprises (DPE) | Naresh Kumar | Under Secretary / Under Secretary to the Govt. of India | 4 | 2023-09-13 |
| Department of Public Enterprises (DPE) | Rajesh Puri | Deputy Director | 4 | 2025-09-15 |
| Department of Science and Technology (DST) | Himanshu Gandhi | Under Secretary to Govt. of India / Under Secretary to the Govt of India | 4 | 2019-04-05 |
| Department of Science and Technology (DST) | Ravi Kumar | Officer / Officer (Pension). | 4 | 2018-09-04 |
| Department of Science and Technology (DST) | Soumitra Basu | Under Secretary to the Govt of India | 4 | 2017-08-23 |
| Department of Telecommunications (DoT) | DEVENDRA KUMAR RAI | Jt. Secy | 4 | 2026-08-21 |
| Development of North Eastern Region (MDONER) | Haradhan Das | Under Secretary to the Govt. of India | 4 | 2016-12-14 |
| Development of North Eastern Region (MDONER) | Silabhadra Das | Deputy Secretary / Deputy Secretary to the Government of India | 4 | 2025-01-09 |
| Earth Sciences (MoES) | Ashok Saha | Scientist -C / Scientist-C, | 4 | 2025-07-04 |
| Earth Sciences (MoES) | P.G. Dastidar | Scientist | 4 | 2025-06-18 |
| Electronics and Information Technology (MeitY) | Saurabh Ranjan | Scientist D / Scientist ‘D’ | 4 | 2026-06-04 |
| Environment, Forest and Climate Change (MoEFCC) | G. V. Subrahmanyam | Adviser / Scientist ‘G’ | 4 | 2021-08 |
| Environment, Forest and Climate Change (MoEFCC) | GEETA MENON | Jt. Secy | 4 | 2017-08 |
| Environment, Forest and Climate Change (MoEFCC) | Lalit Kapur | Adviser | 4 | 2021-08 |
| Environment, Forest and Climate Change (MoEFCC) | Ved Prakash Mishra | Director | 4 | 2021-12 |
| Heavy Industries (MoHI) | VIJAY MITTAL | Jt. Secy | 4 | 2026-01 |
| Housing and Urban Affairs (MoHUA) | A.K. Sinha | Under Secretary (Admn.A / Under Secretary to the Government of India | 4 | 2026-02-22 |
| Housing and Urban Affairs (MoHUA) | U K TIWARI | Under Secy | 4 | 2026-07-01 |
| Legislative Department (LD) | SANJAY SINGH | Secretary to the Govt. of India. | 4 | 2015-05-28 |
| Legislative Department (LD) | Sr. Accounts | Officer (A) / Officer(Admn) | 4 | 2015-12-07 |
| Parliamentary Affairs (MPA) | Anil Kumar | Under Secretary to the Govt. of India | 4 | 2017-03-08 |
| Textiles (MoT) | PRAJAKTA VERMA | Jt. Secy | 4 | 2024-07-03 |
| Tourism | Seema Jain | Director (Destination Development / Director (SD | 4 | 2024-11-12 |
| Department for Promotion of Industry and Internal Trade (DPIIT) | Shambhu Datt Sati | Under Secretary to the Govt. of India / Under Secy | 3 | 2026-07-03 |
| Department of Administrative Reforms and Public Grievances (DARPG) | Kaikam Doungel | Under Secretary to the Govt of India | 3 | 2023-03-23 |
| Department of Animal Husbandry and Dairying (DoAHD) | K. GURUMURTHY | Jt. Secy | 3 | 2026-07-10 |
| Department of Financial Services (DoFS) | Chandragupta Shaurya | Under Secretary to the Govt. of India | 3 |  |
| Department of Financial Services (DoFS) | TARUN BAJAJ | It. Secy | 3 | 2026-01 |
| Department of Fisheries (DoF) | KHAM KHAN SUAN | Under S6cr6tery / Under Secretary to the Govt' of India | 3 | 2025-12-04 |
| Department of Fisheries (DoF) | Meenakshi Sankar | Under Secretary to the Govt. of India | 3 | 2024-09-02 |
| Department of Fisheries (DoF) | YOGINDER KUMAR | Under Secretary to the Government of India / Under Secy | 3 | 2025-12-08 |
| Department of Health Research (DHR) | REETA VASISHTA | Secretary to the Govt. of India. | 3 | 2022-04-18 |
| Department of Health and Family Welfare (DoHFW) | Abhishek Pandey | Under Secretary to the Government of India | 3 | 2026-06-01 |
| Department of Health and Family Welfare (DoHFW) | Anurag Tiwari | Under Secretary to the Government of India | 3 | 2026-08-14 |
| Department of Health and Family Welfare (DoHFW) | D V K Rao | Under Secretary to the Govt. of India | 3 | 2025-12-04 |
| Department of Health and Family Welfare (DoHFW) | PATIBANDLA ASHOK BABU | Jt. Secy | 3 | 2026-05-21 |
| Department of Health and Family Welfare (DoHFW) | Rajesh Kumar | Under Secretary to the Government of India | 3 | 2026-07-06 |
| Department of Higher Education (DoHE) | Manish R. Joshi | Secretary / Secretary, | 3 | 2023-08-31 |
| Department of Legal Affairs (DoLA) | ASHUTOSH MISHRA | Addl. Secy | 3 | 2025-10-17 |
| Department of Legal Affairs (DoLA) | KuFnar Gaurva | Officer (Judicial | 3 | 2025-06-27 |
| Department of Personnel and Training (DoPT) | S. G. Mulchandaney | Under Secretary | 3 | 2025-08-06 |
| Department of Personnel and Training (DoPT) | SUJATA CHATURVEDI | Addl. Secy | 3 | 2020-11-25 |
| Department of Public Enterprises (DPE) | Kalyani Mishra | Director | 3 | 2020-08-05 |
| Department of Public Enterprises (DPE) | Lokesh Bajpai | Director / Director, DPE | 3 | 2025-07-07 |
| Department of School Education and Literacy (DSEL) | J.P Pandey | Director, Samagra Shiksha Department of School Education & Literacy, Govt. of India | 3 | 2025-12-31 |
| Department of Science and Technology (DST) | A. DHANALAKSHMI | Jt. Secy | 3 | 2026-02-13 |
| Department of Scientific and Industrial Research (DSIR) | SRINIBAS PRADHAN | UNDER SECRETARY TO THE GOVT.OF INDIA / Under Secretary to the Govt.of India | 3 | 2025-10-30 |
| Department of Social Justice and Empowerment (DoSJE) | Asokan P K | Under Secretary to the Government of India | 3 |  |
| Department of Social Justice and Empowerment (DoSJE) | K. V. K. SUNDARAM | Secretary,, / Secretary. | 3 |  |
| Department of Telecommunications (DoT) | Harshvardhan Singh Khangarot | Director (SEA | 3 | 2026-10-16 |
| Development of North Eastern Region (MDONER) | Parna Sahana | Under Secretary to the Government of India / Under Secretary to the Govt. of India | 3 | 2025-11-19 |
| Earth Sciences (MoES) | Meena Gopinath | Under Secretary to the Govt. of India | 3 | 2026-08-05 |
| Electronics and Information Technology (MeitY) | Ajay Kumar | Joint Secretary to Govt. of India / Joint Secretary to Govt. of India, | 3 | 2015-03-17 |
| Electronics and Information Technology (MeitY) | Kshitij Kushagra | Scientist- F | 3 | 2026-03-18 |
| Electronics and Information Technology (MeitY) | P. Victor Albuquerque | Deputy Secretary (O&M / Deputy Secretary (Pers. | 3 | 2026-09-15 |
| Electronics and Information Technology (MeitY) | RAJIV MANI | Secretary to the Govt. of India. | 3 | 2025-08-29 |
| Environment, Forest and Climate Change (MoEFCC) | CEO CAMPA | Director, GA, MoEF&CC, New Delhi. / Secretary, Government of Assam, Dispur. | 3 |  |
| Housing and Urban Affairs (MoHUA) | M. Ramachandran | Secretary | 3 | 2025-11-03 |
| Housing and Urban Affairs (MoHUA) | PRAVEER KUMAR | Jt. Secy | 3 | 2026-09-07 |
| Information and Broadcasting (MIB) | Santosh Kumar Maurya | Under Secretary | 3 | 2026-10 |
| Information and Broadcasting (MIB) | Shiv Ram Meena | Under Secrctary to the Govemmont of India / Under Secretary to the Governmenl of India | 3 | 2025-11 |
| Labour and Employment (MoLE) | Babu Cherian | Deputy Secretary to the Government of India | 3 | 2025-07-05 |
| Labour and Employment (MoLE) | Dhananjay Sharma | Under Secretary to the Government of India / Under Secretary to the Government of India : | 3 | 2025-06-23 |
| Mines (MoM) | R. SRIDHARAN | Addl. Secy | 3 |  |
| Mines (MoM) | RAJIV MANI | Secretary to the Govt. of India. | 3 |  |
| Mines (MoM) | REETA VASISHTA | Secretary to the Govt. of India. | 3 |  |
| Mines (MoM) | Shakil Alam | Advisor / Advisor (Mines | 3 |  |
| New and Renewable Energy (MNRE) | AJAY JAIN | PRINCIPAL SECRETARY TO GOVERNMENT | 3 | 2019-01-03 |
| New and Renewable Energy (MNRE) | Sanjay G. Kamdhar | Scientist-E | 3 | 2023-08-23 |
| Ports, Shipping and Waterways (MoPSW) | LUCAS L. KAMSUAN | Jt. Secy | 3 |  |
| Power | Ghanshyam Prasad | Engineer (RR & OM / Joint Secretary to the Govt. of India | 3 | 2025-07-02 |
| Steel (MoS) | G. Sarathy Raja | Deputy Secretary to the Government of India | 3 | 2025-11 |
| Textiles (MoT) | Jayashree Sivakumar | Under Secretary to the Govt. of India | 3 | 2025-01-06 |
| Textiles (MoT) | Ravi Shankar Shukla | Deputy Secretary (AdmIn / Deputy Secretary to the Govt. of India | 3 | 2024-03-11 |
| Tourism | Sayak Nandi | Assistant Director / Director(SD | 3 | 2026-08-20 |
| Department for Promotion of Industry and Internal Trade (DPIIT) | Auditor Superintendent Gazetted | Officer | 2 | 2026-06-23 |
| Department for Promotion of Industry and Internal Trade (DPIIT) | Md. Alam Ansari | Deputy Director / Deputy Director (Startup India | 2 | 2026-03-06 |
| Department for Promotion of Industry and Internal Trade (DPIIT) | NITI Aayog | Comptroller and Auditor General of India / Secretary, DPIIT. | 2 | 2025-11-24 |
| Department for Promotion of Industry and Internal Trade (DPIIT) | RAJEEV SINGH THAKUR | Addl. Secy | 2 | 2026-09-24 |
| Department for Promotion of Industry and Internal Trade (DPIIT) | Sher Singh Meena | Under Secretary to the Govt. of India / Under Secretary to the Govt. of.India | 2 | 2026-09-03 |
| Department for Promotion of Industry and Internal Trade (DPIIT) | SHUBHRA SINGH | Jt. Secy | 2 | 2025-09-01 |
| Department of Administrative Reforms and Public Grievances (DARPG) | Bhuvnendra Singh | Under Secretary to the Govt. of India | 2 | 2025-10-29 |
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
| Department of Financial Services (DoFS) | ANUP WADHAWAN | It. Secy / Jt. Secy | 2 | 2026-01 |
| Department of Financial Services (DoFS) | Arun Kumar Singh | Deputy Secretary (Coord. | 2 | 2026-01 |
| Department of Financial Services (DoFS) | Arvind Gaur AK Thakur CASH | Under Secretary Director | 2 | 2026-01 |
| Department of Financial Services (DoFS) | Arvind Gaur Surender Singh CASH | Under Secretary Director | 2 | 2026-01 |
| Department of Financial Services (DoFS) | Aut Couto | Under Secretary to the Government of India | 2 | 2026-10 |
| Department of Financial Services (DoFS) | DEBASISH PRUSTY | Addl. Secy | 2 | 2026-07 |
| Department of Financial Services (DoFS) | GIC Re | Joint Secretary, DFS | 2 |  |
| Department of Financial Services (DoFS) | JNANATOSH ROY | Under Secy | 2 |  |
| Department of Financial Services (DoFS) | N. RAMAN | Executive Director | 2 | 2026-01 |
| Department of Financial Services (DoFS) | P.K. MALHOTRA | Secy. to the Govt. of India. / Secy. to the Govt. of india. | 2 | 2026-01 |
| Department of Financial Services (DoFS) | PANKAJ SHARMA | Jt. Secy | 2 | 2026-01 |
| Department of Financial Services (DoFS) | RAJENDER SINGH | Under Secy | 2 |  |
| Department of Financial Services (DoFS) | VINOD KLTMAR | Under Secy | 2 |  |
| Department of Fisheries (DoF) | G.R.K. Rao | Assistant Commissioner (Fisheries | 2 | 2026-04-01 |
| Department of Fisheries (DoF) | S. Reshmi | Assistant Director (OL | 2 | 2022-06-09 |
| Department of Fisheries (DoF) | Shankar L | Joint Commissioner (Fisheries-APL / Joint Commissioner(Fisheries | 2 | 2025-12-08 |
| Department of Fisheries (DoF) | WEST BENGAL | Assistant Director , adfmarine.south24pgs@gm / Director of | 2 | 2026-04-01 |
| Department of Health Research (DHR) | Bhavani Shankara Bagepally | Scientist E, ICMR-NIE, Chennai | 2 | 2026-02-01 |
| Department of Health Research (DHR) | DHR-ICMR SECRETARIAT | Scientist F, DHR-ICMR | 2 | 2026-02-01 |
| Department of Health Research (DHR) | Priya Parmar | Director | 2 | 2026-02-01 |
| Department of Health Research (DHR) | Research Units | Director level person of | 2 | 2025-09-02 |
| Department of Health Research (DHR) | RICHA KHODA | Jt. Secy | 2 | 2026-06-23 |
| Department of Health and Family Welfare (DoHFW) | ARUN K. PANDA | Jt. Secy | 2 | 2026-05-21 |
| Department of Health and Family Welfare (DoHFW) | Educational Qualifications | Officer. | 2 | 2026-01-23 |
| Department of Health and Family Welfare (DoHFW) | Md Reyazuddin | Under Secretary of Governrnenl ol India / Under Secretary to the Govt' of India | 2 | 2026-10-08 |
| Department of Health and Family Welfare (DoHFW) | Nikhil Bhatnagar | Under Secr6iifut'tdYne Govt. of t"ndii / Under Secretary to the Govt. of India | 2 | 2026-05-11 |
| Department of Health and Family Welfare (DoHFW) | Nutan Topno | Under Secretary / Under Secretary to the Government of India | 2 | 2026-10-13 |
| Department of Health and Family Welfare (DoHFW) | Srikant Singh Kushwaha | Government of India' / Under Secretary to the Government of India. | 2 | 2026-10-21 |
| Department of Higher Education (DoHE) | ISHITA ROY | Jt. Secy | 2 | 2023-05-11 |
| Department of Higher Education (DoHE) | M. L. Soni | Officer | 2 | 2022-11-03 |
| Department of Higher Education (DoHE) | Nishant Upadhyaya | Under Secretary to the Governmenl of India / Under Secretary to the Govt.-of India | 2 | 2026-06-17 |
| Department of Higher Education (DoHE) | Rajani Saini | Officer | 2 | 2026-06-19 |
| Department of Higher Education (DoHE) | Rajive Kumar | SecretarY / Secretary | 2 | 2023-08-24 |
| Department of Higher Education (DoHE) | Rajnish Jain | Secretary | 2 | 2023-02-28 |
| Department of Justice (DoJ) | Jagannath Shinivasan | Joint Secretary to the Government of India | 2 | 2025-09-20 |
| Department of Justice (DoJ) | JagannatI Srinivasan | Joint Secretary to the Government of India | 2 | 2025-07-22 |
| Department of Land Resources (DLR) | Sushil Kumar Daila | Director (WM / Director(WM | 2 | 2023-01-24 |
| Department of Land Resources (DLR) | Th Lianbol | Under Secretary to the Government of:ndia / under sec「 eta:γ to the Government ofIndia | 2 | 2022-08-29 |
| Department of Legal Affairs (DoLA) | Asst. Legal | Adviser | 2 | 2026-06-03 |
| Department of Legal Affairs (DoLA) | Shweta Kambo | Under Secretary | 2 | 2025-08-11 |
| Department of Pension & Pensioner's Welfare (DoPPW) | D.K. Solanki | Under Secretary to the Government of India | 2 | 2014-05-07 |
| Department of Pension & Pensioner's Welfare (DoPPW) | Dhrubajyoti Sengupta | Joint Secretary to Government of India | 2 | 2026-01-09 |
| Department of Personnel and Training (DoPT) | Ajay Kumar Sinha | Under Secretary to the Government of India | 2 | 2026-09-15 |
| Department of Personnel and Training (DoPT) | BHASKAR KHULBE | Addl. Secy | 2 | 2014-09-08 |
| Department of Personnel and Training (DoPT) | George D. Toppo | Under Secretary to the Government of India | 2 | 2022-06-24 |
| Department of Personnel and Training (DoPT) | LaLt Kumar | Under Secretary to the Government of India | 2 | 2025-08-06 |
| Department of Personnel and Training (DoPT) | LOK RANJAN | Additional Secretary to the Government of India / Addl. Secy | 2 | 2019-10-24 |
| Department of Personnel and Training (DoPT) | Mukta Goel | Director (E.! / Director (E.!). | 2 | 2025-08-06 |
| Department of Personnel and Training (DoPT) | RASHMI CHOWDHARY | Addl. Secy / Addl.Secy | 2 | 2021-01-05 |
| Department of Personnel and Training (DoPT) | RITVIK PANDEY | Jt. Secy | 2 | 2023-06-16 |
| Department of Personnel and Training (DoPT) | S. Radha Chauhan | Secretary (P | 2 | 2023-05-04 |
| Department of Personnel and Training (DoPT) | SRINIVAS R. KATIKITHALA | Addl. Secy | 2 | 2020-03-02 |
| Department of Pharmaceuticals (DoPs) | Arvind Kumar | Under Secretary to the Govt. of India | 2 |  |
| Department of Public Enterprises (DPE) | CONCOR Shri Anurag Mathur | Executive Director (CSR) | 2 | 2018-12-10 |
| Department of Public Enterprises (DPE) | Insurance Companies | Secretary, Department of Public Enterprises, CGO | 2 | 2023-01-17 |
| Department of Public Enterprises (DPE) | K. C. GUPTA | Jt SecY | 2 | 2020-01-08 |
| Department of Public Enterprises (DPE) | Kailash Bhandari | Deputy Director / Joint Director | 2 | 2026-08-03 |
| Department of Public Enterprises (DPE) | P.K. Sinha | Deputy Secretary to the Government of India | 2 | 2025-09-15 |
| Department of Public Enterprises (DPE) | Pavanesh Kr Sharma | Deputy Secretary to the Government of India / Dy. Secretary to Govt of India | 2 | 2020-07-15 |
| Department of School Education and Literacy (DSEL) | Alok Jawahar | Under Secretary to the Government of India / Under Secretary to the Govt. of India | 2 | 2019-07-24 |
| Department of School Education and Literacy (DSEL) | KS. Mahajan | Under Secretary (Public Greivance) - . | 2 | 2016-10-25 |
| Department of School Education and Literacy (DSEL) | Kuldeep Meem | Under Secretary to the Go\,,t. of India | 2 | 2022-11-09 |
| Department of School Education and Literacy (DSEL) | MLC. Worthing | Deputy Secretary to the Government of India | 2 | 2019-03-01 |
| Department of School Education and Literacy (DSEL) | PSto HRM | Secretary, Deptt. of Higher Education | 2 | 2016-05-19 |
| Department of Science and Technology (DST) | Atin Singh Yadav | Under Secretary to the Govt. of India | 2 | 2026-02-10 |
| Department of Scientific and Industrial Research (DSIR) | Nitin Gupta | Under Secretary to the Govt of India : / Under Secretary to the Govt of India H | 2 | 2025-10-09 |
| Department of Social Justice and Empowerment (DoSJE) | Akash Patil | Director / Director, DAIC | 2 |  |
| Department of Social Justice and Empowerment (DoSJE) | D.P. Majhi | Director | 2 |  |
| Department of Social Justice and Empowerment (DoSJE) | Kishan Chand | Under Secretary to the Govt. of India | 2 |  |
| Department of Social Justice and Empowerment (DoSJE) | Prabhudas Xalxo | Deputy Secretary to Govt. of India | 2 |  |
| Department of Social Justice and Empowerment (DoSJE) | Vikas Trivedi | Director | 2 |  |
| Department of Telecommunications (DoT) | Amit Kundan | Under Secretary to the Government of India | 2 | 2026-10-16 |
| Department of Telecommunications (DoT) | Awadhesh Kumar Singh | Director (Electrical | 2 | 2026-09-22 |
| Department of Telecommunications (DoT) | Durgendra Singh Jadaun | Officer (A&P), | 2 | 2026-09-24 |
| Department of Telecommunications (DoT) | PRITINDER SINGH | Deptt. of Tetecom, Govt. of India / Officer | 2 | 2026-09-30 |
| Development of North Eastern Region (MDONER) | Harmeet Singh | Director | 2 | 2017-05-12 |
| Development of North Eastern Region (MDONER) | Rajesh Kumar | Director | 2 | 2012-07-02 |
| Earth Sciences (MoES) | Kailash Chand | Under Secretary to the Govt. of India | 2 | 2018-01-24 |
| Earth Sciences (MoES) | REETA VASISHTA | Secretary to the Govt. of India. | 2 | 2025-06-16 |
| Earth Sciences (MoES) | Tarun Sood | Officer (Genl. / Officer(Genl | 2 | 2025-06-20 |
| Electronics and Information Technology (MeitY) | RAJENDRA KUMAR | Addl. Secy | 2 | 2025-10-23 |
| Electronics and Information Technology (MeitY) | Saurabh Gaur | Joint Secretary to the Government of India / Jt. Secy | 2 | 2021-12-30 |
| Environment, Forest and Climate Change (MoEFCC) | AJAY TYAGI | Jt. Secy | 2 | 2021-10 |
| Environment, Forest and Climate Change (MoEFCC) | ARUN KUMAR MEH IA | Addl. Secy | 2 | 2017-11 |
| Environment, Forest and Climate Change (MoEFCC) | ARUN KUMAR MEHTA J | Secy | 2 | 2018-03 |
| Environment, Forest and Climate Change (MoEFCC) | ATUL KAUSHIK | Jt. Secy | 2 | 2018-03 |
| Environment, Forest and Climate Change (MoEFCC) | Lalit Bakolia | Director | 2 | 2021-08 |
| Environment, Forest and Climate Change (MoEFCC) | NAMEETA PRASAD | Jt. Secy | 2 |  |
| Environment, Forest and Climate Change (MoEFCC) | Prent Prakash Maurya | Under Secretary to the Government of India / Under Secretary to the Government of India ; | 2 |  |
| Environment, Forest and Climate Change (MoEFCC) | R. RAJAMANI | Secy | 2 | 2018-03 |
| Environment, Forest and Climate Change (MoEFCC) | Rajasekhar Ratti | Scientist ‘D’ | 2 | 2022-02 |
| Environment, Forest and Climate Change (MoEFCC) | Satish C. Garkoti | Scientist ‘G' | 2 | 2021-08 |
| Environment, Forest and Climate Change (MoEFCC) | SURJlT SINGH | Jt. Secy | 2 | 2018-03 |
| Environment, Forest and Climate Change (MoEFCC) | YASHVIR SINGH. Economic | Advisor | 2 | 2017-06 |
| External Affairs (MEA) | Kartik Pande | Director (ADP | 2 |  |
| External Affairs (MEA) | Krishan Kumar | Deputy Secretary to the Govt. of India | 2 |  |
| External Affairs (MEA) | Vipra Pandey | Under Secretary (Cadre) | 2 |  |
| Housing and Urban Affairs (MoHUA) | Lalit Kumar | Officer ( Admn.IV / Officer (Admn-IV | 2 | 2025-10-31 |
| Housing and Urban Affairs (MoHUA) | Manoj Kumar Jha | Under Secretary to the Government of India | 2 | 2025-10-31 |
| Housing and Urban Affairs (MoHUA) | R. Sathyanarayanan | Under Secretary to the Government of India | 2 | 2025-11-03 |
| Housing and Urban Affairs (MoHUA) | SANJAY KUMAR | Under Secy | 2 | 2026-04-08 |
| Information and Broadcasting (MIB) | Deepak Negi | Under Secretary (11S | 2 | 2026-05 |
| Information and Broadcasting (MIB) | Kshitij Aggarwal | Deputy Director / Deputy Director (DM | 2 | 2025-11 |
| Information and Broadcasting (MIB) | SANJIV SHANKAR | Jt. Secy / Jt.Secy | 2 | 2025-01 |
| Information and Broadcasting (MIB) | Santosh Kumar Ma | Under Secretary to the Govt. of India | 2 | 2026-10 |
| Labour and Employment (MoLE) | ALOK MISHRA | Jt. Secy | 2 | 2025-12-30 |
| Labour and Employment (MoLE) | Rajesh Kumar | Under Secretary to the Government of India | 2 | 2025-07-05 |
| Legislative Department (LD) | REETA VASISHTA | Secretary to the Govt. of India. | 2 | 2023-09-28 |
| Legislative Department (LD) | T.K. VISWANATHAN | Secy. to the Govt. of India. / Secy. to the Govt. of india. | 2 | 2025-10-30 |
| Micro, Small & Medium Enterprises (MSME) | Ajay Kumar | Deputy Secretary (LC | 2 | 2024-12-31 |
| Micro, Small & Medium Enterprises (MSME) | Bhaskar KaIra | Under Secretary to the Govt. of India | 2 | 2018-04-06 |
| Micro, Small & Medium Enterprises (MSME) | M AGAN LA L | Under Secretary | 2 | 2025-06-23 |
| Micro, Small & Medium Enterprises (MSME) | MAGAN LAL | Under Secretary | 2 | 2025-06-23 |
| Mines (MoM) | Dheeraj Kumar | Dy. Secretary to the Government of India | 2 |  |
| Mines (MoM) | EXPLORATION LICENCE | Director, | 2 |  |
| Mines (MoM) | NIRANJAN KUMAR SINGH | Jt. Secy | 2 |  |
| Minority Affairs (MoMA) | SHERSHA C SHAIK MOHIDDIN | Jt. Secy | 2 |  |
| New and Renewable Energy (MNRE) | ANKUR GUPTA | Principal Secretary to Government Haryana, / Principal Secretary to Govt. Haryana, | 2 | 2018-03-09 |
| New and Renewable Energy (MNRE) | DILIP NIGAM | Adviser (NSM / Director | 2 | 2017-06-19 |
| New and Renewable Energy (MNRE) | Divisional Heads | Officer, MNRE, New Delhi. | 2 | 2022-10-13 |
| New and Renewable Energy (MNRE) | JK Jethani | Scientist ‘F’ | 2 | 2024-11-28 |
| New and Renewable Energy (MNRE) | Monitoring Framework | Secretary, MNRE and other | 2 | 2024-07-04 |
| New and Renewable Energy (MNRE) | Regulatory Commissions | Secretary, MNRE, CGO Complex, New Delhi | 2 | 2023-04-10 |
| New and Renewable Energy (MNRE) | Suman Kumar | Under Secretary to the Govt. of India | 2 | 2025-09-08 |
| New and Renewable Energy (MNRE) | Ye Jha | Deputy Secretary to Govt. of India | 2 | 2025-02-13 |
| Parliamentary Affairs (MPA) | A Lana | Director to the Govt. of India | 2 | 2021-03-17 |
| Parliamentary Affairs (MPA) | Mukesh Bitton | Under Secretary to the Govt. of India | 2 | 2021-02-08 |
| Planning (MoP) | Aseem Kumar Jha | Secretary | 2 | 2026-06 |
| Planning (MoP) | Deo Nath Sah | Director | 2 | 2026-05 |
| Ports, Shipping and Waterways (MoPSW) | Dashrath Prasad | Director | 2 |  |
| Power | Anoop Singh Bisht | Deputy Secretary to the Government of India | 2 | 2025-07-02 |
| Power | Arun Kumar Singh | Under Secretary to the Government of India | 2 | 2025-06-28 |
| Power | Bihari Lal | Under Secretary flrans / Under Secretary to the Govt. of India | 2 | 2025-07-03 |
| Power | JYOTI ARORA | Jt. Secy | 2 | 2025-06-28 |
| Power | Manish Mishra | Director | 2 | 2026-03-27 |
| Power | N. Sriraman | Under Secretary to the Government of India | 2 | 2025-06-28 |
| Road Transport and Highways (MoRTH) | Bidur Kant Jha | Director | 2 |  |
| Road Transport and Highways (MoRTH) | CHETNA NAND SINGH | Jt. Secy | 2 |  |
| Road Transport and Highways (MoRTH) | Naveen. S | Director | 2 |  |
| Steel (MoS) | Addi. Industrial | Adviser | 2 | 2025-04 |
| Steel (MoS) | DALIP SINGH | Jt. Secy | 2 | 2025-04 |
| Steel (MoS) | SUDERSHAN MENDIRATTA | Jt. Secy | 2 | 2026-06 |
| Textiles (MoT) | Nitin Gupta | Under Secretary to the Govt of India | 2 | 2017-11-01 |
| Textiles (MoT) | Sr. Accounts | Officer(Admn) | 2 | 2024-06-10 |
| Tourism | Ajit Pal Singh | Director (North | 2 | 2025-08-04 |
| Tourism | Bharti Sharma | Deputy Director General | 2 | 2026-01-30 |
| Tourism | Manju Maan | Under Secretary (HRD | 2 | 2025-08-05 |
| Tourism | Praveen Kumar Singh | Undcr Secretar.v to the Govt. of India / Under Secretary to the Govt. of India | 2 | 2026-10-22 |
| Tourism | Sudeshna Ramkumar | Assistant Director General / Assistant Director General (M, P and IC | 2 | 2024-09-04 |
| Tourism | Uttank Joshi | Assistant Director General / Assistant Director General (SD | 2 | 2024-05-02 |

## Caveats

- A signature block is read heuristically from the last two pages of each PDF: a name line (often in parentheses) followed by a designation line. Scanned PDFs and Hindi-only signature blocks are not read (counted above).
- Matching is by name similarity with a bonus for the same ministry and a matching designation; `confidence` is `high` (near-exact name, same ministry), `medium`, or `low (name only, other ministry)`. Rosters are a snapshot (who's-who pages, igod, DoPT civil lists), so an officer who signed in 2022 may have moved since.
- 'Contact person for a topic' means *signed documents on that topic*, not a published point of contact. Topics are keyword buckets over subject line + title + site category; a document can fall in two buckets.
- Rows with `match_status=unmatched` in `notification_signatories.csv` are real signatories who are not in any roster — a useful list of people to add to the yellow pages.