import datetime
import re
import time
import xml.etree.cElementTree as et
from urllib import parse

import requests
from bs4 import BeautifulSoup
from flask import Blueprint, render_template, request, current_app, flash, session, redirect, url_for, jsonify
from flask_login import login_required, login_user, current_user
from sqlalchemy import and_
from werkzeug.security import check_password_hash, generate_password_hash
from visitorsystem.forms import LoginForm
from visitorsystem.models import db, Scuser, Ssctenant, Sccompinfo

main = Blueprint('main', __name__)


@main.route('/')
@login_required
def index():
    today_covid = get_covid()
    day = get_day()
    today = time.strftime('%Y.%m.%d', time.localtime(time.time()))

    articles = get_article(current_user.ssctenant.comp_nm)

    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/index.html', today_covid=today_covid, day=day,
                           today=today, articles=articles)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
            # 사용자 조회
            user = Scuser.query.filter(and_(Scuser.login_id == form.login_id.data, Scuser.tenant_id == ssctenant.id)).first()

            if user:
                # 비밀번호 비교
                if not check_password_hash(user.login_pwd, form.login_pwd.data):
                    flash('비밀번호가 잘못 되었습니다.')
                else:
                    # 정상 로그인 - 세션
                    session['id'] = user.id
                    session['_user_id'] = user.id
                    session['login_id'] = user.login_id
                    session['name'] = user.name
                    session['auth_id'] = user.auth_id
                    session['tenant_id'] = user.tenant_id
                    login_user(user)

                    return redirect(request.args.get("next") or url_for('main.index'))
            else:
                flash('회원아이디가 잘못되었습니다.')

    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('main.login'))


def get_covid():
    # 코로나 관련
    serviceUrl = current_app.config['COVID_SERVICE_URL']
    serviceKey = current_app.config['COVID_SECURITY_KEY']
    serviceKey_decode = parse.unquote(serviceKey)
    pageNo = '1'
    numOfRows = '10'

    startCreateDt = time.strftime('%Y%m%d', time.localtime(time.time() - 172800))  # 2일전
    endCreateDt = time.strftime('%Y%m%d', time.localtime(time.time()))

    covid_param = {"serviceKey": serviceKey_decode, "pageNo": pageNo, "numOfRows": numOfRows,
                   "startCreateDt": startCreateDt, "endCreateDt": endCreateDt}

    response = requests.get(serviceUrl, params=covid_param)

    print(response.text)
    covid_list = []
    if response.status_code == 200:
        dataTree = et.fromstring(response.text)
        iterData = dataTree.iter(tag='item')

        for element in iterData:
            accDefRate = element.find("accDefRate")
            print(accDefRate)
            accExamCnt = element.find("accExamCnt")
            accExamCompCnt = element.find("accExamCompCnt")
            careCnt = element.find("careCnt")
            clearCnt = element.find("clearCnt")
            createDt = element.find("createDt")
            deathCnt = element.find("deathCnt")
            decideCnt = element.find("decideCnt")
            examCnt = element.find("examCnt")
            resutlNegCnt = element.find("resutlNegCnt")
            seq = element.find("seq")
            stateDt = element.find("stateDt")
            stateTime = element.find("stateTime")
            updateDt = element.find("updateDt")

            data = {
                "accDefRate": accDefRate.text, "accExamCnt": accExamCnt.text, "accExamCompCnt": accExamCompCnt.text,
                "careCnt": careCnt.text, "clearCnt": clearCnt.text, "createDt": createDt.text,
                "deathCnt": deathCnt.text, "decideCnt": decideCnt.text, "examCnt": examCnt.text,
                "resutlNegCnt": resutlNegCnt.text, "seq": seq.text, "stateDt": stateDt.text,
                "stateTime": stateTime.text, "updateDt": updateDt.text
            }
            covid_list.append(data)

    index = 0

    today_covid = covid_list[index]
    yesterday_covid = covid_list[index + 1]
    stateDt = today_covid.get("stateDt")
    print("ddd" + stateDt)

    today_total_decideCnt = today_covid.get("decideCnt")  # 확진자
    today_total_examCnt = today_covid.get("examCnt")  # 검사자
    today_total_clearCnt = today_covid.get("clearCnt")  # 격리해제
    today_total_deathCnt = today_covid.get("deathCnt")  # 사망자

    yesterday_total_decideCnt = yesterday_covid.get("decideCnt")  # 확진자
    yesterday_total_examCnt = yesterday_covid.get("examCnt")  # 검사자
    yesterday_total_clearCnt = yesterday_covid.get("clearCnt")  # 격리해제
    yesterday_total_deathCnt = yesterday_covid.get("deathCnt")  # 사망자

    today_decideCnt = "{:,}".format(int(today_total_decideCnt) - int(yesterday_total_decideCnt))
    today_examCnt = "{:,}".format(int(today_total_examCnt))
    today_clearCnt = "{:,}".format(int(today_total_clearCnt) - int(yesterday_total_clearCnt))
    today_deathCnt = "{:,}".format(int(today_total_deathCnt) - int(yesterday_total_deathCnt))

    today_total_decideCnt = "{:,}".format(int(today_total_decideCnt))  # 확진자
    today_total_clearCnt = "{:,}".format(int(today_total_clearCnt))  # 격리해제
    today_total_deathCnt = "{:,}".format(int(today_total_deathCnt))  # 사망자

    cr_date = datetime.datetime.strptime(stateDt, '%Y%m%d')
    stateDt = cr_date.strftime('%Y.%m.%d')
    today_covid = {
        "stateDt": stateDt, "today_decideCnt": today_decideCnt, "today_examCnt": today_examCnt,
        "today_examCnt": today_examCnt, "today_clearCnt": today_clearCnt, "today_deathCnt": today_deathCnt,
        "today_total_decideCnt": today_total_decideCnt,
        "today_total_clearCnt": today_total_clearCnt, "today_total_deathCnt": today_total_deathCnt
    }

    return today_covid


def get_day():
    days = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    aday = (time.localtime().tm_mday)%7
    return days[aday - 1]


def get_article(keyword):
    # 쿼리에 검색어를 입력하고 검색 시작날짜부터 끝 날짜까지를 입력합니다.
    query = keyword  # url 인코딩 에러는 encoding parse.quote(query)
    s_date = time.strftime('%Y.%m.%d', time.localtime(time.time() - 2592000))  # 한달지
    e_date = time.strftime('%Y.%m.%d', time.localtime(time.time()))
    s_from = s_date.replace(".", "")
    e_to = e_date.replace(".", "")
    page = 1
    no = 1
    maxpage_t = (5) * 10 + 1

    articles = []

    while page < maxpage_t:
        print(page)

        url = "https://search.naver.com/search.naver?where=news&query=" + query + "&sort=1&ds=" + s_date + "&de=" + e_date + "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(
            page)
        # header 추가
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        }
        req = requests.get(url, headers=header,verify=False)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')

        try:
            urls = soup.findAll('a', href=re.compile('^http(s)?:\/\/(news)\.(naver)\.(com)\/(main)\/(read)\.(nhn)'))[0]

            if urls["href"].startswith("https://news.naver.com"):
                print("naver.com으로 시작하는 href만 추출")
                print(urls['href'])

                # print(urls["href"])
                print("get_new 함수 시작")
                news_detail = get_news(urls["href"])

                print("news_detail[1](url): " + news_detail[0])

                # f.write(news_detail[1] + "&&&")
                print("news_detail[1](날짜): " + news_detail[2])

                # # f.write(news_detail[4] + "&&&")
                print("news_detail[4](언론사) : " + news_detail[4])

                # f.write(news_detail[0] + "&&&")
                print("news_detail[0](제목) : " + news_detail[1])

                # f.write(news_detail[2] + "&&&")
                print("news_detail[2](기사내용) : 기사내용")
                print(news_detail[3])

            articles.append(news_detail)
        except Exception as e:
            print(e)
        page += 10

    return articles


def get_news(n_url):
    news_detail = []
    print(n_url)
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    breq = requests.get(n_url, headers=header,verify=False)
    bsoup = BeautifulSoup(breq.content, 'html.parser')

    # URL
    news_detail.append(n_url)

    # html 파싱
    title = bsoup.select('h3#articleTitle')[0].text
    news_detail.append(title)

    # 날짜 파싱
    pdate = bsoup.select('.t11')[0].get_text()[:11]
    news_detail.append(pdate)

    # 기사 본문 크롤링
    _text = bsoup.select('#articleBodyContents')[0].get_text().replace('\n', " ")
    btext = _text.replace("// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}", "")
    news_detail.append(btext.strip())

    # 신문사 크롤링
    pcompany = bsoup.select('#footer address')[0].a.get_text()
    news_detail.append(pcompany)

    return news_detail


@main.route('/compsearch', methods=['POST'])
def compsearch():
    """ 회원 가입 시 업체 정보 조회"""

    if request.method == 'POST':
        #host로 테넌트 정보 조회
        ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
        #회사 조회 - 1건만. 사업자등록번호로
        compInfo = Sccompinfo.query.filter_by(tenant_id=ssctenant.id, biz_no=request.form['biz_no']).first()

        #데이터 여부 체크 있으면 true 없으면 false
        if (compInfo):
            #튜플로 변경
            comp = {
                'biz_id':compInfo.id,
                'biz_no':compInfo.biz_no,
                'comp_nm':compInfo.comp_nm,
                'addr_1':compInfo.addr_1,
                'addr_2':compInfo.addr_2,
                'tel_no': compInfo.tel_no
            }
        else:
            #데이터 없는 경우
            comp = {'biz_id': 0}

        return jsonify({'msg': comp});


@main.route('/check', methods=['POST'])
def joincheck():
    """ 회원 가입 시 ID 중복 체크"""

    if request.method == 'POST':
        #host로 테넌트 정보 조회
        ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
        #아이디가 있는지 조회
        user = Scuser.query.filter_by(tenant_id=ssctenant.id, login_id=request.form['login_id']).first()

        #데이터 여부 체크 - 데이터가 있어 가입 가능하면 true 불가능 false
        if (user):
            #동일 ID 있는 경우
            comp = {'check':"true"}
        else:
            #데이터 없는 경우
            comp = {'check':"false"}

    return jsonify({'msg': comp});

@main.route('/join', methods=['POST'])
def join():
    """ 회원 가입, 회사정보 저장"""

    if request.method == 'POST':
        #host로 테넌트 정보 조회
        ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()

        #회사 정보가 저장되어 있는지 확인 - bizId가 있는지 확인
        biz_id = int(request.form['biz_id'])
        print(biz_id)
        if(biz_id > 0):
            pass
        else:
            #회사 정보 저장한다.
            compInfo = Sccompinfo()
            compInfo.tenant_id = ssctenant.id
            compInfo.biz_no = request.form['biz_no']
            compInfo.comp_nm = request.form['comp_nm']
            compInfo.addr_1 = request.form['addr_1']
            compInfo.addr_2 = request.form['addr_2']
            compInfo.tel_no = request.form['tel_no']
            db.session.add(compInfo)

            #biz_id조회
            # 회사 조회 - 1건만. 사업자등록번호로
            temp_comp = Sccompinfo.query.filter_by(tenant_id=ssctenant.id, biz_no=compInfo.biz_no).first()
            biz_id = int(temp_comp.id)

        print(biz_id)

        #회원 저장
        user = Scuser()
        user.tenant_id = ssctenant.id
        user.login_id = request.form['login_id']
        user.login_pwd = generate_password_hash(request.form['login_pwd'])
        user.name = request.form['name']
        user.phone = request.form['phone']
        user.email = request.form['email']

        user.biz_id = biz_id
        user.comp_nm = request.form['comp_nm']
        user.user_type = "1"    #외부인력
        user.auth_id = "1000"   #기본권한
        user.sms_yn = 'Y'
        user.info_agr_yn = 'Y'

        db.session.add(user)
        db.session.commit()
        
        #저장 되면 로그인-검토
        #login_user(user)

        #return redirect(request.args.get("next") or url_for('main.index'))

        comp = {'check': "true"}

    return jsonify({'msg': comp});
