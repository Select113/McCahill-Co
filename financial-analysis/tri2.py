import re, glob, os, json, subprocess
from collections import defaultdict
UP="/root/.claude/uploads/3f1b6957-210b-562a-bfd6-e032fdb5edf3"
PAT=re.compile(r"^\s*([A-Z][a-z]{2})\s+(\d{1,2})\s+([A-Z][a-z]{2})\s+(\d{1,2})\s+(.+?)\s{2,}(-?[\d,]+\.\d{2})(?:\s|$)")
ITEM=re.compile(r"^\d+\s{2,}")          # "1   MENS DAKOTA", "4    GC BLACK EARTH" = line-item detail
rows=[]; chk=[]
for f in sorted(glob.glob(os.path.join(UP,"*TriangleMastercard.pdf")), key=lambda p:re.search(r"(\d{8})T",p).group(1)):
    stmt=re.search(r"(\d{8})Triangle",f).group(1)
    txt=subprocess.run(["pdftotext","-layout",f,"-"],capture_output=True,text=True).stdout
    pur=re.search(r"Purchases\s+([\d,]+\.\d\d)\s*\n",txt)
    pay=re.search(r"Total payments received\s+-\$([\d,]+\.\d\d)",txt)
    stated=float(pur.group(1).replace(",","")) if pur else 0.0
    got=0.0; seen=set()
    for line in txt.split("\n"):
        m=PAT.match(line)
        if not m: continue
        d=m.group(5).strip(); a=float(m.group(6).replace(",",""))
        if "CTFS.COM/PAYMENTS" in d: continue
        if ITEM.match(d): continue
        if "INTEREST CHARGE" in d.upper(): continue
        if a<0: continue
        k=(m.group(1),m.group(2),d,a)
        if k in seen: continue
        seen.add(k)
        rows.append({"stmt":stmt,"desc":d,"amt":a}); got+=a
    chk.append((stmt, float(pay.group(1).replace(",","")) if pay else 0.0, stated, round(got,2), round(got-stated,2)))

print("VALIDATION — parsed purchases vs each statement's own stated total")
print(f"{'stmt':10}{'payments in':>13}{'stated purch':>14}{'parsed':>12}{'diff':>10}")
for s,pa,st,g,d in chk: print(f"{s:10}{pa:>13,.2f}{st:>14,.2f}{g:>12,.2f}{d:>10,.2f}")
tp=sum(c[1] for c in chk); ts=sum(c[2] for c in chk); tg=sum(c[3] for c in chk)
print(f"{'TOTAL':10}{tp:>13,.2f}{ts:>14,.2f}{tg:>12,.2f}{tg-ts:>10,.2f}")

print(f"\nCard payments made FROM the business account (per bank):        14,555.74")
print(f"Card payments made from elsewhere (personal):                  {tp-14555.74:>10,.2f}")

BUS=r"MACNUTT|PENINSULA LANDSCAPE|CDN TIRE|CANADIAN TIRE|SLEGG|HOME DEPOT|WINDSOR PLYWOOD|RONA|LORDCO|PRINCESS AUTO|BUCKERFIELD|WESTERN EQUIPMENT|SATINFLOWER|K2 STONE|RUSSELL NURSERY|PND |NURSER|STIHL|HUSQVARNA|KMS TOOLS|FITZS WALKER|INTEGRITY SALES|MARK'S|MARKS WORK|Prov of"
FUEL=r"PETRO-CANADA|SHELL|CHEVRON|ESSO|CO-OP|GAS\+|CHV\d"
PERS=r"THRIFTY|SAVE-ON|WALMART|COSTCO|SUPERSTORE|FAIRWAY|QUALITY FOODS|RED BARN|RESTAURANT|THAI|HOSPITALITY|NOURISH|NUBO|CAFE|COFFEE|STARBUCK|TIM HORTON|PUB|BREWING|SUSHI|PIZZA|MCDONALD|A&W|SUBWAY|WHITE SPOT|DOORDASH|SKIPTHE|UBER|APPLE\.COM|NETFLIX|SPOTIFY|AMAZON|BEST BUY|WINNERS|SPORT CHEK|LONDON DRUGS|LIQUOR|CINEPLEX|HOTEL"
def cat(d):
    if re.search(BUS,d,re.I):  return "Business — trade & supply"
    if re.search(FUEL,d,re.I): return "Fuel"
    if re.search(PERS,d,re.I): return "Personal"
    return "Unclassified"
agg=defaultdict(lambda:[0,0.0])
for r in rows:
    c=cat(r["desc"]); agg[c][0]+=1; agg[c][1]+=r["amt"]
tot=sum(v[1] for v in agg.values())
print(f"\nWHAT THE CARD WAS SPENT ON  (Jan 19 – Aug 18, 2026)")
print(f"{'category':30}{'n':>5}{'amount':>13}{'share':>8}")
for k in sorted(agg,key=lambda x:-agg[x][1]):
    n,a=agg[k]; print(f"{k:30}{n:>5}{a:>13,.2f}{a/tot*100:>7.1f}%")
print(f"{'TOTAL':30}{len(rows):>5}{tot:>13,.2f}")

print(f"\nUNCLASSIFIED LINES (need your answer)")
for r in sorted([r for r in rows if cat(r["desc"])=="Unclassified"],key=lambda x:-x["amt"]):
    print(f"  {r['stmt']}  {r['desc'][:52]:52}{r['amt']:>10,.2f}")
print(f"\nPERSONAL LINES")
for r in sorted([r for r in rows if cat(r["desc"])=="Personal"],key=lambda x:-x["amt"]):
    print(f"  {r['stmt']}  {r['desc'][:52]:52}{r['amt']:>10,.2f}")
json.dump(rows,open("triangle.json","w"),indent=0)
