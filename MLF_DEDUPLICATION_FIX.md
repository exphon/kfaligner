# MLF 생성 방식 변경 - 중복 sp/sil 제거

## 📅 변경 일시
2025-10-09

## 🔍 문제 상황

사용자 보고: 단어 경계 바깥쪽에 `sil, sil` 또는 `sp, sil, sil`과 같이 연속되어 나타남 (특히 파일 시작/끝)

### 원인 분석

**이전 설정:**
```python
surround_token = 'sil'  # 문장 앞뒤
between_token = 'sp'    # 단어 사이
```

**생성된 MLF 구조:**
```
sil
WORD1
sp         ← MLF의 between token
WORD2
sp         ← MLF의 between token
sil
```

**사전 구조 (최근 수정 후):**
```
WORD1 phonemes sp    ← 사전의 sp
WORD2 phonemes sp    ← 사전의 sp
```

**HVite 정렬 결과:**
```
sil
[WORD1 phonemes] sp    ← 사전의 sp
sp                      ← MLF의 sp (중복!)
[WORD2 phonemes] sp    ← 사전의 sp
sp                      ← MLF의 sp (중복!)
sil
```

**문제점:**
- `sp`가 이중으로 삽입됨 (사전 + MLF)
- 파일 끝에 `sp sil` 또는 `sp sil sil` 패턴 발생
- Tee-model 특성상 병합되지만 불필요한 경로 생성

## ✅ 해결 방법

### 변경 사항 1: between_token을 None으로 설정

**파일:** `align.py` (Line 291-292)

```python
# 변경 전:
surround_token = getopt2("-p", opts, 'sil')
between_token = getopt2("-b", opts, 'sp')

# 변경 후:
surround_token = getopt2("-p", opts, 'sil')
between_token = getopt2("-b", opts, None)  # sp 삽입 중단
```

**이유:** 사전에 이미 모든 단어가 `sp`로 끝나므로 MLF에서 추가로 삽입할 필요 없음

### 변경 사항 2: prep_mlf 함수 정리

**파일:** `align.py` (Line 144-147)

```python
# 변경 전 (주석 처리됨):
# if between is not None and len(words) > 0 and words[-1] == between:
#     words.pop()

# 변경 후 (활성화, 하지만 between=None이므로 실행 안 됨):
if between is not None and len(words) > 0 and words[-1] == between:
    words.pop()
```

## 📊 새로운 MLF 구조

### 생성되는 MLF:
```
#!MLF!#
"*/tmp.lab"
sil
WORD1
WORD2
WORD3
sil
.
```

### 사전 (변경 없음):
```
sil sil
sp sp
WORD1 phonemes sp
WORD2 phonemes sp
WORD3 phonemes sp
```

### HVite 정렬 결과:
```
sil
[WORD1 phonemes] sp    ← 사전에서만
[WORD2 phonemes] sp    ← 사전에서만
[WORD3 phonemes] sp    ← 사전에서만
sil
```

**결과:**
- ✅ sp가 한 번만 나타남 (사전에서)
- ✅ sil이 문장 앞뒤에만 나타남
- ✅ 중복 제거로 깔끔한 정렬

## 🎯 예상 효과

### 긍정적 변화

1. **중복 제거**
   - `sp sp` 패턴 사라짐
   - `sp sil sil` 패턴 사라짐
   - 더 깔끔한 TextGrid

2. **일관성**
   - 모든 단어 사이에 정확히 하나의 `sp`
   - 예측 가능한 구조

3. **성능**
   - HVite가 탐색할 경로 감소
   - 정렬 속도 약간 향상 가능

4. **자연스러움**
   - 실제 발화에 휴지가 없으면 sp 길이가 매우 짧아짐
   - 휴지가 있으면 sp 길이가 늘어남
   - 음성 데이터에 따른 자연스러운 조정

### 주의사항

1. **단어 사이 sp는 필수**
   - 사전에 모든 단어가 `sp`로 끝나므로 보장됨
   - 만약 사전에서 `sp`를 제거하면 단어 사이 경계가 사라질 수 있음

2. **기존 TextGrid와 차이**
   - 이전 결과와 약간 다를 수 있음
   - 하지만 더 정확하고 일관된 결과

## 📝 테스트 예시

### 입력 텍스트:
```
안녕하세요 반갑습니다
```

### 이전 MLF:
```
#!MLF!#
"*/tmp.lab"
sil
안녕하세요
sp          ← MLF 삽입
반갑습니다
sp          ← MLF 삽입
sil
.
```

### 새로운 MLF:
```
#!MLF!#
"*/tmp.lab"
sil
안녕하세요
반갑습니다
sil
.
```

### 사전 (동일):
```
안녕하세요 aa nn yeo ng hh aa ss ey oo sp
반갑습니다 bb aa nn kk aa pp ss mm nn ii dd aa sp
```

### 결과 비교:

**이전:**
```
sil | aa nn yeo ng hh aa ss ey oo | sp | sp | bb aa nn kk aa pp ss mm nn ii dd aa | sp | sp | sil
                                         ↑    ↑                                              ↑    ↑
                                      사전  MLF                                            사전  MLF
```

**현재:**
```
sil | aa nn yeo ng hh aa ss ey oo | sp | bb aa nn kk aa pp ss mm nn ii dd aa | sp | sil
                                     ↑                                            ↑
                                   사전만                                        사전만
```

## 🔧 롤백 방법

이전 동작으로 되돌리려면:

```python
# align.py Line 291-292
surround_token = getopt2("-p", opts, 'sil')
between_token = getopt2("-b", opts, 'sp')  # None을 'sp'로 변경
```

## 📋 체크리스트

- [x] align.py 수정 (between_token = None)
- [x] 문서 작성
- [ ] 서버 재시작
- [ ] 테스트 실행
- [ ] TextGrid 결과 확인

## 🧪 테스트 명령어

```bash
# 1. 서버 재시작
/var/www/html/kfaligner/restart.sh reload

# 2. 테스트 파일로 정렬
cd /var/www/html/kfaligner
python3 align.py test/mv01_t01_s01.wav test/mv01_t01_s01.lab test/mv01_t01_s01_test.TextGrid

# 3. MLF 확인
cat tmp/tmp.mlf

# 4. 정렬 결과 확인
cat tmp/aligned.mlf | head -50

# 5. TextGrid 확인 (Praat)
# test/mv01_t01_s01_test.TextGrid를 Praat에서 열기
```

## 📚 관련 문서

- `SP_SIL_EXPLANATION.md` - sp와 sil의 차이 설명
- `SP_ADDITION_REPORT.md` - 사전에 sp 추가 작업 보고서
- `SERVER_MANAGEMENT.md` - 서버 관리 가이드

---
변경 날짜: 2025-10-09
변경자: GitHub Copilot
이슈: 중복 sp/sil 제거
