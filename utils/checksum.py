"""
文件哈希计算与增量处理模块。

提供文件校验和计算、已处理文件记录管理等功能，
支持增量处理避免重复计算。
"""

import os
import json
import hashlib
from typing import Dict, Optional, Set
from pathlib import Path

from config.settings import (
    PROCESSED_RECORDS_PATH,
    FILE_ENCODING,
)


def calculate_file_hash(filepath: str) -> Optional[str]:
    """
    计算文件的 MD5 哈希值。
    
    Args:
        filepath: 文件路径
        
    Returns:
        Optional[str]: 文件哈希值，失败返回 None
    """
    try:
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (IOError, OSError, PermissionError):
        return None


def calculate_string_hash(content: str) -> str:
    """
    计算字符串的 MD5 哈希值。
    
    Args:
        content: 字符串内容
        
    Returns:
        str: 哈希值
    """
    return hashlib.md5(content.encode(FILE_ENCODING)).hexdigest()


class ProcessedRecordsManager:
    """
    已处理文件记录管理器。
    
    管理已处理文件的哈希记录，支持增量处理。
    """
    
    def __init__(self, records_path: str = PROCESSED_RECORDS_PATH):
        """
        初始化管理器。
        
        Args:
            records_path: 记录文件路径
        """
        self.records_path = records_path
        self.records: Dict[str, str] = {}
        self._load_records()
    
    def _load_records(self) -> None:
        """从文件加载已处理记录。"""
        if os.path.exists(self.records_path):
            try:
                with open(self.records_path, 'r', encoding=FILE_ENCODING) as f:
                    self.records = json.load(f)
            except (json.JSONDecodeError, IOError, OSError):
                self.records = {}
    
    def save_records(self) -> bool:
        """
        保存记录到文件。
        
        Returns:
            bool: 保存成功返回 True
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.records_path), exist_ok=True)
            with open(self.records_path, 'w', encoding=FILE_ENCODING) as f:
                json.dump(self.records, f, indent=2)
            return True
        except (IOError, OSError):
            return False
    
    def is_processed(self, filepath: str) -> bool:
        """
        检查文件是否已处理（通过比较哈希值）。
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 已处理且未变更返回 True
        """
        # 获取当前文件哈希
        current_hash = calculate_file_hash(filepath)
        if current_hash is None:
            return False
        
        # 获取记录的哈希
        abs_path = os.path.abspath(filepath)
        recorded_hash = self.records.get(abs_path)
        
        # 如果哈希匹配，说明文件未变更
        return recorded_hash == current_hash
    
    def mark_processed(self, filepath: str) -> bool:
        """
        标记文件为已处理。
        
        Args:
            filepath: 文件路径
            
        Returns:
            bool: 标记成功返回 True
        """
        file_hash = calculate_file_hash(filepath)
        if file_hash is None:
            return False
        
        abs_path = os.path.abspath(filepath)
        self.records[abs_path] = file_hash
        return True
    
    def remove_record(self, filepath: str) -> None:
        """
        移除文件的处理记录。
        
        Args:
            filepath: 文件路径
        """
        abs_path = os.path.abspath(filepath)
        if abs_path in self.records:
            del self.records[abs_path]
    
    def get_processed_count(self) -> int:
        """
        获取已处理文件数量。
        
        Returns:
            int: 已处理文件数
        """
        return len(self.records)
    
    def clear_records(self) -> None:
        """清空所有记录。"""
        self.records.clear()
        if os.path.exists(self.records_path):
            try:
                os.remove(self.records_path)
            except OSError:
                pass


def get_file_size(filepath: str) -> int:
    """
    获取文件大小（字节）。
    
    Args:
        filepath: 文件路径
        
    Returns:
        int: 文件大小，失败返回 -1
    """
    try:
        return os.path.getsize(filepath)
    except OSError:
        return -1


def get_file_mtime(filepath: str) -> Optional[float]:
    """
    获取文件最后修改时间。
    
    Args:
        filepath: 文件路径
        
    Returns:
        Optional[float]: 修改时间戳，失败返回 None
    """
    try:
        return os.path.getmtime(filepath)
    except OSError:
        return None
