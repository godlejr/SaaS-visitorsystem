from operator import and_

import boto3
import shortuuid
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify, flash
from flask_login import current_user, login_required
from visitorsystem.forms import ApplyForm
from visitorsystem.models import db, Vcapplymaster, Ssctenant, Scrule, Vcvisituser, Sccompinfo, Scuser, Sccode, \
    ScRuleFile, Vcapplyuser

inout_apply = Blueprint('inout_apply', __name__)

#메인페이지
@inout_apply.route('/', methods=['GET', 'POST'])
@login_required
def index():
    tenant_id = current_user.ssctenant.id
    biz_id = current_user.biz_id
    sccompinfo = db.session.query(Sccompinfo).filter(
        db.and_(Sccompinfo.tenant_id == tenant_id, Sccompinfo.id == biz_id, Sccompinfo.use_yn == '1')).first()
    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_apply/section4.html', sccompinfo=sccompinfo)


#출입신청
@inout_apply.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        apply = Vcapplymaster()
        apply.tenant_id = tenant_id
        apply.interviewr = request.form['interviewer_name']  # 감독자

        apply.applicant = request.form['applicant_name'] # 신청자
        apply.phone = request.form['applicant_phone']  # 신청자 휴대폰
        apply.visit_category = request.form['inout_purpose_type'] #방문유형
        apply.biz_id = request.form['inout_biz_id']  # 업체번호
        apply.visit_sdate = request.form['inout_sdate'] # 방문시작일
        apply.visit_edate = request.form['inout_edate']  # 방문종료일
        apply.visit_purpose = request.form['inout_title']  # 방문목적
        apply.visit_desc = request.form['inout_purpose_desc']  # 방문목적상세

        apply.site_id = request.form['inout_location_code']  # 방문목적상세
        apply.site_nm = request.form['inout_location']  # 방문목적상세
        apply.site_id2 = request.form['inout_location_code2']  # 방문목적상세
        apply.site_nm2 = request.form['inout_location2']  # 방문목적상세
        apply.login_id = current_user.id # 로그인 사용자
        apply.approval_state = '대기'  # 출입승인 상태 저장
        apply.visit_type = '0' # 0(로그인 한 사용자, 작업자용) #1(로그인 안 함 사용자, 일반사용자용)
        db.session.add(apply)
        db.session.commit()
        visitors = json.loads(request.form['visitors'])
        for row in visitors:
            vcapplyuser = Vcapplyuser()
            vcapplyuser.tenant_id = tenant_id #테넌트 아이디
            vcapplyuser.apply_id = apply.id # 신청번호

            vcapplyuser.visitant = row['name'] #방문자 이름
            vcapplyuser.phone = row['phone'] # 방문자 핸드폰 번호
            vcapplyuser.vehicle_num = row['carType'] #방문자 차량유형
            vcapplyuser.vehicle_type = row['carNum'] #방문자 차량번호
            db.session.add(vcapplyuser)
            db.session.commit()

    return redirect(url_for('main.login'))



#규칙 조회 
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


#텍스트규칙 업데이트
@inout_apply.route('/rule/text/update', methods=['POST'])
def ruleTextUpdate():
    tenant_id = current_user.ssctenant.id
    name = request.form['userName']  # 사용자이름
    phone = request.form['userPhone']  # 휴대폰
    rule = request.form['rule']  # rule 이름
    type = request.form['type']  # rule 종류
    ruleText = request.form['ruleText']
    print(rule)
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


#캘린더규칙 업데이트
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


# 파일규칙 업데이트
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
                                                         Scuser.name == current_user.name,
                                                         Scuser.phone == current_user.phone,
                                                         Scuser.use_yn == '1')).first()

        tenantId = ssctenant.tenant_id
        loginId = scuser.login_id
        applicantName = request.form['applicantName']
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

        bucketUrl = 'https://vms-tenants-rulefile-bucket-dev.s3.ap-northeast-2.amazonaws.com/' + bucketUrl
        return jsonify({'msg': bucketUrl});


# 규칙판별
@inout_apply.route('/rule/valid', methods=['POST'])
def ruleValidate():
    tenant_id = current_user.ssctenant.id

    vsdate = request.form['sdate']  # 방문시작 날짜
    vedate = request.form['edate']  # 방문종료 날짜

    name = request.form['userName']  # 사용자 이름
    phone = request.form['userPhone']  # 휴대폰 번호

    lists = []
    for row in db.session.query(Scrule).filter(db.and_(Scrule.tenant_id == tenant_id,
                                                            Scrule.use_yn == '1',
                                                            )).all():
        dict = {
            "rule_id": row.id,
            "rule_type": row.rule_type,
            "rule_name": row.rule_name,
            "state": False
        }
        lists.append(dict)


    # 1.tenant에 등록된 RULE을 기준으로, name/phone/유효일자를 검색하는 로직, 규칙시작일(s_date) <=방문시작일(vsdate) / 규칙종료일(e_date) >=방문종료일(vedate)
    for row in db.session.query(Vcvisituser).filter(db.and_(Vcvisituser.tenant_id == tenant_id,
                                                            Vcvisituser.use_yn == '1',
                                                            Vcvisituser.name == name,
                                                            Vcvisituser.phone == phone,
                                                            Vcvisituser.s_date <= vsdate,
                                                            Vcvisituser.e_date >= vedate)).group_by(Vcvisituser.rule_id).all():

        for dict in lists:
            rule_id = dict['rule_id']
            if(rule_id == row.rule_id):
                dict['state'] = True

    return jsonify({'msg': lists})


# 감독자조회 Modal
@inout_apply.route('/interview/search', methods=['POST'])
def interviewSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        name = request.form['interviewName']

        lists = []
        for row in db.session.query(Scuser).filter(
                db.and_(Scuser.tenant_id == tenant_id, Scuser.name.like(name + '%'), Scuser.user_type == '0',
                        Scuser.use_yn == '1')):
            scuser = {
                "dept_nm": row.dept_nm,
                "name": row.name,
                "phone": row.phone
            }

            lists.append(scuser)

        return jsonify({'msg': lists});


# 신청자조회 Modal
@inout_apply.route('/apply/search', methods=['POST'])
def applySearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        name = request.form['visitInput']
        lists = []
        for row in db.session.query(Scuser).filter(
                db.and_(Scuser.tenant_id == tenant_id, Scuser.name.like(name + '%'), Scuser.user_type == '1',
                        Scuser.use_yn == '1')):
            scuser = {
                "name": row.name,
                "phone": row.phone,
                "comp_nm": row.sccompinfo.comp_nm,
                "biz_no": row.sccompinfo.biz_no
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
                db.and_(Sccompinfo.tenant_id == tenant_id, Sccompinfo.comp_nm.like(comp_nm + '%'),
                        Sccompinfo.use_yn == '1')):
            sccompinfo = {
                "biz_id": row.id,
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
                db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 3, Sccode.use_yn == '1')):
            sccode = {
                "code_nm": row.code_nm,
            }

            lists.append(sccode)

        return jsonify({'msg': lists});


# 방문유형
@inout_apply.route('/visit/type', methods=['POST'])
def visitTypeSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        lists = []
        for row in db.session.query(Sccode).filter(
                db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 6, Sccode.use_yn == '1')):
            sccode = {
                "code_nm": row.code_nm,
            }

            lists.append(sccode)

        return jsonify({'msg': lists});


# 출입지역
@inout_apply.route('/door/search', methods=['POST'])
def doorSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        lists = []
        for row in db.session.query(Sccode).filter(
                db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 1, Sccode.use_yn == '1')):
            sccode = {
                "code" : row.code,
                "code_nm": row.code_nm
            }

            lists.append(sccode)

        lists2 = []
        for row in db.session.query(Sccode).filter(
                db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 2, Sccode.use_yn == '1')):
            sccode = {
                "code": row.code,
                "code_nm": row.code_nm
            }

            lists2.append(sccode)

        return jsonify({'msg': lists, 'msg2': lists2});


# 사용자 조회
@inout_apply.route('/user/search', methods=['POST'])
def userSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        userName = request.form['userName']
        userPhone = request.form['userPhone']
        lists = []
        vcvisituser = db.session.query(Vcvisituser.name).filter(
            db.and_(Vcvisituser.tenant_id == tenant_id, Vcvisituser.name == userName, Vcvisituser.phone == userPhone,
                    Vcvisituser.use_yn == '1')).group_by(Vcvisituser.name).all()
        if not vcvisituser:
            print('empty')
            for row in db.session.query(Scrule).filter(db.and_(Scrule.tenant_id == tenant_id,
                                                               Scrule.use_yn == '1',
                                                               )).all():
                newUser = Vcvisituser()
                newUser.name = userName
                newUser.phone = userPhone
                newUser.rule_id = row.id
                newUser.tenant_id = tenant_id
                db.session.add(newUser)
                db.session.commit()



        else:
            output = {
                "name": vcvisituser[0].name,
            }
            lists.append(output)

        return jsonify({'msg': lists})
