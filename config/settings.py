"""
config/settings.py - 全局配置模块

存放路径常量、日志级别配置、清洗规则等全局设置。
"""

import os
from typing import Final, List, Set

BASE_DIR: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_LOGS_DIR: Final[str] = os.path.join(BASE_DIR, "raw_logs")

PROCESSED_OUTPUT_DIR: Final[str] = os.path.join(BASE_DIR, "processed_output")

BLACKLIST_FILE_NAME: Final[str] = "do_not_modify_blacklist.log"

STATS_REPORT_FILE: Final[str] = "stats_report.json"

SUMMARY_FILE: Final[str] = "summary.txt"

CHECKSUM_CACHE_FILE: Final[str] = ".processed_cache.json"

LOG_EXTENSIONS: Final[Set[str]] = {".log", ".txt"}

LOG_LEVELS: Final[Set[str]] = {"DEBUG", "INFO", "WARN", "ERROR", "WARNING"}

VALID_LOG_LEVELS: Final[Set[str]] = {"INFO", "WARN", "ERROR", "WARNING"}

SKIP_LOG_LEVELS: Final[Set[str]] = {"DEBUG"}

TIME_PATTERNS: Final[List[str]] = [
    r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}",
    r"\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}",
    r"\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2}",
    r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}",
    r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
    r"\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}",
]

ERROR_CODE_PATTERN: Final[str] = r"(?:error_code|code|err)[\s:=]+(\d+)"

ENCODING: Final[str] = "utf-8"

FALLBACK_ENCODINGS: Final[List[str]] = ["utf-8", "gbk", "gb2312", "latin-1"]

REPORT_SEPARATOR: Final[str] = "=" * 60

REPORT_LINE: Final[str] = "-" * 60
