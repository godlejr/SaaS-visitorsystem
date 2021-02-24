import boto3
import shortuuid
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, current_app, jsonify, flash
from flask_login import current_user, login_required
from visitorsystem.models import db, Vcapplymaster, Ssctenant, Scrule, Vcvisituser, Sccompinfo, Scuser, Sccode, \
    ScRuleFile, Vcapplyuser, Vcstackuser

inout_apply = Blueprint('inout_apply', __name__)


# 메인페이지
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


# 출입신청 수정
@inout_apply.route('/edit/<int:number>', methods=['GET'])
def edit(number):
    if request.method == 'GET':
        num = number

        tenant_id = current_user.ssctenant.id  # 로그인 사용자의 테넌트 아이디
        scrules = db.session.query(Scrule).all()  # 페이지 로드전 동적규칙 조회

        # 출입신청마스터 조회
        vcapplymaster = db.session.query(Vcapplymaster).filter(
            db.and_(Vcapplymaster.tenant_id == tenant_id, Vcapplymaster.id == num,
                    Vcapplymaster.use_yn == '1')).first()

        if not vcapplymaster:
            return render_template('error' + '/404.html')

        # 작업자 업체조회
        sccompinfo = db.session.query(Sccompinfo).filter(
            db.and_(Sccompinfo.tenant_id == tenant_id, Sccompinfo.id == vcapplymaster.biz_id,
                    Sccompinfo.use_yn == '1')).first()

        # 접견자 조회
        scuser = db.session.query(Scuser).filter(
            db.and_(Scuser.tenant_id == tenant_id, Scuser.id == vcapplymaster.interview_id,
                    Sccompinfo.use_yn == '1')).first()

        # 방문유형 조회
        visitCategorys = db.session.query(Sccode).filter(
            db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 6, Sccode.use_yn == '1')).all()
        catagory = vcapplymaster.visit_category

        # 사업장 조회
        locations = db.session.query(Sccode).filter(
            db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 1, Sccode.use_yn == '1')).all()
        site_id = vcapplymaster.site_id
        site_nm = vcapplymaster.site_nm

        # 출입신청시 적용된 rule
        currentRule = []
        for row in db.session.query(Vcvisituser).filter(
                db.and_(Vcvisituser.tenant_id == tenant_id, Vcvisituser.apply_id == num,
                        Vcvisituser.use_yn == '1')).group_by(Vcvisituser.rule_id).all():
            rule_name = db.session.query(Scrule).filter(
                db.and_(Scrule.tenant_id == tenant_id, Scrule.id == row.rule_id)).first().rule_name
            currentRule.append(rule_name)

        # 출입문 조회
        doors = db.session.query(Sccode).filter(
            db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 2, Sccode.attb_a == site_id,
                    Sccode.use_yn == '1')).all()
        site_id2 = vcapplymaster.site_id2
        site_nm2 = vcapplymaster.site_nm2

        sdate = vcapplymaster.visit_sdate
        edate = vcapplymaster.visit_edate

        applyDate = {'sdate': sdate.split('-'), 'edate': edate.split('-')}

        applyDate['sdate'] = applyDate['sdate'][1] + '/' + applyDate['sdate'][2] + '/' + applyDate['sdate'][0]
        applyDate['edate'] = applyDate['edate'][1] + '/' + applyDate['edate'][2] + '/' + applyDate['edate'][0]

        state = vcapplymaster.approval_state
        block = ''

        print(state)
        if state == '반려' or state == '승인':
            block = 'disabled'

        # 차량종류 조회
        cars = db.session.query(Sccode).filter(
            db.and_(Sccode.tenant_id == tenant_id, Sccode.class_id == 3, Sccode.use_yn == '1')).all()

        # 규칙조회
        vcvisitusers = db.session.query(Vcvisituser).filter(
            db.and_(Vcvisituser.tenant_id == tenant_id, Vcvisituser.apply_id == num, Vcvisituser.use_yn == '1')).all()

        # 방문자조회(Table)

        vcapplyusers = db.session.query(Vcapplyuser).filter(
            db.and_(Vcapplyuser.tenant_id == tenant_id, Vcapplyuser.apply_id == num, Vcapplymaster.use_yn == '1')).all()
        tableList = []

        # 출입신청 하나에 연결된, 사용자리스트 조회
        for vcapplyuser in vcapplyusers:
            obj = {'name': vcapplyuser.visitant, 'phone': vcapplyuser.phone, 'vehicle_type': vcapplyuser.vehicle_type,
                   'vehicle_num': vcapplyuser.vehicle_num, 'rule': []}

            for vcvisituser in db.session.query(Vcvisituser).filter(
                    db.and_(Vcvisituser.tenant_id == tenant_id, Vcvisituser.apply_id == num,
                            Vcvisituser.name == obj['name'], Vcvisituser.phone == obj['phone'],
                            Vcvisituser.use_yn == '1')).all():
                dict = {'rule_id': '', 'rule_type': '', 'rule_name': '', 'sdate': '', 'edate': '', 'textDesc': '',
                        'bucketUrl': '', 'fileClassId': ''}
                uuid = 'applyFile' + shortuuid.uuid()  # uuid
                dict['fileClassId'] = uuid
                dict['rule_id'] = vcvisituser.scrule.id
                dict['rule_type'] = vcvisituser.scrule.rule_type
                dict['rule_name'] = vcvisituser.scrule.rule_name
                datechange = vcvisituser.s_date.split('-')
                dict['sdate'] = datechange[1] + '/' + datechange[2] + '/' + datechange[0]
                datechange = vcvisituser.e_date.split('-')
                dict['edate'] = datechange[1] + '/' + datechange[2] + '/' + datechange[0]
                dict['textDesc'] = vcvisituser.text_desc

                if vcvisituser.scrule.rule_type == '파일':
                    scruleFile = db.session.query(ScRuleFile).filter(
                        db.and_(ScRuleFile.tenant_id == tenant_id, ScRuleFile.visit_id == vcvisituser.id,
                                ScRuleFile.use_yn == '1')).first()

                    dict['bucketUrl'] = current_app.config['S3_BUCKET_NAME_VMS'] + scruleFile.s3_url


                obj['rule'].append(dict)

            tableList.append(obj)

            # 출입신청 시점에서 적용된 규칙이름 조회

        return render_template(current_app.config['TEMPLATE_THEME'] + '/inout_apply/edit.html',
                               scrules=scrules, vcapplymaster=vcapplymaster, sccompinfo=sccompinfo, scuser=scuser,
                               applyDate=applyDate, visitCategorys=visitCategorys, catagory=catagory,
                               currentRule=currentRule,
                               locations=locations, site_nm=site_nm, doors=doors, site_nm2=site_nm2, block=block,
                               state=state, cars=cars, tableList=tableList)


# 출입신청 수정저장
@inout_apply.route('/save', methods=['POST'])
def save():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id  # 테넌트아이디
        applicant_name = request.form['applicant_name']
        applicant_phone = request.form['applicant_phone']

        interviewer_name = request.form['interviewer_name']  # 접견자 이름
        interviewer_phone = request.form['interviewer_phone']  # 접견자 휴대폰번호

        # 감독자 조회(내부직원)
        interViewUser = db.session.query(Scuser).filter(db.and_(Scuser.tenant_id == tenant_id, Scuser.user_type == '0',
                                                                Scuser.name == interviewer_name,
                                                                Scuser.phone == interviewer_phone,
                                                                Scuser.use_yn == '1')).first()

        biz_no = request.form['applicant_biz_no']
        comp_nm = request.form['applicant_comp_nm']
        applyId = request.form['applyId']

        # 업체조회
        sccompinfo = db.session.query(Sccompinfo).filter(
            db.and_(Sccompinfo.tenant_id == tenant_id, Sccompinfo.comp_nm == comp_nm, Sccompinfo.biz_no == biz_no,
                    Sccompinfo.use_yn == '1')).first()

        # STEP01. Vcapplymaster 조회
        vcapplymaster = db.session.query(Vcapplymaster).filter(
            db.and_(Vcapplymaster.tenant_id == tenant_id, Vcapplymaster.id == applyId,
                    Vcvisituser.use_yn == '1')).first()
        db.session.query(Vcvisituser).filter(Vcvisituser.tenant_id == tenant_id,
                                             Vcvisituser.apply_id == applyId).delete()
        db.session.query(Vcapplyuser).filter(Vcapplyuser.tenant_id == tenant_id,
                                             Vcapplyuser.apply_id == applyId).delete()
        if vcapplymaster:
            vcapplymaster.interviewr = request.form['interviewer_name']  # 감독자

            vcapplymaster.applicant = request.form['applicant_name']  # 신청자
            vcapplymaster.applicant_comp_id = request.form['applicant_biz_no']  # 신청자 업체번호
            vcapplymaster.applicant_comp_nm = request.form['applicant_comp_nm']  # 신청자 회사명
            vcapplymaster.phone = request.form['applicant_phone']  # 신청자 휴대폰
            vcapplymaster.visit_category = request.form['inout_purpose_type']  # 방문유형
            vcapplymaster.biz_id = sccompinfo.id  # 업체번호
            vcapplymaster.visit_sdate = request.form['inout_sdate']  # 방문시작일
            vcapplymaster.visit_edate = request.form['inout_edate']  # 방문종료일
            vcapplymaster.visit_purpose = request.form['inout_title']  # 방문목적
            vcapplymaster.visit_desc = request.form['inout_purpose_desc']  # 방문목적상세

            vcapplymaster.site_id = request.form['inout_location_code']  # 방문목적상세
            vcapplymaster.site_nm = request.form['inout_location']  # 방문목적상세
            vcapplymaster.site_id2 = request.form['inout_location_code2']  # 방문목적상세
            vcapplymaster.site_nm2 = request.form['inout_location2']  # 방문목적상세
            vcapplymaster.user_id = current_user.id  # 출입신청자 아이디
            vcapplymaster.interview_id = interViewUser.id  # 접견부서 아이디
            vcapplymaster.visit_type = '0'  # 0(로그인 한 사용자, 작업자용) #1(로그인 안 함 사용자, 일반사용자용)
            vcapplymaster.use_yn = '1'
            db.session.add(vcapplymaster)
            db.session.commit()

            # STEP02. Vcapplyuser 생성/Vcvisituser
            visitors = json.loads(request.form['visitors'])
            for row in visitors:
                vcapplyuser = Vcapplyuser()
                vcapplyuser.tenant_id = tenant_id  # 테넌트 아이디
                vcapplyuser.apply_id = vcapplymaster.id  # 출입신청 아이디
                vcapplyuser.visitant = row['name']  # 방문자 이름
                vcapplyuser.phone = row['phone']  # 방문자 핸드폰 번호
                vcapplyuser.vehicle_type = row['carType']  # 방문자 차량유형
                vcapplyuser.vehicle_num = row['carNum']  # 방문자 차량번호
                db.session.add(vcapplyuser)
                db.session.commit()

                name = row['name']
                phone = row['phone']

                for vcstackuser in db.session.query(Vcstackuser).filter(
                        db.and_(Vcstackuser.tenant_id == tenant_id, Vcstackuser.name == name,
                                Vcstackuser.phone == phone, Vcstackuser.use_yn == '1')).all():
                    vcstackuser.apply_id = applyId
                    db.session.add(vcstackuser)
                    db.session.commit()

                for rule in row['rule']:
                    vcvisituser = Vcvisituser()
                    vcvisituser.tenant_id = tenant_id  # 테넌트 아이디
                    vcvisituser.apply_id = applyId  # 출입신청 아이디
                    vcvisituser.name = row['name']  # 방문자이름
                    vcvisituser.phone = row['phone']  # 방문자휴대폰 번호

                    ruleType = rule['ruleType']  # 규칙유형
                    ruleName = rule['ruleName']  # 규칙이름
                    ruleDesc = rule['ruleDesc']  # 텍스트 유형 규칙기술
                    sdate = rule['sDate']  # 시작날짜
                    scrule = db.session.query(Scrule).filter(
                        db.and_(Scrule.tenant_id == tenant_id, Scrule.rule_name == ruleName)).first()
                    vcvisituser.rule_id = scrule.id  # 규칙 아이디
                    vcvisituser.text_desc = ruleDesc  # 텍스트 유형 규칙기술
                    vcvisituser.s_date = sdate  # 규칙 시작날짜
                    time = datetime.strptime(vcvisituser.s_date, '%Y-%m-%d')
                    vcvisituser.e_date = (time + timedelta(days=int(scrule.rule_duedate))).strftime(
                        "%Y-%m-%d")  # 규칙 종료일자
                    db.session.add(vcvisituser)
                    db.session.commit()

                    if ruleType == '파일':
                        scruleFile = ScRuleFile()
                        scruleFile.tenant_id = tenant_id  # 테넌트 아이디
                        scruleFile.rule_id = scrule.id  # 규칙 아이디
                        scruleFile.visit_id = vcvisituser.id  # 출입신청 방문 아이디
                        scruleFile.file_name = rule['bucketUrl'].split('/')[-1]  # 파일명
                        scruleFile.s3_url = rule['bucketUrl'].split('/')[-1]  # 버킷주소

                        db.session.add(scruleFile)
                        db.session.commit()

    return jsonify({'msg': "HTTP STATE CODE 200"})


# 출입신청
@inout_apply.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id  # 테넌트아이디
        applicant_name = request.form['applicant_name']
        applicant_phone = request.form['applicant_phone']

        interviewer_name = request.form['interviewer_name']  # 접견자 이름
        interviewer_phone = request.form['interviewer_phone']  # 접견자 휴대폰번호

        # 감독자 조회(내부직원)
        interViewUser = db.session.query(Scuser).filter(db.and_(Scuser.tenant_id == tenant_id, Scuser.user_type == '0',
                                                                Scuser.name == interviewer_name,
                                                                Scuser.phone == interviewer_phone,
                                                                Scuser.use_yn == '1')).first()

        biz_no = request.form['applicant_biz_no']
        comp_nm = request.form['applicant_comp_nm']

        # 업체조회
        sccompinfo = db.session.query(Sccompinfo).filter(
            db.and_(Sccompinfo.tenant_id == tenant_id, Sccompinfo.comp_nm == comp_nm, Sccompinfo.biz_no == biz_no,
                    Sccompinfo.use_yn == '1')).first()

        # STEP01. Vcapplymaster 생성
        vcapplymaster = Vcapplymaster()  # 출입마스터 생성

        vcapplymaster.tenant_id = tenant_id  # 로그인 사용자의 태넌트아이디
        vcapplymaster.interviewr = request.form['interviewer_name']  # 감독자

        vcapplymaster.applicant = request.form['applicant_name']  # 신청자
        vcapplymaster.applicant_comp_id = request.form['applicant_biz_no']  # 신청자 업체번호
        vcapplymaster.applicant_comp_nm = request.form['applicant_comp_nm']  # 신청자 회사명
        vcapplymaster.phone = request.form['applicant_phone']  # 신청자 휴대폰
        vcapplymaster.visit_category = request.form['inout_purpose_type']  # 방문유형
        vcapplymaster.biz_id = sccompinfo.id  # 업체번호
        vcapplymaster.visit_sdate = request.form['inout_sdate']  # 방문시작일
        vcapplymaster.visit_edate = request.form['inout_edate']  # 방문종료일
        vcapplymaster.visit_purpose = request.form['inout_title']  # 방문목적
        vcapplymaster.visit_desc = request.form['inout_purpose_desc']  # 방문목적상세

        vcapplymaster.site_id = request.form['inout_location_code']  # 방문목적상세
        vcapplymaster.site_nm = request.form['inout_location']  # 방문목적상세
        vcapplymaster.site_id2 = request.form['inout_location_code2']  # 방문목적상세
        vcapplymaster.site_nm2 = request.form['inout_location2']  # 방문목적상세
        vcapplymaster.user_id = current_user.id  # 출입신청자 아이디
        vcapplymaster.interview_id = interViewUser.id  # 접견부서 아이디
        vcapplymaster.approval_state = '대기'  # 출입승인 상태 저장
        vcapplymaster.visit_type = '0'  # 0(로그인 한 사용자, 작업자용) #1(로그인 안 함 사용자, 일반사용자용)
        vcapplymaster.use_yn = '1'
        db.session.add(vcapplymaster)
        db.session.commit()

        # STEP02. Vcapplyuser 생성/Vcvisituser
        visitors = json.loads(request.form['visitors'])
        for row in visitors:
            vcapplyuser = Vcapplyuser()
            vcapplyuser.tenant_id = tenant_id  # 테넌트 아이디
            vcapplyuser.apply_id = vcapplymaster.id  # 출입신청 아이디
            vcapplyuser.visitant = row['name']  # 방문자 이름
            vcapplyuser.phone = row['phone']  # 방문자 핸드폰 번호
            vcapplyuser.vehicle_type = row['carType']  # 방문자 차량유형
            vcapplyuser.vehicle_num = row['carNum']  # 방문자 차량번호
            db.session.add(vcapplyuser)
            db.session.commit()

            name = row['name']
            phone = row['phone']

            for vcstackuser in db.session.query(Vcstackuser).filter(
                    db.and_(Vcstackuser.tenant_id == tenant_id, Vcstackuser.name == name,
                            Vcstackuser.phone == phone, Vcstackuser.use_yn == '1')).all():
                vcstackuser.apply_id = vcapplymaster.id
                db.session.add(vcstackuser)
                db.session.commit()

            for rule in row['rule']:
                vcvisituser = Vcvisituser()
                vcvisituser.tenant_id = tenant_id  # 테넌트 아이디
                vcvisituser.apply_id = vcapplymaster.id  # 출입신청 아이디
                vcvisituser.name = row['name']  # 방문자이름
                vcvisituser.phone = row['phone']  # 방문자휴대폰 번호

                ruleType = rule['ruleType']  # 규칙유형
                ruleName = rule['ruleName']  # 규칙이름
                ruleDesc = rule['ruleDesc']  # 텍스트 유형 규칙기술
                sdate = rule['sDate']  # 시작날짜
                scrule = db.session.query(Scrule).filter(
                    db.and_(Scrule.tenant_id == tenant_id, Scrule.rule_name == ruleName,
                            Scrule.use_yn == '1')).first()
                vcvisituser.rule_id = scrule.id  # 규칙 아이디
                vcvisituser.text_desc = ruleDesc  # 텍스트 유형 규칙기술
                vcvisituser.s_date = sdate  # 규칙 시작날짜
                time = datetime.strptime(vcvisituser.s_date, '%Y-%m-%d')
                vcvisituser.e_date = (time + timedelta(days=int(scrule.rule_duedate))).strftime(
                    "%Y-%m-%d")  # 규칙 종료일자
                db.session.add(vcvisituser)
                db.session.commit()

                if ruleType == '파일':
                    scruleFile = ScRuleFile()
                    scruleFile.tenant_id = tenant_id  # 테넌트 아이디
                    scruleFile.rule_id = scrule.id  # 규칙 아이디
                    scruleFile.visit_id = vcvisituser.id  # 출입신청 방문 아이디
                    scruleFile.file_name = rule['bucketUrl'].split('/')[-1]  # 파일명
                    scruleFile.s3_url = rule['bucketUrl'].split('/')[-1]  # 버킷주소

                    db.session.add(scruleFile)
                    db.session.commit()

    return jsonify({'msg': "HTTP STATE CODE 200"})


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


# 규칙 조회(출입신청 시점의 규칙조회)
@inout_apply.route('/rule/search/before', methods=['POST'])
def ruleSearchBefore():
    tenant_id = current_user.ssctenant.id

    # 특정시점의 출입신청 아이디(정책은 출입신청 시점에서 적용된다.)
    applyId = request.form['applyId']
    vcvisitusers = db.session.query(Vcvisituser).filter(
        db.and_(Vcvisituser.tenant_id == tenant_id, Vcvisituser.apply_id == applyId)).group_by(
        Vcvisituser.rule_id).all()

    lists = []
    for vcvisituser in vcvisitusers:

        for row in db.session.query(Scrule).filter(
                db.and_(Scrule.tenant_id == tenant_id, Scrule.id == vcvisituser.rule_id)).all():
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


# 텍스트규칙 업데이트
@inout_apply.route('/rule/text/update', methods=['POST'])
def ruleTextUpdate():
    tenant_id = current_user.ssctenant.id  # 테넌트 아이디
    name = request.form['name']  # 이름
    phone = request.form['phone']  # 휴대폰
    rule = request.form['rule']  # 규칙이름
    type = request.form['type']  # 규칙종류
    ruleText = request.form['ruleText']  # 업데이트 될 규칙텍스트명
    time = datetime.now()  # 현재시각

    # 규칙이름에 매핑되는 규칙조회
    scrule = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id,
                                             Scrule.rule_name == rule).first()

    # 규칙에 해당하는 사용자조회
    vcstackuser = db.session.query(Vcstackuser).filter(Vcstackuser.tenant_id == tenant_id, Vcstackuser.name == name,
                                                       Vcstackuser.phone == phone, Vcstackuser.rule_id == scrule.id,
                                                       Vcstackuser.use_yn == '1').first()
    if vcstackuser:
        vcstackuser.text_desc = ruleText  # 변경될 규칙
        vcstackuser.s_date = time.strftime("%Y-%m-%d")  # 시작일 
        vcstackuser.e_date = (time + timedelta(days=int(scrule.rule_duedate))).strftime("%Y-%m-%d")  # 종료일
        vcstackuser.use_yn = '1'  # 사용여부
        db.session.add(vcstackuser)
        db.session.commit()

    return jsonify({'msg': "HTTP STATE CODE 200"})


# 캘린더규칙 업데이트
@inout_apply.route('/rule/calendar/update', methods=['POST'])
def ruleFileUpdate():
    tenant_id = current_user.ssctenant.id
    name = request.form['name']  # 사용자이름
    phone = request.form['phone']  # 휴대폰
    rule = request.form['rule']  # rule 이름
    calendar = request.form['calendar']  # 날짜
    time = datetime.strptime(calendar, '%Y-%m-%d')

    # 규칙이름에 매핑되는 규칙조회
    scrule = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id,
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


# 파일규칙 업데이트
@inout_apply.route('/rule/file/upload', methods=['POST'])
def fileUpload():
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
        tenantId = 'VMS_' + str(tenant_id)  # 테넌트아이디
        loginId = scuser.login_id  # 신청자 로그인아이디
        name = request.form['name']  # 사용자이름
        phone = request.form['phone']  # 휴대폰번호
        filename = file.filename  # 파일명
        uuid = shortuuid.uuid()  # uuid
        rule = request.form['rule']  # 규칙이름

        # 업로드될 버킷 url
        # {tenantid(vms_1)}/data/user/{신청한사람id}/files/rule/{개인 핸드폰번호}/{파일명+유효아이디}/{파일명}
        bucketUrl = str(
            tenantId) + '/data/user/' + loginId + '/files/rule/' + name + phone + '/' + uuid + filename + '/' + filename

        print(bucketUrl)
        # STEP02. S3 Upload
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        s3.put_object(
            Bucket=BUCKET_NAME,
            Body=file,  # 업로드할 파일 객체
            Key=bucketUrl,  # S3에 업로드할 파일의 경로
            ContentType=file.content_type)  # 메타데이터설정

        # STEP03. 규칙이름에 매핑되는 규칙조회 및 user 삽입
        scrule = db.session.query(Scrule).filter(Scrule.tenant_id == tenant_id,
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
                        ScRuleFile.visit_stack_id == vcstackuser.id)).first()

            if scrulefile:
                scrulefile.s3_url = bucketUrl
                scrulefile.file_name = filename
                db.session.add(scrulefile)
                db.session.commit()

        bucketUrl = current_app.config['S3_BUCKET_NAME_VMS'] + bucketUrl
        return jsonify({'msg': bucketUrl})


# 규칙판별
@inout_apply.route('/rule/valid', methods=['POST'])
def ruleValidate():
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

                    bucketUrl = current_app.config['S3_BUCKET_NAME_VMS'] + scrulefile.s3_url
                    dict['bucketUrl'] = bucketUrl

                dict['state'] = True
                dict['text_desc'] = row.text_desc
                dict['s_date'] = row.s_date

    return jsonify({'msg': lists})


# 규칙판별
@inout_apply.route('/rule/valid/before', methods=['POST'])
def ruleValidateBefore():
    tenant_id = current_user.ssctenant.id  # 테넌트아이디
    name = request.form['name']  # 사용자 이름
    phone = request.form['phone']  # 휴대폰 번호
    vsdate = request.form['sdate']  # 방문시작 날짜
    vedate = request.form['edate']  # 방문종료 날짜

    # 특정시점의 출입신청 아이디(정책은 출입신청 시점에서 적용된다.)
    applyId = request.form['applyId']
    vcvisitusers = db.session.query(Vcvisituser).filter(
        db.and_(Vcvisituser.tenant_id == tenant_id, Vcvisituser.apply_id == applyId)).group_by(
        Vcvisituser.rule_id).all()

    lists = []
    # Step01.Rule(출입신청 시점에 적용된 규칙적용)
    for vcvisituser in vcvisitusers:

        for row in db.session.query(Scrule).filter(
                db.and_(Scrule.tenant_id == tenant_id, Scrule.id == vcvisituser.rule_id)).all():
            dict = {
                "rule_id": row.id,
                "rule_type": row.rule_type,
                "rule_name": row.rule_name,
                "state": False,
                "bucketUrl": ''
            }

            lists.append(dict)

    # Step02.tenant에 등록된 RULE을 기준으로, name/phone/유효일자를 검색하는 로직, 규칙시작일(s_date) <=방문시작일(vsdate) / 규칙종료일(e_date) >=방문종료일(vedate) 검증
    print(vsdate)
    print(vedate)
    print(name)
    print(phone)
    print(tenant_id)
    for row in db.session.query(Vcstackuser).filter(db.and_(Vcstackuser.tenant_id == tenant_id,
                                                            Vcstackuser.name == name,
                                                            Vcstackuser.phone == phone,
                                                            Vcstackuser.use_yn == '1',
                                                            # Vcstackuser.s_date <= vsdate,
                                                            Vcstackuser.e_date >= vedate)).order_by(
        db.desc(Vcstackuser.created_at)).all():
        print('찍힘2')
        for dict in lists:
            rule_id = dict['rule_id']

            if rule_id == row.rule_id:

                if row.scrule.rule_type == '파일':
                    scrulefile = db.session.query(ScRuleFile).filter(db.and_(ScRuleFile.tenant_id == tenant_id,
                                                                             ScRuleFile.use_yn == '1',
                                                                             ScRuleFile.visit_stack_id == row.id
                                                                             )).first()

                    bucketUrl = current_app.config['S3_BUCKET_NAME_VMS'] + scrulefile.s3_url
                    dict['bucketUrl'] = bucketUrl

                dict['state'] = True
                dict['text_desc'] = row.text_desc
                dict['s_date'] = row.s_date

    return jsonify({'msg': lists})


# 접견자조회 Modal
@inout_apply.route('/interview/search', methods=['POST'])
def interviewSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id  # 테넌트아이디
        name = request.form['interviewName']  # 접견자이름
        site_nm = request.form['site_nm']  # 사업장

        lists = []

        if len(name) == 0:
            return jsonify({'msg': lists});

        for row in db.session.query(Scuser).filter(
                db.and_(Scuser.tenant_id == tenant_id, Scuser.name.like(name + '%'), Scuser.user_type == '0',
                        Scuser.site_nm == site_nm,
                        Scuser.use_yn == '1')).all():
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

        if len(name) == 0:
            return jsonify({'msg': lists});

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

        if len(comp_nm) == 0:
            return jsonify({'msg': lists});

        for row in db.session.query(Sccompinfo).filter(
                db.and_(Sccompinfo.tenant_id == tenant_id, Sccompinfo.comp_nm.like(comp_nm + '%'),
                        Sccompinfo.use_yn == '1')):
            sccompinfo = {
                "biz_id": row.id,
                "comp_nm": row.comp_nm,
                "biz_no": row.biz_no
            }

            lists.append(sccompinfo)

        lists2 = []

        for list in lists:

            for row in db.session.query(Scuser).filter(
                    db.and_(Scuser.tenant_id == tenant_id, Scuser.biz_id == list['biz_id'], Scuser.user_type == '1',
                            Scuser.use_yn == '1')).all():
                scuser = {
                    "name": row.name,
                    "phone": row.phone,
                    "comp_nm": row.sccompinfo.comp_nm,
                    "biz_no": row.sccompinfo.biz_no
                }
                lists2.append(scuser)

        return jsonify({'msg': lists2});


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


# 사업장조회
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


# 사용자 조회
@inout_apply.route('/user/search', methods=['POST'])
def userSearch():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id  # 테넌트 아이디
        name = request.form['name']  # 사용자 이름
        phone = request.form['phone']  # 사용자 휴대폰번호
        lists = []

        # 셀로 추가된 유저에 대한, 신규/기존 사용자인지 확인 및 검증
        vcstackuser = db.session.query(Vcstackuser.name).filter(db.and_(Vcstackuser.tenant_id == tenant_id,
                                                                        # Vcstackuser.name == name,
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
                lists.append({"msg": "0"})

                if row.rule_type == '파일':
                    scruleFile = ScRuleFile()
                    scruleFile.tenant_id = tenant_id
                    scruleFile.rule_id = row.id
                    scruleFile.visit_stack_id = vcstackNuser.id
                    db.session.add(scruleFile)
                    db.session.commit()

        else:  # 사용자 있는 경우(추가된 규칙의 경우 Rule을 추가)

            if vcstackuser.name == name:
                for rule in db.session.query(Scrule).filter(
                        db.and_(Scrule.tenant_id == tenant_id, Scrule.use_yn == '1')).all():

                    vcstacAdduser = db.session.query(Vcstackuser).filter(
                        db.and_(Vcstackuser.tenant_id == tenant_id, Vcstackuser.name == name,
                                Vcstackuser.phone == phone, Vcstackuser.rule_id == rule.id,
                                Vcstackuser.use_yn == '1')).first()

                    if not vcstacAdduser:
                        vcstacAdduser = Vcstackuser()  # 신규사용자
                        vcstacAdduser.tenant_id = tenant_id  # 테넌트아이디
                        vcstacAdduser.name = name  # 이름
                        vcstacAdduser.phone = phone  # 휴대폰번호
                        vcstacAdduser.rule_id = rule.id  # 규칙아이디
                        db.session.add(vcstacAdduser)
                        db.session.commit()

                        if rule.rule_type == '파일':
                            scruleFile = ScRuleFile()
                            scruleFile.tenant_id = tenant_id
                            scruleFile.rule_id = rule.id
                            scruleFile.visit_stack_id = vcstacAdduser.id
                            db.session.add(scruleFile)
                            db.session.commit()
                lists.append({"msg": name})

            else:
                lists.append({"msg": "-1"})

        return jsonify({'msg': lists})


# 사용자 조회(규칙시점 조회용)
@inout_apply.route('/user/search/before', methods=['POST'])
def userSearchBefore():
    if request.method == 'POST':
        tenant_id = current_user.ssctenant.id  # 테넌트 아이디
        name = request.form['name']  # 사용자 이름
        phone = request.form['phone']  # 사용자 휴대폰번호
        lists = []

        # 특정시점의 출입신청 아이디(정책은 출입신청 시점에서 적용된다.)
        applyId = request.form['applyId']

        vcvisitusers = db.session.query(Vcvisituser).filter(
            db.and_(Vcvisituser.tenant_id == tenant_id, Vcvisituser.apply_id == applyId)).group_by(
            Vcvisituser.rule_id).all()

        # 셀로 추가된 유저에 대한, 신규/기존 사용자인지 확인 및 검증
        vcstackuser = db.session.query(Vcstackuser.name).filter(db.and_(Vcstackuser.tenant_id == tenant_id,
                                                                        # Vcstackuser.name == name,
                                                                        Vcstackuser.phone == phone,
                                                                        Vcstackuser.use_yn == '1')).group_by(
            Vcstackuser.name).first()

        if not vcstackuser:  # 사용자가 없는 경우 vcstackuser에 신규사용자를 추가해준다.

            for row in vcvisitusers:

                vcstackNuser = Vcstackuser()  # 신규사용자
                vcstackNuser.tenant_id = tenant_id  # 테넌트아이디
                vcstackNuser.name = name  # 이름
                vcstackNuser.phone = phone  # 휴대폰번호
                vcstackNuser.rule_id = row.rule_id  # 규칙아이디
                db.session.add(vcstackNuser)
                db.session.commit()
                lists.append({"msg": "0"})
                if row.scrule.rule_type == '파일':
                    scruleFile = ScRuleFile()
                    scruleFile.tenant_id = tenant_id
                    scruleFile.rule_id = row.rule_id
                    scruleFile.visit_stack_id = vcstackNuser.id
                    db.session.add(scruleFile)
                    db.session.commit()

        else:  # 사용자 있는 경우(추가된 규칙의 경우 Rule을 추가)
            if vcstackuser.name == name:
                lists.append({"msg": name})
            else:
                lists.append({"msg": "-1"})

        return jsonify({'msg': lists})
