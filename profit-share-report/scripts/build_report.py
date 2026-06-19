#!/usr/bin/env python3
"""
Ballpark CanopyCo profit-share report.
Revenue: invoices_parsed.csv (pre-GST, deposits excluded automatically).
COGS:    cogs.csv (per-client totals supplied by Kyle).
Payroll: payroll_summary.csv (employee gross pay; owner excluded; June periods prorated to May 31).
"""
import csv, datetime, html
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_HTML = ROOT / "CanopyCo-ProfitShare-Ballpark.html"

LABOUR_SHARE = 0.28   # CanopyCo share of labour profit
MATER_SHARE  = 0.50   # CanopyCo share of materials/non-labour profit
JUNE_PRORATE = 0.60   # May 23-Jun 6 -> days through May 31 (9/15)
RYAN_DEPOSIT = 10000.00  # "Ryan Expense Deposit" booked under Trudy COGS (flagged)

def money(x): return "${:,.2f}".format(x)

# ---------- Revenue ----------
inv_rows = list(csv.DictReader(open(ROOT/"invoices_parsed.csv")))
def month_key(d):
    dt = datetime.datetime.strptime(d.strip(), "%B %d, %Y")
    return dt.strftime("%Y-%m"), dt.strftime("%b %Y")

client_rev = defaultdict(lambda: {"labour":0.0,"nonlabour":0.0,"exclusive":False})
month_rev  = defaultdict(lambda: {"labour":0.0,"nonlabour":0.0})
for r in inv_rows:
    c = r["customer"].strip()
    lab = float(r["labour"]); non = float(r["nonlabour"])
    excl = r["exclusive"].strip().lower()=="yes"
    client_rev[c]["labour"]   += lab
    client_rev[c]["nonlabour"]+= non
    client_rev[c]["exclusive"] = excl
    mk,_ = month_key(r["date"])
    month_rev[mk]["labour"]   += lab
    month_rev[mk]["nonlabour"]+= non

# ---------- COGS ----------
cogs_rows = list(csv.DictReader(open(ROOT/"cogs.csv")))
client_cogs = defaultdict(float)
cogs_notes = []
for r in cogs_rows:
    inv_client = r["invoice_client"].strip()
    client_cogs[inv_client] += float(r["cost"])
    if r["notes"].strip():
        cogs_notes.append((r["cogs_client"], r["notes"]))

# ---------- Payroll (deductible employee gross, prorated) ----------
pay_rows = list(csv.DictReader(open(ROOT/"payroll_summary.csv")))
payroll_total = 0.0
pay_detail = []
for r in pay_rows:
    if r["is_owner"].strip().lower()=="yes":
        continue
    gross = float(r["gross_pay"])
    factor = JUNE_PRORATE if "Jun 6" in r["pay_period"] else 1.0
    payroll_total += gross*factor
    pay_detail.append((r["employee"], r["pay_period"], gross, factor, gross*factor))

# ---------- Build per-client table ----------
all_clients = set(client_rev) | set(client_cogs)
total_labour_all = sum(v["labour"] for v in client_rev.values())  # for payroll allocation

rows = []
for c in sorted(all_clients):
    rv = client_rev.get(c, {"labour":0,"nonlabour":0,"exclusive":False})
    lab, non, excl = rv["labour"], rv["nonlabour"], rv["exclusive"]
    cogs = client_cogs.get(c, 0.0)
    alloc_pay = payroll_total*(lab/total_labour_all) if total_labour_all else 0.0
    lab_profit = lab - alloc_pay
    mat_profit = non - cogs
    if excl:
        canopy = 0.0
    else:
        canopy = lab_profit*LABOUR_SHARE + mat_profit*MATER_SHARE
    rows.append(dict(client=c, exclusive=excl, labour=lab, nonlabour=non,
                     cogs=cogs, pay=alloc_pay, lab_profit=lab_profit,
                     mat_profit=mat_profit, canopy=canopy))

def agg(rs):
    return {k:sum(r[k] for r in rs) for k in
            ("labour","nonlabour","cogs","pay","lab_profit","mat_profit","canopy")}

canopy_rows = [r for r in rows if not r["exclusive"]]
excl_rows   = [r for r in rows if r["exclusive"]]
A = agg(canopy_rows)
E = agg(excl_rows)

# Scenario: exclude the $10k Ryan deposit from Trudy COGS
A_adj = dict(A)
A_adj["cogs"]      = A["cogs"] - RYAN_DEPOSIT
A_adj["mat_profit"]= A["mat_profit"] + RYAN_DEPOSIT
A_adj["canopy"]    = A["canopy"] + RYAN_DEPOSIT*MATER_SHARE

# ---------- HTML ----------
STYLE = """
@page { size: Letter; margin: 20mm 16mm 18mm 16mm; }
body { font-family:"Helvetica Neue",Helvetica,Arial,sans-serif; color:#1c2530;
       font-size:10.5pt; line-height:1.5; margin:0; }
.letterhead { display:flex; justify-content:space-between; align-items:flex-end;
       border-bottom:3px solid #2f5d44; padding-bottom:10px; margin-bottom:16px; }
.letterhead .name { font-size:20pt; font-weight:700; color:#2f5d44; letter-spacing:.5px; }
.letterhead .meta { text-align:right; font-size:8.5pt; color:#555; line-height:1.35; }
.small { font-size:8.6pt; color:#5a6470; }
h2 { font-size:11.5pt; color:#2f5d44; border-bottom:1px solid #cdd8d0;
     padding-bottom:4px; margin:22px 0 9px; text-transform:uppercase; letter-spacing:.6px; }
h3 { font-size:10.5pt; margin:14px 0 4px; color:#2f5d44; }
table { width:100%; border-collapse:collapse; margin:8px 0 4px; font-size:8.3pt; table-layout:fixed; }
th,td { padding:3px 5px; border:1px solid #dde4df; overflow-wrap:break-word; }
th:first-child,td:first-child { width:17%; }
th { background:#eef3ef; color:#2f5d44; font-weight:700; text-align:left; }
tr:nth-child(even) td { background:#f8faf8; }
td.num,th.num { text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums; }
.tot td { font-weight:700; background:#eef3ef !important; border-top:2px solid #2f5d44; }
.callout { background:#f1f6f2; border-left:3px solid #2f5d44; padding:8px 12px; margin:12px 0; font-size:9.3pt; }
.warn { background:#fbf2ee; border-left:3px solid #b03a2e; padding:8px 12px; margin:12px 0; font-size:9.3pt; }
.warn b { color:#b03a2e; }
.note { font-size:8.6pt; color:#5a6470; font-style:italic; }
.big { font-size:15pt; font-weight:700; color:#2f5d44; }
.neg { color:#b03a2e; }
"""

def num(x, neg_red=True):
    cls = "num neg" if (neg_red and x<0) else "num"
    return f'<td class="{cls}">{money(x)}</td>'

def client_table(rs, show_canopy=True):
    h = ['<table><tr><th>Client</th><th class="num">Labour billed</th>'
         '<th class="num">Materials billed</th><th class="num">Payroll (alloc.)</th>'
         '<th class="num">COGS</th><th class="num">Labour profit</th>'
         '<th class="num">Materials profit</th>']
    if show_canopy: h.append('<th class="num">CanopyCo share</th>')
    h.append('</tr>')
    for r in rs:
        h.append('<tr><td>'+html.escape(r["client"])+'</td>'
                 +num(r["labour"],False)+num(r["nonlabour"],False)+num(r["pay"],False)
                 +num(r["cogs"],False)+num(r["lab_profit"])+num(r["mat_profit"]))
        if show_canopy: h.append(num(r["canopy"]))
        h.append('</tr>')
    g = agg(rs)
    h.append('<tr class="tot"><td>TOTAL</td>'+num(g["labour"],False)+num(g["nonlabour"],False)
             +num(g["pay"],False)+num(g["cogs"],False)+num(g["lab_profit"])+num(g["mat_profit"]))
    if show_canopy: h.append(num(g["canopy"]))
    h.append('</tr></table>')
    return "".join(h)

# month table (canopyco only, materials+labour profit, no per-client payroll split -> allocate by labour share within month)
month_html = ['<table><tr><th>Month</th><th class="num">Labour billed</th>'
              '<th class="num">Materials billed</th><th class="num">Total billed</th></tr>']
for mk in sorted(month_rev):
    m = month_rev[mk]
    lbl = datetime.datetime.strptime(mk,"%Y-%m").strftime("%b %Y")
    month_html.append(f'<tr><td>{lbl}</td>'+num(m["labour"],False)+num(m["nonlabour"],False)
                      +num(m["labour"]+m["nonlabour"],False)+'</tr>')
month_html.append('</table>')

pay_html = ['<table><tr><th>Employee</th><th>Pay period</th><th class="num">Gross</th>'
            '<th class="num">Factor</th><th class="num">Counted</th></tr>']
for e,p,g,f,c in pay_detail:
    pay_html.append(f'<tr><td>{html.escape(e)}</td><td>{html.escape(p)}</td>'
                    +num(g,False)+f'<td class="num">{f:.2f}</td>'+num(c,False)+'</tr>')
pay_html.append(f'<tr class="tot"><td colspan="4">Total deductible employee payroll</td>'+num(payroll_total,False)+'</tr></table>')

tot_rev = A["labour"]+A["nonlabour"]
mccahill_net = (A["lab_profit"]+A["mat_profit"]) - A["canopy"]
mccahill_net_adj = (A_adj["lab_profit"]+A_adj["mat_profit"]) - A_adj["canopy"]

doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>McCahill &amp; Co. — CanopyCo Profit-Share (Ballpark)</title>
<style>{STYLE}</style></head><body>
<div class="letterhead">
  <div><div class="name">McCahill &amp; Co.</div>
  <div class="small">Landscape Construction &amp; Design</div></div>
  <div class="meta">CanopyCo Profit-Share Report<br>Season start &rarr; May 31, 2026<br>
  Prepared June 19, 2026<br><b>BALLPARK — for review</b></div>
</div>

<div class="warn"><b>&#9888; Read first — this is a ballpark.</b> Built from the supplied
invoices, the COGS sheet (per-client totals), and payroll. Figures will move once the items
flagged below are confirmed. All amounts are <b>pre-GST</b>. Owner (Kyle) hours are excluded
from payroll. Employee payroll is allocated to clients in proportion to labour billed (we don't
yet have per-client billable hours), so <i>per-client</i> labour profit is approximate; the
<i>totals</i> are solid.</div>

<h2>1. Headline — CanopyCo clients</h2>
<table>
<tr><th>Line</th><th class="num">As supplied</th><th class="num">Adj. (excl. $10k Ryan deposit)</th></tr>
<tr><td>Revenue billed (labour + materials, pre-GST)</td>{num(tot_rev,False)}{num(tot_rev,False)}</tr>
<tr><td>Less: Cost of goods</td>{num(-A['cogs'])}{num(-A_adj['cogs'])}</tr>
<tr><td>Less: Employee payroll (excl. owner)</td>{num(-A['pay'])}{num(-A['pay'])}</tr>
<tr class="tot"><td>Total profit pool</td>{num(A['lab_profit']+A['mat_profit'])}{num(A_adj['lab_profit']+A_adj['mat_profit'])}</tr>
<tr><td>&nbsp;&nbsp;Labour profit &times; 28%</td>{num(A['lab_profit']*LABOUR_SHARE)}{num(A_adj['lab_profit']*LABOUR_SHARE)}</tr>
<tr><td>&nbsp;&nbsp;Materials profit &times; 50%</td>{num(A['mat_profit']*MATER_SHARE)}{num(A_adj['mat_profit']*MATER_SHARE)}</tr>
<tr class="tot"><td>&#10148; CanopyCo profit-share owed</td>{num(A['canopy'])}{num(A_adj['canopy'])}</tr>
<tr class="tot"><td>McCahill net (after CanopyCo)</td>{num(mccahill_net)}{num(mccahill_net_adj)}</tr>
</table>
<p class="note">The two columns bracket the single biggest open question: a $10,000
"Ryan Expense Deposit" booked as a cost under Trudy. If that is not a true material cost,
the right-hand column applies.</p>
<p><span class="big">CanopyCo ballpark: {money(A_adj['canopy'])} &ndash; {money(A['canopy'])}</span></p>

<h2>2. Per-client breakdown — CanopyCo (split applies)</h2>
{client_table(canopy_rows)}
<p class="note">Labour profit = labour billed &minus; allocated employee payroll. Materials profit =
materials billed &minus; COGS. CanopyCo share = 28% of labour profit + 50% of materials profit.
Negative = client is currently underwater (usually a timing mismatch — see flags).</p>

<h2>3. Exclusive clients (your own — shown for completeness, NO split)</h2>
{client_table(excl_rows, show_canopy=False)}
<p class="note">These are flagged exclusive in the invoice set (Christine, Ian &amp; Judy, Anita,
Muriel). No profit-share is applied; reproduced here only so the COGS sheet reconciles in full.</p>

<h2>4. Revenue by month (all clients, pre-GST)</h2>
{''.join(month_html)}

<h2>5. Employee payroll (deductible)</h2>
{''.join(pay_html)}
<p class="note">Owner (Kyle) hours excluded entirely. The May 23&ndash;Jun 6 pay periods straddle
the May 31 cutoff and are prorated to 60% (9 of 15 days fall on/before May 31).</p>

<h2>6. Items to confirm (these move the number)</h2>
<div class="warn">
<b>1. $10,000 "Ryan Expense Deposit" (Trudy COGS).</b> Booked as a cost of goods but marked
"SENT" to Ryan. If this is a profit-share advance / inter-company transfer rather than a job
material cost, it should come out of COGS — that swings CanopyCo's share by
{money(RYAN_DEPOSIT*MATER_SHARE)} (the gap between the two headline columns).<br><br>
<b>2. $6,400 "blackbox electrical phase 1" (Trudy COGS) — UNPAID.</b> Included as cost; it is a
real subcontract bill but not yet paid. Kept in for now.<br><br>
<b>3. Trudy work-in-progress.</b> Trudy has ~$39,500 in deposits received that are <i>not</i> in
recognized revenue yet, while her costs are already booked. Her standalone line shows a large loss
purely from this timing — it normalizes when the final invoices are issued.<br><br>
<b>4. "Dave Wallace" vs "Dave Green".</b> COGS sheet says Dave Wallace; invoice #38 says Dave Green.
Assumed same client.<br><br>
<b>5. "Stratta" mapping.</b> Mapped to Oak Park VIS 5459 (a strata). Oak Park's invoices are
labour-only, so this $894.68 mulch has no matching materials revenue and shows as a small loss.
Confirm the correct client.<br><br>
<b>6. Payroll allocation.</b> No per-client billable-hours yet, so total employee payroll is spread
across clients by labour-billed share. Company totals are correct; per-client labour profit is
indicative only.<br><br>
<b>7. June-dated COGS.</b> A few mulch/plant buys are dated June 5 (just past the May 31 cutoff) but
tie to season jobs, so they're included.
</div>

<p class="small">Generated from invoices_parsed.csv, cogs.csv, payroll_summary.csv. Methodology per
project README. Figures pre-GST.</p>
</body></html>"""

OUT_HTML.write_text(doc)
print("Wrote", OUT_HTML)
print("\n--- HEADLINE (CanopyCo) ---")
print("Revenue billed      ", money(tot_rev))
print("COGS                ", money(A['cogs']), " (adj:", money(A_adj['cogs']),")")
print("Employee payroll    ", money(A['pay']))
print("Labour profit       ", money(A['lab_profit']))
print("Materials profit    ", money(A['mat_profit']), " (adj:", money(A_adj['mat_profit']),")")
print("CanopyCo share      ", money(A['canopy']), " (adj:", money(A_adj['canopy']),")")
print("McCahill net        ", money(mccahill_net), " (adj:", money(mccahill_net_adj),")")
print("Total payroll counted", money(payroll_total))
