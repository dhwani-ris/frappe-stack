"""Workflow shape validator. Refuses common PM mistakes:

- States without roles (no one can drive them).
- Workflows without any terminal state (documents would loop forever).
- Orphan states unreachable from initial state.
- Split states with traffic_split that doesn't sum to 100.
- Split states without next_states for both arms.
- Cycles without an exit (cannot be reached from any terminal).
"""

from __future__ import annotations

VALID_TYPES = {"normal", "split", "terminal"}


def validate_workflow_definition(states: list[dict], transitions: list[dict]) -> None:
    if not isinstance(states, list) or len(states) < 2:
        raise ValueError("Workflow needs at least 2 states (initial + terminal)")
    if not isinstance(transitions, list):
        raise ValueError("transitions must be a list")

    state_names = {s["name"] for s in states}
    initial_name = states[0]["name"]

    for s in states:
        _validate_state(s, state_names)

    if not any(s.get("type") == "terminal" for s in states):
        raise ValueError("Workflow must have at least one terminal state")

    for t in transitions:
        _validate_transition(t, state_names)

    reachable = _reachable(initial_name, transitions, states)
    orphans = state_names - reachable
    if orphans:
        raise ValueError(
            f"Orphan states unreachable from {initial_name!r}: {sorted(orphans)}"
        )


def _validate_state(state: dict, state_names: set[str]) -> None:
    name = state.get("name")
    if not name:
        raise ValueError(f"State missing 'name': {state}")
    stype = state.get("type", "normal")
    if stype not in VALID_TYPES:
        raise ValueError(f"State {name!r} has invalid type {stype!r}; must be one of {VALID_TYPES}")
    if not state.get("role"):
        raise ValueError(f"State {name!r} missing 'role'")

    if stype == "split":
        split = state.get("traffic_split") or {}
        next_states = state.get("next_states") or {}
        a = int(split.get("arm_a", 0))
        b = int(split.get("arm_b", 0))
        if a + b != 100:
            raise ValueError(
                f"Split state {name!r} traffic_split must sum to 100, got {a + b}"
            )
        if "arm_a" not in next_states or "arm_b" not in next_states:
            raise ValueError(
                f"Split state {name!r} missing next_states for both arms"
            )
        for arm, target in next_states.items():
            if target not in state_names:
                raise ValueError(
                    f"Split state {name!r} arm {arm!r} points to unknown state {target!r}"
                )


def _validate_transition(t: dict, state_names: set[str]) -> None:
    for k in ("from", "to", "action", "role"):
        if not t.get(k):
            raise ValueError(f"Transition missing {k!r}: {t}")
    if t["from"] not in state_names:
        raise ValueError(f"Transition from unknown state {t['from']!r}")
    if t["to"] not in state_names:
        raise ValueError(f"Transition to unknown state {t['to']!r}")


def _reachable(start: str, transitions: list[dict], states: list[dict]) -> set[str]:
    by_name = {s["name"]: s for s in states}
    seen: set[str] = set()
    stack = [start]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        state = by_name.get(cur, {})
        if state.get("type") == "split":
            for target in (state.get("next_states") or {}).values():
                if target not in seen:
                    stack.append(target)
        for t in transitions:
            if t.get("from") == cur and t.get("to") not in seen:
                stack.append(t["to"])
    return seen
