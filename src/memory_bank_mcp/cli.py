from __future__ import annotations

import argparse
import json

from .server import main as server_main
from .store import MemoryBankStore
from .validator import MemoryBankValidator


def main() -> None:
    parser = argparse.ArgumentParser(prog="memory-bank")
    subcommands = parser.add_subparsers(dest="command", required=True)
    validate = subcommands.add_parser("validate", help="validate Markdown and metadata")
    validate.add_argument("--json", action="store_true", dest="as_json")
    subcommands.add_parser("serve", help="start the stdio MCP server")
    arguments = parser.parse_args()
    if arguments.command == "serve":
        server_main()
        return
    result = MemoryBankValidator(MemoryBankStore.from_environment()).run()
    if arguments.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"documents={result['documents']} total_size={result['total_size']} "
            f"errors={result['errors']} warnings={result['warnings']}"
        )
        for issue in result["issues"]:
            print(
                f"{issue['severity'].upper()} {issue['code']} "
                f"{issue['path']}: {issue['message']}"
            )
    raise SystemExit(1 if result["errors"] else 0)


if __name__ == "__main__":
    main()

