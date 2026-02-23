from enum import Enum


class GraduationLevel(str, Enum):
    INCUBATION = "INCUBATION"     # paper / tiny capital
    CANARY = "CANARY"             # ₹-capped live
    PRODUCTION = "PRODUCTION"     # scaled live
