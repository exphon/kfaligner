#!/bin/bash

echo "==========================================="
echo "사전 파일 분석 리포트"
echo "==========================================="
echo ""

for dict_file in "/var/www/html/kfaligner/model/dict" "/var/www/html/kfaligner/bin/dict"; do
    if [ -f "$dict_file" ]; then
        echo "📁 파일: $dict_file"
        echo "   수정 시간: $(stat -c %y "$dict_file" | cut -d'.' -f1)"
        
        total=$(wc -l < "$dict_file")
        with_sp=$(grep -c "sp$" "$dict_file")
        without_sp=$(grep -v "sp$" "$dict_file" | grep -v "^sil sil$" | grep -v "^sp sp$" | wc -l)
        
        percentage_with=$(echo "scale=2; $with_sp * 100 / $total" | bc)
        percentage_without=$(echo "scale=2; $without_sp * 100 / $total" | bc)
        
        echo "   전체 항목: $total"
        echo "   sp로 끝남: $with_sp ($percentage_with%)"
        echo "   sp 없음: $without_sp ($percentage_without%)"
        echo ""
    fi
done

echo "==========================================="
echo "sp 없는 단어 샘플 (첫 20개)"
echo "==========================================="
grep -v "sp$" /var/www/html/kfaligner/bin/dict | grep -v "^sil sil$" | grep -v "^sp sp$" | head -20
echo ""
echo "==========================================="
echo "마지막 음소 분포 (sp 없는 단어)"
echo "==========================================="
grep -v "sp$" /var/www/html/kfaligner/bin/dict | grep -v "^sil sil$" | grep -v "^sp sp$" | awk '{print $NF}' | sort | uniq -c | sort -rn | head -15
