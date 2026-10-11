import datetime as dt
from decimal import Decimal

import money_plan as mp

D = Decimal


def test_example_blocked_only():
    s = mp.summarise(mp.example_plans()["a_blocked_only"])
    assert s.monthly_costs == D("955.00")
    assert s.blocked_at_extension == D("0.00")
    assert s.free_at_extension == D("238.00")      # 1500 + 11904 - (12*955 + 900 + 2*403)
    assert s.required_at_extension == D("11904.00")
    assert s.top_up == D("11666.00")
    assert s.save_per_month == D("972.17")
    assert s.first_negative_month == dt.date(2027, 10, 1)


def test_example_3000_left_tops_up_only_the_difference():
    s = mp.summarise(mp.example_plans()["b_extra_3000"])
    assert s.blocked_at_extension == D("3000.00")
    assert s.top_up == D("8666.00")                # 11904 - 3000 - 238, not 11904


def test_example_with_job():
    s = mp.summarise(mp.example_plans()["c_with_job"])
    assert s.free_at_extension == D("5638.00")
    assert s.top_up == D("6266.00")


def test_payout_stops_when_blocked_account_is_empty():
    plan = mp.Plan(dt.date(2026, 10, 15), 1500, 0, 992, {"rent": 0}, dt.date(2027, 10, 1))
    rows = mp.forecast(plan, 3)
    assert [r.payout for r in rows] == [D("992.00"), D("508.00"), D("0.00")]
    assert rows[0].month == dt.date(2026, 10, 1)


def test_negative_free_money_does_not_reduce_top_up_below_need():
    plan = mp.Plan(dt.date(2026, 10, 1), 0, 0, 992, {"rent": 500}, dt.date(2027, 4, 1),
                   proof_months=6)
    s = mp.summarise(plan)
    assert s.free_at_extension == D("-3000.00")
    assert s.required_at_extension == D("5952.00")
    assert s.top_up == D("5952.00")
    assert s.first_negative_month == dt.date(2026, 10, 1)


def test_no_top_up_when_enough_money():
    plan = mp.Plan(dt.date(2026, 10, 1), 30000, 0, 992, {"rent": 992}, dt.date(2027, 10, 1))
    s = mp.summarise(plan)
    assert s.top_up == D("0.00") and s.save_per_month == D("0.00")
    assert s.first_negative_month is None


def test_extension_already_reached():
    plan = mp.Plan(dt.date(2027, 10, 1), 2000, 500, 992, {"rent": 400}, dt.date(2027, 10, 1))
    s = mp.summarise(plan)
    assert s.months_to_extension == 0
    assert s.top_up == D("9404.00") and s.save_per_month is None


def test_one_off_income_is_negative_cost():
    plan = mp.Plan(dt.date(2026, 10, 1), 0, 0, 992, {"rent": 0}, dt.date(2027, 10, 1),
                   one_offs=[(dt.date(2026, 11, 1), D("-200"), "deposit back")])
    rows = mp.forecast(plan, 2)
    assert rows[1].spend == D("-200.00") and rows[1].free_close == D("200.00")


def test_add_months_wraps_year():
    assert mp.add_months(dt.date(2026, 11, 1), 3) == dt.date(2027, 2, 1)
