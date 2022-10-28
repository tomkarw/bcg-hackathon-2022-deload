import json
from dataclasses import asdict, dataclass
from typing_extensions import Self


@dataclass
class MonteCarloStatus:
    count_in: int
    count_out: int

    def as_json(self):
        return json.dumps(asdict(self))

    def from_json(data: str) -> Self:
        data = json.loads(data)
        return MonteCarloStatus(count_in=data["count_in"], count_out=data["count_out"])
