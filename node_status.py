from dataclasses import asdict, dataclass
import json
from typing_extensions import Self

LIGHT_SIGNIFICANCE = 100


@dataclass
class NodeStatus:
    node_id: str
    light: bool
    cpu_temperature: float
    environment_temperature: float

    def as_json(self):
        return json.dumps(asdict(self))

    def from_json(data: str) -> Self:
        data = json.loads(data)
        return NodeStatus(
            node_id=data["node_id"],
            light=data["light"],
            cpu_temperature=data["cpu_temperature"],
            environment_temperature=data["environment_temperature"],
        )

    def estimate(self):
        return (
            LIGHT_SIGNIFICANCE * int(self.light)
            - self.environment_temperature
            - self.cpu_temperature
        )
