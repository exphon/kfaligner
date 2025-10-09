# 정렬 실패 문제 해결 및 중복 sil 제거

## 📅 수정 일시
2025-10-09

## 🚨 발생한 문제

### 문제 1: 정렬 실패
**에러 메시지:**
```
'NoneType' object has no attribute 'strip'
```

**원인:**
- `between_token = None`으로 설정
- 하지만 Line 302에서 `between_token.strip()` 호출
- `None`에는 `.strip()` 메서드가 없어 에러 발생

### 문제 2: 중복 sil 토큰
**현상:**
- TextGrid 시작 부분: `sil, sil`
- TextGrid 끝 부분: `sil, sil`

**원인:**
- MLF에 `sil`이 양 끝에 포함됨
- HVite `-b sil` 옵션으로 문장 경계에 `sil` 추가
- 결과: 양쪽 모두에서 중복 발생

## ✅ 해결 방법

### 수정 1: None 체크 추가 (Line 300-303)

**변경 전:**
```python
if surround_token.strip() == "":
    surround_token = None
if between_token.strip() == "":
    between_token = None
```

**변경 후:**
```python
if surround_token is not None and surround_token.strip() == "":
    surround_token = None
if between_token is not None and between_token.strip() == "":
    between_token = None
```

**효과:** `None` 값에 대해 `.strip()` 호출 방지

### 수정 2: -b sil 옵션 제거 (Line 264)

**변경 전:**
```python
os.system('HVite -T 1 -a -m -b sil -I ' + input_mlf + ' ...')
```

**변경 후:**
```python
os.system('HVite -T 1 -a -m -I ' + input_mlf + ' ...')
```

**이유:** MLF에 이미 `sil`이 포함되어 있으므로 `-b sil` 불필요

## 📊 최종 구조

### MLF (입력):
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

### 사전:
```
sil sil
sp sp
WORD1 phonemes sp
WORD2 phonemes sp
WORD3 phonemes sp
```

### 정렬 결과:
```
0-500000    sil
500000-...  [WORD1 phonemes]
...         sp (0 길이 또는 매우 짧음)
...         [WORD2 phonemes]
...         sp (0 길이 또는 매우 짧음)
...         [WORD3 phonemes]
...         sp (짧은 길이)
...-15000   sil
```

### TextGrid (출력):

**Phone tier:**
```
sil → g → i → c → a → d → o → j → eo → n → g → i → d → o → eo → b → s → eo → dd → a → sp → sil
```

**Word tier:**
```
sil → GICADO → JEONGIDO → EOBSEOSSDA → sil
```

## 🎯 개선 효과

### Before (문제 있음):
```
TextGrid:
sil (0-0.0325)
sil (0.0325-0.0625)     ← 중복!
...단어들...
sil (1.4725-1.4925)
sil (1.4925-1.5125)     ← 중복!
```

### After (수정 후):
```
TextGrid:
sil (0.0125-0.0625)     ← 한 번만!
g (0.0625-0.1325)
...단어들...
sp (1.4725-1.4925)
sil (1.4925-1.5125)     ← 한 번만!
```

## 📈 최종 정리

### 현재 설정:
- **surround_token**: `'sil'` (문장 양 끝)
- **between_token**: `None` (사전의 sp 사용)
- **HVite 옵션**: `-b` 옵션 제거
- **사전**: 모든 단어가 `sp`로 끝남

### 장점:
✅ **중복 제거**: 시작/끝에 sil이 한 번씩만  
✅ **일관성**: 모든 단어 사이에 sp (사전에서)  
✅ **깔끔함**: 명확한 경계 구분  
✅ **자연스러움**: 음성에 따라 sp 길이 조정  

### sp의 특성:
- 사전에 `sp`가 있지만 실제 음성에 휴지가 없으면 0 길이로 나타남
- 실제 휴지가 있으면 적절한 길이로 확장됨
- Tee-model 특성상 유연하게 조정됨

## 🧪 테스트 결과

### 테스트 명령어:
```bash
cd /var/www/html/kfaligner
python3 align.py test/mv01_t01_s01.wav test/mv01_t01_s01.lab test/test_output.TextGrid
```

### 결과:
- ✅ MLF 생성 성공
- ✅ HVite 정렬 성공
- ✅ TextGrid 생성 성공
- ✅ sil 중복 없음
- ✅ sp가 단어 사이에 적절히 삽입됨

## 🔄 변경 이력

| 시간 | 변경 내용 | 파일 | 라인 |
|------|-----------|------|------|
| 17:00 | between_token = None 설정 | align.py | 292 |
| 17:01 | None 체크 추가 (첫 번째 시도) | align.py | 300-303 |
| 17:02 | -b sil 옵션 제거 | align.py | 264 |
| 17:03 | 테스트 성공 확인 | - | - |
| 17:04 | 서버 재시작 | - | - |

## 📝 남은 관찰 사항

### sp의 0 길이 현상
일부 sp가 0 길이 또는 매우 짧게 나타나는 것은 정상입니다:
- 음성에 실제 휴지가 없는 경우
- Tee-model이 최소 길이로 조정
- 경계는 표시되지만 시간은 거의 없음

예시:
```
4600000 4600000 sp -0.217552    ← 0 길이
8100000 8100000 sp -0.217552    ← 0 길이
14600000 14800000 sp -157.495865 ← 약간의 길이 (마지막)
```

이는 HTK의 정상적인 동작이며, 실제 음성 데이터의 특성을 반영합니다.

## 🎓 교훈

1. **None 체크의 중요성**
   - 옵션 파라미터는 항상 None일 수 있음
   - 메서드 호출 전 None 체크 필수

2. **옵션 중복 주의**
   - MLF와 HVite 옵션이 겹칠 수 있음
   - 한 곳에서만 처리하는 것이 명확함

3. **사전 구조의 영향**
   - 사전에 sp가 있으면 MLF에서 중복 삽입 불필요
   - 일관된 정책 유지 중요

---
수정 완료: 2025-10-09 17:04
수정자: GitHub Copilot
상태: ✅ 테스트 통과, 프로덕션 배포 완료
