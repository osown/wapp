#!/usr/bin/env python

import logging
import sys

import coloredlogs

from wapp.argparser import create_argparser

logger = logging.getLogger(__name__)


def setup_logging(log_level=logging.INFO):
    if log_level == logging.INFO:
        coloredlogs.DEFAULT_LOG_FORMAT = "%(message)s"
    else:
        coloredlogs.DEFAULT_LOG_FORMAT = "%(levelname)s:%(name)s: %(message)s"

    coloredlogs.DEFAULT_FIELD_STYLES = {}
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        "warning": {"color": "yellow"},
        "error": {"color": "red"},
        "critical": {"color": "red", "bold": True},
    }
    coloredlogs.install(level=log_level)
    logging.getLogger().setLevel(level=log_level)
    logger.setLevel(level=log_level)


def main():
    try:
        args = sys.argv[1:] or ["--help"]

        parser = create_argparser()
        parsed_args = parser.parse_args(args)

        log_level = (
            logging.DEBUG
            if hasattr(parsed_args, "debug") and parsed_args.debug
            else logging.INFO
        )
        setup_logging(log_level)

        from wapp.commands.create import create  # pylint: disable=C0415
        from wapp.commands.update import update  # pylint: disable=C0415

        command = parsed_args.command  # type: str
        if command == "create":
            create(parsed_args)
        elif command == "update":
            update(parsed_args)
        else:
            raise RuntimeError("Command not implemented")

    except RuntimeError as e:
        logger.error(e)
        sys.exit(1)
    except Exception as e:
        logger.error("Raised unhandled exception:")
        logger.exception(e)
        sys.exit(-1)


if __name__ == "__main__":
    main()
