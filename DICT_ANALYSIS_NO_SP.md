# 사전 분석: SP 없는 단어 목록

## 통계 요약

- **전체 사전 항목**: 5,590개
- **sp로 끝나는 항목**: 5,192개 (92.9%)
- **sp 없는 항목**: 398개 (7.1%)
  - sil, sp 정의 제외

## SP 없는 단어들의 마지막 음소 분포

| 순위 | 음소 | 개수 | 비율 | 특성 |
|------|------|------|------|------|
| 1 | a | 88 | 22.1% | 모음 |
| 2 | i | 42 | 10.6% | 모음 |
| 3 | l | 26 | 6.5% | 유음 |
| 4 | m | 25 | 6.3% | 비음 |
| 5 | ng | 23 | 5.8% | 비음 |
| 6 | g | 21 | 5.3% | 파열음 |
| 7 | eu | 19 | 4.8% | 모음 |
| 7 | ae | 19 | 4.8% | 모음 |
| 9 | u | 17 | 4.3% | 모음 |
| 9 | n | 17 | 4.3% | 비음 |
| 11 | o | 16 | 4.0% | 모음 |
| 12 | yo | 9 | 2.3% | 모음 |
| 12 | yi | 9 | 2.3% | 모음 |
| 12 | e | 9 | 2.3% | 모음 |

**나머지**: oe(7), eo(6), b(6), yu(5), wi(5), k(4), yeo(3), ye(3), ya(3), wa(3), d(3), we(2), c(2), yae(1), weo(1), wae(1)

## 음소 타입별 분류

### 모음으로 끝나는 단어: 약 72%
- **단모음**: a(88), i(42), eu(19), ae(19), u(17), o(16), e(9), oe(7), eo(6)
- **이중모음**: yo(9), yi(9), yu(5), wi(5), yeo(3), ye(3), ya(3), wa(3), we(2), yae(1), weo(1), wae(1)
- **총계**: 약 286개 (71.9%)

### 자음으로 끝나는 단어: 약 28%
- **비음**: m(25), ng(23), n(17) → 65개 (16.3%)
- **유음**: l(26) → 26개 (6.5%)
- **파열음**: g(21), k(4), d(3), b(6) → 34개 (8.5%)
- **파찰음**: c(2) → 2개 (0.5%)
- **총계**: 약 112개 (28.1%)

## 패턴 분석

### 1. 모음 종결 단어
모음으로 끝나는 단어들은 주로 sp가 없는 경향:
- 조사, 어미가 붙는 경우가 많음
- 발화 중간에서 연결되는 경우가 많음
- 예시: `A a`, `AGA a g a`, `BABO b a b o`

### 2. 비음/유음 종결 단어
연속음(sonorant)으로 끝나는 단어들:
- 다음 음절로 자연스럽게 연결
- sp가 선택적으로 필요할 수 있음
- 예시: `BAM b a m`, `BAL b a l`, `BANG b a ng`

### 3. 파열음 종결 단어
파열음으로 끝나는 경우:
- 자연스러운 경계 형성
- sp 없이도 명확한 구분
- 예시: `BAB b a b`, `BAG b a g`, `BAD b a d`

## 발견된 이슈

### 중복 항목 발견
일부 단어가 sp 있는 버전과 없는 버전 모두 존재:

```bash
# 예시 확인
grep "^BARAM " model/dict
```

결과:
```
BARAM b a r a m
BARAM b a r a m sp
```

이는 HVite가 문맥에 따라 선택할 수 있도록 하기 위한 것으로 보입니다.

## SP 없는 주요 단어 예시 (처음 100개)

```
A, ABA, ABBA, ABEOJI, ACA, ACIM, ADA, ADDA, ADEUL, ADONG,
AE, AEBI, AEJIJUNGJI, AEMO, AG, AGA, AGGA, AGGI, AGI, AHA,
AI, AIKU, AJA, AJEOSSI, AJJA, AKA, ALRYEOJUMYEON, AMA, AMUGAE, AN,
ANA, ANGA, ANGAE, ANMA, AO, APA, APAYO, ARA, ASA, ASSA,
ATA, AU, BA, BAB, BABO, BAD, BAE, BAETAL, BAG, BAL,
BAM, BAN, BANG, BATMEORI, BBA, BBANG, BBEU, BBUL, BBYEO, BEONGEORI,
BEU, BISEUSI, BOGGASSGO, BUEOK, BUGNYEOK, BUNGEO, BUSDAE, CA, CAM, CAMGGAE,
CAMOE, CEMYEON, CEOMA, CEONEUL, CEU, CIMA, CIMCAG, COEGO, CURI, CYEODABODA,
DA, DAEDANHAE, DAETONGRYEONG, DAL, DANCE, DDA, DDAE, DDAL, DDANG, DDEDA,
DDEU, DDEUM, DDO, DEU, DEULPAN, ...
```

## 권장 조치

### 옵션 1: 일관성 있는 사전 구축
모든 단어에 대해 sp 없는 버전과 있는 버전을 모두 제공:

```
WORD phonemes
WORD phonemes sp
```

### 옵션 2: 규칙 기반 처리
- 모음으로 끝나는 단어: sp 없는 버전만
- 자음으로 끝나는 단어: 두 가지 버전 모두

### 옵션 3: 현재 상태 유지
- HVite가 음성 데이터에 따라 적절히 선택하도록 함
- 유연성은 있지만 예측 가능성이 낮음

## 생성된 파일

1. **words_without_sp.txt**: 단어 목록만 (398개)
2. **words_without_sp_full.txt**: 전체 발음 정보 포함 (398줄)

## 사용 방법

```bash
# 단어 목록 확인
cat /var/www/html/kfaligner/words_without_sp.txt

# 전체 발음 정보 확인
cat /var/www/html/kfaligner/words_without_sp_full.txt

# 특정 단어 검색
grep "^WORD" /var/www/html/kfaligner/model/dict
```

## 다음 단계

1. **사전 정리**: 중복 항목 확인 및 정리
2. **테스트**: 다양한 문장으로 정렬 테스트
3. **분석**: sp 삽입 패턴 분석
4. **최적화**: 필요에 따라 사전 수정

---

생성 날짜: 2025-10-09
분석 대상: /var/www/html/kfaligner/model/dict
