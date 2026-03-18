"""
log_cleaner.py - 日志清洗模块

负责按规则清洗单条日志行，过滤无效数据。
"""

import re
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field
from enum import Enum

from config.settings import (
    SKIP_LOG_LEVELS,
    VALID_LOG_LEVELS,
    TIME_PATTERNS,
    ERROR_CODE_PATTERN,
    FALLBACK_ENCODINGS
)


class LogLineStatus(Enum):
    """日志行状态枚举。"""
    VALID = "valid"
    EMPTY = "empty"
    DEBUG_LEVEL = "debug_level"
    INVALID_TIME = "invalid_time"
    PARSED = "parsed"


@dataclass
class LogLine:
    """
    日志行数据类。
    
    Attributes:
        raw_content: 原始内容
        content: 清洗后的内容
        level: 日志级别
        timestamp: 时间戳
        hour: 小时（用于统计）
        error_code: 错误码（如果有）
        status: 日志行状态
        line_number: 行号
    """
    raw_content: str
    content: str = field(default="", init=False)
    level: Optional[str] = field(default=None, init=False)
    timestamp: Optional[str] = field(default=None, init=False)
    hour: Optional[int] = field(default=None, init=False)
    error_code: Optional[str] = field(default=None, init=False)
    status: LogLineStatus = field(default=LogLineStatus.VALID, init=False)
    line_number: int = field(default=0, init=False)
    
    def __post_init__(self) -> None:
        """初始化后处理。"""
        self.content = self.raw_content.strip()


class LogCleaner:
    """
    日志清洗器类。
    
    负责按规则清洗单条日志行，过滤无效数据。
    """
    
    def __init__(self) -> None:
        """初始化日志清洗器。"""
        self._time_patterns = [re.compile(p) for p in TIME_PATTERNS]
        self._error_code_pattern = re.compile(ERROR_CODE_PATTERN, re.IGNORECASE)
        self._level_pattern = re.compile(
            r'\b(DEBUG|INFO|WARN|WARNING|ERROR)\b',
            re.IGNORECASE
        )
        self._stats: Dict[str, int] = {
            "total_lines": 0,
            "valid_lines": 0,
            "empty_lines": 0,
            "debug_lines": 0,
            "invalid_time_lines": 0
        }
    
    def reset_stats(self) -> None:
        """重置统计信息。"""
        for key in self._stats:
            self._stats[key] = 0
    
    def is_empty_line(self, line: str) -> bool:
        """
        检查是否为空行。
        
        Args:
            line: 日志行内容
            
        Returns:
            bool: 是否为空行
        """
        return not line or not line.strip()
    
    def contains_debug_level(self, line: str) -> bool:
        """
        检查是否包含 DEBUG 级别。
        
        Args:
            line: 日志行内容
            
        Returns:
            bool: 是否包含 DEBUG 级别
        """
        match = self._level_pattern.search(line)
        if match:
            level = match.group(1).upper()
            return level in SKIP_LOG_LEVELS
        return False
    
    def extract_log_level(self, line: str) -> Optional[str]:
        """
        提取日志级别。
        
        Args:
            line: 日志行内容
            
        Returns:
            Optional[str]: 日志级别
        """
        match = self._level_pattern.search(line)
        if match:
            level = match.group(1).upper()
            if level == "WARNING":
                level = "WARN"
            if level in VALID_LOG_LEVELS:
                return level
        return None
    
    def has_valid_time_format(self, line: str) -> bool:
        """
        检查时间格式是否合法。
        
        Args:
            line: 日志行内容
            
        Returns:
            bool: 时间格式是否合法
        """
        for pattern in self._time_patterns:
            if pattern.search(line):
                return True
        return False
    
    def extract_timestamp(self, line: str) -> Optional[str]:
        """
        提取时间戳。
        
        Args:
            line: 日志行内容
            
        Returns:
            Optional[str]: 时间戳字符串
        """
        for pattern in self._time_patterns:
            match = pattern.search(line)
            if match:
                return match.group(0).strip('[')
        return None
    
    def extract_hour(self, timestamp: Optional[str]) -> Optional[int]:
        """
        从时间戳中提取小时。
        
        Args:
            timestamp: 时间戳字符串
            
        Returns:
            Optional[int]: 小时数
        """
        if not timestamp:
            return None
        
        time_match = re.search(r'(\d{2}):\d{2}:\d{2}', timestamp)
        if time_match:
            return int(time_match.group(1))
        return None
    
    def extract_error_code(self, line: str) -> Optional[str]:
        """
        提取错误码。
        
        Args:
            line: 日志行内容
            
        Returns:
            Optional[str]: 错误码
        """
        match = self._error_code_pattern.search(line)
        if match:
            return match.group(1)
        return None
    
    def clean_line(self, raw_line: str, line_number: int = 0) -> LogLine:
        """
        清洗单条日志行。
        
        Args:
            raw_line: 原始日志行
            line_number: 行号
            
        Returns:
            LogLine: 清洗后的日志行对象
        """
        self._stats["total_lines"] += 1
        
        log_line = LogLine(raw_content=raw_line)
        log_line.line_number = line_number
        
        if self.is_empty_line(raw_line):
            log_line.status = LogLineStatus.EMPTY
            self._stats["empty_lines"] += 1
            return log_line
        
        if self.contains_debug_level(raw_line):
            log_line.status = LogLineStatus.DEBUG_LEVEL
            self._stats["debug_lines"] += 1
            return log_line
        
        if not self.has_valid_time_format(raw_line):
            log_line.status = LogLineStatus.INVALID_TIME
            self._stats["invalid_time_lines"] += 1
            return log_line
        
        log_line.level = self.extract_log_level(raw_line)
        log_line.timestamp = self.extract_timestamp(raw_line)
        log_line.hour = self.extract_hour(log_line.timestamp)
        log_line.error_code = self.extract_error_code(raw_line)
        log_line.status = LogLineStatus.PARSED
        self._stats["valid_lines"] += 1
        
        return log_line
    
    def clean_lines(self, raw_lines: List[str]) -> List[LogLine]:
        """
        批量清洗日志行。
        
        Args:
            raw_lines: 原始日志行列表
            
        Returns:
            List[LogLine]: 清洗后的日志行列表
        """
        return [
            self.clean_line(line, line_number=i)
            for i, line in enumerate(raw_lines, start=1)
        ]
    
    def filter_valid_lines(self, log_lines: List[LogLine]) -> List[LogLine]:
        """
        过滤出有效的日志行。
        
        Args:
            log_lines: 日志行列表
            
        Returns:
            List[LogLine]: 有效日志行列表
        """
        return [
            line for line in log_lines
            if line.status == LogLineStatus.PARSED
        ]
    
    def get_stats(self) -> Dict[str, int]:
        """
        获取清洗统计信息。
        
        Returns:
            Dict[str, int]: 统计信息字典
        """
        return self._stats.copy()


class LogFileReader:
    """
    日志文件读取器类。
    """
    
    @staticmethod
    def read_file(filepath: str) -> Tuple[List[str], Optional[str]]:
        """
        读取日志文件内容。
        
        Args:
            filepath: 文件路径
            
        Returns:
            Tuple[List[str], Optional[str]]: (行列表, 使用的编码)
        """
        for encoding in FALLBACK_ENCODINGS:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                lines = content.splitlines()
                return lines, encoding
            except UnicodeDecodeError:
                continue
            except FileNotFoundError:
                print(f"文件不存在: {filepath}")
                return [], None
            except PermissionError:
                print(f"无权限读取文件: {filepath}")
                return [], None
            except Exception as e:
                print(f"读取文件时发生错误: {filepath} - {str(e)}")
                return [], None
        
        print(f"无法解码文件: {filepath}")
        return [], None
