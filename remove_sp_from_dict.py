#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Remove 'sp' from the end of dictionary entries.
Preserves 'sil sil' and 'sp sp' definitions.
"""

import sys
import os

def remove_sp_from_dict(input_file, output_file):
    """Remove sp from words that have it at the end."""
    
    with open(input_file, 'r', encoding='utf-8') as fin:
        lines = fin.readlines()
    
    updated_lines = []
    removed_count = 0
    
    for line in lines:
        line = line.rstrip('\n')
        
        # Skip empty lines
        if not line.strip():
            updated_lines.append(line)
            continue
        
        parts = line.split()
        
        # Preserve sil and sp definitions
        if line == "sil sil" or line == "sp sp":
            updated_lines.append(line)
        # If ends with sp, remove it
        elif len(parts) > 2 and parts[-1] == "sp":
            # Remove the last 'sp'
            updated_lines.append(' '.join(parts[:-1]))
            removed_count += 1
        # Otherwise keep as is
        else:
            updated_lines.append(line)
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as fout:
        for line in updated_lines:
            fout.write(line + '\n')
    
    return removed_count

def analyze_dict(dict_file):
    """Analyze dictionary file."""
    total = 0
    with_sp = 0
    without_sp = 0
    
    with open(dict_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            total += 1
            
            if line.endswith(" sp"):
                with_sp += 1
            elif line not in ["sil sil", "sp sp"]:
                without_sp += 1
    
    return total, with_sp, without_sp

if __name__ == "__main__":
    base_path = "/var/www/html/kfaligner"
    
    # Files to process
    dict_files = [
        (f"{base_path}/model/dict", "model/dict"),
        (f"{base_path}/bin/dict", "bin/dict")
    ]
    
    print("=" * 60)
    print("사전 파일에서 sp 제거")
    print("=" * 60)
    print()
    
    for dict_path, dict_name in dict_files:
        if not os.path.exists(dict_path):
            print(f"⚠️  {dict_name} 파일을 찾을 수 없습니다.")
            continue
        
        print(f"📝 처리 중: {dict_name}")
        
        # Analyze before
        total_before, with_sp_before, without_sp_before = analyze_dict(dict_path)
        print(f"   변경 전: 전체 {total_before} / sp 있음 {with_sp_before} / sp 없음 {without_sp_before}")
        
        # Backup
        backup_path = dict_path + ".with_sp_backup"
        os.system(f'cp "{dict_path}" "{backup_path}"')
        print(f"   백업 완료: {backup_path}")
        
        # Remove sp
        temp_path = dict_path + ".tmp"
        removed = remove_sp_from_dict(dict_path, temp_path)
        
        # Replace original
        os.rename(temp_path, dict_path)
        
        # Analyze after
        total_after, with_sp_after, without_sp_after = analyze_dict(dict_path)
        print(f"   변경 후: 전체 {total_after} / sp 있음 {with_sp_after} / sp 없음 {without_sp_after}")
        print(f"   ✅ {removed}개 항목에서 sp 제거됨")
        print()
    
    print("=" * 60)
    print("✅ 완료!")
    print("=" * 60)
