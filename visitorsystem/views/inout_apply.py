import boto3
import shortuuid
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify, flash
from flask_login import current_user, login_required
from visitorsystem.forms import ApplyForm
from visitorsystem.models import db, Vcapplymaster, Ssctenant, Scrule, Vcvisituser, Sccompinfo, Scuser, Sccode, \
    ScRuleFile, Vcapplyuser, Vcstackuser

inout_apply = Blueprint('inout_apply', __name__)


# 메인페이지(완료)
@inout_apply.route('/', methods=['GET', 'POST'])
@login_required
def index():
    tenant_id = current_user.ssctenant.id  # 로그인 사용자의 테넌트 아이디
    biz_id = current_user.biz_id  # 로그인 사용자의 사업자번호
    sccompinfo = db.session.query(Sccompinfo).filter(
        db.and_(Sccompinfo.tenant_id == tenant_id, Sccompinfo.id == biz_id, Sccompinfo.use_yn == '1')).first()
    scrules = db.session.query(Scrule).all()  # 페이지 로드전 동적규칙 조회
    return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_apply/section4.html', sccompinfo=sccompinfo,
                           scrules=scrules)


# 출입신청
@inout_apply.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        applyId = request.form['applyId'];
        apply = db.session.query(Vcapplymaster).filter(
            db.and_(Vcapplymaster.tenant_id == tenant_id, Vcapplymaster.id == applyId,
                    Vcapplymaster.use_yn == '0')).first()

        apply.tenant_id = tenant_id
        apply.interviewr = request.form['interviewer_name']  # 감독자

        apply.applicant = request.form['applicant_name']  # 신청자
        apply.phone = request.form['applicant_phone']  # 신청자 휴대폰
        apply.visit_category = request.form['inout_purpose_type']  # 방문유형
        apply.biz_id = request.form['inout_biz_id']  # 업체번호
        apply.visit_sdate = request.form['inout_sdate']  # 방문시작일
        apply.visit_edate = request.form['inout_edate']  # 방문종료일
        apply.visit_purpose = request.form['inout_title']  # 방문목적
        apply.visit_desc = request.form['inout_purpose_desc']  # 방문목적상세

        apply.site_id = request.form['inout_location_code']  # 방문목적상세
        apply.site_nm = request.form['inout_location']  # 방문목적상세
        apply.site_id2 = request.form['inout_location_code2']  # 방문목적상세
        apply.site_nm2 = request.form['inout_location2']  # 방문목적상세
        apply.login_id = current_user.id  # 로그인 사용자
        apply.approval_state = '대기'  # 출입승인 상태 저장
        apply.visit_type = '0'  # 0(로그인 한 사용자, 작업자용) #1(로그인 안 함 사용자, 일반사용자용)
        apply.use_yn = '1'
        db.session.add(apply)
        db.session.commit()
        visitors = json.loads(request.form['visitors'])
        for row in visitors:
            vcapplyuser = Vcapplyuser()
            vcapplyuser.tenant_id = tenant_id  # 테넌트 아이디
            vcapplyuser.apply_id = applyId  # 신청번호

            vcapplyuser.visitant = row['name']  # 방문자 이름
            vcapplyuser.phone = row['phone']  # 방문자 핸드폰 번호
            vcapplyuser.vehicle_num = row['carType']  # 방문자 차량유형
            vcapplyuser.vehicle_type = row['carNum']  # 방문자 차량번호
            db.session.add(vcapplyuser)
            db.session.commit()

    return redirect(url_for('main.login'))


# 규칙 조회
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


# 텍스트규칙 업데이트(완료)
@inout_apply.route('/rule/text/update', methods=['POST'])
def ruleTextUpdate():
    print('텍스트규칙 업데이트')
    tenant_id = current_user.ssctenant.id  # 테넌트 아이디
    name = request.form['name']  # 이름
    phone = request.form['phone']  # 휴대폰
    rule = request.form['rule']  # 규칙이름
    type = request.form['type']  # 규칙종류
    ruleText = request.form['ruleText']  # 업데이트 될 규칙텍스트명
    time = datetime.now()  # 현재시각

    # 규칙이름에 매핑되는 규칙조회
    scrule = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.use_yn == '1',
                                             Scrule.rule_name == rule).first()

    # 규칙에 해당하는 사용자조회
    vcstackuser = db.session.query(Vcstackuser).filter(Vcstackuser.tenant_id == tenant_id, Vcstackuser.name == name,
                                                       Vcstackuser.phone == phone, Vcstackuser.rule_id == scrule.id,
                                                       Vcstackuser.use_yn == '1').first()
    if vcstackuser:
        print(vcstackuser)
        vcstackuser.text_desc = ruleText  # 변경될 규칙
        vcstackuser.s_date = time.strftime("%Y-%m-%d")  # 시작일 
        vcstackuser.e_date = (time + timedelta(days=int(scrule.rule_duedate))).strftime("%Y-%m-%d")  # 종료일
        vcstackuser.use_yn = '1'  # 사용여부
        db.session.add(vcstackuser)
        db.session.commit()

    return jsonify({'msg': "HTTP STATE CODE 200"})


# 캘린더규칙 업데이트(완료)
@inout_apply.route('/rule/calendar/update', methods=['POST'])
def ruleFileUpdate():
    tenant_id = current_user.ssctenant.id
    name = request.form['name']  # 사용자이름
    phone = request.form['phone']  # 휴대폰
    rule = request.form['rule']  # rule 이름
    calendar = request.form['calendar']  # 날짜
    time = datetime.strptime(calendar, '%Y-%m-%d')

    # 규칙이름에 매핑되는 규칙조회
    scrule = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.use_yn == '1',
                                             Scrule.rule_name == rule).first()

    # 규칙에 해당하는 사용자조회
    vcstackuser = db.session.query(Vcstackuser).filter(
        db.and_(Vcstackuser.tenant_id == tenant_id, Vcstackuser.name == name,
                Vcstackuser.phone == phone, Vcstackuser.rule_id == scrule.id,
                Vcstackuser.use_yn == '1')).first()

    if vcstackuser:
        vcstackuser.s_date = time.strftime("%Y-%m-%d")
        vcstackuser.e_date = (time + timedelta(days=int(scrule.rule_duedate))).strftime("%Y-%m-%d")
        vcstackuser.use_yn = '1'
        db.session.add(vcstackuser)
        db.session.commit()

    return jsonify({'msg': "HTTP STATE CODE 200"})


# 파일규칙 업데이트(완료)
@inout_apply.route('/rule/file/upload', methods=['POST'])
def fileUpload():
    print('파일규칙 업데이트')
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id  # 테넌트이름
        lists = []
        file = request.files['file']  # file객체
        AWS_ACCESS_KEY = current_app.config['AWS_ACCESS_KEY']  # AWS ACCESS KEY
        AWS_SECRET_KEY = current_app.config['AWS_SECRET_KEY']  # AWS SECRET KEY
        BUCKET_NAME = current_app.config['BUCKET_NAME']  # AWS BUCKET NAME

        # STEP01. 신청한사용자 조회
        scuser = db.session.query(Scuser).filter(db.and_(Scuser.tenant_id == tenant_id,
                                                         Scuser.name == current_user.name,
                                                         Scuser.phone == current_user.phone,
                                                         Scuser.use_yn == '1')).first()
        tenantId = tenant_id  # 테넌트아이디
        loginId = scuser.login_id  # 신청자 로그인아이디
        name = request.form['name']  # 사용자이름
        phone = request.form['phone']  # 휴대폰번호
        filename = file.filename  # 파일명
        uuid = shortuuid.uuid()  # uuid
        rule = request.form['rule']  # 규칙이름

        # 업로드될 버킷 url
        # {tenantid(vms_1)}/data/user/{신청한사람id}/files/rule/{개인 핸드폰번호}/{파일명+유효아이디}
        bucketUrl = str(tenantId) + '/data/user/' + loginId + '/files/rule/' + name + phone + '/' + uuid + filename

        # STEP02. S3 Upload
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        s3.put_object(
            Bucket=BUCKET_NAME,
            Body=file,  # 업로드할 파일 객체
            Key=bucketUrl,  # S3에 업로드할 파일의 경로
            ContentType=file.content_type)  # 메타데이터설정

        # STEP03. 규칙이름에 매핑되는 규칙조회 및 user 삽입
        scrule = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id, Scrule.use_yn == '1',
                                                 Scrule.rule_name == rule).first()
        time = datetime.now()
        vcstackuser = db.session.query(Vcstackuser).filter(
            db.and_(Vcstackuser.tenant_id == tenant_id, Vcstackuser.name == name,
                    Vcstackuser.phone == phone, Vcstackuser.rule_id == scrule.id,
                    Vcstackuser.use_yn == '1')).first()

        if vcstackuser:
            vcstackuser.s_date = time.strftime("%Y-%m-%d")
            vcstackuser.e_date = (time + timedelta(days=int(scrule.rule_duedate))).strftime("%Y-%m-%d")
            vcstackuser.use_yn = '1'
            db.session.add(vcstackuser)
            db.session.commit()
            scrulefile = db.session.query(ScRuleFile).filter(
                db.and_(ScRuleFile.tenant_id == tenant_id, ScRuleFile.rule_id == scrule.id,
                        ScRuleFile.visit_stack_id == vcstackuser.id, ScRuleFile.use_yn == '1')).first()

            if scrulefile:
                scrulefile.s3_url = bucketUrl
                scrulefile.file_name = filename
                db.session.add(scrulefile)
                db.session.commit()

        bucketUrl = 'https://vms-tenants-rulefile-bucket-dev.s3.ap-northeast-2.amazonaws.com/' + bucketUrl
        return jsonify({'msg': bucketUrl})


# 규칙판별(완료)
@inout_apply.route('/rule/valid', methods=['POST'])
def ruleValidate():
    print('규칙판별')
    tenant_id = current_user.ssctenant.id  # 테넌트아이디
    name = request.form['name']  # 사용자 이름
    phone = request.form['phone']  # 휴대폰 번호
    vsdate = request.form['sdate']  # 방문시작 날짜
    vedate = request.form['edate']  # 방문종료 날짜

    lists = []
    # Step01.Rule전체조회
    for row in db.session.query(Scrule).filter(db.and_(Scrule.tenant_id == tenant_id, Scrule.use_yn == '1')).all():
        dict = {
            "rule_id": row.id,
            "rule_type": row.rule_type,
            "rule_name": row.rule_name,
            "state": False,
            "bucketUrl": ''
        }
        lists.append(dict)

    # Step02.tenant에 등록된 RULE을 기준으로, name/phone/유효일자를 검색하는 로직, 규칙시작일(s_date) <=방문시작일(vsdate) / 규칙종료일(e_date) >=방문종료일(vedate) 검증
    for row in db.session.query(Vcstackuser).filter(db.and_(Vcstackuser.tenant_id == tenant_id,
                                                            Vcstackuser.name == name,
                                                            Vcstackuser.phone == phone,
                                                            Vcstackuser.use_yn == '1',
                                                            Vcstackuser.s_date <= vsdate,
                                                            Vcstackuser.e_date >= vedate)).order_by(
        db.desc(Vcstackuser.created_at)).all():
        for dict in lists:
            rule_id = dict['rule_id']
            if rule_id == row.rule_id:

                if row.scrule.rule_type == '파일':
                    scrulefile = db.session.query(ScRuleFile).filter(db.and_(ScRuleFile.tenant_id == tenant_id,
                                                                             ScRuleFile.use_yn == '1',
                                                                             ScRuleFile.visit_stack_id == row.id
                                                                             )).first()

                    bucketUrl = 'https://vms-tenants-rulefile-bucket-dev.s3.ap-northeast-2.amazonaws.com/' + scrulefile.s3_url
                    dict['bucketUrl'] = bucketUrl

                dict['state'] = True
                dict['text_desc'] = row.text_desc
                dict['s_date'] = row.s_date

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


# 사업장조회(완료)
@inout_apply.route('/workspace/search', methods=['POST'])
def workSpaceSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id
        lists = []
        lists2 = []

        for row in db.session.query(Sccode).filter(
                db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 1, Sccode.use_yn == '1')):
            sccode = {
                "code": row.code,
                "code_nm": row.code_nm,
                "attb_a": row.attb_a
            }

            lists.append(sccode)

        attb_a = lists[0]['code']

        # 해당 사업장의 출입지역을 조회해온다.
        for row in db.session.query(Sccode).filter(
                db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 2, Sccode.attb_a == attb_a,
                        Sccode.use_yn == '1')).all():
            sccode = {
                "code": row.code,
                "code_nm": row.code_nm
            }
            lists2.append(sccode)

        return jsonify({'msg': lists,
                        'msg2': lists2});


# 출입지역
@inout_apply.route('/door/search', methods=['POST'])
def doorSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id  # 테넌트아이디
        lists = []
        code = request.form['code']  # 코드
        code_nm = request.form['code_nm']  # 코드이름

        # 해당 사업장의 출입지역을 조회해온다. 
        for row in db.session.query(Sccode).filter(
                db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 2, Sccode.attb_a == code,
                        Sccode.use_yn == '1')).all():
            sccode = {
                "code": row.code,
                "code_nm": row.code_nm
            }

            lists.append(sccode)

    return jsonify({'msg': lists});


# 사용자 조회(완료)
@inout_apply.route('/user/search', methods=['POST'])
def userSearch():
    print('사용자 조회')
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id  # 테넌트 아이디
        name = request.form['name']  # 사용자 이름
        phone = request.form['phone']  # 사용자 휴대폰번호
        lists = []

        # 셀로 추가된 유저에 대한, 신규/기존 사용자인지 확인 및 검증
        vcstackuser = db.session.query(Vcstackuser.name).filter(db.and_(Vcstackuser.tenant_id == tenant_id,
                                                                        Vcstackuser.name == name,
                                                                        Vcstackuser.phone == phone,
                                                                        Vcstackuser.use_yn == '1')).group_by(
            Vcstackuser.name).first()

        if not vcstackuser:  # 사용자가 없는 경우 vcstackuser에 신규사용자를 추가해준다.
            for row in db.session.query(Scrule).filter(
                    db.and_(Scrule.tenant_id == tenant_id, Scrule.use_yn == '1')).all():
                vcstackNuser = Vcstackuser()  # 신규사용자
                vcstackNuser.tenant_id = tenant_id  # 테넌트아이디
                vcstackNuser.name = name  # 이름
                vcstackNuser.phone = phone  # 휴대폰번호
                vcstackNuser.rule_id = row.id  # 규칙아이디
                db.session.add(vcstackNuser)
                db.session.commit()

                if row.rule_type == '파일':
                    scruleFile = ScRuleFile()
                    scruleFile.tenant_id = tenant_id
                    scruleFile.rule_id = row.id
                    scruleFile.visit_stack_id = vcstackNuser.id
                    db.session.add(scruleFile)
                    db.session.commit()

        else:  # 사용자 있는 경우
            lists.append({"name": vcstackuser[0]})

        return jsonify({'msg': lists})
