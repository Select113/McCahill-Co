import csv, glob, os, json, re
from datetime import datetime
from collections import defaultdict
UP="/root/.claude/uploads/3f1b6957-210b-562a-bfd6-e032fdb5edf3"
rows=[]; seen=set()
for f in glob.glob(os.path.join(UP,"*activity*.csv")):
    with open(f,newline="",encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            d=datetime.strptime(r["Date"].strip(),"%d %b %Y").date()
            desc=re.sub(r"\s{2,}"," ",r["Description"].strip())
            amt=float(r["Amount"])
            k=(d,desc,amt,r["Card Member"].strip(),r["Account #"].strip())
            if k in seen: continue
            seen.add(k)
            rows.append({"date":d,"desc":desc,"amt":amt,"who":r["Card Member"].strip(),
                         "acct":r["Account #"].strip()})
rows.sort(key=lambda r:r["date"])
print(f"AMEX — {len(rows)} unique lines   {rows[0]['date']} to {rows[-1]['date']}")

pays=[r for r in rows if "PAYMENT RECEIVED" in r["desc"]]
credits=[r for r in rows if r["amt"]<0 and "PAYMENT RECEIVED" not in r["desc"]]
charges=[r for r in rows if r["amt"]>0]
print(f"\nPayments to the card : {len(pays):>3}  ${-sum(r['amt'] for r in pays):>12,.2f}")
print(f"Refunds / credits    : {len(credits):>3}  ${-sum(r['amt'] for r in credits):>12,.2f}")
print(f"Charges              : {len(charges):>3}  ${sum(r['amt'] for r in charges):>12,.2f}")
print(f"NET CHARGES          :      ${sum(r['amt'] for r in charges)+sum(r['amt'] for r in credits):>12,.2f}")

print("\nPAYMENTS vs the bank (business account paid AMEX $21,441.14 in 8 payments)")
for r in pays: print(f"  {r['date']}  {-r['amt']:>10,.2f}")

print("\nCARDHOLDERS")
byw=defaultdict(lambda:[0,0.0])
for r in rows:
    if r["amt"]>0: byw[(r["who"],r["acct"])][0]+=1; byw[(r["who"],r["acct"])][1]+=r["amt"]
for k,v in sorted(byw.items(),key=lambda x:-x[1][1]):
    print(f"  {k[0]:20} acct {k[1]:8} {v[0]:>4} charges  ${v[1]:>11,.2f}")

BUS = {
 "Materials & plants": r"ISLAND VIEW NURSERY|RUSSELL NURSERY|SATINFLOWERNUR|LS PATIO GARDENS|VICTORIA LANDSCAPE GRAV|T MARTIN & SON|K2 STONE|PND",
 "Building & hardware": r"HOME DEPOT|SOOKE HOME HARDWARE|CANADIAN TIRE|CDN TIRE|SLEGG|WINDSOR PLYWOOD|RONA",
 "Equipment & rental": r"SAANICH RENTALS|SOOKE TOOLS|WESTERN EQUIPMENT|KMS TOOLS|FITZS WALKER|STIHL|HUSQVARNA",
 "Fuel":               r"PENINSULA CO-OP|OLDFIELD'S SAVE ON GAS|PETRO-CANADA|SHELL|CHEVRON|CHV\d|ESSO|MALAHAT CENTEX|7-ELEVEN",
 "Lawn care (Weedman)": r"WEEDMAN",
 "Workwear":           r"MARK'S",
 "Software & web":     r"GOOGLE|CANVA|SQSP|SQUARESPACE|WAVE PRO|ANTHROPIC|MICROSOFT|ADOBE",
 "Recruitment & ads":  r"INDEED|BARK\.COM|ONLINE JOB ADS",
 "WorkSafeBC":         r"WORKSAFEBC",
 "Card fees":          r"SUPPLEMENTARY CARD FEE|ANNUAL FEE|INTEREST",
}
PERS = r"DOMINOS|MUCHO BURRITO|PEPPER'S FOOD|UBER TRIP|BEST BUY"
def cat(d):
    for name,pat in BUS.items():
        if re.search(pat,d,re.I): return name
    if re.search(PERS,d,re.I): return "Personal / mixed — REVIEW"
    return "Unclassified"
for r in rows: r["cat"]=cat(r["desc"])

agg=defaultdict(lambda:[0,0.0])
for r in rows:
    if r["amt"]>0 or (r["amt"]<0 and "PAYMENT RECEIVED" not in r["desc"]):
        agg[r["cat"]][0]+=1; agg[r["cat"]][1]+=r["amt"]
tot=sum(v[1] for v in agg.values())
print(f"\nWHAT THE AMEX WAS SPENT ON  (net of refunds)")
print(f"{'category':30}{'n':>5}{'amount':>13}{'share':>8}")
for k in sorted(agg,key=lambda x:-agg[x][1]):
    n,a=agg[k]; print(f"{k:30}{n:>5}{a:>13,.2f}{a/tot*100:>7.1f}%")
print(f"{'TOTAL':30}{sum(v[0] for v in agg.values()):>5}{tot:>13,.2f}")

print("\nMERCHANTS over $100")
mer=defaultdict(lambda:[0,0.0])
for r in rows:
    if "PAYMENT RECEIVED" in r["desc"]: continue
    k=re.sub(r"\s+(VICTORIA|SAANICHTON|SOOKE|SIDNEY|NORTH SAANICH|DEEP COVE|LANGFORD|TORONTO|DELTA|AUSTIN|NEW YORK|DUBLIN|LONDON|RICHMOND|SAANICH|SAN FRANCISCO).*$","",r["desc"]).strip()
    k=re.sub(r"\s*[#*]?\s*\d{4,}.*$","",k).strip()
    mer[k][0]+=1; mer[k][1]+=r["amt"]
for k in sorted(mer,key=lambda x:-mer[x][1]):
    n,a=mer[k]
    if abs(a)>=100: print(f"  {k[:44]:44}{n:>4}{a:>11,.2f}   {cat(k)}")

print("\nEVERY LINE NEEDING A DECISION (personal/mixed + unclassified)")
for r in rows:
    if r["cat"] in ("Personal / mixed — REVIEW","Unclassified") and "PAYMENT RECEIVED" not in r["desc"]:
        print(f"  {r['date']}  {r['desc'][:46]:46}{r['amt']:>10,.2f}  {r['who'][:14]}")
json.dump([{**r,"date":r["date"].isoformat()} for r in rows],open("amex.json","w"),indent=0)
