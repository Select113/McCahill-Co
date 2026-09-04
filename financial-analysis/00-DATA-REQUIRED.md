# Data Required for the Liquid Cash Position Analysis

Status: **analysis blocked — no financial records supplied.**

The repository contains only the Invoice #40 dispute package. No bank statements,
transaction exports, accounting records, payroll records, or personal account data are
present. The upload mounts are empty. This document specifies exactly what is needed.

---

## A. Blocking issue: the period is not finished

The requested corporate period is **July 1 → January 31**. The Invoice #40 correspondence is
dated June 2026, which places the sole-proprietorship period at **Feb 1 – Jun 30, 2026** and
the corporate period at **Jul 1, 2026 – Jan 31, 2027**.

Today is **September 4, 2026**. Roughly five of the seven corporate months have not happened
yet. A full-year corporate cash analysis cannot be produced. Confirm which you want:

- **(a)** Analyse actuals through today (Feb 1 – Aug 31, 2026), then forecast Sep – Jan; or
- **(b)** The period is actually Feb 2025 – Jan 2026 and is complete — send that year's data.

---

## B. Bank and account data — the core requirement

For **every** account, for **Jan 1, 2026 through today** (January gives the opening balance
immediately before Feb 1):

- Full transaction export — **CSV or OFX/QBO preferred**, PDF statements acceptable
- Every month, no gaps — a missing month breaks the reconciliation chain
- Opening and closing balance on each statement

Accounts to cover:

| Entity | Accounts |
|---|---|
| Personal | Chequing, savings, cash, any liquid investment (TFSA/non-registered — state whether accessible) |
| Sole proprietorship | Business chequing, business savings, any payment processor (Stripe/Square/PayPal), e-transfer-receiving account |
| Corporation | Corporate chequing, corporate savings, payment processors |
| Both | Credit cards and lines of credit (needed to identify expenses paid on credit and to size real liquidity) |

Note: `kyle@canopyco.ca` receives e-transfers. Identify which account those land in, and
whether it changed on July 1.

## C. Entity and transfer mapping

Without this, transfers get double-counted as revenue — the single largest risk to the numbers.

- A list of every account with its **last 4 digits**, owning entity, and open/close dates
- The date the corporate accounts opened and the date the sole-prop accounts stopped being used
- Any account you are unsure how to classify — flag it, do not guess
- Any transfer between accounts that does not appear as a matched pair (e.g. cash withdrawn
  from business and deposited personally days later)

## D. Corporate formation

- Incorporation date and certificate
- Corporate fiscal year end (may not be January 31 — this drives the tax estimate)
- Opening capital contribution into the corporation
- Whether sole-prop assets (vehicles, equipment, tools) were rolled into the corporation, and
  at what value; whether a s.85 rollover election was filed
- Whether the sole prop was formally closed and its final return filed

## E. Payroll

- Payroll register for every pay period: gross, CPP, EI, income tax, net, per employee
- CRA source-deduction remittance amounts and dates
- Number of employees and hourly rates for each period
- **Crew wage rate is the single most important missing number** — job profitability on
  Invoice #40 and every other job cannot be computed without it
- Any subcontractors paid, with amounts (G&C Excavation confirmed; others?)
- WorkSafeBC premium payments

## F. GST

- GST filing frequency (annual/quarterly/monthly) and periods filed
- GST collected, input tax credits claimed, and net remitted per period, with payment dates
- Whether the corporation obtained its **own** GST number or continued using 740677638 RT0001
- Any GST owing or refund outstanding

## G. Revenue and receivables

- All invoices issued Feb 2026 onward: number, date, client, amount excl. GST, GST, total
- Payment received date and amount for each
- Which invoices are unpaid as of today (Invoice #40's $15,925.09 is one — disputed)
- Any customer deposits or prepayments held for work not yet performed

## H. Taxes

- 2025 personal tax return (establishes instalment obligations and carryforwards)
- Any personal tax instalments paid in 2026, with dates
- Sole-prop net income for Feb–Jun (drives the personal tax bill that must be reserved for)
- Corporate instalments, if any have started

## I. Assets, debt, and capital spending

Not liquid cash, but required to distinguish cash flow from profit:

- Vehicle list: year/model, purchase price and date, current loan/lease balance, monthly
  payment, condition and mileage
- Equipment purchases over ~$500 with dates and amounts
- Every loan and lease: original amount, balance, monthly payment, interest rate, maturity
- Any personal funds put into the business, or business funds used personally

## J. Fixed costs (for the reserve calculation)

Monthly or annual amount for: insurance (liability, vehicle, WorkSafeBC), rent or yard/storage,
phone and internet, software, accounting and legal fees, fuel, vehicle maintenance, shop supplies.

---

## What gets delivered once the data arrives

1. Account-by-account classification, with anything ambiguous flagged rather than assumed
2. Inter-account/inter-entity transfer register, excluded from revenue and expenses
3. Reconciled cash walk per entity: opening + inflows − outflows = closing, tied to statements
4. Month-by-month table, Feb through the last complete month, split sole prop / corp / personal
5. Separate sole-prop (Feb–Jun) and corporate (Jul onward) performance, GST stripped out
6. Cash vs. accounting profit bridge
7. Tax reserve, operating reserve, and deployable capital
8. Vehicle scenarios at $20k / $30k / $40k / $50k against reserves
9. Conservative / base / aggressive scenarios for next season
10. Verification queue for everything that doesn't tie

## Minimum viable subset

If assembling all of the above is slow, these four alone produce a defensible liquid cash
figure and a first-cut reserve recommendation:

1. **B** — all bank exports, Jan 2026 to today
2. **C** — the account-to-entity map
3. **E** — payroll register and crew wage rates
4. **F** — GST filing status and amounts remitted
