import json
from dataclasses import asdict, dataclass


@dataclass
class MonteCarloStatus:
    count_in: int
    count_out: int

    def asJson(self):
        return json.dumps(asdict(self))