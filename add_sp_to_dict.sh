#!/bin/bash

# Function to add sp to words that don't have it
add_sp_to_dict() {
    local input_file=$1
    local output_file=$2
    
    awk '{
        # Keep sil and sp definitions as is
        if ($0 == "sil sil" || $0 == "sp sp") {
            print $0
        }
        # If line already ends with sp, keep it
        else if ($NF == "sp") {
            print $0
        }
        # Otherwise, add sp at the end
        else {
            print $0 " sp"
        }
    }' "$input_file" > "$output_file"
}

echo "=========================================="
echo "사전 파일에 sp 추가 중..."
echo "=========================================="
echo ""

# Process model/dict
echo "처리 중: model/dict"
add_sp_to_dict "/var/www/html/kfaligner/model/dict.backup_$(ls -t /var/www/html/kfaligner/model/dict.backup_* | head -1 | xargs basename | cut -d'_' -f3-)" "/var/www/html/kfaligner/model/dict.tmp"
mv /var/www/html/kfaligner/model/dict.tmp /var/www/html/kfaligner/model/dict

# Get stats for model/dict
total_model=$(wc -l < /var/www/html/kfaligner/model/dict)
with_sp_model=$(grep -c "sp$" /var/www/html/kfaligner/model/dict)
without_sp_model=$(grep -v "sp$" /var/www/html/kfaligner/model/dict | grep -v "^sil sil$" | grep -v "^sp sp$" | wc -l)

echo "  전체 항목: $total_model"
echo "  sp로 끝남: $with_sp_model"
echo "  sp 없음: $without_sp_model"
echo ""

# Process bin/dict
echo "처리 중: bin/dict"
add_sp_to_dict "/var/www/html/kfaligner/bin/dict.backup_$(ls -t /var/www/html/kfaligner/bin/dict.backup_* | head -1 | xargs basename | cut -d'_' -f3-)" "/var/www/html/kfaligner/bin/dict.tmp"
mv /var/www/html/kfaligner/bin/dict.tmp /var/www/html/kfaligner/bin/dict

# Get stats for bin/dict
total_bin=$(wc -l < /var/www/html/kfaligner/bin/dict)
with_sp_bin=$(grep -c "sp$" /var/www/html/kfaligner/bin/dict)
without_sp_bin=$(grep -v "sp$" /var/www/html/kfaligner/bin/dict | grep -v "^sil sil$" | grep -v "^sp sp$" | wc -l)

echo "  전체 항목: $total_bin"
echo "  sp로 끝남: $with_sp_bin"
echo "  sp 없음: $without_sp_bin"
echo ""

echo "=========================================="
echo "완료!"
echo "=========================================="
