#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志文件批量清洗与统计工具 - 程序入口。

本工具用于批量读取指定目录下的日志文件，按规则清洗无效日志行，
统计关键指标，并生成结构化的统计报告，同时支持增量处理避免重复计算。

**强约束条件（必须严格遵守）：**
1. 路径约束：
   - 输入目录：./raw_logs/（必须使用基于脚本位置的绝对路径）
   - 输出目录：./processed_output/（必须使用基于脚本位置的绝对路径）

2. 不可修改特定文件：
   - ./raw_logs/do_not_modify_blacklist.log 严禁读取、解析或任何操作
   - 代码包含防御性检查，直接跳过该文件

3. 命名规范：
   - 核心业务逻辑文件必须使用前缀 log_（如 log_cleaner.py）
   - 配置常量必须放在 config/ 子包中，文件名为 settings.py

4. 文件格式约束：
   - 统计报告必须输出为 stats_report.json
   - 可视化摘要必须输出为 summary.txt

用法：
    python main.py              # 执行完整的扫描、清洗、分析和报告生成
    python main.py --force      # 强制重新处理所有文件（忽略增量记录）
    python main.py --clear      # 清空增量处理记录
"""

import sys
import argparse
from typing import Optional, List

from config.settings import (
    RAW_LOGS_DIR,
    PROCESSED_OUTPUT_DIR,
    SUCCESS_PROCESSING_COMPLETE,
    SUCCESS_SKIPPED_FILES,
)
from utils.checksum import ProcessedRecordsManager
from log_scanner import LogScanner
from log_cleaner import LogCleaner
from log_analyzer import BatchAnalyzer
from log_reporter import LogReporter, generate_console_summary


def ensure_output_directory() -> bool:
    """
    确保输出目录存在。
    
    Returns:
        bool: 目录可用返回 True
    """
    import os
    try:
        os.makedirs(PROCESSED_OUTPUT_DIR, exist_ok=True)
        return True
    except OSError as e:
        print(f"错误：无法创建输出目录: {e}")
        return False


def process_files(force_reprocess: bool = False) -> int:
    """
    处理日志文件的主流程。
    
    Args:
        force_reprocess: 是否强制重新处理所有文件
        
    Returns:
        int: 退出码
    """
    # 确保输出目录存在
    if not ensure_output_directory():
        return 1
    
    # 初始化记录管理器
    records_manager = ProcessedRecordsManager()
    
    # 扫描日志文件
    print("正在扫描日志文件...")
    scanner = LogScanner(RAW_LOGS_DIR)
    log_files = scanner.scan_directory(recursive=True)
    
    if not log_files:
        print("未找到需要处理的日志文件。")
        return 0
    
    print(f"发现 {len(log_files)} 个日志文件")
    
    # 筛选需要处理的文件（增量处理）
    files_to_process = []
    skipped_count = 0
    
    for filepath in log_files:
        if not force_reprocess and records_manager.is_processed(filepath):
            skipped_count += 1
        else:
            files_to_process.append(filepath)
    
    if skipped_count > 0:
        print(SUCCESS_SKIPPED_FILES.format(skipped_count))
    
    if not files_to_process:
        print("所有文件已是最新状态，无需处理。")
        print(f"使用 --force 参数可强制重新处理。")
        return 0
    
    print(f"将处理 {len(files_to_process)} 个文件...")
    print("-" * 40)
    
    # 批量分析
    analyzer = BatchAnalyzer()
    results = analyzer.analyze_files(files_to_process)
    
    # 标记已处理的文件
    for filepath in files_to_process:
        records_manager.mark_processed(filepath)
    records_manager.save_records()
    
    # 生成报告
    print("\n正在生成报告...")
    reporter = LogReporter(results)
    if reporter.generate_all_reports():
        print("\n所有报告生成成功！")
    else:
        print("\n警告：部分报告生成失败。")
    
    # 控制台摘要
    generate_console_summary(results)
    
    print(SUCCESS_PROCESSING_COMPLETE.format(len(files_to_process)))
    return 0


def clear_records() -> int:
    """
    清空增量处理记录。
    
    Returns:
        int: 退出码
    """
    records_manager = ProcessedRecordsManager()
    count = records_manager.get_processed_count()
    records_manager.clear_records()
    print(f"已清空 {count} 条处理记录。")
    return 0


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器。
    
    Returns:
        argparse.ArgumentParser: 配置好的解析器
    """
    parser = argparse.ArgumentParser(
        prog='log_processor',
        description='日志文件批量清洗与统计工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py              # 执行完整的处理流程
  python main.py --force      # 强制重新处理所有文件
  python main.py --clear      # 清空增量处理记录
        """
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='强制重新处理所有文件（忽略增量记录）'
    )
    
    parser.add_argument(
        '--clear', '-c',
        action='store_true',
        help='清空增量处理记录'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    主入口函数。
    
    Args:
        args: 命令行参数列表，None 表示使用 sys.argv
        
    Returns:
        int: 程序退出码，0 表示成功
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    try:
        if parsed_args.clear:
            return clear_records()
        else:
            return process_files(force_reprocess=parsed_args.force)
    except KeyboardInterrupt:
        print("\n\n操作已取消。")
        return 130
    except Exception as e:
        print(f"\n错误：程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
