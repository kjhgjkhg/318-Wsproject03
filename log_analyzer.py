"""
log_analyzer.py - 日志分析模块

负责统计清洗后的数据，计算各项指标。
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from datetime import datetime

from log_cleaner import LogLine, LogLineStatus


@dataclass
class HourlyStats:
    """
    小时统计数据类。
    
    Attributes:
        hour: 小时（0-23）
        info_count: INFO 级别数量
        warn_count: WARN 级别数量
        error_count: ERROR 级别数量
    """
    hour: int
    info_count: int = 0
    warn_count: int = 0
    error_count: int = 0
    
    @property
    def total(self) -> int:
        """计算总数。"""
        return self.info_count + self.warn_count + self.error_count


@dataclass
class DailyPeak:
    """
    单日峰值数据类。
    
    Attributes:
        date: 日期字符串
        count: 日志数量
    """
    date: str
    count: int = 0


@dataclass
class AnalysisResult:
    """
    分析结果数据类。
    
    Attributes:
        total_files: 处理的文件总数
        total_lines: 总行数
        valid_lines: 有效行数
        hourly_stats: 按小时统计
        error_code_distribution: 错误码分布
        daily_peak: 单日峰值
        level_distribution: 日志级别分布
        processing_time: 处理耗时
    """
    total_files: int = 0
    total_lines: int = 0
    valid_lines: int = 0
    hourly_stats: Dict[int, HourlyStats] = field(default_factory=dict)
    error_code_distribution: Dict[str, int] = field(default_factory=dict)
    daily_peak: Optional[DailyPeak] = None
    level_distribution: Dict[str, int] = field(default_factory=dict)
    processing_time: float = 0.0


class LogAnalyzer:
    """
    日志分析器类。
    
    负责统计清洗后的数据，计算各项指标。
    """
    
    def __init__(self) -> None:
        """初始化日志分析器。"""
        self._hourly_stats: Dict[int, HourlyStats] = {}
        self._error_code_counter: Counter = Counter()
        self._level_counter: Counter = Counter()
        self._daily_counter: Counter = Counter()
        self._total_lines: int = 0
        self._valid_lines: int = 0
        self._total_files: int = 0
    
    def reset(self) -> None:
        """重置所有统计数据。"""
        self._hourly_stats = {}
        self._error_code_counter = Counter()
        self._level_counter = Counter()
        self._daily_counter = Counter()
        self._total_lines = 0
        self._valid_lines = 0
        self._total_files = 0
    
    def _init_hour_stats(self, hour: int) -> None:
        """
        初始化小时统计数据。
        
        Args:
            hour: 小时（0-23）
        """
        if hour not in self._hourly_stats:
            self._hourly_stats[hour] = HourlyStats(hour=hour)
    
    def _extract_date(self, timestamp: Optional[str]) -> Optional[str]:
        """
        从时间戳中提取日期。
        
        Args:
            timestamp: 时间戳字符串
            
        Returns:
            Optional[str]: 日期字符串（YYYY-MM-DD）
        """
        if not timestamp:
            return None
        
        date_match = None
        
        patterns = [
            (r'(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),
            (r'(\d{4}/\d{2}/\d{2})', '%Y/%m/%d'),
            (r'(\d{2}-\d{2}-\d{4})', '%m-%d-%Y'),
            (r'(\d{2}/\d{2}/\d{4})', '%m/%d/%Y'),
        ]
        
        for pattern, _ in patterns:
            match = __import__('re').search(pattern, timestamp)
            if match:
                date_match = match.group(1)
                break
        
        return date_match
    
    def analyze_line(self, log_line: LogLine) -> None:
        """
        分析单条日志行。
        
        Args:
            log_line: 日志行对象
        """
        self._total_lines += 1
        
        if log_line.status != LogLineStatus.PARSED:
            return
        
        self._valid_lines += 1
        
        if log_line.level:
            self._level_counter[log_line.level] += 1
        
        if log_line.hour is not None:
            self._init_hour_stats(log_line.hour)
            hour_stats = self._hourly_stats[log_line.hour]
            
            if log_line.level == "INFO":
                hour_stats.info_count += 1
            elif log_line.level == "WARN":
                hour_stats.warn_count += 1
            elif log_line.level == "ERROR":
                hour_stats.error_count += 1
        
        if log_line.error_code:
            self._error_code_counter[log_line.error_code] += 1
        
        date_str = self._extract_date(log_line.timestamp)
        if date_str:
            self._daily_counter[date_str] += 1
    
    def analyze_lines(self, log_lines: List[LogLine]) -> None:
        """
        批量分析日志行。
        
        Args:
            log_lines: 日志行列表
        """
        for line in log_lines:
            self.analyze_line(line)
    
    def add_file_count(self, count: int = 1) -> None:
        """
        增加处理文件计数。
        
        Args:
            count: 增加的数量
        """
        self._total_files += count
    
    def get_hourly_stats(self) -> Dict[int, HourlyStats]:
        """
        获取按小时统计数据。
        
        Returns:
            Dict[int, HourlyStats]: 小时统计数据字典
        """
        for hour in range(24):
            self._init_hour_stats(hour)
        return dict(sorted(self._hourly_stats.items()))
    
    def get_error_code_distribution(self, top_n: int = 10) -> Dict[str, int]:
        """
        获取错误码分布（Top N）。
        
        Args:
            top_n: 返回前 N 个
            
        Returns:
            Dict[str, int]: 错误码分布字典
        """
        return dict(self._error_code_counter.most_common(top_n))
    
    def get_all_error_codes(self) -> Dict[str, int]:
        """
        获取所有错误码分布。
        
        Returns:
            Dict[str, int]: 错误码分布字典
        """
        return dict(self._error_code_counter.most_common())
    
    def get_level_distribution(self) -> Dict[str, int]:
        """
        获取日志级别分布。
        
        Returns:
            Dict[str, int]: 日志级别分布字典
        """
        return dict(self._level_counter)
    
    def get_daily_peak(self) -> Optional[DailyPeak]:
        """
        获取单日请求峰值。
        
        Returns:
            Optional[DailyPeak]: 单日峰值数据
        """
        if not self._daily_counter:
            return None
        
        peak_date, peak_count = self._daily_counter.most_common(1)[0]
        return DailyPeak(date=peak_date, count=peak_count)
    
    def get_result(self) -> AnalysisResult:
        """
        获取分析结果。
        
        Returns:
            AnalysisResult: 分析结果对象
        """
        return AnalysisResult(
            total_files=self._total_files,
            total_lines=self._total_lines,
            valid_lines=self._valid_lines,
            hourly_stats=self.get_hourly_stats(),
            error_code_distribution=self.get_all_error_codes(),
            daily_peak=self.get_daily_peak(),
            level_distribution=self.get_level_distribution()
        )
    
    def get_summary(self) -> str:
        """
        获取分析摘要。
        
        Returns:
            str: 分析摘要字符串
        """
        lines = [
            "=" * 60,
            "日志分析摘要",
            "=" * 60,
            "",
            f"处理文件数: {self._total_files}",
            f"总行数: {self._total_lines}",
            f"有效行数: {self._valid_lines}",
            "",
            "日志级别分布:",
        ]
        
        for level, count in sorted(self._level_counter.items()):
            lines.append(f"  {level}: {count}")
        
        lines.append("")
        lines.append("错误码分布 (Top 10):")
        
        for code, count in self._error_code_counter.most_common(10):
            lines.append(f"  错误码 {code}: {count} 次")
        
        peak = self.get_daily_peak()
        if peak:
            lines.append("")
            lines.append(f"单日峰值: {peak.date} ({peak.count} 条)")
        
        return "\n".join(lines)
