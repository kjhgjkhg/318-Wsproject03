"""
日志清洗模块。

负责按规则清洗单条日志行，过滤无效数据。
支持过滤 DEBUG 级别、空行、时间格式不合法的日志行。
"""

import re
from typing import Optional, Dict, Any, List
from datetime import datetime

from config.settings import (
    FILTERED_LEVELS,
    VALID_LOG_LEVELS,
    TIME_FORMAT_PATTERNS,
    DATETIME_PARSE_FORMATS,
    LOG_LEVEL_PATTERN,
    ERROR_CODE_PATTERN,
)

# 所有日志级别常量
ALL_LOG_LEVELS = {"DEBUG", "INFO", "WARN", "ERROR"}


class LogEntry:
    """
    日志条目数据结构。
    
    解析并存储单条日志的信息。
    """
    
    def __init__(self, raw_line: str):
        """
        初始化日志条目。
        
        Args:
            raw_line: 原始日志行
        """
        self.raw_line = raw_line
        self.timestamp: Optional[datetime] = None
        self.level: Optional[str] = None
        self.message: str = ""
        self.error_code: Optional[str] = None
        self.is_valid: bool = False
        
        self._parse()
    
    def _parse(self) -> None:
        """解析日志行。"""
        if not self.raw_line or not self.raw_line.strip():
            return
        
        line = self.raw_line.strip()
        
        # 提取时间戳
        self.timestamp = self._extract_timestamp(line)
        
        # 提取日志级别
        self.level = self._extract_level(line)
        
        # 提取错误码
        self.error_code = self._extract_error_code(line)
        
        # 提取消息内容（简化处理：移除时间戳和级别后的部分）
        self.message = self._extract_message(line)
        
        # 验证有效性
        self.is_valid = self._validate()
    
    def _extract_timestamp(self, line: str) -> Optional[datetime]:
        """
        从日志行中提取时间戳。
        
        Args:
            line: 日志行
            
        Returns:
            Optional[datetime]: 解析成功返回 datetime 对象
        """
        for pattern in TIME_FORMAT_PATTERNS:
            match = re.search(pattern, line)
            if match:
                time_str = match.group(0)
                # 尝试不同的解析格式
                for fmt in DATETIME_PARSE_FORMATS:
                    try:
                        return datetime.strptime(time_str, fmt)
                    except ValueError:
                        continue
        return None
    
    def _extract_level(self, line: str) -> Optional[str]:
        """
        从日志行中提取日志级别。
        
        Args:
            line: 日志行
            
        Returns:
            Optional[str]: 日志级别
        """
        match = re.search(LOG_LEVEL_PATTERN, line, re.IGNORECASE)
        if match:
            level = match.group(1).upper()
            if level in ALL_LOG_LEVELS:
                return level
        return None
    
    def _extract_error_code(self, line: str) -> Optional[str]:
        """
        从日志行中提取错误码。
        
        Args:
            line: 日志行
            
        Returns:
            Optional[str]: 错误码
        """
        match = re.search(ERROR_CODE_PATTERN, line, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return None
    
    def _extract_message(self, line: str) -> str:
        """
        提取消息内容。
        
        Args:
            line: 日志行
            
        Returns:
            str: 消息内容
        """
        # 移除时间戳
        message = line
        for pattern in TIME_FORMAT_PATTERNS:
            message = re.sub(pattern, "", message, count=1)
        
        # 移除日志级别标记
        message = re.sub(LOG_LEVEL_PATTERN, "", message, flags=re.IGNORECASE)
        
        # 清理多余空格
        message = re.sub(r"\s+", " ", message).strip()
        
        return message
    
    def _validate(self) -> bool:
        """
        验证日志条目是否有效。
        
        有效条件：
        1. 非空行
        2. 时间戳格式合法
        3. 日志级别不是被过滤的级别
        
        Returns:
            bool: 有效返回 True
        """
        # 检查是否为空行
        if not self.raw_line or not self.raw_line.strip():
            return False
        
        # 检查时间戳
        if self.timestamp is None:
            return False
        
        # 检查日志级别
        if self.level and self.level in FILTERED_LEVELS:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式。
        
        Returns:
            Dict[str, Any]: 日志条目字典
        """
        return {
            'raw_line': self.raw_line,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'level': self.level,
            'message': self.message,
            'error_code': self.error_code,
            'is_valid': self.is_valid,
        }


class LogCleaner:
    """
    日志清洗器。
    
    批量清洗日志文件，过滤无效行。
    """
    
    def __init__(self):
        """初始化清洗器。"""
        self.cleaned_entries: List[LogEntry] = []
        self.filtered_count = 0
        self.error_count = 0
    
    def clean_line(self, line: str) -> Optional[LogEntry]:
        """
        清洗单条日志行。
        
        Args:
            line: 原始日志行
            
        Returns:
            Optional[LogEntry]: 有效返回 LogEntry，无效返回 None
        """
        entry = LogEntry(line)
        
        if entry.is_valid:
            return entry
        else:
            self.filtered_count += 1
            if entry.level == "ERROR":
                self.error_count += 1
            return None
    
    def clean_file(self, filepath: str) -> List[LogEntry]:
        """
        清洗整个日志文件。
        
        Args:
            filepath: 日志文件路径
            
        Returns:
            List[LogEntry]: 清洗后的日志条目列表
        """
        from config.settings import FILE_ENCODING
        
        entries = []
        
        try:
            with open(filepath, 'r', encoding=FILE_ENCODING, errors='replace') as f:
                for line in f:
                    entry = self.clean_line(line)
                    if entry:
                        entries.append(entry)
        except (IOError, OSError) as e:
            print(f"错误：无法读取文件 {filepath}: {e}")
        
        self.cleaned_entries.extend(entries)
        return entries
    
    def clean_lines(self, lines: List[str]) -> List[LogEntry]:
        """
        清洗多行日志。
        
        Args:
            lines: 日志行列表
            
        Returns:
            List[LogEntry]: 清洗后的日志条目列表
        """
        entries = []
        for line in lines:
            entry = self.clean_line(line)
            if entry:
                entries.append(entry)
        
        self.cleaned_entries.extend(entries)
        return entries
    
    def get_stats(self) -> Dict[str, int]:
        """
        获取清洗统计信息。
        
        Returns:
            Dict[str, int]: 统计信息
        """
        return {
            'cleaned_count': len(self.cleaned_entries),
            'filtered_count': self.filtered_count,
            'error_count': self.error_count,
        }
    
    def reset(self) -> None:
        """重置清洗器状态。"""
        self.cleaned_entries = []
        self.filtered_count = 0
        self.error_count = 0
