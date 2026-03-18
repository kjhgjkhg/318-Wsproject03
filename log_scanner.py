"""
log_scanner.py - 日志文件扫描模块

负责遍历目录，筛选符合条件的日志文件。
"""

import os
from typing import List, Tuple, Optional

from config.settings import (
    RAW_LOGS_DIR,
    LOG_EXTENSIONS,
    BLACKLIST_FILE_NAME
)


class LogScanner:
    """
    日志文件扫描器类。
    
    负责递归扫描指定目录，筛选符合条件的日志文件。
    """
    
    def __init__(self, input_dir: Optional[str] = None) -> None:
        """
        初始化日志扫描器。
        
        Args:
            input_dir: 输入目录路径，默认使用配置中的 RAW_LOGS_DIR
        """
        self.input_dir = input_dir or RAW_LOGS_DIR
        self._scanned_files: List[str] = []
        self._skipped_files: List[str] = []
    
    def validate_input_directory(self) -> Tuple[bool, str]:
        """
        验证输入目录是否存在且可访问。
        
        Returns:
            Tuple[bool, str]: (是否有效, 错误消息或成功消息)
        """
        if not os.path.exists(self.input_dir):
            return False, f"输入目录不存在: {self.input_dir}"
        
        if not os.path.isdir(self.input_dir):
            return False, f"输入路径不是目录: {self.input_dir}"
        
        if not os.access(self.input_dir, os.R_OK):
            return False, f"输入目录不可读: {self.input_dir}"
        
        return True, f"输入目录验证通过: {self.input_dir}"
    
    def is_valid_log_file(self, filepath: str) -> bool:
        """
        检查文件是否为有效的日志文件。
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 是否为有效的日志文件
        """
        _, ext = os.path.splitext(filepath)
        return ext.lower() in LOG_EXTENSIONS
    
    def is_blacklisted_file(self, filepath: str) -> bool:
        """
        检查文件是否在黑名单中。
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 是否在黑名单中
        """
        filename = os.path.basename(filepath)
        return filename == BLACKLIST_FILE_NAME
    
    def scan(self) -> List[str]:
        """
        扫描目录，返回所有有效的日志文件路径。
        
        Returns:
            List[str]: 有效日志文件路径列表
        """
        self._scanned_files = []
        self._skipped_files = []
        
        valid, msg = self.validate_input_directory()
        if not valid:
            print(f"错误: {msg}")
            return []
        
        try:
            for root, dirs, files in os.walk(self.input_dir):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    
                    if self.is_blacklisted_file(filepath):
                        self._skipped_files.append(filepath)
                        print(f"跳过黑名单文件: {filepath}")
                        continue
                    
                    if self.is_valid_log_file(filepath):
                        self._scanned_files.append(filepath)
                    else:
                        self._skipped_files.append(filepath)
        
        except PermissionError as e:
            print(f"遍历目录时权限错误: {str(e)}")
        except Exception as e:
            print(f"扫描目录时发生错误: {str(e)}")
        
        return self._scanned_files
    
    def get_scanned_files(self) -> List[str]:
        """
        获取已扫描的有效文件列表。
        
        Returns:
            List[str]: 有效文件路径列表
        """
        return self._scanned_files
    
    def get_skipped_files(self) -> List[str]:
        """
        获取被跳过的文件列表。
        
        Returns:
            List[str]: 被跳过的文件路径列表
        """
        return self._skipped_files
    
    def get_scan_summary(self) -> str:
        """
        获取扫描摘要信息。
        
        Returns:
            str: 扫描摘要字符串
        """
        lines = [
            "=" * 60,
            "日志文件扫描摘要",
            "=" * 60,
            "",
            f"扫描目录: {self.input_dir}",
            f"有效日志文件: {len(self._scanned_files)} 个",
            f"跳过文件: {len(self._skipped_files)} 个",
            ""
        ]
        
        if self._scanned_files:
            lines.append("有效文件列表:")
            for i, filepath in enumerate(self._scanned_files, start=1):
                filename = os.path.basename(filepath)
                lines.append(f"  {i}. {filename}")
        
        return "\n".join(lines)


def scan_log_files(input_dir: Optional[str] = None) -> List[str]:
    """
    便捷函数：扫描日志文件。
    
    Args:
        input_dir: 输入目录路径
        
    Returns:
        List[str]: 有效日志文件路径列表
    """
    scanner = LogScanner(input_dir)
    return scanner.scan()
