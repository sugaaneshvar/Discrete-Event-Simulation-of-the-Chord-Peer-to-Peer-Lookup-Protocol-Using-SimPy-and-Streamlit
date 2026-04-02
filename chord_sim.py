from __future__ import annotations

from dataclasses import dataclass, field
import math
import random
from typing import Dict, List, Optional

import simpy


@dataclass
class FingerEntry:
    start: int
    successor: int


@dataclass
class Node:
    node_id: int
    predecessor: int = -1
    successor: int = -1
    fingers: List[FingerEntry] = field(default_factory=list)


@dataclass
class LookupStep:
    time: float
    from_node: int
    to_node: int
    key: int
    note: str


@dataclass
class LookupRecord:
    key: int
    start_node: int
    responsible_node: int
    hops: int
    latency: float
    steps: List[LookupStep]
    churn_events: List[str]


class ChordNetwork:
    def __init__(
        self,
        bits: int,
        node_ids: Optional[List[int]] = None,
        seed: int = 7,
        hop_latency: float = 1.0,
    ) -> None:
        self.bits = bits
        self.ring_size = 2 ** bits
        self.seed = seed
        self.random = random.Random(seed)
        self.hop_latency = hop_latency
        self.nodes: Dict[int, Node] = {}
        self.churn_log: List[str] = []
        self._initial_node_ids = sorted(node_ids or [])
        for node_id in self._initial_node_ids:
            self.nodes[node_id] = Node(node_id=node_id)
        self.rebuild_routing()

    @classmethod
    def generate(
        cls,
        bits: int,
        node_count: int,
        seed: int = 7,
        hop_latency: float = 1.0,
    ) -> "ChordNetwork":
        ring_size = 2 ** bits
        if node_count < 2:
            raise ValueError("Chord needs at least 2 nodes to form a useful ring.")
        if node_count > ring_size:
            raise ValueError("Node count cannot exceed identifier space size.")
        rng = random.Random(seed)
        node_ids = sorted(rng.sample(range(ring_size), node_count))
        return cls(bits=bits, node_ids=node_ids, seed=seed, hop_latency=hop_latency)

    def clone(self) -> "ChordNetwork":
        return ChordNetwork(
            bits=self.bits,
            node_ids=self.node_ids(),
            seed=self.seed,
            hop_latency=self.hop_latency,
        )

    def node_ids(self) -> List[int]:
        return sorted(self.nodes.keys())

    def rebuild_routing(self) -> None:
        node_ids = self.node_ids()
        if not node_ids:
            return
        total = len(node_ids)
        for index, node_id in enumerate(node_ids):
            node = self.nodes[node_id]
            node.predecessor = node_ids[(index - 1) % total]
            node.successor = node_ids[(index + 1) % total]
            node.fingers = []
            for offset in range(self.bits):
                start = (node_id + 2**offset) % self.ring_size
                node.fingers.append(
                    FingerEntry(start=start, successor=self.find_successor_id(start))
                )

    def find_successor_id(self, identifier: int) -> int:
        node_ids = self.node_ids()
        if not node_ids:
            raise ValueError("No nodes available in the ring.")
        for node_id in node_ids:
            if node_id >= identifier:
                return node_id
        return node_ids[0]

    def interval_contains(
        self,
        start: int,
        end: int,
        value: int,
        include_start: bool = False,
        include_end: bool = False,
    ) -> bool:
        if start == end:
            return include_start or include_end or value != start

        if start < end:
            left_ok = value > start or (include_start and value == start)
            right_ok = value < end or (include_end and value == end)
            return left_ok and right_ok

        left_side = value > start or (include_start and value == start)
        right_side = value < end or (include_end and value == end)
        return left_side or right_side

    def responsible_for_key(self, node_id: int, key: int) -> bool:
        node = self.nodes[node_id]
        return self.interval_contains(
            node.predecessor,
            node.node_id,
            key,
            include_start=False,
            include_end=True,
        )

    def closest_preceding_finger(self, node_id: int, key: int) -> int:
        node = self.nodes[node_id]
        for finger in reversed(node.fingers):
            if self.interval_contains(node.node_id, key, finger.successor):
                return finger.successor
        return node.successor

    def add_node(self, node_id: int) -> None:
        if node_id in self.nodes:
            return
        self.nodes[node_id] = Node(node_id=node_id)
        self.rebuild_routing()

    def remove_node(self, node_id: int) -> None:
        if node_id not in self.nodes or len(self.nodes) <= 2:
            return
        del self.nodes[node_id]
        self.rebuild_routing()

    def finger_table_rows(self, node_id: int) -> List[Dict[str, int]]:
        node = self.nodes[node_id]
        rows = []
        for index, finger in enumerate(node.fingers, start=1):
            rows.append(
                {
                    "finger": index,
                    "start": finger.start,
                    "successor": finger.successor,
                }
            )
        return rows

    def ring_rows(self) -> List[Dict[str, float]]:
        rows = []
        for node_id in self.node_ids():
            angle = (2 * math.pi * node_id) / self.ring_size
            rows.append(
                {
                    "node_id": node_id,
                    "angle": angle,
                    "x": math.cos(angle),
                    "y": math.sin(angle),
                }
            )
        return rows

    def _lookup_process(
        self,
        env: simpy.Environment,
        start_node: int,
        key: int,
        result_box: Dict[str, LookupRecord],
    ):
        current = start_node
        hops = 0
        steps: List[LookupStep] = []
        while True:
            if current not in self.nodes:
                current = self.find_successor_id(current)
                steps.append(
                    LookupStep(
                        time=env.now,
                        from_node=current,
                        to_node=current,
                        key=key,
                        note=f"Node departed; resumed lookup from successor {current}",
                    )
                )
            if self.responsible_for_key(current, key):
                break
            next_node = self.closest_preceding_finger(current, key)
            if next_node == current:
                next_node = self.nodes[current].successor
            yield env.timeout(self.hop_latency)
            if next_node not in self.nodes:
                next_node = self.find_successor_id(next_node)
            hops += 1
            steps.append(
                LookupStep(
                    time=env.now,
                    from_node=current,
                    to_node=next_node,
                    key=key,
                    note=f"Forward via finger table from {current} to {next_node}",
                )
            )
            current = next_node

        result_box["record"] = LookupRecord(
            key=key,
            start_node=start_node,
            responsible_node=current,
            hops=hops,
            latency=env.now,
            steps=steps,
            churn_events=list(self.churn_log),
        )

    def _join_process(self, env: simpy.Environment, node_id: int, at_time: float):
        yield env.timeout(at_time)
        self.add_node(node_id)
        self.churn_log.append(f"t={env.now:.1f}: node {node_id} joined")

    def _leave_process(self, env: simpy.Environment, node_id: int, at_time: float):
        yield env.timeout(at_time)
        self.remove_node(node_id)
        self.churn_log.append(f"t={env.now:.1f}: node {node_id} departed")

    def simulate_lookup(
        self,
        start_node: int,
        key: int,
        join_events: Optional[List[Dict[str, float]]] = None,
        leave_events: Optional[List[Dict[str, float]]] = None,
    ) -> LookupRecord:
        if start_node not in self.nodes:
            raise ValueError("Start node must exist in the current ring.")

        env = simpy.Environment()
        self.churn_log = []
        result_box: Dict[str, LookupRecord] = {}
        env.process(self._lookup_process(env, start_node, key, result_box))

        for event in join_events or []:
            env.process(self._join_process(env, int(event["node_id"]), float(event["time"])))
        for event in leave_events or []:
            env.process(self._leave_process(env, int(event["node_id"]), float(event["time"])))

        env.run()
        return result_box["record"]

    def lookup_metrics(
        self,
        trial_count: int = 64,
        seed_offset: int = 0,
    ) -> Dict[str, float]:
        rng = random.Random(self.seed + seed_offset)
        node_ids = self.node_ids()
        total_hops = 0
        total_latency = 0.0
        for _ in range(trial_count):
            start = rng.choice(node_ids)
            key = rng.randrange(self.ring_size)
            record = self.clone().simulate_lookup(start_node=start, key=key)
            total_hops += record.hops
            total_latency += record.latency

        average_hops = total_hops / trial_count
        average_latency = total_latency / trial_count
        return {
            "node_count": len(node_ids),
            "avg_hops": average_hops,
            "avg_latency": average_latency,
            "log2_n": math.log2(len(node_ids)),
        }


def build_scaling_rows(
    bits: int,
    seed: int,
    hop_latency: float,
    counts: List[int],
    trial_count: int = 64,
) -> List[Dict[str, float]]:
    rows = []
    for index, count in enumerate(counts):
        network = ChordNetwork.generate(
            bits=bits,
            node_count=count,
            seed=seed + index,
            hop_latency=hop_latency,
        )
        rows.append(network.lookup_metrics(trial_count=trial_count, seed_offset=index))
    return rows
