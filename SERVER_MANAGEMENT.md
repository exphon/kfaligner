# KFAligner 서버 관리 가이드

## restart.sh 사용법

`restart.sh`는 KFAligner 웹 애플리케이션 서버를 관리하는 스크립트입니다.

### 기본 사용법

```bash
/var/www/html/kfaligner/restart.sh [command]
```

### 사용 가능한 명령어

#### 1. **start** - 서버 시작
```bash
/var/www/html/kfaligner/restart.sh start
```
- 실행 중인 서버를 종료하고 새로 시작합니다
- 시스템 부팅 후 처음 서버를 시작할 때 사용

#### 2. **stop** - 서버 중지
```bash
/var/www/html/kfaligner/restart.sh stop
```
- 실행 중인 서버를 안전하게 종료합니다

#### 3. **restart** - 서버 재시작 (기본값)
```bash
/var/www/html/kfaligner/restart.sh restart
# 또는
/var/www/html/kfaligner/restart.sh
```
- 서버를 완전히 중지한 후 다시 시작합니다
- 설정 파일 변경이나 큰 변경사항이 있을 때 사용

#### 4. **reload** - 서버 리로드 (권장)
```bash
/var/www/html/kfaligner/restart.sh reload
```
- 서버를 중단 없이 graceful하게 재시작합니다
- Python 코드 변경 시 사용 (예: `align.py` 수정 후)
- 실행 중인 요청을 완료한 후 워커 프로세스만 재시작
- **코드 변경 후 가장 권장되는 방법**

#### 5. **status** - 서버 상태 확인
```bash
/var/www/html/kfaligner/restart.sh status
```
- 현재 서버가 실행 중인지 확인합니다
- 프로세스 ID와 워커 프로세스 정보를 표시합니다

## 서버 설정

### 서버 정보
- **바인드 주소**: 127.0.0.1:5011
- **워커 수**: 2
- **타임아웃**: 300초
- **프론트엔드 포트**: 5010 (nginx 프록시)

### 로그 파일
- **접속 로그**: `/var/www/html/kfaligner/webapp/access.log`
- **에러 로그**: `/var/www/html/kfaligner/webapp/error.log`
- **PID 파일**: `/var/www/html/kfaligner/webapp/server.pid`

## 일반적인 사용 시나리오

### 코드 수정 후
```bash
# align.py나 webapp/app.py 등을 수정한 경우
/var/www/html/kfaligner/restart.sh reload
```

### 시스템 재부팅 후
```bash
# 시스템이 재부팅된 후 서버를 시작할 때
/var/www/html/kfaligner/restart.sh start
```

### 서버 문제 해결
```bash
# 1. 상태 확인
/var/www/html/kfaligner/restart.sh status

# 2. 문제가 있으면 재시작
/var/www/html/kfaligner/restart.sh restart

# 3. 에러 로그 확인
tail -f /var/www/html/kfaligner/webapp/error.log
```

### 서버 점검
```bash
# 1. 서버 중지
/var/www/html/kfaligner/restart.sh stop

# 2. 점검 작업 수행
# ... (데이터베이스 백업, 파일 정리 등)

# 3. 서버 재시작
/var/www/html/kfaligner/restart.sh start
```

## 자동 시작 설정 (선택사항)

시스템 부팅 시 자동으로 서버를 시작하려면 systemd 서비스를 생성할 수 있습니다:

```bash
sudo nano /etc/systemd/system/kfaligner.service
```

다음 내용을 입력:

```ini
[Unit]
Description=KFAligner Web Application
After=network.target

[Service]
Type=forking
User=tyoon
Group=tyoon
WorkingDirectory=/var/www/html/kfaligner/webapp
ExecStart=/var/www/html/kfaligner/restart.sh start
ExecReload=/var/www/html/kfaligner/restart.sh reload
ExecStop=/var/www/html/kfaligner/restart.sh stop
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

서비스 활성화:

```bash
sudo systemctl daemon-reload
sudo systemctl enable kfaligner
sudo systemctl start kfaligner
```

## 트러블슈팅

### 서버가 시작되지 않을 때
1. 포트가 이미 사용 중인지 확인:
   ```bash
   lsof -i:5011
   ```

2. 에러 로그 확인:
   ```bash
   tail -50 /var/www/html/kfaligner/webapp/error.log
   ```

3. conda 환경 확인:
   ```bash
   conda activate aligner
   python -c "import flask; print(flask.__version__)"
   ```

### 프로세스가 응답하지 않을 때
```bash
# 강제 종료
pkill -9 -f "gunicorn.*webapp.app:app"

# 재시작
/var/www/html/kfaligner/restart.sh start
```

### 로그 파일이 너무 클 때
```bash
# 로그 파일 정리 (백업 후)
cd /var/www/html/kfaligner/webapp
mv access.log access.log.old
mv error.log error.log.old
/var/www/html/kfaligner/restart.sh reload
```

## 접근 URL

- **웹 인터페이스**: http://localhost:5010
- **직접 접근 (내부)**: http://127.0.0.1:5011

## 참고 사항

- `reload` 명령은 무중단 배포(zero-downtime deployment)를 지원합니다
- 서버는 conda 환경 'aligner'를 자동으로 활성화합니다
- nginx가 5010 포트로 프록시하므로 외부에서는 5010으로 접속합니다
