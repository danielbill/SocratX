#!/usr/bin/env python
"""清理 socratx/ 目录下的 .pyc 缓存文件"""
import os
import sys

def clean_pycache(root_dir: str) -> int:
    """
    清理指定目录下的 __pycache__ 和 .pyc 文件
    
    Args:
        root_dir: 要清理的根目录
        
    Returns:
        删除的文件数量
    """
    deleted_count = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 删除 __pycache__ 目录
        if '__pycache__' in dirpath:
            try:
                import shutil
                shutil.rmtree(dirpath)
                print(f"Removed: {dirpath}")
                deleted_count += 1
                continue
            except Exception as e:
                print(f"Error removing {dirpath}: {e}")
        
        # 删除 .pyc 文件
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                filepath = os.path.join(dirpath, filename)
                try:
                    os.remove(filepath)
                    print(f"Removed: {filepath}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Error removing {filepath}: {e}")
    
    return deleted_count


if __name__ == '__main__':
    # 默认清理当前目录
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    if not os.path.isdir(root):
        print(f"Error: {root} is not a directory")
        sys.exit(1)
    
    print(f"Cleaning {root}...")
    count = clean_pycache(root)
    print(f"\nDone! Removed {count} files/directories")
