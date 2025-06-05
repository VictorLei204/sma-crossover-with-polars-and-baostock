"""
简单的配置管理模块

提供基本的配置文件读取功能，最小化对现有代码的修改。
"""

import json
import os


def load_config(config_file="config.json"):
    """
    加载配置文件
    
    Args:
        config_file: 配置文件路径
    
    Returns:
        dict: 配置字典
    """
    # 默认配置
    default_config = {
        "stock_code": "sh.600000",
        "start_date": "2020-01-01",
        "end_date": "2024-12-31",
        "short_window": 20,
        "long_window": 60,
        "initial_capital": 100000,
        "trading_fees": {
            "commission_rate": 0.0003,      # 佣金率：万分之三
            "stamp_tax_rate": 0.001,        # 印花税率：千分之一
            "transfer_fee_rate": 0.001,     # 过户费率：千分之一
            "min_commission": 5.0           # 最低佣金：5元
        }
    }
    
    # 如果配置文件不存在，创建默认配置文件
    if not os.path.exists(config_file):
        print(f"配置文件 {config_file} 不存在，创建默认配置文件")
        save_config(default_config, config_file)
        return default_config
    
    # 读取配置文件
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 确保所有必需的键都存在，如果不存在则使用默认值
        for key, default_value in default_config.items():
            if key not in config:
                config[key] = default_value
                
        return config
        
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"读取配置文件失败: {e}")
        print("使用默认配置")
        return default_config


def save_config(config, config_file="config.json"):
    """
    保存配置到文件
    
    Args:
        config: 配置字典
        config_file: 配置文件路径
    """
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"配置已保存到 {config_file}")
    except Exception as e:
        print(f"保存配置文件失败: {e}")


def get_config_value(config, key, default=None):
    """
    安全地获取配置值
    
    Args:
        config: 配置字典
        key: 配置键
        default: 默认值
    
    Returns:
        配置值或默认值
    """
    return config.get(key, default)
