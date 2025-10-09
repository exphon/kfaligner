# KFAligner Flask Webapp

간단한 업로더로 wav/txt(lab) 파일들을 업로드하면 `align.py`를 호출하여 Praat TextGrid를 생성하고 다운로드할 수 있습니다.

## 요구 사항
- Python 3
- Flask
- sox, HCopy, HVite 실행 가능 (PATH에 존재)

## 실행
```bash
# (선택) 가상환경 준비 후
pip install flask werkzeug

# 앱 실행
python3 webapp/app.py
# 브라우저에서 http://localhost:5001 접속
```

업로드된 파일은 `webapp/data/uploads/<job_id>/`, 결과 TextGrid는 `webapp/data/jobs/<job_id>/`에 저장됩니다.

## 기능
- 여러 파일 동시 업로드
- 파일명(stem) 기준 wav↔txt 자동 매칭
- 개별 TextGrid 또는 ZIP 일괄 다운로드