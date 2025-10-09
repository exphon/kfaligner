# HTK SP/SIL 처리 방식 설명

## 현재 시스템의 동작

### 1. MLF 생성 방식

현재 `align.py`는 다음과 같이 MLF를 생성합니다:

```python
surround_token = 'sil'     # 문장 시작/끝
between_token = 'sp'       # 단어 사이
```

**생성되는 MLF 예시:**
```
#!MLF!#
"*/tmp.lab"
sil
WORD1
sp
WORD2
sp
WORD3
sp         # 이제 마지막 sp도 유지됨
sil
.
```

### 2. 사전(Dictionary) 구조

사전에는 세 가지 타입의 항목이 있습니다:

```
# 1. 침묵 음소 정의
sil sil          # 긴 침묵 (3-state HMM)
sp sp            # 짧은 휴지 (1-state tee-model, sil의 중간 상태 공유)

# 2. 단어 정의 (sp 없음)
BARAM b a r a m

# 3. 단어 정의 (선택적 sp 포함)
BARAM b a r a m sp
SARAM s a r a m sp
```

### 3. HVite 정렬 과정

HVite는 MLF와 사전을 조합하여 최적 경로를 찾습니다:

#### 케이스 1: 사전에 두 가지 버전 모두 있는 경우
```
MLF:  sil → WORD → sp → sil
Dict: WORD → [phonemes]      (옵션 1)
      WORD → [phonemes sp]   (옵션 2)

HVite 선택:
- 문맥에 따라 최적 경로 선택
- 음성 데이터에 실제 휴지가 있으면 sp 포함 버전 선택
- 휴지가 없으면 sp 없는 버전 선택
```

#### 케이스 2: 사전에 sp 포함 버전만 있는 경우
```
MLF:  sil → WORD → sp → sil
Dict: WORD → [phonemes sp]

결과: sil → phonemes → sp → sp → sil
     (하지만 sp는 tee-model이므로 실제로는 한 번만 나타남)
```

### 4. SP의 Tee-Model 특성

```
        ┌─────────────────┐
        │   sil (3-state) │
        │  s1 → s2 → s3   │
        └─────────────────┘
               ↑
               │ (tied state)
               │
        ┌──────┴──────┐
        │  sp (1-state)│
        └─────────────┘
```

- `sp`는 `sil`의 중간 상태(s2)를 공유
- 여러 `sp`가 연속되어도 중복되지 않고 병합됨
- 이것이 "dur<=0" 문제의 원인이 될 수 있음

## 질문과 답변

### Q1: 시작과 끝에 "sil"이 두 번 나타나나요?

**A:** 아니요. `sil`은 문장의 시작에 한 번, 끝에 한 번만 나타납니다.

```
TextGrid 구조:
[sil] [phone1] [phone2] ... [phoneN] [sp?] [sil]
 ↑                                           ↑
 시작                                        끝
```

### Q2: 마지막 단어에서만 "sp"가 "sil" 앞에 나타나는 이유?

**A:** 다음 두 가지 요인의 조합 때문입니다:

1. **MLF 구조**: 현재는 모든 단어 뒤에 `sp`를 포함 (마지막 포함)
2. **사전 선택성**: 
   - 사전에 `WORD phonemes sp` 버전이 있으면 → 해당 단어 끝에 `sp` 추가 가능
   - 사전에 `WORD phonemes` 버전만 있으면 → 단어 끝에 `sp` 없음

### Q3: "바깥"과 "바람"에서 sp 삽입이 다른 이유?

**A:** 사전의 항목 차이 때문입니다:

```bash
# 사전 확인 예시
BARAM b a r a m        # sp 없는 버전
BARAM b a r a m sp     # sp 있는 버전 (두 가지 모두 존재)
```

HVite는 음성 신호를 분석하여:
- 실제로 휴지(pause)가 있으면 → `sp` 포함 버전 선택
- 휴지가 없으면 → `sp` 없는 버전 선택

**"바람" (m으로 끝남)**
- [m]은 비음으로 연속성이 있어 다음 음소로 자연스럽게 연결
- 실제 휴지가 있을 가능성 ↑ → `sp` 선택 가능성 ↑

**"바깥" (t으로 끝남)**  
- [t]은 파열음으로 자연스러운 경계
- 실제 휴지가 없을 가능성 ↑ → `sp` 없는 버전 선택 가능성 ↑

## 해결 방법

### 방법 1: 일관된 sp 삽입 (현재 적용됨)

**변경 사항:**
```python
# align.py의 prep_mlf 함수에서 마지막 sp를 제거하지 않음
# 이제 모든 단어 뒤에 sp가 일관되게 삽입됨
```

**장점:**
- 모든 단어 사이에 일관된 처리
- 예측 가능한 동작

**단점:**
- 마지막 단어 뒤에도 `sp`가 나타남 (문장 끝: `...phonemes sp sil`)

### 방법 2: 사전 정리

사전에서 중복 항목을 제거하고 일관성 있게 만들기:

```bash
# 옵션 A: 모든 단어에서 sp 제거
BARAM b a r a m

# 옵션 B: 모든 단어에 sp 포함
BARAM b a r a m sp

# 옵션 C: 두 가지 모두 유지 (HVite가 선택)
BARAM b a r a m
BARAM b a r a m sp
```

### 방법 3: between_token을 None으로 설정

```python
surround_token = 'sil'
between_token = None  # MLF에 sp를 넣지 않음
```

- MLF: `sil WORD1 WORD2 WORD3 sil`
- 사전의 선택적 `sp`에만 의존
- 더 자연스러운 결과 (음성에 따라 sp가 선택적으로 삽입됨)

## 권장 설정

### 상황 1: 명시적이고 일관된 휴지가 필요한 경우
```python
# align.py
surround_token = 'sil'
between_token = 'sp'

# 사전 - sp 없는 버전만
WORD phonemes
```

### 상황 2: 자연스러운 휴지 검출을 원하는 경우 (권장)
```python
# align.py
surround_token = 'sil'
between_token = None

# 사전 - 두 가지 버전 제공
WORD phonemes
WORD phonemes sp
```

### 상황 3: 현재 설정 (절충안)
```python
# align.py
surround_token = 'sil'
between_token = 'sp'

# 사전 - 두 가지 버전 제공 (그대로 유지)
WORD phonemes
WORD phonemes sp

# HVite -b sil 옵션으로 경계 명확화
```

## 테스트 방법

### 1. MLF 확인
```bash
cat /var/www/html/kfaligner/tmp/tmp.mlf
```

### 2. 정렬 결과 확인
```bash
cat /var/www/html/kfaligner/tmp/aligned.mlf
```

### 3. 사전 확인
```bash
grep "^WORD" /var/www/html/kfaligner/tmp/dict
```

## 참고 자료

- HTK Book: Chapter 7 (HVite)
- Tee-model: 짧은 음소를 다른 음소의 상태를 공유하여 모델링하는 방법
- `-b sil`: 문장 경계에서 사용할 단어 지정 옵션
