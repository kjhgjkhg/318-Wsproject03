"""
配置常量模块。

定义项目使用的所有常量，包括路径、文件名模板、日志级别配置、清洗规则等。
所有路径配置集中在此，便于统一管理和修改。
"""

import os
from typing import Final, Set, List

# =============================================================================
# 目录路径配置（绝对路径，基于脚本所在位置）
# =============================================================================

# 项目根目录（基于当前文件位置计算）
PROJECT_ROOT: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 输入目录（只读）- 日志文件存放处
RAW_LOGS_DIR: Final[str] = os.path.join(PROJECT_ROOT, "raw_logs")

# 输出目录（只写）- 用于保存统计报告和摘要
PROCESSED_OUTPUT_DIR: Final[str] = os.path.join(PROJECT_ROOT, "processed_output")

# =============================================================================
# 受保护文件配置
# =============================================================================

# 严禁处理的文件（在 raw_logs 目录中）
BLACKLIST_FILE: Final[str] = "do_not_modify_blacklist.log"
BLACKLIST_FILE_PATH: Final[str] = os.path.join(RAW_LOGS_DIR, BLACKLIST_FILE)

# =============================================================================
# 输出文件名配置
# =============================================================================

# JSON 格式统计报告
STATS_REPORT_FILENAME: Final[str] = "stats_report.json"
STATS_REPORT_PATH: Final[str] = os.path.join(PROCESSED_OUTPUT_DIR, STATS_REPORT_FILENAME)

# 纯文本可视化摘要
SUMMARY_FILENAME: Final[str] = "summary.txt"
SUMMARY_PATH: Final[str] = os.path.join(PROCESSED_OUTPUT_DIR, SUMMARY_FILENAME)

# 增量处理记录文件
PROCESSED_RECORDS_FILENAME: Final[str] = ".processed_records.json"
PROCESSED_RECORDS_PATH: Final[str] = os.path.join(PROCESSED_OUTPUT_DIR, PROCESSED_RECORDS_FILENAME)

# =============================================================================
# 文件匹配规则
# =============================================================================

# 支持的日志文件扩展名
VALID_EXTENSIONS: Final[Set[str]] = {".log", ".txt"}

# 文件编码
FILE_ENCODING: Final[str] = "utf-8"

# =============================================================================
# 日志级别配置
# =============================================================================

# 需要过滤掉的日志级别（清洗规则）
FILTERED_LEVELS: Final[Set[str]] = {"DEBUG"}

# 需要统计的日志级别
VALID_LOG_LEVELS: Final[Set[str]] = {"INFO", "WARN", "ERROR"}

# 所有日志级别
ALL_LOG_LEVELS: Final[Set[str]] = {"DEBUG", "INFO", "WARN", "ERROR"}

# =============================================================================
# 时间格式配置
# =============================================================================

# 标准日志时间格式（用于匹配和解析）
# 支持格式：2024-01-15 14:30:25 或 2024-01-15T14:30:25
TIME_FORMAT_PATTERNS: Final[List[str]] = [
    r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}",  # 2024-01-15 14:30:25
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",     # 2024-01-15T14:30:25
    r"\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}",  # 2024/01/15 14:30:25
]

# 用于解析时间的 strptime 格式
DATETIME_PARSE_FORMATS: Final[List[str]] = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
]

# =============================================================================
# 正则表达式模式
# =============================================================================

# 日志级别匹配模式
LOG_LEVEL_PATTERN: Final[str] = r"\b(DEBUG|INFO|WARN|ERROR)\b"

# 错误码匹配模式（假设格式为 ERR-XXX 或 ERROR_XXX）
ERROR_CODE_PATTERN: Final[str] = r"\b(ERR-?\d+|ERROR[_-]?\d+)\b"

# 请求ID匹配模式（用于统计请求）
REQUEST_ID_PATTERN: Final[str] = r"\b(request[_-]?id[:=]\s*[\w-]+)\b"

# =============================================================================
# 统计配置
# =============================================================================

# 每小时时间段格式
HOUR_FORMAT: Final[str] = "%Y-%m-%d %H:00"

# 日期格式
DATE_FORMAT: Final[str] = "%Y-%m-%d"

# =============================================================================
# 报告格式配置
# =============================================================================

# 报告分隔线
REPORT_SEPARATOR: Final[str] = "=" * 60
REPORT_SUB_SEPARATOR: Final[str] = "-" * 40

# JSON 缩进
JSON_INDENT: Final[int] = 2

# =============================================================================
# 错误提示信息模板
# =============================================================================

ERROR_INPUT_DIR_NOT_FOUND: Final[str] = "错误：输入目录不存在: {}"
ERROR_OUTPUT_DIR_NOT_FOUND: Final[str] = "错误：输出目录不存在，正在创建: {}"
ERROR_NO_LOG_FILES: Final[str] = "警告：在 {} 中未找到任何日志文件"
ERROR_FILE_READ: Final[str] = "错误：无法读取文件 {}: {}"
ERROR_BLACKLIST_FILE: Final[str] = "警告：跳过受保护文件: {}"
ERROR_INVALID_TIME_FORMAT: Final[str] = "错误：时间格式不合法: {}"

# =============================================================================
# 成功提示信息模板
# =============================================================================

SUCCESS_REPORT_SAVED: Final[str] = "报告已保存至: {}"
SUCCESS_PROCESSING_COMPLETE: Final[str] = "处理完成，共处理 {} 个文件"
SUCCESS_SKIPPED_FILES: Final[str] = "跳过 {} 个已处理文件"
