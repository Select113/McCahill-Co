import json
from datetime import date
from collections import defaultdict
TX = json.load(open("tx.json"))
for r in TX: r["date"] = date.fromisoformat(r["date"])
G = 1.05

def s(pred): return sum(r["amt"] for r in TX if pred(r))
SP  = lambda r: r["acct"]=="400101914" and r["date"] <= date(2026,6,30)
JA  = lambda r: r["acct"]=="400101914" and r["date"] >  date(2026,6,30)
CO  = lambda r: r["acct"]=="400190507"
def T(t): return lambda r: r["type"]==t

print("="*92); print("MONTH BY MONTH — sole prop account 400101914 + corporate account 400190507"); print("="*92)
print(f"{'month':9}{'revenue':>12}{'COGS':>11}{'labour?':>10}{'payroll':>10}{'cards':>11}{'draws':>11}{'other':>10}{'net':>12}{'closing':>12}")
months = sorted({(r['date'].year, r['date'].month) for r in TX})
NAMES = {2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug'}
rowsout=[]
for y,m in months:
    inm = lambda r: r["date"].year==y and r["date"].month==m
    rev = s(lambda r: inm(r) and r["type"] in ("Revenue","Other Income"))
    cog = s(lambda r: inm(r) and r["type"]=="COGS")
    lab = s(lambda r: inm(r) and r["type"]=="Labour-Unclear")
    pay = s(lambda r: inm(r) and r["type"]=="Payroll")
    crd = s(lambda r: inm(r) and r["type"]=="Card Payment")
    drw = s(lambda r: inm(r) and r["type"]=="Owner Draw/Comp")
    oth = s(lambda r: inm(r) and r["type"] in ("Operating Expense","Financing","Review"))
    net = rev+cog+lab+pay+crd+drw+oth
    close = [r for r in TX if r["date"].year==y and r["date"].month==m][-1]["bal"]
    sp = [r for r in TX if r["acct"]=="400101914" and r["date"].year==y and r["date"].month==m]
    co = [r for r in TX if r["acct"]=="400190507" and r["date"].year==y and r["date"].month==m]
    close = (sp[-1]["bal"] if sp else 0) + (co[-1]["bal"] if co else 0)
    print(f"{NAMES[m]+' '+str(y)[2:]:9}{rev:>12,.0f}{cog:>11,.0f}{lab:>10,.0f}{pay:>10,.0f}{crd:>11,.0f}{drw:>11,.0f}{oth:>10,.0f}{net:>12,.0f}{close:>12,.0f}")
    rowsout.append((NAMES[m]+" "+str(y), rev,cog,lab,pay,crd,drw,oth,net,close))

def block(name, pred):
    rev  = s(lambda r: pred(r) and r["type"]=="Revenue")
    oi   = s(lambda r: pred(r) and r["type"]=="Other Income")
    cog  = s(lambda r: pred(r) and r["type"]=="COGS")
    lab  = s(lambda r: pred(r) and r["type"]=="Labour-Unclear")
    pay  = s(lambda r: pred(r) and r["type"]=="Payroll")
    ope  = s(lambda r: pred(r) and r["type"]=="Operating Expense")
    crd  = s(lambda r: pred(r) and r["type"]=="Card Payment")
    drw  = s(lambda r: pred(r) and r["type"]=="Owner Draw/Comp")
    fin  = s(lambda r: pred(r) and r["type"]=="Financing")
    rvw  = s(lambda r: pred(r) and r["type"]=="Review")
    revx = rev/G; gst = rev-revx
    cogx = cog/G; crdx = crd/G
    prof = revx + oi + cogx + lab + pay + ope + crdx
    print(f"\n{'='*92}\n{name}\n{'='*92}")
    print(f"  Gross revenue collected (incl GST)      {rev:>14,.2f}")
    print(f"  Less GST at 5/105                       {-gst:>14,.2f}")
    print(f"  REVENUE EXCLUDING GST                   {revx:>14,.2f}")
    print(f"  Interest income                         {oi:>14,.2f}")
    print(f"  COGS — suppliers (ex GST)               {cogx:>14,.2f}")
    print(f"  GROSS MARGIN                            {revx+cogx:>14,.2f}   ({(revx+cogx)/revx*100 if revx else 0:.1f}%)")
    print(f"  Payroll — Kierran + Wave                {pay:>14,.2f}")
    print(f"  Labour, unidentified                    {lab:>14,.2f}")
    print(f"  Insurance                               {ope:>14,.2f}")
    print(f"  Credit card payments (ex GST)*          {crdx:>14,.2f}")
    print(f"  APPROX OPERATING PROFIT (cash basis)    {prof:>14,.2f}   ({prof/revx*100 if revx else 0:.1f}%)")
    print(f"  ---- reconciling to cash ----")
    print(f"  Add back GST collected                  {gst:>14,.2f}")
    print(f"  Add back GST in costs                   {-(cogx-cog)-(crdx-crd):>14,.2f}")
    print(f"  Owner draws                             {drw:>14,.2f}")
    print(f"  Owner capital in                        {fin:>14,.2f}")
    print(f"  Unidentified transfers                  {rvw:>14,.2f}")
    net = rev+oi+cog+lab+pay+ope+crd+drw+fin+rvw
    print(f"  NET CASH MOVEMENT                       {net:>14,.2f}")
    return dict(rev=rev,revx=revx,gst=gst,oi=oi,cog=cog,cogx=cogx,lab=lab,pay=pay,ope=ope,
                crd=crd,crdx=crdx,drw=drw,fin=fin,rvw=rvw,prof=prof,net=net)

A = block("SOLE PROPRIETORSHIP — Feb 1 to Jun 30, 2026 (account 400101914)", SP)
B = block("JULY 1 to AUG 31 — corporate period, but run through the SOLE PROP account", JA)
C = block("CORPORATE ACCOUNT 400190507 — Aug 28 to Aug 31 only", CO)

print(f"\n{'='*92}\nCASH RECONCILIATION\n{'='*92}")
print(f"  Opening cash before Feb 1, 2026 (business did not exist)        {0:>14,.2f}")
print(f"  Sole prop period net movement (Feb-Jun)                        {A['net']:>14,.2f}")
print(f"  Jul-Aug net movement in sole prop account                      {B['net']:>14,.2f}")
print(f"  = Sole prop account balance, Aug 31                            {A['net']+B['net']:>14,.2f}")
print(f"  Corporate account net movement                                 {C['net']:>14,.2f}")
print(f"  TOTAL BUSINESS CASH AT AUG 31, 2026                            {A['net']+B['net']+C['net']:>14,.2f}")
actual = 67159.36 + 32107.90
print(f"  Actual closing balances per statements                         {actual:>14,.2f}")
print(f"  DIFFERENCE                                                     {A['net']+B['net']+C['net']-actual:>14,.2f}")

print(f"\n{'='*92}\nGST — ESTIMATE\n{'='*92}")
gst_col = A['gst']+B['gst']+C['gst']
itc_cog = (A['cog']+B['cog']+C['cog'])/G*0.05*-1
itc_crd = (A['crd']+B['crd']+C['crd'])/G*0.05*-1
print(f"  GST collected on all revenue (5/105 of gross)                  {gst_col:>14,.2f}")
print(f"  Input tax credits on supplier costs                            {-itc_cog:>14,.2f}")
print(f"  Input tax credits on card spending (IF all business, GST-bearing) {-itc_crd:>13,.2f}")
print(f"  NET GST OWING (estimate)                                       {gst_col-itc_cog-itc_crd:>14,.2f}")

print(f"\n{'='*92}\nPAYROLL REMITTANCE — ESTIMATE (Kierran only; excludes unidentified labour)\n{'='*92}")
gross = -(A['pay']+B['pay'])
cpp = max(0, gross-3500)*0.0595*2; ei = gross*0.0164*2.4; tax = gross*0.12
print(f"  Gross paid to crew via payroll lines                           {gross:>14,.2f}")
print(f"  CPP employee + employer @5.95% x2 (over $3,500 exemption)      {cpp:>14,.2f}")
print(f"  EI employee + employer @1.64% x2.4                             {ei:>14,.2f}")
print(f"  Income tax that should have been withheld @12% est             {tax:>14,.2f}")
print(f"  SUBTOTAL                                                       {cpp+ei+tax:>14,.2f}")
print(f"  Penalty @10% first failure                                     {(cpp+ei+tax)*0.10:>14,.2f}")
print(f"  TOTAL PAYROLL REMITTANCE EXPOSURE (estimate)                   {(cpp+ei+tax)*1.10:>14,.2f}")

print(f"\n{'='*92}\nSOLE PROP INCOME TAX — ESTIMATE\n{'='*92}")
print(f"  Sole prop cash operating profit Feb-Jun                        {A['prof']:>14,.2f}")
print(f"  Note: owner draws of {-A['drw']:,.2f} are NOT deductible for a sole prop")
for rate,lbl in ((0.25,"at 25%"),(0.30,"at 30%"),(0.35,"at 35%")):
    print(f"  Personal income tax + CPP reserve {lbl:9}                    {A['prof']*rate:>14,.2f}")

print(f"\n{'='*92}\nCASH QUALITY\n{'='*92}")
cash = actual
gstL = gst_col-itc_cog-itc_crd
payL = (cpp+ei+tax)*1.10
taxL = A['prof']*0.30
tot = gstL+payL+taxL
opex_m = -(A['cog']+A['lab']+A['pay']+A['ope']+A['crd']+B['cog']+B['lab']+B['pay']+B['ope']+B['crd'])/7
print(f"  Total business cash at Aug 31                                  {cash:>14,.2f}")
print(f"  Less estimated GST owing                                       {-gstL:>14,.2f}")
print(f"  Less estimated payroll remittance + penalty                    {-payL:>14,.2f}")
print(f"  Less estimated personal tax on sole prop income (30%)          {-taxL:>14,.2f}")
print(f"  CASH AFTER CRA OBLIGATIONS                                     {cash-tot:>14,.2f}")
print(f"  Average monthly operating outflow (7 months)                   {opex_m:>14,.2f}")
print(f"  Months of operating cost covered, after CRA                    {(cash-tot)/opex_m:>14,.1f}")
print(f"  3-month operating reserve                                      {opex_m*3:>14,.2f}")
print(f"  DEPLOYABLE CAPITAL                                             {max(0,cash-tot-opex_m*3):>14,.2f}")
json.dump({"A":A,"B":B,"C":C,"cash":cash,"gstL":gstL,"payL":payL,"taxL":taxL,
           "opex_m":opex_m,"rows":rowsout}, open("res.json","w"), default=str, indent=1)
