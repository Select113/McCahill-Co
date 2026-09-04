import csv, glob, re, os, json
from datetime import datetime, date
from collections import defaultdict
UP = "/root/.claude/uploads/3f1b6957-210b-562a-bfd6-e032fdb5edf3"

def money(s):
    s = s.strip().replace("$","").replace(",","")
    neg = s.startswith("-"); s = s.lstrip("-")
    return (-1 if neg else 1)*float(s or 0)

ACCT = defaultdict(list)
for p in glob.glob(os.path.join(UP,"*.csv")):
    m = re.search(r"_(\d{9})_(\d{2})(\d{4})\.csv", p)
    ACCT[m.group(1)].append((m.group(3)+m.group(2), p))

TX = []
for acct, lst in ACCT.items():
    for _, p in sorted(lst):
        with open(p, newline="", encoding="utf-8-sig") as fh:
            for rec in csv.DictReader(fh):
                TX.append({"acct": acct,
                           "date": datetime.strptime(rec["Transfer date"], "%m/%d/%Y").date(),
                           "desc": rec["Description"].replace("&amp;amp;","&").replace("&amp;","&").strip(),
                           "amt": money(rec["Amount"]), "bal": money(rec["Balance"])})

CLIENTS = {"CAROL-ANN SAARI","CAROL ANN SAARI","PACIFIC CITY DEVELOPMENTS INC.","Robert Niven",
 "Ramsay P Attisha","Mark A","ANITA FLEICE","WILLIAM SANDERSON","CHRISTINE ADKINS","DAVID ROBIN GREEN",
 "Filomena Giulione","DAVID C NEWSOME","BRUCE D REID","BEVERLY DEVRIES","Andrei Moldoveanu","JUSTIN TSE",
 "YUHUAN BAI","WEI ZHAO","LAURIE IRWIN","John Woods","LYNN KATHLEEN MARINI","CHRISTINE ADRIENNE SCHWARTZ"}
SUPPLIERS = {"K2 Stone","PND GRAVEL MART","PND","GC Excavation","Myles (YGGDRASIL HORTICUL","Dean (black box)"}
CREWISH   = {"Kierran Kivinen","Isayas","Kevin","Declan","Patrick Wong","Ryan","Liam Manchester","Graham","Michelle"}
CARDS     = {"AMEX BILL PYMT","Canadian Tire Bank"}

def party(d):
    d = re.sub(r"^Interac e-Transfer (received from|sent to|cancelled)\s*","",d)
    d = re.sub(r"^Auto-withdrawal by\s*","",d)
    return d.strip()

def classify(r):
    p, a, d = party(r["desc"]), r["amt"], r["desc"]
    if d.startswith("Mobile cheque deposit"):
        return ("Revenue — cheque", "Revenue") if a > 0 else ("Returned/NSF cheque", "Revenue")
    if p == "Interest received":            return ("Interest income", "Other Income")
    if p == "KYLE JOHN BENJAMIN MCCAHILL":  return ("Owner capital contributed", "Financing")
    if p == "Kyle (Personal Account)":      return ("Owner draw to personal", "Owner Draw/Comp")
    if p == "Canopyco":                     return ("? Canopyco — UNIDENTIFIED", "Review")
    if p == "MCCAHILL & CO.":               return ("? McCahill & Co. inbound — UNIDENTIFIED", "Review")
    if p == "Ryan Roberts (Personal Ac":    return ("? Ryan Roberts — UNIDENTIFIED", "Review")
    if p in CARDS:                          return (f"Credit card payment — {p}", "Card Payment")
    if p == "Gore Mutual":                  return ("Insurance", "Operating Expense")
    if p == "Wave PYRL":                    return ("Payroll (via Wave)", "Payroll")
    if p == "Kierran Kivinen":              return ("Crew pay — Kierran", "Payroll")
    if p in CREWISH:                        return (f"? Crew or sub — {p}", "Labour-Unclear")
    if p in SUPPLIERS:                      return (f"Supplier — {p}", "COGS")
    if p == "Booker, Daniel":               return ("? Booker, Daniel — UNIDENTIFIED", "Labour-Unclear")
    if p in CLIENTS:                        return ("Revenue — e-transfer", "Revenue")
    return (f"? {p}", "Review")

for r in TX:
    r["label"], r["type"] = classify(r)

SP_END = date(2026,6,30)
def period(r):
    if r["acct"] == "400190507": return "CORP-ACCT"
    return "SP (Feb-Jun)" if r["date"] <= SP_END else "JUL-AUG (sole prop acct)"

for r in TX: r["period"] = period(r)

print("="*104)
print("CASH BY PERIOD AND CATEGORY  —  natural signs, money in positive")
print("="*104)
periods = ["SP (Feb-Jun)", "JUL-AUG (sole prop acct)", "CORP-ACCT"]
types = ["Revenue","Other Income","COGS","Labour-Unclear","Payroll","Operating Expense",
         "Card Payment","Owner Draw/Comp","Financing","Review"]
grid = defaultdict(float); cnt = defaultdict(int)
for r in TX:
    grid[(r["period"], r["type"])] += r["amt"]; cnt[(r["period"], r["type"])] += 1
print(f"{'category':26}" + "".join(f"{p:>26}" for p in periods) + f"{'TOTAL':>16}")
for t in types:
    row = f"{t:26}"
    tot = 0
    for p in periods:
        v = grid[(p,t)]; tot += v
        row += f"{v:>18,.2f}{('('+str(cnt[(p,t)])+')'):>8}"
    row += f"{tot:>16,.2f}"
    print(row)
print("-"*104)
row = f"{'NET MOVEMENT':26}"; g=0
for p in periods:
    v = sum(grid[(p,t)] for t in types); g += v
    row += f"{v:>18,.2f}{'':>8}"
print(row + f"{g:>16,.2f}")

print("\n" + "="*104)
print("CLOSING CASH")
print("="*104)
for acct in sorted(ACCT):
    rows = [r for r in TX if r["acct"]==acct]
    print(f"  account {acct}: ${rows[-1]['bal']:,.2f}  ({rows[0]['date']} to {rows[-1]['date']})")
tot = sum([r for r in TX if r["acct"]==a][-1]["bal"] for a in ACCT)
print(f"  TOTAL BUSINESS CASH AT AUG 31, 2026: ${tot:,.2f}")

print("\n" + "="*104)
print("UNIDENTIFIED / REVIEW ITEMS — every transaction, nothing summarised away")
print("="*104)
rev = [r for r in TX if r["type"] in ("Review","Labour-Unclear")]
byp = defaultdict(lambda: {"n":0,"net":0.0,"items":[]})
for r in rev:
    k = r["label"]
    byp[k]["n"] += 1; byp[k]["net"] += r["amt"]
    byp[k]["items"].append((r["date"], r["amt"]))
for k in sorted(byp, key=lambda x: -abs(byp[x]["net"])):
    v = byp[k]
    print(f"\n{k}   [{v['n']} txns, net ${v['net']:,.2f}]")
    print("   " + "  ".join(f"{d.strftime('%b%d')}:{a:,.0f}" for d,a in v["items"]))

json.dump([{**r,"date":r["date"].isoformat()} for r in TX], open("tx.json","w"), indent=0)
print(f"\n\nwrote tx.json  ({len(TX)} transactions)")
