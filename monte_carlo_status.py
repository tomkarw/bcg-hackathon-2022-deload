import json
from dataclasses import asdict, dataclass
from typing_extensions import Self
import random


@dataclass
class MonteCarloStatus:
    count_in: int
    count_out: int

    def as_json(self):
        return json.dumps(asdict(self))

    def from_json(data: str) -> Self:
        data = json.loads(data)
        return MonteCarloStatus(count_in=data["count_in"], count_out=data["count_out"])

    def step(self):
        rand_x = random.uniform(-1, 1)
        rand_y = random.uniform(-1, 1)

        origin_dist = rand_x**2 + rand_y**2

        # Checking if (x, y) lies inside the circle
        if origin_dist <= 1:
            self.count_in += 1

        self.count_out += 1

    def approximation(self):
        if self.count_out == 0:
            return 4
        return 4 * self.count_in / self.count_out
