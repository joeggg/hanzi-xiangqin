import argparse
import asyncio

from hanzi_xiangqin.config import get_config
from hanzi_xiangqin.data_types import load_character_list
from hanzi_xiangqin.logger import set_up_logging


def main() -> None:
    args = parse_args()

    match args.command:
        case "api":
            run_api()
        case "worker":
            run_worker()
        case "cli":
            run_cli()
        case _:
            raise RuntimeError("Invalid command")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "hanzi_xiangqin",
        description="Test your knowledge of Chinese characters",
    )
    subparsers = parser.add_subparsers(
        description="Specific command to use", dest="command", required=True
    )

    subparsers.add_parser("api", description="Run the api")
    subparsers.add_parser("worker", description="Run the tester worker")

    tester = subparsers.add_parser("cli", description="Run the tester in CLI mode")
    tester.add_argument(
        "--tester",
        "-t",
        choices=["simple"],
        default="simple",
        help="The tester algorithm to use",
    )

    return parser.parse_args()


def run_api() -> None:
    import uvicorn

    set_up_logging()
    config = get_config()
    uvicorn.run("hanzi_xiangqin.api.app:create_app", host="0.0.0.0", port=8000, reload=config.dev)


def run_worker() -> None:
    from hanzi_xiangqin.worker import worker

    set_up_logging()

    asyncio.run(worker())


def run_cli() -> None:
    from hanzi_xiangqin.testers import SimpleTester

    tester = SimpleTester(load_character_list(), bin_size=500)

    test = tester.characters()
    for char in test:
        print(char)
        answer = input("Do you know this? (y/n): ") == "y"
        try:
            test.send(answer)
        except StopIteration:
            pass

    tester.print_debug_info()
    count = tester.estimate_count()
    print(f"You know an estimated {count} characters")


if __name__ == "__main__":
    main()
