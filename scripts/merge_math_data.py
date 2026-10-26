#!/usr/bin/env python3
"""
合并数学数据文件
将分散的topics/dependencies/questions文件合并为统一文件
"""

import json
from pathlib import Path

def merge_json_files(data_dir, pattern, output_file):
    """合并多个JSON文件"""
    files = sorted(data_dir.glob(pattern))
    merged = []
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            merged.extend(data)
            print(f"  Loaded {len(data)} items from {f.name}")
    
    with open(output_file, 'w', encoding='utf-8') as fp:
        json.dump(merged, fp, ensure_ascii=False, indent=2)
    
    print(f"  Merged {len(merged)} items -> {output_file}")
    return len(merged)

def main():
    data_dir = Path('data/math')
    
    print("Merging math topics...")
    topics_count = merge_json_files(data_dir, 'topics*.json', data_dir / 'topics_all.json')
    
    print("\nMerging math dependencies...")
    deps_count = merge_json_files(data_dir, 'dependencies*.json', data_dir / 'dependencies_all.json')
    
    print("\nMerging math questions...")
    questions_count = merge_json_files(data_dir, 'questions*.json', data_dir / 'questions_all.json')
    
    print("\n" + "="*50)
    print("Merge Summary:")
    print(f"  Topics: {topics_count}")
    print(f"  Dependencies: {deps_count}")
    print(f"  Questions: {questions_count}")

if __name__ == '__main__':
    main()
