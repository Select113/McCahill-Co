#!/usr/bin/env python3
"""Parse McCahill & Co invoice PDFs -> per-invoice labour vs non-labour split.
Run: python3 parse_invoices.py <invoice_dir>
Dedupes by invoice number, classifies each line item, writes invoices_parsed.csv.
"""
import re, glob, os, sys, csv, subprocess
from collections import defaultdict

INV_DIR = sys.argv[1] if len(sys.argv)>1 else "/tmp/invoices"

# --- classification (PROPOSED defaults; deposits & blended flagged for review) ---
LABOUR = {"Labour", "Kyle’s labour", "Kyle's labour",
          "Monthly Maintenance", "Property Maintenance"}
DEPOSIT = {"2026 Project Deposit"}
# everything else -> non-labour (materials / subcontractor / extras), 50% bucket
BLENDED = {"Lighting Installation", "May Project"}   # supply+install, flagged
EXTRAS  = {"Warranty", "Miscellaneous", "Irrigation quote", "Debris Hauling",
           "Equipment Rentals", "Power Rake Rental", "Lawn Roller"}

EXCLUSIVE = {"Christine", "Ian & Judy", "Muriel", "Anita", "Justin"}

amount_re = re.compile(r'^(.*?)\s+([\d.]+)\s+\$([\d,]+\.\d{2})\s+\$\(?([\d,]+\.\d{2})\)?$')
def num(s): return float(s.replace(',',''))

def text(f):
    return subprocess.run(["pdftotext","-layout",f,"-"],capture_output=True,text=True).stdout

# dedupe by invoice number
files={}
for f in glob.glob(os.path.join(INV_DIR,"Invoice_*.pdf")):
    n=int(re.search(r'Invoice_(\d+)_',os.path.basename(f)).group(1))
    files.setdefault(n,f)   # first file wins (dupes are identical)

rows=[]
for n in sorted(files):
    f=files[n]; txt=text(f); lines=txt.splitlines()
    # customer = first non-empty line after BILL TO
    cust=""
    for i,l in enumerate(lines):
        if l.strip().startswith("BILL TO"):
            for j in range(i+1,i+4):
                cand=lines[j].split("  ")[0].strip()
                if cand: cust=cand; break
            break
    mdate=re.search(r'Invoice Date:\s*([A-Za-z]+ \d+, \d{4})',txt)
    date=mdate.group(1) if mdate else ""
    lab=nonlab=dep=0.0
    cats=defaultdict(float)
    for l in lines:
        s=l.strip()
        m=amount_re.match(s)
        if not m: continue
        label=m.group(1).strip(); amt=num(m.group(4))
        if label.lower().startswith(('subtotal','gst','total','payment','amount due')): continue
        cats[label]+=amt
        if label in DEPOSIT: dep+=amt
        elif label in LABOUR: lab+=amt
        else: nonlab+=amt
    mg=re.search(r'GST 5%[^\$]*\$([\d,]+\.\d{2})',txt)
    gst=num(mg.group(1)) if mg else 0.0
    mt=re.search(r'Total:\s*\$([\d,]+\.\d{2})',txt)
    total=num(mt.group(1)) if mt else 0.0
    rows.append(dict(num=n,date=date,customer=cust,
                     labour=round(lab,2),nonlabour=round(nonlab,2),deposit=round(dep,2),
                     gst=gst,total=total,
                     exclusive=("yes" if cust in EXCLUSIVE else "no")))

with open("/tmp/invoices_parsed.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["num","date","customer","exclusive","labour","nonlabour","deposit","gst","total"])
    w.writeheader(); w.writerows(rows)

tl=sum(r['labour'] for r in rows); tn=sum(r['nonlabour'] for r in rows)
td=sum(r['deposit'] for r in rows); tg=sum(r['gst'] for r in rows); tt=sum(r['total'] for r in rows)
print(f"Invoices parsed (deduped): {len(rows)}")
print(f"{'Labour billed':<22}{tl:>14,.2f}")
print(f"{'Non-labour billed':<22}{tn:>14,.2f}")
print(f"{'Deposits (flagged)':<22}{td:>14,.2f}")
print(f"{'GST':<22}{tg:>14,.2f}")
print(f"{'Sum of invoice totals':<22}{tt:>14,.2f}")
print(f"{'check labour+nonlab+dep+gst':<28}{tl+tn+td+tg:>14,.2f}")
