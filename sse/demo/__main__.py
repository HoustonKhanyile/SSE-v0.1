from __future__ import annotations

import argparse
import json
import sys

from sse.demo.examples import EXAMPLES
from sse.orchestrator import RunConfig, run_sse


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SSE demo")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--example", choices=sorted(EXAMPLES.keys()), help="Run a predefined example")
    group.add_argument("--situation", help="Custom situation text")
    parser.add_argument("--depth", choices=["default", "deep"], default="default")
    parser.add_argument("--alternatives", action="store_true", help="Include alternative outcomes")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    if args.example:
        example = EXAMPLES[args.example]
        situation_text = example.situation
        config = RunConfig(
            depth=args.depth,
            include_alternatives=args.alternatives,
            example_id=example.id,
        )
    else:
        situation_text = args.situation
        config = RunConfig(depth=args.depth, include_alternatives=args.alternatives)

    result = run_sse(situation_text, config)
    print(json.dumps(result.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
