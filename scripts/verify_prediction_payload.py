from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_PATH = ROOT / "predictions.json"
EXPECTED_TRACK_COUNT = 22
EXPECTED_DRIVER_COUNT = 22
EXPECTED_PROBABILITY_ROWS = 10


def _driver_order(rows: list[dict[str, object]]) -> tuple[str, ...]:
    return tuple(str(row["driver"]) for row in rows)


def main() -> None:
    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    tracks = payload["tracks"]
    if len(tracks) != EXPECTED_TRACK_COUNT:
        raise AssertionError(f"Expected {EXPECTED_TRACK_COUNT} tracks, found {len(tracks)}")

    for mode in ("qualifying", "race"):
        dry_orders = []
        wet_orders = []
        changed_by_weather = []

        for rain_key, orders in (("0", dry_orders), ("1", wet_orders)):
            for track in tracks:
                scenario = payload["predictions"][mode][rain_key][track]
                ranking = scenario["ranking"]
                probabilities = scenario["probabilities"]
                if len(ranking) != EXPECTED_DRIVER_COUNT:
                    raise AssertionError(f"{mode}/{rain_key}/{track} has {len(ranking)} ranking rows")
                if len(probabilities) != EXPECTED_PROBABILITY_ROWS:
                    raise AssertionError(
                        f"{mode}/{rain_key}/{track} has {len(probabilities)} probability rows"
                    )
                orders.append(_driver_order(ranking))

        for track in tracks:
            dry = _driver_order(payload["predictions"][mode]["0"][track]["ranking"])
            wet = _driver_order(payload["predictions"][mode]["1"][track]["ranking"])
            if dry != wet:
                changed_by_weather.append(track)

        if len(set(dry_orders)) < 2 or len(set(wet_orders)) < 2:
            raise AssertionError(f"{mode} predictions do not vary enough by track")
        if len(changed_by_weather) < 2:
            raise AssertionError(f"{mode} predictions do not vary enough by weather")

        print(
            f"{mode}: {len(set(dry_orders))} dry orders, "
            f"{len(set(wet_orders))} wet orders, "
            f"{len(changed_by_weather)} weather-sensitive tracks"
        )

    print(f"Verified {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
