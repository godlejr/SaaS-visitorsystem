import requests
import time, datetime
from urllib import parse
import xml.etree.cElementTree as et

from flask import Blueprint, render_template, request, current_app, flash, session, redirect, url_for
from flask_login import login_required, login_user
from werkzeug.security import check_password_hash

from visitorsystem.forms import LoginForm
from visitorsystem.models import Scuser, Ssctenant

main = Blueprint('main', __name__)


@main.route('/')
# @login_required
def index():
    today_covid = get_covid()
    day = get_day()
    today = time.strftime('%Y.%m.%d', time.localtime(time.time()))

    return render_template(current_app.config['TEMPLATE_THEME'] + '/main/index.html', today_covid=today_covid, day=day,
                           today=today)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            ssctenant = Ssctenant.query.filter_by(event_url=request.host).first()
            # 사용자 조회
            user = Scuser.query.filter_by(login_id=form.login_id.data, tenant_id=ssctenant.id).first()

            if user:
                # 비밀번호 비교
                if not check_password_hash(user.login_pwd, form.login_pwd.data):
                    flash('비밀번호가 잘못 되었습니다.')
                else:
                    # 정상 로그인 - 세션
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
    aday = time.localtime().tm_mday
    return days[aday - 1]
