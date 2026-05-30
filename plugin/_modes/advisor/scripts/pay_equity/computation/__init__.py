"""Pure-Python computation modules.

No LLM in the computation loop. All numerical results are deterministic.
"""

from scripts.pay_equity.computation.predominance import determine_predominance
from scripts.pay_equity.computation.scoring import score_class
from scripts.pay_equity.computation.comparison import (
    compare_job_to_job,
    compare_with_regression,
)
from scripts.pay_equity.computation.regression import fit_male_wage_line
from scripts.pay_equity.computation.gap import compute_gap
from scripts.pay_equity.computation.schedule import build_payment_schedule
from scripts.pay_equity.computation.interest import (
    compute_period_interest,
    compute_per_pay_period_interest,
)
from scripts.pay_equity.computation.global_comparison import lookup_prescribed_comparators

__all__ = [
    "build_payment_schedule",
    "compare_job_to_job",
    "compare_with_regression",
    "compute_gap",
    "compute_per_pay_period_interest",
    "compute_period_interest",
    "determine_predominance",
    "fit_male_wage_line",
    "lookup_prescribed_comparators",
    "score_class",
]
