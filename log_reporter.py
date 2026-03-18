"""
日志报告生成模块。

负责生成 JSON 格式的统计报告和纯文本的可视化摘要。
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime

from config.settings import (
    STATS_REPORT_PATH,
    SUMMARY_PATH,
    REPORT_SEPARATOR,
    REPORT_SUB_SEPARATOR,
    JSON_INDENT,
    FILE_ENCODING,
    SUCCESS_REPORT_SAVED,
)


class LogReporter:
    """
    日志报告生成器。
    
    生成 JSON 统计报告和纯文本可视化摘要。
    """
    
    def __init__(self, analysis_results: Dict[str, Any]):
        """
        初始化报告生成器。
        
        Args:
            analysis_results: 分析结果字典
        """
        self.results = analysis_results
        self.report_timestamp = datetime.now().isoformat()
    
    def generate_json_report(self) -> str:
        """
        生成 JSON 格式的统计报告。
        
        Returns:
            str: JSON 格式的报告内容
        """
        report = {
            'report_metadata': {
                'generated_at': self.report_timestamp,
                'version': '1.0.0',
            },
            'data': self.results,
        }
        
        return json.dumps(report, indent=JSON_INDENT, ensure_ascii=False)
    
    def generate_text_summary(self) -> str:
        """
        生成纯文本的可视化摘要。
        
        Returns:
            str: 文本格式的摘要内容
        """
        lines = []
        
        # 报告头部
        lines.append(REPORT_SEPARATOR)
        lines.append("日志文件清洗与统计报告")
        lines.append(f"生成时间: {self.report_timestamp}")
        lines.append(REPORT_SEPARATOR)
        lines.append("")
        
        # 处理信息
        processing_info = self.results.get('processing_info', {})
        lines.append("【处理概况】")
        lines.append(REPORT_SUB_SEPARATOR)
        lines.append(f"处理文件数:     {processing_info.get('processed_files', 0)}")
        lines.append(f"总行数:         {processing_info.get('total_lines', 0)}")
        lines.append(f"有效条目数:     {processing_info.get('valid_entries', 0)}")
        lines.append(f"过滤行数:       {processing_info.get('filtered_count', 0)}")
        lines.append("")
        
        # 日志级别分布
        summary = self.results.get('summary', {})
        level_dist = summary.get('level_distribution', {})
        lines.append("【日志级别分布】")
        lines.append(REPORT_SUB_SEPARATOR)
        for level in ['INFO', 'WARN', 'ERROR']:
            count = level_dist.get(level, 0)
            lines.append(f"  {level:<10} {count:>6} 条")
        lines.append("")
        
        # 峰值统计
        peak_stats = self.results.get('peak_stats', {})
        lines.append("【峰值统计】")
        lines.append(REPORT_SUB_SEPARATOR)
        peak_hour = peak_stats.get('peak_hour')
        peak_hour_count = peak_stats.get('peak_hour_count', 0)
        if peak_hour:
            lines.append(f"小时峰值: {peak_hour}  ({peak_hour_count} 条)")
        
        peak_day = peak_stats.get('peak_day')
        peak_day_count = peak_stats.get('peak_day_count', 0)
        if peak_day:
            lines.append(f"单日峰值: {peak_day}  ({peak_day_count} 条)")
        lines.append("")
        
        # 错误码分布
        error_dist = self.results.get('error_code_distribution', {})
        if error_dist:
            lines.append("【错误码分布】")
            lines.append(REPORT_SUB_SEPARATOR)
            sorted_errors = sorted(error_dist.items(), key=lambda x: x[1], reverse=True)
            for error_code, count in sorted_errors[:10]:  # 最多显示10个
                lines.append(f"  {error_code:<15} {count:>6} 次")
            lines.append("")
        
        # 按小时统计
        hourly_stats = self.results.get('hourly_stats', {})
        if hourly_stats:
            lines.append("【按小时统计】")
            lines.append(REPORT_SUB_SEPARATOR)
            lines.append(f"{'时间':<20} {'INFO':>8} {'WARN':>8} {'ERROR':>8} {'总计':>8}")
            lines.append(REPORT_SUB_SEPARATOR)
            
            for hour in sorted(hourly_stats.keys())[-24:]:  # 最近24小时
                stats = hourly_stats[hour]
                info = stats.get('INFO', 0)
                warn = stats.get('WARN', 0)
                error = stats.get('ERROR', 0)
                total = info + warn + error
                lines.append(f"{hour:<20} {info:>8} {warn:>8} {error:>8} {total:>8}")
            lines.append("")
        
        # 报告尾部
        lines.append(REPORT_SEPARATOR)
        lines.append("报告生成完成")
        lines.append(REPORT_SEPARATOR)
        
        return '\n'.join(lines)
    
    def save_json_report(self) -> bool:
        """
        保存 JSON 报告到文件。
        
        Returns:
            bool: 保存成功返回 True
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(STATS_REPORT_PATH), exist_ok=True)
            
            report = self.generate_json_report()
            with open(STATS_REPORT_PATH, 'w', encoding=FILE_ENCODING) as f:
                f.write(report)
            
            print(SUCCESS_REPORT_SAVED.format(STATS_REPORT_PATH))
            return True
        except (IOError, OSError) as e:
            print(f"错误：无法保存 JSON 报告: {e}")
            return False
    
    def save_text_summary(self) -> bool:
        """
        保存文本摘要到文件。
        
        Returns:
            bool: 保存成功返回 True
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
            
            summary = self.generate_text_summary()
            with open(SUMMARY_PATH, 'w', encoding=FILE_ENCODING) as f:
                f.write(summary)
            
            print(SUCCESS_REPORT_SAVED.format(SUMMARY_PATH))
            return True
        except (IOError, OSError) as e:
            print(f"错误：无法保存文本摘要: {e}")
            return False
    
    def generate_all_reports(self) -> bool:
        """
        生成并保存所有报告。
        
        Returns:
            bool: 全部保存成功返回 True
        """
        json_success = self.save_json_report()
        text_success = self.save_text_summary()
        
        return json_success and text_success


def generate_console_summary(results: Dict[str, Any]) -> None:
    """
    在控制台打印简要摘要。
    
    Args:
        results: 分析结果
    """
    print("\n" + REPORT_SEPARATOR)
    print("处理完成摘要")
    print(REPORT_SEPARATOR)
    
    processing_info = results.get('processing_info', {})
    print(f"处理文件: {processing_info.get('processed_files', 0)} 个")
    print(f"有效条目: {processing_info.get('valid_entries', 0)} 条")
    print(f"过滤行数: {processing_info.get('filtered_count', 0)} 条")
    
    summary = results.get('summary', {})
    level_dist = summary.get('level_distribution', {})
    print(f"\n日志级别: INFO={level_dist.get('INFO', 0)}, "
          f"WARN={level_dist.get('WARN', 0)}, "
          f"ERROR={level_dist.get('ERROR', 0)}")
    
    peak_stats = results.get('peak_stats', {})
    if peak_stats.get('peak_hour'):
        print(f"\n小时峰值: {peak_stats['peak_hour']} "
              f"({peak_stats['peak_hour_count']} 条)")
    
    print(REPORT_SEPARATOR)
