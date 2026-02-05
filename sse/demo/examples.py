from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class DemoExample:
    id: str
    situation: str
    expected_mode: str
    expected_outcome_id: str


EXAMPLES: Dict[str, DemoExample] = {
    "exam_cheating": DemoExample(
        id="exam_cheating",
        situation=(
            "A student notices that the invigilator has stepped out briefly during an exam "
            "and considers whether to cheat."
        ),
        expected_mode="A",
        expected_outcome_id="no_cheat_internal_conflict",
    ),
    "workplace_promotion": DemoExample(
        id="workplace_promotion",
        situation=(
            "An employee who has consistently exceeded performance targets has been denied "
            "a promotion without a clear explanation and is deciding how to respond."
        ),
        expected_mode="B",
        expected_outcome_id="quiet_job_search",
    ),
    "manager_confrontation": DemoExample(
        id="manager_confrontation",
        situation=(
            "An employee confronts their manager about unpaid overtime while knowing HR may become involved."
        ),
        expected_mode="B",
        expected_outcome_id="cautious_raise_issue",
    ),
    "public_tax_policy": DemoExample(
        id="public_tax_policy",
        situation=(
            "A government announces a sudden increase in fuel taxes, affecting commuters and small businesses."
        ),
        expected_mode="C",
        expected_outcome_id="dissatisfaction_protest",
    ),
    "platform_algorithm_change": DemoExample(
        id="platform_algorithm_change",
        situation=(
            "A social media platform changes its algorithm, reducing visibility for independent creators."
        ),
        expected_mode="C",
        expected_outcome_id="creator_migration_criticism",
    ),
}
