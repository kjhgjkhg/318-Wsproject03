"""
日志分析模块。

负责统计清洗后的数据，计算各项指标：
- 按小时统计 INFO/WARN/ERROR 级别的日志数量
- 统计错误码分布
- 计算单日请求峰值
"""

import re
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime, date

from log_cleaner import LogEntry
from config.settings import (
    HOUR_FORMAT,
    DATE_FORMAT,
    VALID_LOG_LEVELS,
    ERROR_CODE_PATTERN,
)


class LogAnalyzer:
    """
    日志分析器。
    
    分析清洗后的日志条目，生成统计指标。
    """
    
    def __init__(self):
        """初始化分析器。"""
        self.entries: List[LogEntry] = []
        
        # 统计指标
        self.hourly_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.daily_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.error_code_distribution: Dict[str, int] = defaultdict(int)
        self.level_distribution: Dict[str, int] = defaultdict(int)
        
        # 峰值统计
        self.peak_hour: Optional[str] = None
        self.peak_hour_count: int = 0
        self.peak_day: Optional[str] = None
        self.peak_day_count: int = 0
    
    def add_entries(self, entries: List[LogEntry]) -> None:
        """
        添加日志条目进行分析。
        
        Args:
            entries: 日志条目列表
        """
        self.entries.extend(entries)
    
    def analyze(self) -> Dict[str, Any]:
        """
        执行完整分析。
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        self._analyze_hourly_stats()
        self._analyze_daily_stats()
        self._analyze_error_codes()
        self._analyze_level_distribution()
        self._calculate_peaks()
        
        return self.get_results()
    
    def _analyze_hourly_stats(self) -> None:
        """按小时统计日志级别数量。"""
        for entry in self.entries:
            if entry.timestamp and entry.level:
                hour_key = entry.timestamp.strftime(HOUR_FORMAT)
                self.hourly_stats[hour_key][entry.level] += 1
    
    def _analyze_daily_stats(self) -> None:
        """按天统计日志级别数量。"""
        for entry in self.entries:
            if entry.timestamp and entry.level:
                day_key = entry.timestamp.strftime(DATE_FORMAT)
                self.daily_stats[day_key][entry.level] += 1
    
    def _analyze_error_codes(self) -> None:
        """统计错误码分布。"""
        for entry in self.entries:
            if entry.error_code:
                self.error_code_distribution[entry.error_code] += 1
    
    def _analyze_level_distribution(self) -> None:
        """统计日志级别分布。"""
        for entry in self.entries:
            if entry.level:
                self.level_distribution[entry.level] += 1
    
    def _calculate_peaks(self) -> None:
        """计算峰值。"""
        # 计算小时峰值
        if self.hourly_stats:
            for hour, stats in self.hourly_stats.items():
                total = sum(stats.values())
                if total > self.peak_hour_count:
                    self.peak_hour_count = total
                    self.peak_hour = hour
        
        # 计算日峰值
        if self.daily_stats:
            for day, stats in self.daily_stats.items():
                total = sum(stats.values())
                if total > self.peak_day_count:
                    self.peak_day_count = total
                    self.peak_day = day
    
    def get_results(self) -> Dict[str, Any]:
        """
        获取分析结果。
        
        Returns:
            Dict[str, Any]: 分析结果字典
        """
        return {
            'summary': {
                'total_entries': len(self.entries),
                'level_distribution': dict(self.level_distribution),
                'unique_error_codes': len(self.error_code_distribution),
            },
            'hourly_stats': {k: dict(v) for k, v in self.hourly_stats.items()},
            'daily_stats': {k: dict(v) for k, v in self.daily_stats.items()},
            'error_code_distribution': dict(self.error_code_distribution),
            'peak_stats': {
                'peak_hour': self.peak_hour,
                'peak_hour_count': self.peak_hour_count,
                'peak_day': self.peak_day,
                'peak_day_count': self.peak_day_count,
            },
        }
    
    def get_hourly_summary(self) -> List[Dict[str, Any]]:
        """
        获取按小时汇总的统计列表。
        
        Returns:
            List[Dict[str, Any]]: 小时统计列表
        """
        result = []
        for hour in sorted(self.hourly_stats.keys()):
            stats = self.hourly_stats[hour]
            result.append({
                'hour': hour,
                'INFO': stats.get('INFO', 0),
                'WARN': stats.get('WARN', 0),
                'ERROR': stats.get('ERROR', 0),
                'total': sum(stats.values()),
            })
        return result
    
    def get_top_error_codes(self, n: int = 10) -> List[tuple]:
        """
        获取出现次数最多的错误码。
        
        Args:
            n: 返回前 N 个
            
        Returns:
            List[tuple]: (错误码, 次数) 列表
        """
        sorted_errors = sorted(
            self.error_code_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_errors[:n]
    
    def reset(self) -> None:
        """重置分析器状态。"""
        self.entries = []
        self.hourly_stats = defaultdict(lambda: defaultdict(int))
        self.daily_stats = defaultdict(lambda: defaultdict(int))
        self.error_code_distribution = defaultdict(int)
        self.level_distribution = defaultdict(int)
        self.peak_hour = None
        self.peak_hour_count = 0
        self.peak_day = None
        self.peak_day_count = 0


class BatchAnalyzer:
    """
    批量分析器。
    
    支持多文件的批量分析。
    """
    
    def __init__(self):
        """初始化批量分析器。"""
        self.analyzer = LogAnalyzer()
        self.processed_files: List[str] = []
        self.total_lines: int = 0
    
    def analyze_file(self, filepath: str, cleaner: Optional[Any] = None) -> List[LogEntry]:
        """
        分析单个文件。
        
        Args:
            filepath: 文件路径
            cleaner: 日志清洗器，None 则创建新实例
            
        Returns:
            List[LogEntry]: 清洗后的日志条目
        """
        from log_cleaner import LogCleaner
        
        if cleaner is None:
            cleaner = LogCleaner()
        
        entries = cleaner.clean_file(filepath)
        self.analyzer.add_entries(entries)
        self.processed_files.append(filepath)
        
        # 统计总行数（包括被过滤的）
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                self.total_lines += sum(1 for _ in f)
        except (IOError, OSError):
            pass
        
        return entries
    
    def analyze_files(self, filepaths: List[str]) -> Dict[str, Any]:
        """
        分析多个文件。
        
        Args:
            filepaths: 文件路径列表
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        from log_cleaner import LogCleaner
        
        cleaner = LogCleaner()
        
        for filepath in filepaths:
            self.analyze_file(filepath, cleaner)
        
        return self.get_results()
    
    def get_results(self) -> Dict[str, Any]:
        """
        获取完整分析结果。
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        results = self.analyzer.analyze()
        results['processing_info'] = {
            'processed_files': len(self.processed_files),
            'total_lines': self.total_lines,
            'valid_entries': len(self.analyzer.entries),
            'filtered_count': self.total_lines - len(self.analyzer.entries),
        }
        return results
    
    def reset(self) -> None:
        """重置批量分析器状态。"""
        self.analyzer.reset()
        self.processed_files = []
        self.total_lines = 0
