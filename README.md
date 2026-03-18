# 日志文件批量清洗与统计工具

一个用于批量处理日志文件的 Python CLI 工具，支持日志清洗、统计分析、报告生成和增量处理。

## 功能特性

- **递归扫描**: 自动扫描指定目录下的 `.log` 和 `.txt` 文件
- **智能清洗**: 过滤 DEBUG 级别、空行、时间格式不合法的日志
- **统计分析**: 按小时统计日志级别分布、错误码分布、单日峰值
- **增量处理**: 基于文件哈希的缓存机制，避免重复处理
- **双格式输出**: JSON 格式统计报告 + 纯文本可视化摘要

## 项目结构

```
.
├── main.py              # 程序入口
├── log_scanner.py       # 日志文件扫描模块
├── log_cleaner.py       # 日志清洗模块
├── log_analyzer.py      # 统计分析模块
├── log_reporter.py      # 报告生成模块
├── config/
│   ├── __init__.py
│   └── settings.py      # 全局配置
├── utils/
│   ├── __init__.py
│   └── checksum.py      # 文件哈希与缓存工具
├── raw_logs/            # 输入目录（只读）
└── processed_output/    # 输出目录
    ├── stats_report.json
    └── summary.txt
```

## 使用方法

```bash
# 查看帮助
python main.py --help

# 处理日志文件
python main.py process

# 强制重新处理所有文件
python main.py process --force

# 显示系统信息
python main.py info

# 清除处理缓存
python main.py clear-cache
```

## 清洗规则

1. 过滤空行
2. 过滤 DEBUG 级别日志
3. 过滤时间格式不合法的日志行

## 统计指标

- 日志级别分布 (INFO/WARN/ERROR)
- 按小时统计各级别数量
- 错误码分布
- 单日请求峰值

## 约束条件

- 输入目录: `./raw_logs/`
- 输出目录: `./processed_output/`
- 黑名单文件: `do_not_modify_blacklist.log` (自动跳过)
- 仅使用 Python 标准库

## 技术栈

- Python 3.10+
- 仅标准库 (os, sys, argparse, re, json, hashlib, collections)
