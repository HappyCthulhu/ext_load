from __future__ import annotations

import sys
from pathlib import Path

import loguru
from loguru import logger as loguru_logger

from server.settings import BASE_DIR

file_name = 'file.log'
DL = 'DEBUG'  # Debug Level
IL = 'INFO'  # Info Level
CL = 'CRITICAL'  # Critical Level


def set_logger() -> loguru.Logger:
    loguru_logger.remove()

    logger_format_debug: str = (
        "<green>{time:DD-MM-YY HH:mm:ss}</> | <bold><blue>{level}</></> | "
        "<cyan>{file}:{function}:{line}</> | <blue>{message}</> | <blue>🛠</>"
    )
    logger_format_info: str = (
        "<green>{time:DD-MM-YY HH:mm:ss}</> | <bold><fg 255,255,255>{level}</></> | "
        "<cyan>{file}:{function}:{line}</> | <fg 255,255,255>{message}</> | <fg 255,255,255>✔</>"
    )
    logger_format_critical: str = (
        "<green>{time:DD-MM-YY HH:mm:ss}</> | <RED><fg 255,255,255>{level}</></> | "
        "<cyan>{file}:{function}:{line}</> | <fg 255,255,255><RED>{message}</></> | "
        "<RED><fg 255,255,255>❌</></>"
    )

    loguru_logger.add(
        sys.stderr,
        format=logger_format_debug,
        level=DL,
        filter=lambda record: record["level"].name == DL,
    )
    loguru_logger.add(
        sys.stderr,
        format=logger_format_info,
        level=IL,
        filter=lambda record: record["level"].name == IL,
    )
    loguru_logger.add(
        sys.stderr,
        format=logger_format_critical,
        level=CL,
        filter=lambda record: record["level"].name == CL,
    )
    loguru_logger.add(Path(logging_dp, file_name), level=DL, rotation='5 MB')
    loguru_logger.add(Path(logging_dp, file_name), level=IL, rotation='5 MB')
    loguru_logger.add(Path(logging_dp, file_name), level=CL, rotation='5 MB')

    return loguru_logger


logging_dp = f'{BASE_DIR}/logging_dir'
logger = set_logger()
