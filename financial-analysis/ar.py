SP = {
 "Cycle 1 (Feb 11-23), billed Feb 25": (39244.70, [], 0.0),
 "Cycle 2 (Feb 26-Mar 31), billed Apr 1": (38550.27, [("Josh",360.00)], 0.0),
 "Cycle 3 (Apr 1-30), billed May 1": (61790.32, [("Josh",315.00)], 0.0),
 "Cycle 4 (May 1-31)": (45904.02, [("Jenica",240.00),("Sen",189.00),("Bill",236.00),("Josh",535.00)], 15500.00),
 "Cycle 5 (Jun 1-30)": (65222.41, [("Trudy French Drain remainder",3500.00),("Stratta mulching",2913.75),
                                   ("Stratta",1764.00),("Josh",157.50),("Andrei",210.00),
                                   ("Anita project walkway",3675.00)], 0.0),
}
CORP = {
 "Cycle 6 (Jul 1-31)":  (18217.32, 909.30,  "billed"),
 "Cycle 7 (Aug 1-31)":  (34121.02, 420.00,  "billed"),
 "Cycle 8 (Sep 1-30)":  (20186.15, 0.0,     "forecast, not sent"),
 "Cycle 9 (Oct 1-31)":  (20186.15, 0.0,     "forecast, not sent"),
 "Cycle 10 (Nov 1-30)": (20186.15, 0.0,     "forecast, not sent"),
 "Cycle 11 (Dec 1-31)": (19706.15, 0.0,     "forecast, not sent"),
}
W=96
print("="*W); print("SOLE PROPRIETORSHIP TRACKER"); print("="*W)
sp_tot=sp_red=sp_yel=0
for k,(tot,red,yel) in SP.items():
    r=sum(a for _,a in red); sp_tot+=tot; sp_red+=r; sp_yel+=yel
    print(f"{k:42} billed {tot:>11,.2f}   unpaid {r:>10,.2f}   pending {yel:>10,.2f}")
    for n,a in red: print(f"{'':46}   - {n}: {a:,.2f}")
print("-"*W)
print(f"{'TOTAL BILLED (Feb-Jun)':42} {sp_tot:>17,.2f}")
print(f"{'  unpaid (red)':42} {sp_red:>17,.2f}")
print(f"{'  pending (yellow, Teresa/Invoice #40)':42} {sp_yel:>17,.2f}")
print(f"{'  collected per tracker':42} {sp_tot-sp_red-sp_yel:>17,.2f}")

print("\n"+"="*W); print("CORPORATION TRACKER"); print("="*W)
c_bill=c_paid=c_fore=0
for k,(tot,paid,st) in CORP.items():
    if st=="billed": c_bill+=tot; c_paid+=paid
    else: c_fore+=tot
    print(f"{k:22} {tot:>11,.2f}   collected {paid:>9,.2f}   unpaid {tot-paid:>11,.2f}   {st}")
print("-"*W)
print(f"{'BILLED to Aug 31 (Jul+Aug)':42} {c_bill:>17,.2f}")
print(f"{'  collected':42} {c_paid:>17,.2f}   ({c_paid/c_bill*100:.1f}%)")
print(f"{'  OUTSTANDING':42} {c_bill-c_paid:>17,.2f}")
print(f"{'FORECAST Sep-Dec (not yet billed)':42} {c_fore:>17,.2f}")
print(f"{'Corporate tracker grand total':42} {c_bill+c_fore:>17,.2f}")

print("\n"+"="*W); print("ACCOUNTS RECEIVABLE — work done, invoice issued, money not received"); print("="*W)
ar = sp_red+sp_yel+(c_bill-c_paid)
print(f"  Sole prop, unpaid (red)                          {sp_red:>13,.2f}")
print(f"  Sole prop, Teresa / Invoice #40 (yellow)         {sp_yel:>13,.2f}")
print(f"  Corporation, Jul + Aug unpaid                    {c_bill-c_paid:>13,.2f}")
print(f"  TOTAL RECEIVABLE                                 {ar:>13,.2f}")
print(f"\n  For comparison, cash actually in the bank        {99267.26:>13,.2f}")
print(f"  Receivables as a share of cash                   {ar/99267.26*100:>12.0f}%")

print("\n"+"="*W); print("CROSS-CHECK AGAINST THE BANK"); print("="*W)
trk_coll = (sp_tot-sp_red-sp_yel) + c_paid
bank = 237313.84
print(f"  Tracker says collected                           {trk_coll:>13,.2f}")
print(f"  Bank actually received (client revenue)          {bank:>13,.2f}")
print(f"  Bank EXCEEDS tracker by                          {bank-trk_coll:>13,.2f}")
UNTRACKED = [("Pacific City Developments Inc.",9827.79),("Mark A",4556.00),("David C Newsome",1992.38),
             ("Bruce D Reid",1758.75),("Yuhuan Bai",567.00),("Wei Zhao",567.00),
             ("Christine Adrienne Schwartz",183.75)]
u=sum(a for _,a in UNTRACKED)
print(f"\n  Bank deposits from payers with no tracker line:")
for n,a in UNTRACKED: print(f"    {n:36} {a:>11,.2f}")
print(f"    {'TOTAL':36} {u:>11,.2f}")
print(f"\n  That $useful{u:,.2f} more than covers the ${bank-trk_coll:,.2f} gap.".replace("$useful",""))

print("\n"+"="*W); print("REVENUE PICTURE, FULL YEAR"); print("="*W)
print(f"  Sole prop billed Feb-Jun                         {sp_tot:>13,.2f}")
print(f"  Corporation billed Jul-Aug                       {c_bill:>13,.2f}")
print(f"  EARNED TO DATE (work done, invoiced)             {sp_tot+c_bill:>13,.2f}")
print(f"  Corporation forecast Sep-Dec                     {c_fore:>13,.2f}")
print(f"  ANTICIPATED FULL YEAR                            {sp_tot+c_bill+c_fore:>13,.2f}")
print(f"\n  Collected in cash to Aug 31                      {bank:>13,.2f}")
print(f"  Still owed                                       {ar:>13,.2f}")
print(f"  Collection rate on work invoiced                 {bank/(sp_tot+c_bill)*100:>12.0f}%")
