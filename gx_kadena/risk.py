import math
from typing import List, Optional, Tuple

def risk_score(balance: int, tx24: Optional[int], is_contract: Optional[bool]) -> Tuple[int, List[str]]:
    score = 50
    flags: List[str] = []

    if balance > 0:
        score += min(15, int(math.log10(balance + 1) * 6))
    if tx24 is not None:
        if tx24 >= 20:
            score += 10
        elif tx24 >= 5:
            score += 5
    if is_contract:
        score -= 10
        flags.append("contract-like")
    score = max(0, min(100, score))
    if balance == 0 and (tx24 is None or tx24 == 0):
        flags.append("dormant-or-new")
    return score, flags