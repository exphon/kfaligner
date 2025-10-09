import os
import shutil
import subprocess
import uuid
import secrets
import string
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    send_file,
    flash,
    abort,
    session,
    after_this_request,
)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename


# Base paths
KFALIGNER_ROOT = Path(__file__).resolve().parents[1]  # /var/www/html/kfaligner
WEBAPP_ROOT = Path(__file__).resolve().parent


ALLOWED_WAV_EXTS = {".wav"}
ALLOWED_TXT_EXTS = {".txt", ".lab"}


def allowed_file(filename: str, allowed: set[str]) -> bool:
    return "." in filename and Path(filename).suffix.lower() in allowed


def stem(path: Path) -> str:
    return path.stem


def read_text_any_encoding(path: Path) -> str:
    encodings = ["utf-8", "utf-16", "utf-16le", "utf-16be", "cp949", "euc-kr"]
    data = path.read_bytes()
    for enc in encodings:
        try:
            s = data.decode(enc)
            if s and s[0] == "\ufeff":
                s = s[1:]
            return s
        except Exception:
            continue
    try:
        s = data.decode("utf-8", errors="replace")
        if s and s[0] == "\ufeff":
            s = s[1:]
        return s
    except Exception:
        return ""


def text_contains_hangul(s: str) -> bool:
    for ch in s:
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7A3:
            return True
    return False


def is_valid_wav_header(path: Path, max_read: int = 64) -> bool:
    """Basic RIFF/WAVE header check to mitigate disguised binaries."""
    try:
        with path.open("rb") as f:
            hdr = f.read(max_read)
        return (
            len(hdr) >= 12
            and hdr[0:4] == b"RIFF"
            and hdr[8:12] == b"WAVE"
        )
    except Exception:
        return False


def is_probably_text(path: Path, sample_size: int = 1024 * 64) -> bool:
    """Heuristic: reject if NUL bytes exist, and require most bytes to be printable/whitespace."""
    try:
        data = path.read_bytes()
        if len(data) > sample_size:
            data = data[:sample_size]
        # Accept if it strictly decodes in common encodings (UTF-8/UTF-16/CP949/EUC-KR)
        for enc in ("utf-8", "utf-16", "utf-16le", "utf-16be", "cp949", "euc-kr"):
            try:
                data.decode(enc, errors="strict")
                return True
            except Exception:
                continue
        return False
    except Exception:
        return False


def clamscan_available() -> bool:
    from shutil import which

    return which("clamscan") is not None


def scan_with_clamav(path: Path) -> tuple[bool, str]:
    """Scan a file with clamscan when available. Returns (clean, message)."""
    try:
        res = subprocess.run(
            ["clamscan", "--no-summary", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        out = res.stdout or ""
        # clamscan exits with 0 if OK, 1 if malware found, 2 if error
        if res.returncode == 0:
            return True, out.strip()
        elif res.returncode == 1:
            return False, (out.strip() or "Malware detected")
        else:
            return True, f"clamscan error ignored: {out.strip()}"
    except Exception as e:
        return True, f"clamscan unavailable: {e}"


def clamdscan_available() -> bool:
    from shutil import which

    return which("clamdscan") is not None


def scan_with_clamd(path: Path) -> tuple[bool, str]:
    """Scan a file via clamd (clamdscan). Returns (clean, message)."""
    try:
        # --fdpass lets clamd read files even if clamd user lacks direct access
        res = subprocess.run(
            ["clamdscan", "--no-summary", "--fdpass", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        out = res.stdout or ""
        # clamdscan exits with 0 if OK, 1 if malware found, 2 if error
        if res.returncode == 0:
            return True, out.strip()
        elif res.returncode == 1:
            return False, (out.strip() or "Malware detected")
        else:
            return True, f"clamdscan error ignored: {out.strip()}"
    except Exception as e:
        return True, f"clamdscan unavailable: {e}"


def romanize_hangul_text(s: str) -> str:
    """Mimic convert_sentences_unicode.py behavior: per line, convert Hangul to token sequence."""
    import unicodedata

    lines = s.splitlines()
    out_lines: list[str] = []
    for line in lines:
        parts = line.strip().split()
        out_words: list[str] = []
        for word in parts:
            tokens: list[str] = []
            for ch in str(word):
                try:
                    fullname = unicodedata.name(ch)
                except Exception:
                    continue
                pieces = fullname.split()
                if len(pieces) == 3 and pieces[0] != "CJK":
                    tokens.append(pieces[2])
                elif len(pieces) == 2:
                    digit_map = {
                        "ZERO": "0", "ONE": "1", "TWO": "2", "THREE": "3",
                        "FOUR": "4", "FIVE": "5", "SIX": "6", "SEVEN": "7",
                        "EIGHT": "8", "NINE": "9",
                    }
                    if pieces[1] in digit_map:
                        tokens.append(digit_map[pieces[1]])
            if tokens:
                out_words.append(''.join(tokens))
        if out_words:
            out_lines.append(' '.join(out_words))
    # Limit preview to first few lines to keep UI compact
    return '\n'.join(out_lines[:5])


def run_align(wav_path: Path, txt_path: Path, out_path: Path) -> tuple[bool, str]:
    """Run align.py for a single pair. Returns (success, message)."""
    # Ensure output directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Build command; run from kfaligner root so relative model/paths work
    cmd = [
        "python3",
        str(KFALIGNER_ROOT / "align.py"),
        str(wav_path),
        str(txt_path),
        str(out_path),
    ]

    try:
        res = subprocess.run(
            cmd,
            cwd=str(KFALIGNER_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            text=True,
        )
        ok = res.returncode == 0 and out_path.exists()
        return ok, res.stdout if res.stdout else ("OK" if ok else "Failed without output")
    except Exception as e:
        return False, f"Exception: {e}"


def make_zip(job_dir: Path, zip_path: Path, upload_dir: Path = None):
    """Create ZIP file with TextGrid results and optionally uploaded files"""
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        # Add TextGrid files to results/ folder
        for p in sorted(job_dir.glob("*.TextGrid")):
            zf.write(p, arcname=f"results/{p.name}")
        
        # Add uploaded files to uploads/ folder if upload_dir provided
        if upload_dir and upload_dir.exists():
            for p in sorted(upload_dir.glob("*")):
                if p.is_file():
                    zf.write(p, arcname=f"uploads/{p.name}")


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "kfaligner-webapp-dev")
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(WEBAPP_ROOT / "data" / "users.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Email configuration
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", "587"))
    app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@kfaligner.local")
    
    # Upload security limits
    max_mb = int(os.environ.get("MAX_CONTENT_LENGTH_MB", "64"))
    app.config["MAX_CONTENT_LENGTH"] = max_mb * 1024 * 1024
    app.config["MAX_FILES_PER_REQUEST"] = int(os.environ.get("MAX_FILES_PER_REQUEST", "100"))
    app.config["ENABLE_CLAMAV_SCAN"] = os.environ.get("ENABLE_CLAMAV_SCAN", "0") in {"1", "true", "True"}
    
    # WTF CSRF protection
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["WTF_CSRF_TIME_LIMIT"] = None
    
    # Initialize extensions
    from .models import db, User
    from .forms import SignupForm, LoginForm, ForgotPasswordForm
    
    db.init_app(app)
    mail = Mail(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = '로그인이 필요합니다.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default guest account if it doesn't exist
        default_user = User.query.filter_by(username='KAligner').first()
        if not default_user:
            default_user = User(
                username='KAligner',
                email='guest@kfaligner.local'
            )
            default_user.set_password('K@re@n')
            db.session.add(default_user)
            db.session.commit()
            print("Default guest account created: KAligner / K@re@n")

    data_root = WEBAPP_ROOT / "data"
    uploads_root = data_root / "uploads"
    jobs_root = data_root / "jobs"
    for d in (data_root, uploads_root, jobs_root):
        d.mkdir(parents=True, exist_ok=True)

    @app.route("/")
    @login_required
    def index():
        return render_template("index.html", username=current_user.username)
    
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        
        form = SignupForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            flash(f"회원가입이 완료되었습니다. 로그인해주세요.", "success")
            return redirect(url_for("login"))
        
        return render_template("signup.html", form=form)
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        
        # Generate CAPTCHA
        import random
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        captcha_answer = num1 + num2
        
        form = LoginForm()
        if form.validate_on_submit():
            # Verify CAPTCHA
            if form.captcha.data != session.get('captcha_answer'):
                flash("보안 문자가 올바르지 않습니다.", "error")
                return render_template("login.html", form=form, num1=num1, num2=num2)
            
            # Check for guest account first (KAligner / K@re@n)
            if form.username.data == "KAligner" and form.password.data == "K@re@n":
                # Get or create guest user
                user = User.query.filter_by(username="KAligner").first()
                if not user:
                    user = User(username="KAligner", email="guest@kfaligner.local")
                    user.set_password("K@re@n")
                    db.session.add(user)
                    db.session.commit()
                login_user(user)
                flash(f"환영합니다, {user.username}님!", "success")
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("index"))
            
            # Regular user login
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                if not user.is_active:
                    flash("계정이 비활성화되었습니다. 관리자에게 문의하세요.", "error")
                    return redirect(url_for("login"))
                login_user(user)
                flash(f"환영합니다, {user.username}님!", "success")
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("index"))
            else:
                flash("사용자명 또는 비밀번호가 올바르지 않습니다.", "error")
        
        # Store CAPTCHA answer in session
        session['captcha_answer'] = captcha_answer
        return render_template("login.html", form=form, num1=num1, num2=num2)
    
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("로그아웃되었습니다.", "info")
        return redirect(url_for("login"))
    
    def generate_temporary_password(length=10):
        """Generate a random temporary password"""
        characters = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user:
                # Generate temporary password
                temp_password = generate_temporary_password()
                user.set_password(temp_password)
                db.session.commit()
                
                # Send email with credentials
                try:
                    # Check if email is configured
                    if app.config["MAIL_USERNAME"]:
                        msg = Message(
                            subject="Korean Forced Aligner - 계정 정보",
                            recipients=[user.email]
                        )
                        msg.body = f"""
안녕하세요,

Korean Forced Aligner 계정 정보를 보내드립니다.

사용자명: {user.username}
임시 비밀번호: {temp_password}

보안을 위해 로그인 후 비밀번호를 변경해주세요.

감사합니다.
Korean Forced Aligner 팀
"""
                        msg.html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
        <h2 style="color: #0d6efd;">🔐 Korean Forced Aligner</h2>
        <p>안녕하세요,</p>
        <p>요청하신 계정 정보를 보내드립니다.</p>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 6px; margin: 20px 0;">
            <p style="margin: 10px 0;"><strong>사용자명:</strong> <code style="background: #e9ecef; padding: 4px 8px; border-radius: 4px;">{user.username}</code></p>
            <p style="margin: 10px 0;"><strong>임시 비밀번호:</strong> <code style="background: #fff3cd; padding: 4px 8px; border-radius: 4px; color: #856404;">{temp_password}</code></p>
        </div>
        
        <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; border-radius: 4px; margin: 20px 0;">
            <p style="margin: 0; color: #856404;"><strong>⚠️ 보안 안내:</strong> 로그인 후 반드시 비밀번호를 변경해주세요.</p>
        </div>
        
        <p>감사합니다.<br>Korean Forced Aligner 팀</p>
    </div>
</body>
</html>
"""
                        mail.send(msg)
                        flash(f"이메일로 사용자명과 임시 비밀번호를 전송했습니다. ({user.email})", "success")
                    else:
                        # Email not configured - display on screen
                        flash(f"이메일 서버가 설정되지 않았습니다. 다음 정보를 사용하세요:", "warning")
                        flash(f"사용자명: {user.username}, 임시 비밀번호: {temp_password}", "info")
                except Exception as e:
                    flash(f"이메일 전송 중 오류가 발생했습니다. 관리자에게 문의하세요.", "error")
                    print(f"Email error: {e}")
            else:
                # Don't reveal if email exists or not for security
                flash("입력하신 이메일로 계정 정보를 전송했습니다. (등록된 이메일인 경우)", "info")
            
            return redirect(url_for("login"))
        
        return render_template("forgot_password.html", form=form)

    @app.route("/align", methods=["POST"])
    @login_required
    def align():
        if "files" not in request.files:
            flash("파일을 선택해 주세요.", "error")
            return redirect(url_for("index"))

        job_id = uuid.uuid4().hex[:12]
        job_upload_dir = uploads_root / job_id
        job_out_dir = jobs_root / job_id
        job_upload_dir.mkdir(parents=True, exist_ok=True)
        job_out_dir.mkdir(parents=True, exist_ok=True)

        # Enforce a sane limit on number of files
        incoming_files = [f for f in request.files.getlist("files") if f and f.filename]
        if not incoming_files:
            flash("파일을 선택해 주세요.", "error")
            return redirect(url_for("index"))
        if len(incoming_files) > app.config["MAX_FILES_PER_REQUEST"]:
            flash(f"파일 개수 초과 (최대 {app.config['MAX_FILES_PER_REQUEST']}개)", "error")
            return redirect(url_for("index"))

        # Split uploaded files into wav and txt groups; do not save yet
        wav_candidates: dict[str, str] = {}
        txt_candidates: dict[str, str] = {}
        others_ignored: list[str] = []
        for f in incoming_files:
            if not f.filename:
                continue
            filename = secure_filename(f.filename)
            ext = Path(filename).suffix.lower()
            if ext in ALLOWED_WAV_EXTS:
                wav_candidates[Path(filename).stem] = filename
            elif ext in ALLOWED_TXT_EXTS:
                txt_candidates[Path(filename).stem] = filename
            else:
                others_ignored.append(filename)

        if not wav_candidates or not txt_candidates:
            flash("WAV와 TXT/LAB 파일이 모두 필요합니다.", "error")
            return redirect(url_for("index"))

        # Ensure full pairing for all WAVs; if any missing, abort with warning
        missing_txt = [stem for stem in wav_candidates.keys() if stem not in txt_candidates]
        missing_wav = [stem for stem in txt_candidates.keys() if stem not in wav_candidates]
        if missing_txt or missing_wav:
            detail = []
            if missing_txt:
                detail.append("TXT 없음: " + ", ".join(sorted(missing_txt)))
            if missing_wav:
                detail.append("WAV 없음: " + ", ".join(sorted(missing_wav)))
            flash("페어링 실패 — " + " | ".join(detail), "error")
            return redirect(url_for("index"))

        # Save files now that pairing validated
        wav_paths: list[Path] = []
        txt_paths: list[Path] = []
        previews: dict[str, str] = {}

        file_map = {**{v: ("wav", k) for k, v in wav_candidates.items()}, **{v: ("txt", k) for k, v in txt_candidates.items()}}
        for storage in incoming_files:
            if not storage.filename:
                continue
            filename = secure_filename(storage.filename)
            if filename not in file_map:
                continue
            ftype, s = file_map[filename]
            dst = job_upload_dir / filename
            storage.save(dst)
            # Optional: ClamAV scan (prefer clamdscan for speed, fallback to clamscan)
            if app.config["ENABLE_CLAMAV_SCAN"]:
                clean, msg = (True, "")
                if clamdscan_available():
                    clean, msg = scan_with_clamd(dst)
                elif clamscan_available():
                    clean, msg = scan_with_clamav(dst)
                if not clean:
                    shutil.rmtree(job_upload_dir, ignore_errors=True)
                    shutil.rmtree(job_out_dir, ignore_errors=True)
                    flash(f"악성코드 의심 파일 차단: {filename}", "error")
                    return redirect(url_for("index"))
            if ftype == "wav":
                # Validate WAV header
                if not is_valid_wav_header(dst):
                    try:
                        dst.unlink(missing_ok=True)
                    except Exception:
                        pass
                    flash(f"유효하지 않은 WAV 파일: {filename}", "error")
                    return redirect(url_for("index"))
                wav_paths.append(dst)
            else:
                # Validate text payload
                if not is_probably_text(dst):
                    try:
                        dst.unlink(missing_ok=True)
                    except Exception:
                        pass
                    flash(f"텍스트 형식이 아닙니다: {filename}", "error")
                    return redirect(url_for("index"))
                txt_paths.append(dst)
                # Build romanized preview
                try:
                    text = read_text_any_encoding(dst)
                    if text_contains_hangul(text):
                        previews[filename] = romanize_hangul_text(text)
                    else:
                        previews[filename] = '\n'.join(text.splitlines()[:5])
                except Exception as e:
                    previews[filename] = f"(미리보기 생성 실패: {e})"

        if not wav_paths or not txt_paths:
            flash("업로드 처리 중 문제가 발생했습니다.", "error")
            return redirect(url_for("index"))

        # Pair by stem
        txt_by_stem = {stem(p): p for p in txt_paths}
        pairs: list[tuple[Path, Path]] = []
        skipped: list[str] = []
        for w in wav_paths:
            s = stem(w)
            t = txt_by_stem.get(s)
            if t is None:
                # Try case-insensitive match
                t = next((p for k, p in txt_by_stem.items() if k.lower() == s.lower()), None)
            if t is None:
                skipped.append(w.name)
            else:
                pairs.append((w, t))

        results: list[dict] = []
        for w, t in pairs:
            out_tg = job_out_dir / (stem(w) + ".TextGrid")
            ok, msg = run_align(w, t, out_tg)
            results.append(
                {
                    "wav": w.name,
                    "txt": t.name,
                    "preview": previews.get(t.name, ""),
                    "out": out_tg.name,
                    "ok": ok,
                    "log": msg,
                }
            )

        total_ok = sum(1 for r in results if r["ok"]) if results else 0
        zip_name = f"{job_id}.zip"
        zip_path = job_out_dir / zip_name
        try:
            make_zip(job_out_dir, zip_path, job_upload_dir)
        except Exception:
            # Ignore zip errors; user can still download individually
            pass

        return render_template(
            "results.html",
            job_id=job_id,
            results=results,
            skipped=skipped,
            total_ok=total_ok,
            zip_available=zip_path.exists(),
        )

    @app.route("/download/<job_id>/<path:filename>")
    @login_required
    def download(job_id: str, filename: str):
        job_out_dir = jobs_root / job_id
        if not job_out_dir.exists():
            abort(404)
        return send_from_directory(job_out_dir, filename, as_attachment=True)

    @app.route("/download_zip/<job_id>")
    @login_required
    def download_zip(job_id: str):
        job_out_dir = jobs_root / job_id
        job_upload_dir = uploads_root / job_id
        if not job_out_dir.exists():
            abort(404)
        zip_path = job_out_dir / f"{job_id}.zip"
        if not zip_path.exists():
            make_zip(job_out_dir, zip_path, job_upload_dir)
        
        @after_this_request
        def cleanup(response):
            """Delete files and folders after download completes"""
            try:
                # Delete upload directory and its contents
                if job_upload_dir.exists():
                    shutil.rmtree(job_upload_dir, ignore_errors=True)
                
                # Delete job output directory and its contents
                if job_out_dir.exists():
                    shutil.rmtree(job_out_dir, ignore_errors=True)
                
                flash("다운로드가 완료되었습니다. 서버의 파일이 삭제되었습니다.", "info")
            except Exception as e:
                # Log error but don't fail the download
                print(f"Cleanup error for job {job_id}: {e}")
            return response
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"{job_id}.zip",
            mimetype='application/zip'
        )

    return app


app = create_app()


if __name__ == "__main__":
    # Environment notes:
    # - Ensure 'sox', 'HCopy', and 'HVite' are in PATH
    # - Run from within the container/host where kfaligner dependencies are installed
    port = int(os.environ.get("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=False)
