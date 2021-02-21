from datetime import datetime

from flask_sqlalchemy import xrange
from wtforms import Form, BooleanField, StringField, PasswordField, validators, RadioField, DateField
from wtforms.validators import Email, Length, EqualTo, DataRequired, ValidationError
from math import ceil


class BusinessCheck(object):
    def __init__(self, message=None):
        if not message:
            message = u'유효한 사업자 번호가 아닙니다.'
        self.message = message

    def __call__(self, form, field):
        number = list(map(int, str(field.data)))
        key = [1, 3, 7, 1, 3, 7, 1, 3, 5]
        sum = 0

        for i in range(0, 9):
            sum += number[i] * key[i]

        sum += int((number[8] * 5) / 10)
        magic = sum % 10
        master = (10 - magic) % 10

        if master != number[9]:
            raise ValidationError(self.message)


class HomepageCheck(object):
    def __init__(self, message=None):
        if not message:
            message = u''"http://"'를 반드시 입력해주세요.'
        self.message = message

    def __call__(self, form, field):
        if field.data[0:7] != 'http://':
            raise ValidationError(self.message)

validators = {
    'email': [
        DataRequired(message='이메일을 입력해주세요'),
        Email(message='Email 형식이 맞지 않습니다.')
    ],
    'phone': [
        DataRequired(message='전화번호를 입력해주세요')
    ],
    'password': [
        DataRequired(message='비밀번호를 입력해주세요'),
        Length(min=6, max=50, message='6자 이상의 비밀번호를 입력하세요'),
        EqualTo('confirm', message='동일한 비밀번호를 입력해주세요.')
    ],
    'password_login': [
        DataRequired()
    ],
    'name': [
        DataRequired(message='이름 또는 상호명을 입력해주세요'),
        Length(min=2, max=35)
    ],
    'agreement': [
        DataRequired(message='개인정보취급방침과 서비스약관에 동의해주세요.')
    ],
    'business_no': [
        DataRequired(message='사업자번호를 입력하세요.'),
        Length(min=10, max=10, message='사업자번호는 10자리의 숫자입니다.'),
        BusinessCheck(message='유효한 사업자번호를 입력하세요.')
    ],
    'homepage': [
        HomepageCheck(message=''"http://"'를 반드시 입력해주세요.')
    ]
}


class ProfessionalUpdateForm(Form):
    name = StringField('이름', validators['name'])
    business_no = StringField('사업자번호('"-"'를 빼고 입력하세요)', validators['business_no'])
    address = StringField('주소찾기를 선택하세요.')
    sub_address = StringField('상세 주소를 입력하세요.')
    phone = StringField('ex) 010-0000-0000')
    homepage = StringField(''"http://"'를 반드시 입력해주세요.', validators['homepage'])


class PasswordUpdateForm(Form):
    password = PasswordField('변경을 원하는 비밀번호를 입력하세요', validators['password'])
    confirm = PasswordField('변경을 원하는 비밀번호 한번 더 입력하세요')


class UpdateForm(Form):
    name = StringField('이름', validators['name'])
    email = StringField('이메일', validators['email'])


class JoinForm(Form):
    name = StringField('이름', validators['name'])
    email = StringField('이메일', validators['email'])
    password = PasswordField('비밀번호', validators['password'])
    confirm = PasswordField('비밀번호 확인')
    agreement = BooleanField('동의', validators['agreement'])
    business_no = StringField('사업자번호('"-"'를 빼고 입력하세요)', validators['business_no'])
    joiner = RadioField('joiner', choices=[('1', '일반회원'), ('2', '사업자 회원')], default='2')



class LoginForm(Form):
    login_id = StringField('아이디', validators['name'])
    login_pwd = PasswordField('비밀번호', validators['password_login'])


class Pagination(object):
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def serializable(self, page_iter, p_pages):
        return {
            'page': self.page,
            'per_page': self.per_page,
            'total_count': self.total_count,
            'iter_pages': page_iter,
            'p_pages': p_pages
        }

    def iter_pages(self, left_edge=0, left_current=2,
                   right_current=5, right_edge=0):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or (
                    num > self.page - left_current - 1 and num < self.page + right_current) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class TestForm(Form):
    email = StringField('이메일', validators['email'])
    password = PasswordField('비밀번호', validators['password_login'])


#감독부서승인 조회조건 폼 by 박정은
class superApprovalSearchForm(Form):
    # 날짜 유효성 검사 부분 추가 필요 -> 동작한함.
    # visit_sdate = DateField('시작일')
    # visit_edate = DateField('종료일')
    visit_sdate = StringField('시작일')
    visit_edate = StringField('종료일')
    visit_category = StringField('방문구분')
    apply_nm = StringField('작업명')
    comp_nm = StringField('업체명')
    approval_state = StringField('진행상태')


class ApplyForm(Form):
    applicant_name = StringField('신청자')
    applicant_phone = StringField('신청자연락처')
    applicant_biz_no = StringField('업체번호')
    applicant_comp_nm = StringField('업체명')
    interviewer_name = StringField('감독자')
    interviewer_phone = StringField('감독자연락처')
    inout_biz_no = StringField('업체번호')
    inout_comp_nm = StringField('업체명')
    inout_sdate = StringField('시작시간')
    inout_edate = StringField('종료시간')
    inout_purpose_type = StringField('방문유형')
    input_title = StringField('방문제목')
    inout_purpose_desc = StringField('방문상세')
    inout_location = StringField('방문지역')
    inout_location_desc = StringField('지역상세')

    approve_interviewer = StringField('감독자')
    approve_state = StringField('출입승인상태')
    approve_date = StringField('일시')
    approve_remark = StringField('비고')


class UserAccountFrom(Form):
    """사용자 폼"""
    login_id = StringField('아이디', validators['name'])
    login_pwd = PasswordField('비밀번호', validators['password_login'])
    login_pw_conf = PasswordField('비밀번호확인', validators['password_login'])
    name = StringField('이름', validators['name'])
    phone = StringField('핸드폰', validators['phone'])
    email = StringField('이메일', validators['email'])
    comp_nm = StringField('회사명')
    biz_no = StringField('업체번호')