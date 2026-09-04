import csv, glob, re, os
from datetime import datetime
from collections import defaultdict
UP = "/root/.claude/uploads/3f1b6957-210b-562a-bfd6-e032fdb5edf3"

def money(s):
    s = s.strip().replace("$","").replace(",","")
    neg = s.startswith("-"); s = s.lstrip("-")
    return (-1 if neg else 1)*float(s or 0)

ACCT = {}
for p in glob.glob(os.path.join(UP,"*.csv")):
    m = re.search(r"_(\d{9})_(\d{2})(\d{4})\.csv", p)
    acct, mm, yy = m.group(1), m.group(2), m.group(3)
    ACCT.setdefault(acct, []).append((yy+mm, p))

data = {}
for acct, lst in ACCT.items():
    rows = []
    for _, p in sorted(lst):
        with open(p, newline="", encoding="utf-8-sig") as fh:
            for rec in csv.DictReader(fh):
                rows.append({"date": datetime.strptime(rec["Transfer date"], "%m/%d/%Y").date(),
                             "desc": rec["Description"].replace("&amp;amp;","&").replace("&amp;","&").strip(),
                             "amt": money(rec["Amount"]), "bal": money(rec["Balance"])})
    data[acct] = rows
    run = 0.0; bad = 0
    for r in rows:
        run = round(run+r["amt"],2)
        if abs(run-r["bal"])>0.005: bad += 1; run = r["bal"]
    print(f"ACCOUNT {acct}: {len(rows)} txns  {rows[0]['date']} -> {rows[-1]['date']}  "
          f"opening $0.00  closing ${rows[-1]['bal']:,.2f}  chain breaks: {bad}")

print("\n" + "="*100)
print("COUNTERPARTY SUMMARY — sole prop account 400101914")
print("="*100)
rows = data["400101914"]

def party(d):
    d = re.sub(r"^Interac e-Transfer (received from|sent to|cancelled)\s*", "", d)
    d = re.sub(r"^Auto-withdrawal by\s*", "", d)
    return d.strip()

agg = defaultdict(lambda: {"n":0,"in":0.0,"out":0.0})
for r in rows:
    k = party(r["desc"])
    agg[k]["n"] += 1
    agg[k]["in" if r["amt"]>0 else "out"] += r["amt"]
print(f"{'counterparty':46} {'n':>3} {'money in':>13} {'money out':>13} {'net':>13}")
for k in sorted(agg, key=lambda x: -(abs(agg[x]['in'])+abs(agg[x]['out']))):
    v = agg[k]
    print(f"{k[:46]:46} {v['n']:>3} {v['in']:>13,.2f} {v['out']:>13,.2f} {v['in']+v['out']:>13,.2f}")
