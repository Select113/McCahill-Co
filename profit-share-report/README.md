# McCahill & Co. — CanopyCo Profit-Share Report

**Purpose:** A transparent, month-by-month and client-by-client report for Ryan (CanopyCo)
covering the season **start → end of May 2026** (invoices closed out), showing:

- Total invoices billed (revenue)
- Cost of goods (materials, plants, subcontractor, equipment, dump/fuel, etc.)
- Employee payroll cost (deductible — **excluding Kyle's own hours**)
- The CanopyCo profit-share split, per client, per month

---

## The profit-share agreement (as I understand it)

CanopyCo earns a share of **profit**, calculated in two separate buckets:

| Bucket | What's in it | CanopyCo share of *profit* |
|---|---|---|
| **Labour** | Labour billed to the client | **28%** |
| **Materials, subcontractor & extras** | Everything billed that isn't labour | **50%** |

"Profit" means revenue **minus the allowable cost** in each bucket:

```
Labour profit      = labour billed            − employee payroll cost (your own hours NOT deducted)
Materials profit   = materials/sub/extras billed − cost of goods (supplier + subcontractor cost)

CanopyCo share     = (Labour profit    × 28%)
                   + (Materials profit × 50%)

McCahill net       = Total profit − CanopyCo share
                   = (Labour profit + Materials profit) − CanopyCo share
```

**Key rule on payroll (CONFIRMED):** you can write off your **employees'** payroll against
labour profit, but **not your own hours**. Any row flagged `is_owner = yes` is excluded entirely.

**Paid time vs billable time:** an employee's real cost is their **full paid day** (from clock-in
in the morning to back at the office), but revenue is driven by **billable on-site hours per
client**. So the method is:

```
employee daily cost = paid_hours × hourly_cost          (the real cost to you)
allocate that cost to clients in proportion to that day's billable_hours per client
```

Non-billable time (travel, sourcing, dump runs) is therefore still written off — it just lands
on the client(s) the employee was billable to that day.

**Exclusive clients:** clients flagged as your own (not CanopyCo's) are reported separately
and **no split is applied** — they're shown for completeness only.

---

## Worked example (one client, one month)

| Item | Amount |
|---|---|
| Labour billed | $5,000 |
| Employee payroll (excl. your hours) | $1,800 |
| Materials / sub / extras billed | $8,000 |
| Cost of goods (supplier + sub) | $5,000 |

```
Labour profit     = 5,000 − 1,800 = 3,200   → CanopyCo 28% = $896
Materials profit  = 8,000 − 5,000 = 3,000   → CanopyCo 50% = $1,500
                                              CanopyCo share = $2,396

Total revenue 13,000 − COGS 5,000 − payroll 1,800 − CanopyCo 2,396 = $3,804 to McCahill
```

> **Note on GST (CONFIRMED):** all figures are **pre-GST (net)**. GST is collected and remitted —
> it isn't revenue or profit — so it's excluded from the split throughout.

---

## How to supply the data — fill in these four CSVs

Open each in Excel / Google Sheets, fill the rows, keep the header line. One row per item.
Don't worry about getting categories perfect — flag anything uncertain in the `notes` column
and I'll sort it.

### 1. `clients.csv` — who's who
Lists every client and whether the split applies.

| column | meaning |
|---|---|
| `client_name` | as it appears on invoices |
| `type` | `canopyco` (split applies) or `exclusive` (your own client, no split) |
| `notes` | anything useful |

### 2. `invoices.csv` — revenue, split by category
One row per invoice (or per line if you prefer). Amounts **pre-GST**.

| column | meaning |
|---|---|
| `invoice_no` | invoice number |
| `client_name` | must match `clients.csv` |
| `invoice_date` | `YYYY-MM-DD` |
| `labour_billed` | $ of labour on the invoice |
| `materials_billed` | $ of materials/plants |
| `subcontractor_billed` | $ of subcontracted work |
| `extras_billed` | any other non-labour charges (equipment, fees, etc.) |
| `gst` | GST charged (tracked but excluded from split) |
| `status` | `closed` / `open` |
| `notes` | e.g. "fence = supply+install, blended" |

### 3. `cogs.csv` — what you paid out (cost of goods)
One row per supplier receipt / subcontractor bill. Tie each to a client (and invoice if you can).

| column | meaning |
|---|---|
| `date` | `YYYY-MM-DD` |
| `client_name` | must match `clients.csv` |
| `invoice_no` | optional — which invoice it belongs to |
| `category` | `materials` / `plants` / `subcontractor` / `equipment` / `dump` / `fuel` / `other` |
| `supplier` | e.g. K2 Stone, PND |
| `description` | short detail |
| `cost` | $ you paid (pre-GST) |
| `notes` | |

### 4a. `payroll_days.csv` — the paid-time log (your cost)
One row per employee per day — their actual paid day, start to back-at-office.

| column | meaning |
|---|---|
| `date` | `YYYY-MM-DD` |
| `employee_name` | |
| `is_owner` | `yes` for your own hours (excluded entirely), `no` for employees |
| `start_time` / `end_time` | clock-in / clock-out (optional if you give paid_hours) |
| `paid_hours` | total paid hours for the day |
| `hourly_cost` | what the hour costs **you** (wage, plus burden if you want) — not the billed rate |
| `notes` | |

### 4b. `billable_hours.csv` — the billable log (revenue side / allocation)
One row per employee per client per day — the on-site hours billed to that client.

| column | meaning |
|---|---|
| `date` | `YYYY-MM-DD` (matches `payroll_days.csv`) |
| `employee_name` | |
| `client_name` | must match `clients.csv` |
| `invoice_no` | optional |
| `billable_hours` | on-site hours billed to that client that day |
| `notes` | |

> I join these two by `date` + `employee_name`: the paid-day cost is spread across whatever
> clients the employee was billable to that day.

---

## What I'll produce

A polished report (HTML + PDF, matching your Invoice #40 letterhead) containing:

1. **Season summary** — totals: revenue, COGS, payroll, total profit, CanopyCo share, McCahill net.
2. **Month-by-month** breakdown of the same.
3. **Per-client** breakdown (CanopyCo clients with split; exclusive clients shown separately).
4. **Per-client × per-month** detail tables — the full transparent picture for Ryan.
5. A clear methodology page so Ryan can follow exactly how each number was derived.

---

## Confirmed methodology
- Labour profit = labour billed − **employee** payroll (owner hours excluded).
- All figures **pre-GST**.
- Employee cost = full paid day, allocated to clients by billable hours per date.
- Split applies only to `canopyco` clients; `exclusive` clients shown separately, no split.

## What I still need from you
1. **Season start date** (looks like ~Feb 2026 from Invoice #40 — confirm).
2. The raw files — drop them in `source/` (see `source/README.md`) or paste into chat:
   - invoices (start of season → end of May)
   - cost-of-goods receipts / supplier & subcontractor bills
   - employee daily time logs + billable-hours-per-client log
   I'll extract the invoices and logs and reconcile everything into the report.
