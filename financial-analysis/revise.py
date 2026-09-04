W=94
print("="*W); print("WHAT YOUR ANSWERS CHANGED"); print("="*W)
print("\n1. RECLASSIFIED AS DEDUCTIBLE SUBCONTRACT / PROFIT SHARE (Canopyco relationship)")
rc=[("Canopyco (Ryan Roberts' company)",15250.00,"was: unidentified transfer"),
    ("Ryan Roberts — subcontractor bill, French Drain",10000.00,"was: unidentified transfer"),
    ("Michelle — subcontract work",5175.00,"was: unclassified labour (already expensed)")]
for n,a,w in rc: print(f"   {n:48}{a:>11,.2f}   {w}")
NEW_DED = 15250.00+10000.00     # Michelle was already inside operating profit
print(f"   {'NEW deductible expense not previously counted':48}{NEW_DED:>11,.2f}")

print("\n2. BOOKER RECLASSIFIED FROM UNKNOWN TO EMPLOYEE")
print(f"   {'Booker — wages paid by e-transfer':48}{7791.44:>11,.2f}   now payroll, was unclassified")
print(f"   {'Booker — AMEX supplementary card charges':48}{1303.03:>11,.2f}   confirmed deductible")

print("\n3. BEST BUY CONFIRMED BUSINESS")
print(f"   {'Work computer + office supplies':48}{2514.98:>11,.2f}   capital asset, not an expense")

print("\n4. SUBCONTRACTORS / CASUAL LABOUR CONFIRMED")
subs=[("Isayas",1528.40),("Kevin",1250.00),("Declan",533.33),("Patrick Wong",312.37),
      ("Ryan (small payments)",300.00),("Liam Manchester",139.93),("Graham",74.49)]
for n,a in subs: print(f"   {n:48}{a:>11,.2f}")
S=sum(a for _,a in subs); print(f"   {'subtotal':48}{S:>11,.2f}")

print("\n"+"="*W); print("REVISED PAYROLL EXPOSURE — two employees, not one"); print("="*W)
K=15276.03; B=7791.44; EX=3500.0
cppK=max(0,K-EX)*0.0595*2; cppB=max(0,B-EX)*0.0595*2
gross=K+B
ei=gross*0.0164*2.4; tax=gross*0.12
sub=cppK+cppB+ei+tax; pen=sub*0.10
print(f"   Kierran, gross paid                              {K:>11,.2f}")
print(f"   Booker, gross paid                               {B:>11,.2f}")
print(f"   Total gross wages                                {gross:>11,.2f}")
print(f"   CPP employee+employer (exemption each)           {cppK+cppB:>11,.2f}")
print(f"   EI employee+employer                             {ei:>11,.2f}")
print(f"   Income tax that should have been withheld        {tax:>11,.2f}")
print(f"   Penalty at 10%                                   {pen:>11,.2f}")
print(f"   REVISED PAYROLL EXPOSURE                         {sub+pen:>11,.2f}   (was 4,557.87)")
PAYL=sub+pen

print("\n"+"="*W); print("REVISED SOLE PROP PROFIT AND TAX"); print("="*W)
prof=109359.48
bestbuy_addback = 2514.98 - 692.00      # capital; only ~27.5% CCA deductible in year 1
pers_cards = 1336.95                     # personal card spend after Best Buy reclassified
newprof = prof - NEW_DED + bestbuy_addback + pers_cards*0.75
print(f"   Previously reported cash operating profit        {prof:>11,.2f}")
print(f"   Less Canopyco + Ryan Roberts, now deductible     {-NEW_DED:>11,.2f}")
print(f"   Add back Best Buy (capital, CCA ~$692 yr 1)      {bestbuy_addback:>11,.2f}")
print(f"   Add back personal card spend (non-deductible)    {pers_cards*0.75:>11,.2f}")
print(f"   REVISED SOLE PROP PROFIT                         {newprof:>11,.2f}   (was 109,359.48)")
for r in (0.25,0.30,0.35):
    print(f"   Personal tax reserve at {int(r*100)}%                       {newprof*r:>11,.2f}")

print("\n"+"="*W); print("REVISED GST"); print("="*W)
col=11300.66; i1=1404.66; i2=828.92; i3=809.62
bb=2514.98/1.05*0.05
print(f"   GST collected                                    {col:>11,.2f}")
print(f"   ITC — suppliers / Triangle / AMEX                {-(i1+i2+i3):>11,.2f}")
print(f"   ITC — Best Buy now confirmed business            {-bb:>11,.2f}")
net=col-i1-i2-i3-bb
print(f"   NET GST OWING                                    {net:>11,.2f}   (was 8,257.45)")
print(f"\n   NOT included: if Canopyco/Ryan is GST-registered and charged GST on the")
print(f"   $30,425 of profit share and subcontract, that is a further ITC of ~{30425/1.05*0.05:,.2f}")

print("\n"+"="*W); print("REVISED CRA POSITION"); print("="*W)
taxres=newprof*0.30
tot=net+PAYL+taxres
cash=99267.26; opexm=14220.47
print(f"   Net GST owing                                    {net:>11,.2f}")
print(f"   Payroll remittance + penalty (2 employees)       {PAYL:>11,.2f}")
print(f"   Personal tax on sole prop profit at 30%          {taxres:>11,.2f}")
print(f"   TOTAL CRA OBLIGATION                             {tot:>11,.2f}   (was 44,829.74)")
print(f"\n   Business cash                                    {cash:>11,.2f}")
print(f"   Cash after CRA                                   {cash-tot:>11,.2f}   (was 54,437.52)")
print(f"   Three-month operating reserve                    {opexm*3:>11,.2f}")
print(f"   DEPLOYABLE CAPITAL                               {max(0,cash-tot-opexm*3):>11,.2f}   (was 11,776.11)")
