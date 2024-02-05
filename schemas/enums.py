from enum import Enum


class DNRS3SearchScopeLevel(Enum):
    year = "%Y"
    month = "%Y-%m"
    day = "%Y-%m-%d"
