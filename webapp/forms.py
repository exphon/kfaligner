from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import User


class SignupForm(FlaskForm):
    username = StringField('사용자명', validators=[
        DataRequired(message='사용자명을 입력하세요.'),
        Length(min=3, max=80, message='사용자명은 3-80자 사이여야 합니다.')
    ])
    email = StringField('이메일', validators=[
        DataRequired(message='이메일을 입력하세요.'),
        Email(message='유효한 이메일 주소를 입력하세요.')
    ])
    password = PasswordField('비밀번호', validators=[
        DataRequired(message='비밀번호를 입력하세요.'),
        Length(min=6, message='비밀번호는 최소 6자 이상이어야 합니다.')
    ])
    password2 = PasswordField('비밀번호 확인', validators=[
        DataRequired(message='비밀번호를 다시 입력하세요.'),
        EqualTo('password', message='비밀번호가 일치하지 않습니다.')
    ])
    submit = SubmitField('회원가입')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('이미 사용 중인 사용자명입니다.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('이미 등록된 이메일입니다.')


class LoginForm(FlaskForm):
    username = StringField('사용자명', validators=[
        DataRequired(message='사용자명을 입력하세요.')
    ])
    password = PasswordField('비밀번호', validators=[
        DataRequired(message='비밀번호를 입력하세요.')
    ])
    captcha = IntegerField('보안 문자', validators=[
        DataRequired(message='보안 문자를 입력하세요.')
    ])
    submit = SubmitField('로그인')


class ForgotPasswordForm(FlaskForm):
    email = StringField('이메일', validators=[
        DataRequired(message='이메일을 입력하세요.'),
        Email(message='유효한 이메일 주소를 입력하세요.')
    ])
    submit = SubmitField('비밀번호 찾기')
