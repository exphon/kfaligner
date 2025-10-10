# KFaligner - Korean Forced Aligner

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![HTK](https://img.shields.io/badge/HTK-3.4.1-green.svg)](http://htk.eng.cam.ac.uk/)

**KFaligner**는 HTK(Hidden Markov Model Toolkit) 기반의 한국어 강제 정렬(Forced Alignment) 시스템입니다. 음성 파일과 전사 텍스트를 입력받아 음소(phoneme) 및 단어(word) 단위의 정확한 시간 정렬 정보를 Praat TextGrid 형식으로 출력합니다.

## 📋 목차

- [주요 기능](#주요-기능)
- [시스템 요구사항](#시스템-요구사항)
- [설치](#설치)
- [사용법](#사용법)
- [프로젝트 구조](#프로젝트-구조)
- [웹 애플리케이션](#웹-애플리케이션)
- [기술 세부사항](#기술-세부사항)
- [문제 해결](#문제-해결)
- [라이선스](#라이선스)

## 🎯 주요 기능

- **자동 음소 정렬**: 한국어 음성과 텍스트를 음소 단위로 정확하게 정렬
- **다중 샘플레이트 지원**: 8kHz, 11.025kHz, 16kHz 음성 파일 처리
- **자동 리샘플링**: Praat 스크립트를 이용한 16kHz 자동 변환
- **TextGrid 출력**: Praat에서 바로 사용 가능한 표준 형식
- **사전 자동 확장**: 미등록 단어에 대한 발음 사전 자동 생성
- **웹 인터페이스**: Flask 기반 웹 애플리케이션 제공
- **Short Pause (sp) 처리**: 단어 사이의 휴지를 별도 구간으로 분리

## 💻 시스템 요구사항

### 필수 요구사항

- **Python**: 3.6 이상
- **HTK**: 3.4.1 (Hidden Markov Model Toolkit)
- **Praat**: 음성 분석 및 리샘플링용 (선택사항)
- **OS**: Linux (Ubuntu 20.04+ 권장)

### Python 패키지

```bash
flask>=2.0.0
gunicorn>=20.0.0
numpy
```

## 🚀 설치

### 1. 저장소 클론

```bash
git clone https://github.com/exphon/kfaligner.git
cd kfaligner
```

### 2. HTK 설치

HTK는 라이선스 제약으로 직접 다운로드가 필요합니다:

1. [HTK 공식 사이트](http://htk.eng.cam.ac.uk/)에서 HTK-3.4.1 다운로드
2. 압축 해제 및 컴파일:

```bash
tar -xvf HTK-3.4.1.tar.gz
cd htk
./configure --prefix=/usr/local
make all
sudo make install
```

### 3. Python 환경 설정

```bash
# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt  # requirements.txt가 있는 경우
# 또는
pip install flask gunicorn numpy
```

## 📖 사용법

### 기본 사용법 (커맨드라인)

```bash
python3 align.py <audio.wav> <transcript.lab> <output.TextGrid>
```

**예시:**
```bash
python3 align.py test/mv01_t01_s01.wav test/mv01_t01_s01.lab output.TextGrid
```

### 입력 파일 형식

#### 1. 음성 파일 (.wav)
- **샘플레이트**: 16000 Hz (권장)
  - 8000 Hz, 11025 Hz도 지원 (자동 모델 선택)
  - 다른 샘플레이트는 자동으로 16kHz로 리샘플링
- **채널**: 모노 (Mono)
- **비트 깊이**: 16-bit PCM

#### 2. 전사 파일 (.lab)
- **인코딩**: UTF-8
- **형식**: 한국어 철자법 텍스트 (한 줄)
- **예시**: `기차도 정이도 없었다`

### 출력 파일 형식

**TextGrid 파일** (Praat 호환):
- **phone tier**: 음소 단위 정렬 (`gg`, `i`, `c`, `a`, `d`, `o`, ...)
- **word tier**: 단어 단위 정렬 (`GICADO`, `JEONGIDO`, `EOBSEOSSDA`)
- **경계 표시**: `sil` (silence), `sp` (short pause)

### 리샘플링 (옵션)

16kHz가 아닌 음성 파일은 Praat 스크립트로 변환:

```bash
# Praat 스크립트 실행
praat --run resampleTo16000.praat input.wav output_16k.wav
```

### 사전에 없는 단어 추가

```bash
# 문장 리스트 파일 준비 (flist.txt)
echo "새로운 문장들" > flist.txt

# 사전 생성 및 추가
./make_dict.sh flist.txt
```

이 스크립트는 `bin/` 디렉토리의 도구를 사용하여:
1. 한글을 유니코드로 변환
2. 음소 시퀀스 생성
3. 기존 사전에 병합

## 📁 프로젝트 구조

```
kfaligner/
├── align.py                    # 메인 정렬 스크립트
├── __init__.py                 # Python 패키지 초기화
├── restart.sh                  # 서버 관리 스크립트
├── make_dict.sh               # 사전 생성 스크립트
├── resampleTo16000.praat      # 리샘플링 Praat 스크립트
├── check_alignment.praat      # 정렬 결과 검증 스크립트
│
├── bin/                        # 유틸리티 스크립트
│   ├── make_kdict.py          # 한국어 사전 생성기
│   ├── add_dict.py            # 사전 추가 도구
│   ├── kdictmap.py            # 음소 매핑
│   ├── han2uniconversion.py   # 한글-유니코드 변환
│   ├── convert_sentences_unicode.py
│   ├── dict                   # 발음 사전
│   ├── kdict0.txt             # 기본 한국어 사전
│   └── kdict1.txt             # 확장 사전
│
├── model/                      # HTK 음향 모델
│   ├── dict                   # 메인 발음 사전 (5,589+ 단어)
│   ├── monophones             # 음소 목록
│   └── 16000/                 # 16kHz 모델
│       ├── hmmdefs            # HMM 정의
│       ├── macros             # 매크로 정의
│       └── config             # HTK 설정
│
├── test/                       # 테스트 파일
│   ├── *.wav                  # 샘플 음성 파일
│   ├── *.lab                  # 샘플 전사 파일
│   └── *.TextGrid             # 출력 예시
│
├── webapp/                     # Flask 웹 애플리케이션
│   ├── app.py                 # 메인 애플리케이션
│   ├── forms.py               # 웹 폼 정의
│   ├── models.py              # 데이터베이스 모델
│   ├── templates/             # HTML 템플릿
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   └── results.html
│   └── data/                  # 업로드 및 작업 데이터
│       ├── users.db           # 사용자 데이터베이스
│       ├── uploads/           # 업로드된 파일
│       └── jobs/              # 처리 작업 디렉토리
│
├── tmp/                        # 임시 처리 파일
│   ├── tmp.mlf                # 입력 MLF
│   ├── aligned.mlf            # HVite 출력
│   └── *.mfc                  # MFCC 특징 파일
│
└── examples/                   # 예제 파일
    └── code.scp               # 파일 리스트 예시
```

## 🌐 웹 애플리케이션

### 서버 시작

```bash
# 개발 서버 (5010 포트)
cd webapp
python3 app.py

# 프로덕션 서버 (Gunicorn + Systemd)
sudo systemctl start kfaligner
sudo systemctl enable kfaligner

# 서버 관리 스크립트 사용
./restart.sh start|stop|restart|reload|status
```

### 웹 인터페이스 접근

```
http://localhost:5010
```

### 주요 기능

- **파일 업로드**: WAV + LAB 파일 동시 업로드
- **배치 처리**: 여러 파일 동시 정렬
- **결과 다운로드**: TextGrid 파일 다운로드
- **사용자 관리**: 회원가입/로그인 시스템
- **작업 히스토리**: 과거 정렬 결과 조회

### 환경 변수 설정

```bash
# webapp/app.py 또는 systemd 서비스에서
export MAX_CONTENT_LENGTH_MB=64        # 최대 업로드 크기
export MAX_FILES_PER_REQUEST=100       # 최대 파일 수
export ENABLE_CLAMAV_SCAN=1            # 바이러스 스캔 활성화
```

## 🔧 기술 세부사항

### HTK 기반 강제 정렬

KFaligner는 HVite를 사용한 Viterbi 정렬을 수행합니다:

```bash
HVite -T 1 -a -m \
      -I tmp/tmp.mlf \
      -H model/16000/macros \
      -H model/16000/hmmdefs \
      -S tmp/test.scp \
      model/dict \
      model/monophones \
      > tmp/aligned.mlf
```

**주요 옵션:**
- `-T 1`: 트레이스 레벨 (디버깅)
- `-a`: 음소 경계 출력
- `-m`: 모델 사용
- `-I`: 입력 MLF (Master Label File)
- `-H`: HMM 정의 파일

### Short Pause (sp) 처리

**문제**: HTK의 sp는 tee-model (1-state)로 sil의 중간 상태를 공유합니다.

**해결 방법** (2025-10-09 업데이트):
1. **사전**: 모든 단어가 `sp`로 끝남 (5,589 단어)
2. **MLF**: `sp` 삽입 없음, `sil`만 문장 양 끝에
3. **후처리**: `readAlignedMLF()`에서 단어 끝 `sp`를 별도 항목으로 분리

```python
# align.py Line 196-205
for wrd in ret:
    if len(wrd) > 1 and wrd[-1][0] == 'sp':
        sp_entry = wrd.pop()  # sp를 단어에서 분리
        separated_ret.append(wrd)  # 단어만
        separated_ret.append(['sp', sp_entry])  # sp 별도
```

**결과**: 단어 사이의 pause가 별도 구간으로 TextGrid에 표시됩니다.

자세한 내용: [SP_SEPARATION_FINAL.md](SP_SEPARATION_FINAL.md)

### 음소 체계

한국어 로마자 표기 기반 음소:

- **자음**: `gg`, `dd`, `bb`, `jj`, `ss`, `k`, `t`, `p`, `c`, `h`, `g`, `d`, `b`, `j`, `m`, `n`, `ng`, `r`, `s`
- **모음**: `a`, `eo`, `o`, `u`, `eu`, `i`, `ae`, `e`, `wa`, `weo`, `wo`, `we`, `oe`, `wi`, `ui`, `ya`, `yeo`, `yo`, `yu`, `yae`, `ye`
- **특수**: `sil` (silence), `sp` (short pause)

### 지원 샘플레이트

| 샘플레이트 | 모델 디렉토리 | 자동 변환 |
|----------|------------|---------|
| 8000 Hz  | model/8000/ | ✅ |
| 11025 Hz | model/11025/ | ✅ |
| 16000 Hz | model/16000/ | - |
| 기타     | -          | → 16000 Hz |

## 🐛 문제 해결

### 1. "dur<=0" 에러

**증상**: HVite가 `ERROR [+8522] LatFromPaths: Align have dur<=0` 출력

**원인**: sp가 MLF와 사전 양쪽에 있어 tee-model 충돌

**해결**: 
- `between_token = None` 설정 (MLF에 sp 삽입 안 함)
- 사전에만 sp 유지

참고: [ALIGNMENT_FIX_REPORT.md](ALIGNMENT_FIX_REPORT.md)

### 2. 중복 sil 토큰

**증상**: 문장 시작/끝에 `sil sil` 나타남

**원인**: `-b sil` 옵션 + MLF의 sil = 중복

**해결**: HVite에서 `-b` 옵션 제거

참고: [MLF_DEDUPLICATION_FIX.md](MLF_DEDUPLICATION_FIX.md)

### 3. 사전에 없는 단어

**증상**: 특정 단어에서 정렬 실패

**해결**:
```bash
# 자동 사전 생성
./make_dict.sh flist.txt

# 또는 수동 추가
python3 bin/make_kdict.py
```

### 4. 샘플레이트 불일치

**증상**: 정렬 품질 저하 또는 실패

**해결**:
```bash
# Praat으로 리샘플링
praat --run resampleTo16000.praat input.wav output.wav

# 또는 sox 사용
sox input.wav -r 16000 output.wav
```

### 5. 웹앱 업로드 실패

**증상**: "Maximum file size exceeded"

**해결**:
```bash
# app.py 또는 환경변수 수정
export MAX_CONTENT_LENGTH_MB=128

# Nginx 설정 (프록시 사용 시)
client_max_body_size 128M;
```

## 📚 추가 문서

- [SP_SEPARATION_FINAL.md](SP_SEPARATION_FINAL.md) - sp 분리 로직 상세 설명
- [SP_SIL_EXPLANATION.md](SP_SIL_EXPLANATION.md) - sp와 sil의 차이
- [ALIGNMENT_FIX_REPORT.md](ALIGNMENT_FIX_REPORT.md) - dur<=0 에러 해결
- [MLF_DEDUPLICATION_FIX.md](MLF_DEDUPLICATION_FIX.md) - 중복 토큰 수정
- [SERVER_MANAGEMENT.md](SERVER_MANAGEMENT.md) - 서버 운영 가이드
- [CHANGELOG_RESAMPLING.md](CHANGELOG_RESAMPLING.md) - 리샘플링 변경 이력

## 🙏 감사의 말

이 프로젝트는 다음 기술을 기반으로 합니다:

- **HTK (Hidden Markov Model Toolkit)**: Cambridge University Engineering Department
- **Praat**: Paul Boersma and David Weenink
- **Flask**: Pallets Projects

## 👤 저자

**Tae-Jin Yoon**  
Sungshin Women's University 
© January 2016-2025

## 📧 문의

프로젝트 관련 문의사항이나 버그 리포트는 GitHub Issues를 이용해주세요:  
https://github.com/exphon/kfaligner/issues

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

**⭐ 이 프로젝트가 유용하다면 Star를 눌러주세요!**
