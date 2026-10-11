"""Reference model for the Money plan feature (F13, docs/features/money-plan.md).

The student's numbers live only in their own Budget sheet and are computed by sheet formulas
(rule 2: numbers from formulas). This module mirrors those formulas so the template (task P7)
can be tested against known inputs → known outputs. It is never run on student data.

Model, month by month from the plan start:
  blocked_open   blocked account balance at the start of the month
  payout         min(monthly payout, blocked_open); the bank pays it into the free account
  income         payout + job income + family support
  spend          monthly costs + one-off costs (a one-off income is a negative cost)
  free_close     free money after the month (current account and cash)
At the permit extension date:
  required       proof_months × monthly_need                (the office's benchmark)
  have           blocked balance + free money (free money can be moved into the blocked account)
  top_up         max(0, required − have)                     money to find from outside
  save_per_month top_up ÷ months left until the extension
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal


def euros(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def add_months(day: dt.date, months: int) -> dt.date:
    index = day.month - 1 + months
    return dt.date(day.year + index // 12, index % 12 + 1, 1)


@dataclass
class Plan:
    start: dt.date                       # first month of the plan (day ignored)
    blocked_start: Decimal               # blocked account balance at the start
    free_start: Decimal                  # money in the current account and cash at the start
    payout: Decimal                      # monthly payout from the blocked account
    monthly_costs: dict[str, Decimal]    # rent, insurance, phone, food, ...
    extension: dt.date                   # date the current permit ends
    proof_months: int = 12               # months the office asks for at extension (Kiel: confirm)
    monthly_need: Decimal = euros(992)   # benchmark per month (pack: de.proof-of-funds.amount)
    job_income: Decimal = euros(0)
    family_support: Decimal = euros(0)
    one_offs: list[tuple[dt.date, Decimal, str]] = field(default_factory=list)
    # one-off amounts: positive = cost (deposit, semester fee), negative = income (refund)

    def __post_init__(self):
        self.start = self.start.replace(day=1)
        self.extension = self.extension.replace(day=1)
        for name in ("blocked_start", "free_start", "payout", "monthly_need", "job_income",
                     "family_support"):
            setattr(self, name, euros(getattr(self, name)))
        self.monthly_costs = {k: euros(v) for k, v in self.monthly_costs.items()}
        self.one_offs = [(d.replace(day=1), euros(a), n) for d, a, n in self.one_offs]


@dataclass
class Month:
    month: dt.date
    blocked_open: Decimal
    payout: Decimal
    blocked_close: Decimal
    income: Decimal
    spend: Decimal
    free_close: Decimal


def forecast(plan: Plan, months: int = 24) -> list[Month]:
    rows: list[Month] = []
    blocked = plan.blocked_start
    free = plan.free_start
    base_costs = sum(plan.monthly_costs.values(), Decimal("0"))
    for i in range(months):
        month = add_months(plan.start, i)
        payout = min(plan.payout, blocked)
        one_off = sum((a for d, a, _ in plan.one_offs if d == month), Decimal("0"))
        income = payout + plan.job_income + plan.family_support
        spend = base_costs + one_off
        blocked_close = blocked - payout
        free = free + income - spend
        rows.append(Month(month, blocked, payout, blocked_close, euros(income), euros(spend),
                          euros(free)))
        blocked = blocked_close
    return rows


@dataclass
class Summary:
    monthly_costs: Decimal
    first_negative_month: dt.date | None   # over-budget date (FR-5.2)
    months_to_extension: int
    blocked_at_extension: Decimal
    free_at_extension: Decimal
    required_at_extension: Decimal
    top_up: Decimal
    save_per_month: Decimal | None         # None when the extension month has already started


def summarise(plan: Plan, months: int = 24) -> Summary:
    rows = forecast(plan, months)
    months_to_ext = (plan.extension.year - plan.start.year) * 12 + (
        plan.extension.month - plan.start.month)
    if months_to_ext <= 0:
        blocked_ext, free_ext = plan.blocked_start, plan.free_start
    else:
        before = rows[min(months_to_ext, len(rows)) - 1]
        blocked_ext, free_ext = before.blocked_close, before.free_close
    required = euros(plan.proof_months * plan.monthly_need)
    have = blocked_ext + max(free_ext, Decimal("0"))
    top_up = euros(max(Decimal("0"), required - have))
    save = euros(top_up / months_to_ext) if months_to_ext > 0 else None
    negative = next((r.month for r in rows if r.free_close < 0), None)
    return Summary(
        monthly_costs=euros(sum(plan.monthly_costs.values(), Decimal("0"))),
        first_negative_month=negative,
        months_to_extension=max(months_to_ext, 0),
        blocked_at_extension=euros(blocked_ext),
        free_at_extension=euros(free_ext),
        required_at_extension=required,
        top_up=top_up,
        save_per_month=save,
    )


def example_plans() -> dict[str, Plan]:
    """Invented examples used in docs/features/money-plan.md and the template tests."""
    costs = {"rent": 450, "health insurance": 140, "phone": 15, "food": 250, "other": 100}
    start = dt.date(2026, 10, 1)
    fees = [(dt.date(2027, 2, 1), euros(403), "semester fee"),
            (dt.date(2027, 8, 1), euros(403), "semester fee")]
    return {
        "a_blocked_only": Plan(start, euros(11904), euros(1500), euros(992), costs,
                               dt.date(2027, 10, 1),
                               one_offs=[(start, euros(900), "rent deposit"), *fees]),
        "b_extra_3000": Plan(start, euros(14904), euros(1500), euros(992), costs,
                             dt.date(2027, 10, 1),
                             one_offs=[(start, euros(900), "rent deposit"), *fees]),
        "c_with_job": Plan(start, euros(11904), euros(1500), euros(992), costs,
                           dt.date(2027, 10, 1), job_income=euros(450),
                           one_offs=[(start, euros(900), "rent deposit"), *fees]),
    }


if __name__ == "__main__":  # pragma: no cover
    for name, p in example_plans().items():
        s = summarise(p)
        print(name, s)
