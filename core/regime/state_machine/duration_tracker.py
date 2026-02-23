from typing import Tuple, Literal

AgeBucket = Literal["early", "mid", "late"]


def compute_duration_and_age(
    previous_label: str,
    previous_duration: int,
    new_label: str,
) -> Tuple[int, AgeBucket]:
    if previous_label == new_label:
        duration = previous_duration + 1
    else:
        duration = 1

    if duration <= 3:
        age = "early"
    elif duration <= 15:
        age = "mid"
    else:
        age = "late"

    return duration, age