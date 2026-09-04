from collections import defaultdict
# corporation unpaid, from the tracker red cells
JUL=[("Trudy",10822.02,1),("Stratta",1764.00,1),("Ramsay",1200.00,1),("Stephanie",735.00,1),
     ("Jenica",682.50,1),("Carol Ann",567.00,0),("Bill",378.00,1),("Justin",367.50,1),
     ("Madeline",294.00,1),("Josh",252.00,1),("Judy",183.00,1),("Laurie (Norris)",63.00,1)]
AUG=[("Trudy",8190.00,1),("Trudy — irrigation",7854.00,1),("Trudy — tree trimming",6772.50,1),
     ("Stratta",1764.00,1),("Justin — wall project",1434.22,1),("Anita",960.00,0),
     ("Linda",819.00,0),("Stephanie",661.50,1),("Jenica",656.25,1),("Ramsay",600.00,1),
     ("Sen",540.00,0),("Josh",480.00,0),("Teresa",480.00,0),("Madeline",483.00,1),
     ("Fil",425.25,0),("Andrei",384.30,1),("Sen ",378.00,0),("Justin",346.50,1),
     ("Bill",252.00,1),("Judy",220.50,1)]
def base(n): return n.split(" —")[0].strip()
cli=defaultdict(lambda:{"jul":0.0,"aug":0.0,"sent":True})
for n,a,s in JUL:
    cli[base(n)]["jul"]+=a
    if not s: cli[base(n)]["sent"]=False
for n,a,s in AUG:
    cli[base(n)]["aug"]+=a
    if not s: cli[base(n)]["sent"]=False
tot=sum(v["jul"]+v["aug"] for v in cli.values())
print("="*92); print("CORPORATE RECEIVABLE BY CLIENT — $51,009.04 outstanding at Sept 4"); print("="*92)
print(f"{'client':22}{'July (66+ days)':>17}{'August (35+ days)':>19}{'total':>12}{'share':>8}  invoice sent?")
run=0
for k,v in sorted(cli.items(), key=lambda x:-(x[1]['jul']+x[1]['aug'])):
    t=v["jul"]+v["aug"]; run+=t
    print(f"{k:22}{v['jul']:>17,.2f}{v['aug']:>19,.2f}{t:>12,.2f}{t/tot*100:>7.1f}%  {'yes' if v['sent'] else 'NO — NEVER SENT'}")
print("-"*92)
print(f"{'TOTAL':22}{sum(v['jul'] for v in cli.values()):>17,.2f}{sum(v['aug'] for v in cli.values()):>19,.2f}{tot:>12,.2f}")

print("\n"+"="*92); print("CONCENTRATION"); print("="*92)
tr=cli["Trudy"]["jul"]+cli["Trudy"]["aug"]
print(f"  Trudy alone                                    {tr:>12,.2f}   {tr/tot*100:.1f}% of everything owed")
top3=sorted((v['jul']+v['aug'] for v in cli.values()),reverse=True)[:3]
print(f"  Top 3 clients                                  {sum(top3):>12,.2f}   {sum(top3)/tot*100:.1f}%")
print(f"  Everyone else combined ({len(cli)-3} clients)          {tot-sum(top3):>12,.2f}   {(tot-sum(top3))/tot*100:.1f}%")

ns=sum(v["jul"]+v["aug"] for v in cli.values() if not v["sent"])
print(f"\n  Never invoiced at all                          {ns:>12,.2f}   cannot be collected until sent")
print(f"  Invoiced and simply unpaid                     {tot-ns:>12,.2f}")

print("\n"+"="*92); print("AGEING AT SEPT 4"); print("="*92)
j=sum(v['jul'] for v in cli.values()); a=sum(v['aug'] for v in cli.values())
print(f"  July work, billed ~Aug 1   — now ~35 days past due   {j:>12,.2f}")
print(f"  August work, billed ~Sep 1 — just becoming due       {a:>12,.2f}")
print(f"\n  Genuinely overdue right now:                        {j:>12,.2f}")
print(f"  Of which Trudy:                                     {cli['Trudy']['jul']:>12,.2f}")

print("\n"+"="*92); print("ALSO OUTSTANDING — SOLE PROP (older, Feb-Jun)"); print("="*92)
sp=[("Teresa / Invoice #40 — disputed",15500.00),("Anita — project walkway",3675.00),
    ("Trudy — French Drain remainder",3500.00),("Stratta — mulching",2913.75),
    ("Stratta",1764.00),("Josh (4 cycles)",1367.50),("Jenica",240.00),("Bill",236.00),
    ("Andrei",210.00),("Sen",189.00)]
for n,v in sp: print(f"  {n:48}{v:>12,.2f}")
print(f"  {'SOLE PROP TOTAL':48}{sum(v for _,v in sp):>12,.2f}")
print(f"\n  GRAND TOTAL OWED                                {tot+sum(v for _,v in sp):>12,.2f}")
