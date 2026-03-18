"""
log_reporter.py - 日志报告生成模块

负责生成 JSON 报告和文本摘要。
"""

import os
import json
from typing import Dict, Optional, Tuple
from datetime import datetime

from log_analyzer import AnalysisResult, HourlyStats, DailyPeak
from config.settings import (
    PROCESSED_OUTPUT_DIR,
    STATS_REPORT_FILE,
    SUMMARY_FILE,
    ENCODING,
    REPORT_SEPARATOR,
    REPORT_LINE
)


class LogReporter:
    """
    日志报告生成器类。
    
    负责生成 JSON 报告和文本摘要。
    """
    
    def __init__(self, output_dir: Optional[str] = None) -> None:
        """
        初始化报告生成器。
        
        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = output_dir or PROCESSED_OUTPUT_DIR
        self._ensure_output_dir()
    
    def _ensure_output_dir(self) -> bool:
        """
        确保输出目录存在。
        
        Returns:
            bool: 是否成功
        """
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建输出目录失败: {str(e)}")
            return False
    
    def _hourly_stats_to_dict(self, hourly_stats: Dict[int, HourlyStats]) -> Dict:
        """
        将小时统计数据转换为字典。
        
        Args:
            hourly_stats: 小时统计数据
            
        Returns:
            Dict: 字典格式数据
        """
        result = {}
        for hour, stats in hourly_stats.items():
            result[str(hour)] = {
                "hour": stats.hour,
                "info_count": stats.info_count,
                "warn_count": stats.warn_count,
                "error_count": stats.error_count,
                "total": stats.total
            }
        return result
    
    def _daily_peak_to_dict(self, daily_peak: Optional[DailyPeak]) -> Optional[Dict]:
        """
        将单日峰值数据转换为字典。
        
        Args:
            daily_peak: 单日峰值数据
            
        Returns:
            Optional[Dict]: 字典格式数据
        """
        if daily_peak is None:
            return None
        
        return {
            "date": daily_peak.date,
            "count": daily_peak.count
        }
    
    def generate_json_report(self, result: AnalysisResult) -> Dict:
        """
        生成 JSON 格式的统计报告数据。
        
        Args:
            result: 分析结果
            
        Returns:
            Dict: JSON 格式的报告数据
        """
        report = {
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "tool_version": "1.0.0"
            },
            "summary": {
                "total_files": result.total_files,
                "total_lines": result.total_lines,
                "valid_lines": result.valid_lines,
                "invalid_lines": result.total_lines - result.valid_lines
            },
            "level_distribution": result.level_distribution,
            "hourly_stats": self._hourly_stats_to_dict(result.hourly_stats),
            "error_code_distribution": result.error_code_distribution,
            "daily_peak": self._daily_peak_to_dict(result.daily_peak)
        }
        
        return report
    
    def generate_text_summary(self, result: AnalysisResult) -> str:
        """
        生成纯文本格式的可视化摘要。
        
        Args:
            result: 分析结果
            
        Returns:
            str: 文本摘要
        """
        lines = [
            REPORT_SEPARATOR,
            "日志文件统计分析报告",
            REPORT_SEPARATOR,
            "",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            REPORT_LINE,
            "基础统计",
            REPORT_LINE,
            f"  处理文件数: {result.total_files}",
            f"  总行数: {result.total_lines}",
            f"  有效行数: {result.valid_lines}",
            f"  无效行数: {result.total_lines - result.valid_lines}",
            "",
            REPORT_LINE,
            "日志级别分布",
            REPORT_LINE,
        ]
        
        if result.level_distribution:
            total_level_count = sum(result.level_distribution.values())
            for level in ["INFO", "WARN", "ERROR"]:
                count = result.level_distribution.get(level, 0)
                percentage = (count / total_level_count * 100) if total_level_count > 0 else 0
                bar = self._generate_bar(count, total_level_count)
                lines.append(f"  {level:6s}: {count:6d} ({percentage:5.1f}%) {bar}")
        else:
            lines.append("  无数据")
        
        lines.append("")
        lines.append(REPORT_LINE)
        lines.append("按小时统计")
        lines.append(REPORT_LINE)
        
        hourly_header = "  小时 |  INFO |  WARN | ERROR |  总计"
        lines.append(hourly_header)
        lines.append("  " + "-" * 36)
        
        for hour in range(24):
            stats = result.hourly_stats.get(hour)
            if stats:
                lines.append(
                    f"  {hour:4d}时 | {stats.info_count:5d} | {stats.warn_count:5d} | "
                    f"{stats.error_count:5d} | {stats.total:5d}"
                )
        
        lines.append("")
        lines.append(REPORT_LINE)
        lines.append("错误码分布 (Top 10)")
        lines.append(REPORT_LINE)
        
        if result.error_code_distribution:
            sorted_codes = sorted(
                result.error_code_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            for code, count in sorted_codes:
                lines.append(f"  错误码 {code}: {count} 次")
        else:
            lines.append("  无错误码数据")
        
        lines.append("")
        lines.append(REPORT_LINE)
        lines.append("单日请求峰值")
        lines.append(REPORT_LINE)
        
        if result.daily_peak:
            lines.append(f"  日期: {result.daily_peak.date}")
            lines.append(f"  日志数: {result.daily_peak.count} 条")
        else:
            lines.append("  无日期数据")
        
        lines.append("")
        lines.append(REPORT_SEPARATOR)
        lines.append("报告生成完成")
        lines.append(REPORT_SEPARATOR)
        
        return "\n".join(lines)
    
    def _generate_bar(self, value: int, total: int, width: int = 20) -> str:
        """
        生成进度条。
        
        Args:
            value: 当前值
            total: 总值
            width: 进度条宽度
            
        Returns:
            str: 进度条字符串
        """
        if total == 0:
            return "[" + " " * width + "]"
        
        filled = int(width * value / total)
        return "[" + "#" * filled + " " * (width - filled) + "]"
    
    def save_json_report(self, result: AnalysisResult) -> bool:
        """
        保存 JSON 格式的统计报告。
        
        Args:
            result: 分析结果
            
        Returns:
            bool: 是否保存成功
        """
        filepath = os.path.join(self.output_dir, STATS_REPORT_FILE)
        
        try:
            report_data = self.generate_json_report(result)
            
            with open(filepath, 'w', encoding=ENCODING) as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"JSON 报告已保存: {filepath}")
            return True
        except IOError as e:
            print(f"保存 JSON 报告失败: {str(e)}")
            return False
        except Exception as e:
            print(f"保存 JSON 报告时发生错误: {str(e)}")
            return False
    
    def save_text_summary(self, result: AnalysisResult) -> bool:
        """
        保存纯文本格式的可视化摘要。
        
        Args:
            result: 分析结果
            
        Returns:
            bool: 是否保存成功
        """
        filepath = os.path.join(self.output_dir, SUMMARY_FILE)
        
        try:
            summary_text = self.generate_text_summary(result)
            
            with open(filepath, 'w', encoding=ENCODING) as f:
                f.write(summary_text)
                f.write("\n")
            
            print(f"文本摘要已保存: {filepath}")
            return True
        except IOError as e:
            print(f"保存文本摘要失败: {str(e)}")
            return False
        except Exception as e:
            print(f"保存文本摘要时发生错误: {str(e)}")
            return False
    
    def generate_all_reports(self, result: AnalysisResult) -> Tuple[bool, bool]:
        """
        生成所有报告。
        
        Args:
            result: 分析结果
            
        Returns:
            Tuple[bool, bool]: (JSON报告保存状态, 文本摘要保存状态)
        """
        json_success = self.save_json_report(result)
        text_success = self.save_text_summary(result)
        return json_success, text_success
