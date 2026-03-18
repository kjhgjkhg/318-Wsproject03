"""
日志文件扫描模块。

负责递归遍历目录，筛选符合条件的日志文件。
提供文件发现和验证功能。
"""

import os
from typing import List, Optional
from pathlib import Path

from config.settings import (
    RAW_LOGS_DIR,
    VALID_EXTENSIONS,
    BLACKLIST_FILE,
    ERROR_INPUT_DIR_NOT_FOUND,
    ERROR_NO_LOG_FILES,
    ERROR_BLACKLIST_FILE,
)


class LogScanner:
    """
    日志文件扫描器。
    
    递归扫描指定目录，发现并筛选符合要求的日志文件。
    """
    
    def __init__(self, input_dir: str = RAW_LOGS_DIR):
        """
        初始化扫描器。
        
        Args:
            input_dir: 输入目录路径
        """
        self.input_dir = input_dir
        self.blacklist_file = BLACKLIST_FILE
        self.skipped_files: List[str] = []
    
    def validate_input_directory(self) -> bool:
        """
        验证输入目录是否存在。
        
        Returns:
            bool: 目录存在返回 True，否则返回 False
        """
        if not os.path.exists(self.input_dir):
            print(ERROR_INPUT_DIR_NOT_FOUND.format(self.input_dir))
            return False
        if not os.path.isdir(self.input_dir):
            print(ERROR_INPUT_DIR_NOT_FOUND.format(self.input_dir))
            return False
        return True
    
    def is_valid_log_file(self, filepath: str) -> bool:
        """
        检查文件是否为有效的日志文件。
        
        检查条件：
        1. 文件扩展名在允许列表中
        2. 不是受保护的黑名单文件
        3. 是普通文件（不是目录）
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 有效返回 True
        """
        # 检查是否为文件
        if not os.path.isfile(filepath):
            return False
        
        # 检查扩展名
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in VALID_EXTENSIONS:
            return False
        
        # 检查是否为黑名单文件
        filename = os.path.basename(filepath)
        if filename == self.blacklist_file:
            print(ERROR_BLACKLIST_FILE.format(filename))
            self.skipped_files.append(filepath)
            return False
        
        return True
    
    def scan_directory(self, recursive: bool = True) -> List[str]:
        """
        扫描目录中的所有有效日志文件。
        
        Args:
            recursive: 是否递归扫描子目录
            
        Returns:
            List[str]: 有效日志文件路径列表
        """
        if not self.validate_input_directory():
            return []
        
        log_files = []
        
        try:
            if recursive:
                # 递归遍历
                for root, _, files in os.walk(self.input_dir):
                    for filename in files:
                        filepath = os.path.join(root, filename)
                        if self.is_valid_log_file(filepath):
                            log_files.append(filepath)
            else:
                # 仅扫描当前目录
                for filename in os.listdir(self.input_dir):
                    filepath = os.path.join(self.input_dir, filename)
                    if self.is_valid_log_file(filepath):
                        log_files.append(filepath)
        except OSError as e:
            print(f"错误：扫描目录时出错: {e}")
            return []
        
        # 按路径排序，确保顺序一致
        log_files.sort()
        
        if not log_files:
            print(ERROR_NO_LOG_FILES.format(self.input_dir))
        
        return log_files
    
    def get_file_info(self, filepath: str) -> Optional[dict]:
        """
        获取文件信息。
        
        Args:
            filepath: 文件路径
            
        Returns:
            Optional[dict]: 文件信息字典，失败返回 None
        """
        try:
            stat = os.stat(filepath)
            return {
                'path': filepath,
                'name': os.path.basename(filepath),
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'extension': os.path.splitext(filepath)[1].lower(),
            }
        except OSError:
            return None
    
    def scan_with_info(self, recursive: bool = True) -> List[dict]:
        """
        扫描目录并返回带信息的文件列表。
        
        Args:
            recursive: 是否递归扫描子目录
            
        Returns:
            List[dict]: 文件信息字典列表
        """
        filepaths = self.scan_directory(recursive)
        file_infos = []
        
        for filepath in filepaths:
            info = self.get_file_info(filepath)
            if info:
                file_infos.append(info)
        
        return file_infos
    
    def get_skipped_files(self) -> List[str]:
        """
        获取被跳过的文件列表。
        
        Returns:
            List[str]: 被跳过的文件路径列表
        """
        return self.skipped_files.copy()


def scan_log_files(input_dir: Optional[str] = None, recursive: bool = True) -> List[str]:
    """
    便捷函数：扫描日志文件。
    
    Args:
        input_dir: 输入目录，None 使用默认目录
        recursive: 是否递归扫描
        
    Returns:
        List[str]: 日志文件路径列表
    """
    scanner = LogScanner(input_dir or RAW_LOGS_DIR)
    return scanner.scan_directory(recursive)
