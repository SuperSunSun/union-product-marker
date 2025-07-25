# -*- coding: utf-8 -*-
"""
批量文件重命名工具

这个工具用于对指定目录（包括子目录）下的文件进行批量重命名操作。
支持多种重命名规则和模式，如添加前缀、替换特定模式等。

使用方法：
1. 在 RENAME_STRATEGIES 中选择或配置重命名策略
2. 运行脚本
3. 确认要重命名的文件列表
4. 输入 'y' 执行重命名操作

注意事项：
- 脚本会递归处理所有子目录
- 只处理指定后缀的文件
- 根据选择的策略执行不同的重命名规则
- 建议先备份重要文件
- 可通过 OVERWRITE_EXISTING 配置是否覆盖已存在的同名文件
"""

import os
import re
from typing import List, Dict, Callable, Any
from dataclasses import dataclass

# === 全局配置 ===
FOLDER_PATH = r"D:\PROJECTS\union_scraper\output"  # 要处理的根目录路径
EXTENSIONS = (".html", ".jpg", ".json")  # 要处理的文件后缀列表
OVERWRITE_EXISTING = True  # 是否覆盖已存在的同名文件

@dataclass
class RenameStrategy:
    """重命名策略配置类"""
    name: str                              # 策略名称
    description: str                       # 策略描述
    should_process: Callable[[str], bool]  # 文件是否需要处理的判断函数
    get_new_name: Callable[[str], str]     # 生成新文件名的函数
    config: Dict[str, Any]                 # 策略配置参数

# === 重命名策略配置 ===
RENAME_STRATEGIES = {
    'add_prefix': RenameStrategy(
        name='add_prefix',
        description=lambda c: f"添加前缀: '{c['prefix']}'",
        should_process=lambda filename, c: not filename.startswith(c['prefix']),
        get_new_name=lambda filename, c: c['prefix'] + filename,
        config={
            'prefix': 'a_'  # 要添加的前缀
        }
    ),
    
    'replace_prefix': RenameStrategy(
        name='replace_prefix',
        description=lambda c: (f"替换前缀: 将以 '{c['old_prefix']}' 开头但不以 "
                             f"'{c['exclude_prefix']}' 开头的文件改为以 "
                             f"'{c['new_prefix']}' 开头"),
        should_process=lambda filename, c: (
            filename.startswith(c['old_prefix']) and 
            not filename.startswith(c['exclude_prefix'])
        ),
        get_new_name=lambda filename, c: (
            c['new_prefix'] + filename[len(c['old_prefix']):]
            if filename.startswith(c['old_prefix']) else filename
        ),
        config={
            'old_prefix': 'a',     # 要匹配的前缀（不含下划线）
            'new_prefix': 'a_',    # 要替换成的新前缀
            'exclude_prefix': 'a_'  # 排除的前缀
        }
    ),
    
    'pattern_replace': RenameStrategy(
        name='pattern_replace',
        description=lambda c: f"模式替换: '{c['pattern']}' → '{c['replacement']}'",
        should_process=lambda filename, c: bool(re.match(c['pattern'], filename)),
        get_new_name=lambda filename, c: re.sub(c['pattern'], c['replacement'], filename),
        config={
            'pattern': r'old_(\w+)',      # 要匹配的模式
            'replacement': r'new_\1'      # 替换后的模式
        }
    )
}

# 当前使用的重命名策略
CURRENT_STRATEGY = 'replace_prefix'

def collect_target_files(folder_path: str, extensions: tuple, strategy: RenameStrategy) -> list:
    """
    扫描目录及其子目录，收集需要重命名的文件列表
    
    参数：
        folder_path (str): 要扫描的根目录路径
        extensions (tuple): 要处理的文件后缀元组
        strategy (RenameStrategy): 重命名策略
        
    返回：
        list: 需要重命名的文件完整路径列表
    """
    targets = []
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if (filename.lower().endswith(extensions) and 
                strategy.should_process(filename, strategy.config)):
                full_path = os.path.join(root, filename)
                targets.append(full_path)
    return targets

def rename_files(file_list: list, strategy: RenameStrategy) -> None:
    """
    执行文件重命名操作
    
    参数：
        file_list (list): 要重命名的文件路径列表
        strategy (RenameStrategy): 重命名策略
    """
    for old_path in file_list:
        dir_name = os.path.dirname(old_path)
        filename = os.path.basename(old_path)
        new_filename = strategy.get_new_name(filename, strategy.config)
        new_path = os.path.join(dir_name, new_filename)

        try:
            if os.path.exists(new_path):
                if OVERWRITE_EXISTING:
                    os.remove(new_path)
                    print(f"🗑️ 删除已存在的文件: {new_filename}")
                    os.rename(old_path, new_path)
                    print(f"✅ 重命名: {filename} → {new_filename}")
                else:
                    print(f"⚠️ 跳过: {filename} → {new_filename} (目标文件已存在)")
                    continue
            else:
                os.rename(old_path, new_path)
                print(f"✅ 重命名: {filename} → {new_filename}")
        except Exception as e:
            print(f"❌ 重命名失败: {filename}，原因: {e}")

if __name__ == "__main__":
    strategy = RENAME_STRATEGIES[CURRENT_STRATEGY]
    
    # 打印配置信息
    print(f"\n📁 扫描目录: {FOLDER_PATH}")
    print(f"🎯 目标后缀: {EXTENSIONS}")
    print(f"🔄 重命名策略: {strategy.description(strategy.config)}")
    print(f"⚙️ 覆盖已存在文件: {'是' if OVERWRITE_EXISTING else '否'}\n")

    # 收集需要重命名的文件
    targets = collect_target_files(FOLDER_PATH, EXTENSIONS, strategy)

    if not targets:
        print("✅ 未找到需要重命名的文件。程序结束。")
    else:
        # 显示待处理文件列表
        print("即将重命名以下文件：\n")
        for path in targets:
            print("  " + path)

        # 请求用户确认
        choice = input("\n是否继续重命名？(y/n): ").strip().lower()
        if choice == 'y':
            rename_files(targets, strategy)
            print("\n🎉 所有操作完成！")
        else:
            print("🚫 操作已取消。")
