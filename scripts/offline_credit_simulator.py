"""Offline CLI facade for the packaged pure simulation engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from flow_otomatis.application.services.offline_credit_simulation import (
    InvalidSimulationInput as InvalidSimulationInput,
    simulate,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline multi-profile credit planning (NO Google Flow access)."
    )
    parser.add_argument("input_json", type=Path, help="Synthetic input JSON")
    parser.add_argument("--output", type=Path, help="Optional NEW JSON output path")
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.input_json.read_text(encoding="utf-8"))
        report = simulate(data)
        output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output is None:
            sys.stdout.write(output)
        else:
            # No-clobber: never overwrite the operator's existing plan or report.
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(output)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"OFFLINE SIMULATION BLOCKED: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
