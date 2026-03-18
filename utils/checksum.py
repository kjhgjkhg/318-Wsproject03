"""
utils/checksum.py - 文件哈希计算与增量处理模块

提供文件哈希计算、增量处理等辅助工具函数。
"""

import os
import json
import hashlib
from typing import Dict, Optional, Set

from config.settings import (
    PROCESSED_OUTPUT_DIR,
    CHECKSUM_CACHE_FILE,
    ENCODING
)


def calculate_file_hash(filepath: str, block_size: int = 65536) -> Optional[str]:
    """
    计算文件的 MD5 哈希值。
    
    Args:
        filepath: 文件路径
        block_size: 读取块大小
        
    Returns:
        Optional[str]: 文件哈希值，失败返回 None
    """
    try:
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    except FileNotFoundError:
        print(f"文件不存在: {filepath}")
        return None
    except PermissionError:
        print(f"无权限读取文件: {filepath}")
        return None
    except Exception as e:
        print(f"计算文件哈希时发生错误: {filepath} - {str(e)}")
        return None


def load_processed_cache() -> Dict[str, str]:
    """
    加载已处理文件的缓存。
    
    Returns:
        Dict[str, str]: 文件路径到哈希值的映射
    """
    cache_path = os.path.join(PROCESSED_OUTPUT_DIR, CHECKSUM_CACHE_FILE)
    
    if not os.path.exists(cache_path):
        return {}
    
    try:
        with open(cache_path, 'r', encoding=ENCODING) as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"缓存文件格式错误，将重新创建")
        return {}
    except Exception as e:
        print(f"加载缓存文件时发生错误: {str(e)}")
        return {}


def save_processed_cache(cache: Dict[str, str]) -> bool:
    """
    保存已处理文件的缓存。
    
    Args:
        cache: 文件路径到哈希值的映射
        
    Returns:
        bool: 是否保存成功
    """
    cache_path = os.path.join(PROCESSED_OUTPUT_DIR, CHECKSUM_CACHE_FILE)
    
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w', encoding=ENCODING) as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"保存缓存文件失败: {str(e)}")
        return False
    except Exception as e:
        print(f"保存缓存文件时发生错误: {str(e)}")
        return False


def is_file_processed(filepath: str, cache: Dict[str, str]) -> bool:
    """
    检查文件是否已被处理过（哈希值匹配）。
    
    Args:
        filepath: 文件路径
        cache: 缓存字典
        
    Returns:
        bool: 是否已处理过
    """
    if filepath not in cache:
        return False
    
    current_hash = calculate_file_hash(filepath)
    if current_hash is None:
        return False
    
    return cache[filepath] == current_hash


def update_cache(filepath: str, cache: Dict[str, str]) -> bool:
    """
    更新缓存中文件的哈希值。
    
    Args:
        filepath: 文件路径
        cache: 缓存字典
        
    Returns:
        bool: 是否更新成功
    """
    file_hash = calculate_file_hash(filepath)
    if file_hash is None:
        return False
    
    cache[filepath] = file_hash
    return True


def get_files_to_process(filepaths: list, cache: Dict[str, str]) -> list:
    """
    获取需要处理的文件列表（排除已处理的）。
    
    Args:
        filepaths: 所有文件路径列表
        cache: 缓存字典
        
    Returns:
        list: 需要处理的文件路径列表
    """
    to_process = []
    
    for filepath in filepaths:
        if not is_file_processed(filepath, cache):
            to_process.append(filepath)
    
    return to_process


def clear_cache() -> bool:
    """
    清除缓存文件。
    
    Returns:
        bool: 是否清除成功
    """
    cache_path = os.path.join(PROCESSED_OUTPUT_DIR, CHECKSUM_CACHE_FILE)
    
    if not os.path.exists(cache_path):
        return True
    
    try:
        os.remove(cache_path)
        return True
    except Exception as e:
        print(f"清除缓存失败: {str(e)}")
        return False
