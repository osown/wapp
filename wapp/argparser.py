import argparse
from pathlib import Path


def create_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wapp.py", description="wrap as python package"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser(
        "create", help="create crafted python package"
    )
    create_parser.add_argument(
        "--debug", help="Enable debug logging", action="store_true", default=False
    )
    create_parser.add_argument(
        "--pipx",
        help="After a successful build, install via pipx",
        action="store_true",
        default=False,
    )
    create_parser.add_argument(
        "repo_url", help="Git URL containing project to be wrapped", type=str
    )
    create_parser.add_argument(
        "--package_name",
        help="Name of crafted package. Defaults to repo name",
        type=str,
    )
    create_parser.add_argument(
        "--dest_dir", help="Directory containing project to be wrapped", type=Path
    )
    create_parser.add_argument(
        "--scripts",
        help="Script files to be exposed, can renamed by <script>:<link_name>. Defaults to all .py files in the root of the git repo",
        nargs="*",
        type=str,
        default=[],
    )
    create_parser.add_argument(
        "--requires",
        help="Create requirements.txt and include listed dependency",
        nargs="+",
        type=str,
        default=[],
    )

    update_parser = subparsers.add_parser(
        "update", help="update crafted python package"
    )
    update_parser.add_argument(
        "--debug", help="Enable debug logging", action="store_true", default=False
    )
    update_parser.add_argument(
        "--pipx",
        help="After a successful build, upgrade via pipx",
        action="store_true",
        default=False,
    )
    update_parser.add_argument(
        "wrapped_dir", help="Directory containing wrapped python package", type=Path
    )

    return parser
