"""
main.py - 程序主入口

日志文件批量清洗与统计工具

功能：
- 递归扫描日志目录
- 按规则清洗无效日志
- 统计关键指标
- 生成结构化报告
- 支持增量处理
"""

import sys
import argparse
import time
from typing import Optional, List

from config.settings import (
    RAW_LOGS_DIR,
    PROCESSED_OUTPUT_DIR,
    REPORT_SEPARATOR,
    REPORT_LINE
)
from log_scanner import LogScanner, scan_log_files
from log_cleaner import LogCleaner, LogFileReader
from log_analyzer import LogAnalyzer
from log_reporter import LogReporter
from utils.checksum import (
    load_processed_cache,
    save_processed_cache,
    get_files_to_process,
    update_cache
)


def print_banner() -> None:
    """打印程序横幅。"""
    banner = [
        REPORT_SEPARATOR,
        "日志文件批量清洗与统计工具",
        "Log File Batch Cleaning & Statistics Tool",
        REPORT_SEPARATOR,
        ""
    ]
    print("\n".join(banner))


def print_config_info() -> None:
    """打印配置信息。"""
    info = [
        "配置信息:",
        REPORT_LINE,
        f"  输入目录: {RAW_LOGS_DIR}",
        f"  输出目录: {PROCESSED_OUTPUT_DIR}",
        ""
    ]
    print("\n".join(info))


def process_files(
    filepaths: List[str],
    cleaner: LogCleaner,
    analyzer: LogAnalyzer,
    cache: dict
) -> int:
    """
    处理文件列表。
    
    Args:
        filepaths: 文件路径列表
        cleaner: 日志清洗器
        analyzer: 日志分析器
        cache: 缓存字典
        
    Returns:
        int: 成功处理的文件数
    """
    processed_count = 0
    
    for filepath in filepaths:
        print(f"处理文件: {filepath}")
        
        lines, encoding = LogFileReader.read_file(filepath)
        if not lines:
            print(f"  跳过: 无法读取文件")
            continue
        
        print(f"  编码: {encoding}, 行数: {len(lines)}")
        
        cleaned_lines = cleaner.clean_lines(lines)
        valid_lines = cleaner.filter_valid_lines(cleaned_lines)
        
        print(f"  有效行数: {len(valid_lines)}")
        
        analyzer.analyze_lines(valid_lines)
        analyzer.add_file_count()
        
        update_cache(filepath, cache)
        processed_count += 1
    
    return processed_count


def run_pipeline(force: bool = False, verbose: bool = False) -> int:
    """
    运行处理管道。
    
    Args:
        force: 是否强制重新处理所有文件
        verbose: 是否显示详细输出
        
    Returns:
        int: 退出码
    """
    start_time = time.time()
    
    print_banner()
    print_config_info()
    
    print("步骤 1: 扫描日志文件")
    print(REPORT_LINE)
    
    scanner = LogScanner()
    all_files = scanner.scan()
    
    if not all_files:
        print("未找到有效的日志文件")
        return 0
    
    print(f"发现 {len(all_files)} 个日志文件")
    
    print("")
    print("步骤 2: 加载处理缓存")
    print(REPORT_LINE)
    
    cache = {} if force else load_processed_cache()
    
    if force:
        print("强制模式: 将重新处理所有文件")
    
    files_to_process = all_files if force else get_files_to_process(all_files, cache)
    
    if not files_to_process:
        print("所有文件已处理过，无需重新处理")
        print("使用 --force 参数强制重新处理")
        return 0
    
    print(f"需要处理 {len(files_to_process)} 个文件")
    
    print("")
    print("步骤 3: 清洗与分析日志")
    print(REPORT_LINE)
    
    cleaner = LogCleaner()
    analyzer = LogAnalyzer()
    
    processed_count = process_files(files_to_process, cleaner, analyzer, cache)
    
    print("")
    print(f"处理完成: {processed_count} 个文件")
    
    cleaner_stats = cleaner.get_stats()
    print("")
    print("清洗统计:")
    print(f"  总行数: {cleaner_stats['total_lines']}")
    print(f"  有效行数: {cleaner_stats['valid_lines']}")
    print(f"  空行: {cleaner_stats['empty_lines']}")
    print(f"  DEBUG 级别: {cleaner_stats['debug_lines']}")
    print(f"  无效时间格式: {cleaner_stats['invalid_time_lines']}")
    
    print("")
    print("步骤 4: 生成报告")
    print(REPORT_LINE)
    
    result = analyzer.get_result()
    result.processing_time = time.time() - start_time
    
    reporter = LogReporter()
    json_ok, text_ok = reporter.generate_all_reports(result)
    
    print("")
    print("步骤 5: 保存缓存")
    print(REPORT_LINE)
    
    if save_processed_cache(cache):
        print("缓存已保存")
    else:
        print("警告: 缓存保存失败")
    
    print("")
    print(REPORT_SEPARATOR)
    print("处理完成")
    print(REPORT_SEPARATOR)
    print(f"总耗时: {result.processing_time:.2f} 秒")
    
    return 0


def cmd_process(args: argparse.Namespace) -> int:
    """
    处理命令。
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    return run_pipeline(force=args.force, verbose=args.verbose)


def cmd_info(args: argparse.Namespace) -> int:
    """
    显示信息命令。
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    print_banner()
    print_config_info()
    
    print("扫描结果:")
    print(REPORT_LINE)
    
    scanner = LogScanner()
    files = scanner.scan()
    
    print(f"有效日志文件: {len(files)} 个")
    
    if files:
        print("")
        for i, filepath in enumerate(files, start=1):
            print(f"  {i}. {filepath}")
    
    cache = load_processed_cache()
    print("")
    print(f"已缓存文件: {len(cache)} 个")
    
    return 0


def cmd_clear_cache(args: argparse.Namespace) -> int:
    """
    清除缓存命令。
    
    Args:
        args: 命令行参数
        
    Returns:
        int: 退出码
    """
    from utils.checksum import clear_cache
    
    print("清除处理缓存...")
    
    if clear_cache():
        print("缓存已清除")
        return 0
    else:
        print("清除缓存失败")
        return 1


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器。
    
    Returns:
        argparse.ArgumentParser: 参数解析器
    """
    parser = argparse.ArgumentParser(
        prog="logtool",
        description="日志文件批量清洗与统计工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    subparsers = parser.add_subparsers(
        title="可用命令",
        dest="command",
        description="使用 'logtool <command> --help' 查看命令详情"
    )
    
    process_parser = subparsers.add_parser(
        "process",
        help="处理日志文件",
        description="扫描、清洗、分析日志文件并生成报告"
    )
    process_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="强制重新处理所有文件"
    )
    process_parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细输出"
    )
    process_parser.set_defaults(func=cmd_process)
    
    info_parser = subparsers.add_parser(
        "info",
        help="显示系统信息",
        description="显示配置信息和扫描结果"
    )
    info_parser.set_defaults(func=cmd_info)
    
    clear_parser = subparsers.add_parser(
        "clear-cache",
        help="清除处理缓存",
        description="清除已处理文件的缓存"
    )
    clear_parser.set_defaults(func=cmd_clear_cache)
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    主函数。
    
    Args:
        argv: 命令行参数列表
        
    Returns:
        int: 退出码
    """
    parser = create_parser()
    
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    
    if args.command is None:
        parser.print_help()
        return 0
    
    if hasattr(args, 'func'):
        return args.func(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
