# align.py 리샘플링 개선 사항

## 변경 날짜
2025-10-09

## 변경 내용

### 1. 기본 샘플레이트 변경
- **이전**: 11025 Hz
- **이후**: 16000 Hz
- **이유**: 더 나은 음질과 정렬 정확도 제공

### 2. Sox 명령어 구문 수정
- **이전**: `sox input -r RATE output polyphase`
- **이후**: `sox "input" "output" rate -v RATE`
- **개선사항**:
  - 올바른 sox 명령어 구문 사용
  - 파일명에 공백이나 특수문자가 있을 경우 대비하여 따옴표 추가
  - `rate -v` 사용으로 고품질 리샘플링 (very high quality)

### 3. 지원되는 입력 샘플레이트
모든 샘플레이트가 자동으로 16000 Hz로 변환됩니다:
- ✅ 8000 Hz
- ✅ 11025 Hz
- ✅ 16000 Hz (변환 없음)
- ✅ 22050 Hz
- ✅ **44100 Hz** (NEW!)
- ✅ **48000 Hz** (NEW!)
- ✅ 기타 모든 샘플레이트

### 4. 테스트 결과

#### 44100 Hz 테스트
```bash
# 입력: test_44100hz.wav (44100 Hz)
# 출력: test_44100hz_output.TextGrid
# 결과: ✅ 성공 (16000 Hz로 리샘플링 후 정렬)
```

#### 48000 Hz 테스트
```bash
# 입력: test_48000hz.wav (48000 Hz)
# 출력: test_48000hz_output.TextGrid  
# 결과: ✅ 성공 (16000 Hz로 리샘플링 후 정렬)
```

## 사용 예시

### 기본 사용 (자동 16000 Hz 리샘플링)
```bash
python align.py audio_44100hz.wav transcript.txt output.TextGrid
```

### 특정 샘플레이트 지정
```bash
python align.py -r 8000 audio.wav transcript.txt output.TextGrid
```

## 주의사항
- sox가 시스템에 설치되어 있어야 합니다
- conda 환경 `aligner`를 활성화한 상태에서 실행하세요
