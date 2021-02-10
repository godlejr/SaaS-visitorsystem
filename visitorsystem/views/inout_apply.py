from operator import and_

import boto3
import shortuuid
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify, flash
from flask_login import current_user, login_required
from visitorsystem.forms import ApplyForm
from visitorsystem.models import db, Vcapplymaster, Ssctenant, Scrule, Vcvisituser, Sccompinfo, Scuser, Sccode, \
    ScRuleFile

inout_apply = Blueprint('inout_apply', __name__)


@inout_apply.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_apply/section4.html')


@inout_apply.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        applyform = ApplyForm(request.form)
        apply = Vcapplymaster()
        apply.apply_code = 'APPLY-002'
        apply.apply_nm = '출입신청 2번'
        apply.interviewr = request.form['interviewer_name']  # 감독자
        apply.applicant = request.form['applicant_name']  # 신청자
        apply.phone = request.form['applicant_phone']  # 감독자 휴대폰
        apply.visit_category = request.form['inout_purpose_type']  # 방문종류
        apply.biz_no = request.form['inout_biz_no']  # 사업자번호
        apply.visit_sdate = request.form['inout_sdate']  # 방문시작일
        apply.visit_edate = request.form['inout_edate']  # 방문종료일
        apply.visit_purpose = request.form['inout_title']  # 방문목적
        apply.visit_desc = request.form['inout_purpose_desc']  # 방문목적 상세기술
        apply.site_id = 'U1'  # 사업장코드
        apply.site_nm = '울산1공장'  # 사업장명
        # apply.site_id = request.form['inout_location'].data #
        # apply.site_nm = request.form['inout_location_desc'].data
        apply.login_id = 'admin'  # 로그인 아이디(세션에서 가져오기)
        apply.approval_state = '대기'  # 출입승인 상태 저장
        db.session.add(apply)
        db.session.commit()

    return jsonify({'file_name': 'output'})


"""
감독자 조회로직
001.SC_USER 테이블에서, name 필드로 조회
002.조회 후, return 값은 json 형식으로 반환
003. 표 binding 후 보여주기
"""


@inout_apply.route('/rule/search', methods=['POST'])
def ruleSearch():
    tenant_id = current_user.ssctenant.id
    lists = []
    for row in db.session.query(Scrule).filter(db.and_(Scrule.tenant_id == tenant_id, Scrule.use_yn == '1')).all():
        scrule = {
            "rule_name": row.rule_name,
            "rule_type": row.rule_type,
            "rule_duedate": row.rule_duedate,
            "rule_desc": row.rule_desc
        }
        lists.append(scrule)

    lists2 = []
    for row in db.session.query(Sccode).filter(
            db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 3)):
        sccode = {
            "code_nm": row.code_nm,
        }

        lists2.append(sccode)

    return jsonify({'msg': lists,
                    'msg2': lists2})


"""
Rule 업데이트
"""


@inout_apply.route('/rule/text/update', methods=['POST'])
def ruleTextUpdate():
    tenant_id = current_user.ssctenant.id
    name = request.form['userName']  # 사용자이름
    phone = request.form['userPhone']  # 휴대폰
    rule = request.form['rule']  # rule 이름
    type = request.form['type']  # rule 종류
    ruleText = request.form['ruleText']
    scrule = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.use_yn == '1',
                                             Scrule.rule_name == rule).first()
    time = datetime.now()
    vcvisituser = Vcvisituser()

    vcvisituser.tenant_id = tenant_id
    vcvisituser.name = name
    vcvisituser.phone = phone
    vcvisituser.rule_id = scrule.id
    vcvisituser.text_desc = ruleText
    vcvisituser.s_date = time.strftime("%Y-%m-%d")
    vcvisituser.e_date = (time + timedelta(days=int(scrule.rule_duedate))).strftime("%Y-%m-%d")
    vcvisituser.use_yn = '1'

    db.session.add(vcvisituser)
    db.session.commit()

    return jsonify({'msg': "success"})


"""
Rule Calendar 업데이트
"""


@inout_apply.route('/rule/calendar/update', methods=['POST'])
def ruleFileUpdate():
    tenant_id = current_user.ssctenant.id
    name = request.form['userName']  # 사용자이름
    phone = request.form['userPhone']  # 휴대폰
    rule = request.form['rule']  # rule 이름
    type = request.form['type']  # rule 종류
    ruleCalender = request.form['ruleCalender']
    scrule = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.use_yn == '1',
                                             Scrule.rule_name == rule).first()
    time = datetime.strptime(ruleCalender, '%Y-%m-%d')
    vcvisituser = Vcvisituser()
    print(time.strftime("%Y-%m-%d"))

    vcvisituser.tenant_id = tenant_id
    vcvisituser.name = name
    vcvisituser.phone = phone
    vcvisituser.rule_id = scrule.id
    vcvisituser.s_date = time.strftime("%Y-%m-%d")
    vcvisituser.e_date = (time + timedelta(days=int(scrule.rule_duedate))).strftime("%Y-%m-%d")
    vcvisituser.use_yn = '1'

    db.session.add(vcvisituser)
    db.session.commit()

    return jsonify({'msg': "success"})


# 파일업로드
@inout_apply.route('/rule/file/upload', methods=['POST'])
def fileUpload():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        lists = []
        file = request.files['file']
        # print(request.form['userName'])
        AWS_ACCESS_KEY = current_app.config['AWS_ACCESS_KEY']
        AWS_SECRET_KEY = current_app.config['AWS_SECRET_KEY']
        BUCKET_NAME = current_app.config['BUCKET_NAME']

        ssctenant = db.session.query(Ssctenant).filter(
            db.and_(Ssctenant.id == tenant_id, Ssctenant.use_yn == '1')).first()
        scuser = db.session.query(Scuser).filter(db.and_(Scuser.tenant_id == tenant_id,
                                                         Scuser.name == request.form['userName'],
                                                         Scuser.phone == request.form['phone'],
                                                         Scuser.use_yn == '1')).first()

        tenantId = ssctenant.tenant_id
        applicantName = request.form['applicantName']
        loginId = scuser.login_id
        applicantPhone = request.form['applicantPhone']
        userName = request.form['userName']
        phone = request.form['phone']
        filename = file.filename
        uuid = shortuuid.uuid()
        rule = request.form['rule']


        bucketUrl = tenantId + '/data/user/' + loginId + '/files/rule/' + userName + phone + '/' + uuid + filename

        print(bucketUrl)

        # {tenantid(vms_1)}/data/user/{신청한사람id}/files/rule/{개인 핸드폰번호}/{파일명+유효아이디}
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        s3.put_object(
            Bucket=BUCKET_NAME,
            Body=file,  # 업로드할 파일 객체
            Key=bucketUrl,  # S3에 업로드할 파일의 경로
            ContentType=file.content_type)  # 메타데이터설정

        # vc_visit_user에 삽입하고 그 아이디를 받아온다.
        # sc_rule에서 조회
        scrule = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.use_yn == '1',
                                                 Scrule.rule_name == rule).first()
        time = datetime.now()
        vcvisituser = Vcvisituser()

        vcvisituser.tenant_id = tenant_id
        vcvisituser.name = userName
        vcvisituser.phone = phone
        vcvisituser.rule_id = scrule.id
        vcvisituser.s_date = time.strftime("%Y-%m-%d")
        vcvisituser.e_date = (time + timedelta(days=int(scrule.rule_duedate))).strftime("%Y-%m-%d")
        vcvisituser.use_yn = '1'
        db.session.add(vcvisituser)
        db.session.commit()

        scrulefile = ScRuleFile()
        scrulefile.tenant_id = tenant_id
        scrulefile.visit_id = vcvisituser.id
        scrulefile.rule_id = scrule.id
        scrulefile.s3_url = bucketUrl
        scrulefile.file_name = filename

        db.session.add(scrulefile)
        db.session.commit()

        return jsonify({'msg': "success"});


"""
Rule 유효성 판별
"""


@inout_apply.route('/rule/valid', methods=['POST'])
def ruleValidate():
    tenant_id = current_user.ssctenant.id

    vsdate = request.form['sdate']  # 방문시작 날짜
    vedate = request.form['edate']  # 방문종료 날짜

    name = request.form['userName']  # 사용자 이름
    phone = request.form['userPhone']  # 휴대폰 번호

    lists = []

    # 1.tenant에 등록된 RULE을 기준으로, name/phone/유효일자를 검색하는 로직, 규칙시작일(s_date) <=방문시작일(vsdate) / 규칙종료일(e_date) >=방문종료일(vedate)
    for row in db.session.query(Vcvisituser).filter(db.and_(Vcvisituser.tenant_id == tenant_id,
                                                            Vcvisituser.use_yn == '1',
                                                            Vcvisituser.name == name,
                                                            Vcvisituser.phone == phone)).all():

        dict = {}
        if row.s_date <= vsdate and row.e_date >= vedate:
            dict = {
                "rule_id": row.id,
                "rule_type": row.scrule.rule_type,
                "rule_name": row.scrule.rule_name,
                "rule_desc": row.text_desc,
                "state": True
            }
        else:
            dict = {
                "rule_id": row.id,
                "rule_type": row.scrule.rule_type,
                "rule_name": row.scrule.rule_name,
                "rule_desc": row.text_desc,
                "state": False
            }

        lists.append(dict)
    return jsonify({'msg': lists})


# 감독자조회 Modal
@inout_apply.route('/interview/search', methods=['POST'])
def interviewSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        name = request.form['interviewName']

        lists = []
        for row in db.session.query(Scuser).filter(
                db.and_(Scuser.tenant_id == tenant_id, Scuser.name.like(name + '%'), Scuser.user_type == '0')):
            scuser = {
                "dept_nm": row.dept_nm,
                "name": row.name,
                "phone": row.phone
            }

            lists.append(scuser)

        return jsonify({'msg': lists});


# 업체조회 Modal
@inout_apply.route('/comp/search', methods=['POST'])
def compSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        comp_nm = request.form['compSearchInput']
        lists = []
        for row in db.session.query(Sccompinfo).filter(
                db.and_(Sccompinfo.tenant_id == tenant_id, Sccompinfo.comp_nm.like(comp_nm + '%'))):
            sccompinfo = {
                "comp_nm": row.comp_nm,
                "biz_no": row.biz_no
            }

            lists.append(sccompinfo)

        return jsonify({'msg': lists});


# 차량조회
@inout_apply.route('/car/search', methods=['POST'])
def carSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        lists = []
        for row in db.session.query(Sccode).filter(
                db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 3)):
            sccode = {
                "code_nm": row.code_nm,
            }

            lists.append(sccode)

        return jsonify({'msg': lists});
