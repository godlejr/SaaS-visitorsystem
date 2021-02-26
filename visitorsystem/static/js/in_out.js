var ruleList = [];
var gb;
$(document).ready(function() {
    //URL에 해당하는 컨트롤러 호출
    function apiCallPost(url, handler, data, opt) {
        $.ajax({
                type: 'POST',
                url: url,
                async: false,
                cache: false,
                data: data
            })
            .done(function(data) {
                handler(data, opt);
            });
    }

    //type에 맞는 URL을 반환하는 함수
    function urlMake(url, args) {
        var reqUrl = "/inoutApply/";
        switch (url) {
            case 'CREATE':
                reqUrl = reqUrl + `create`;
                break;

            case 'INTERVIEW_SEARCH':
                reqUrl = reqUrl + `interview/search`;
                break;

            case 'RULE_SEARCH':
                reqUrl = reqUrl + `rule/search`;
                break;

            case 'RULE_VALID':
                reqUrl = reqUrl + `rule/valid`;
                break;

            case 'APPLY_SEARCH':
                reqUrl = reqUrl + `apply/search`;
                break;

            case 'COMP_SEARCH':
                reqUrl = reqUrl + `comp/search`;
                break;

            case 'USER_SEARCH':
                reqUrl = reqUrl + `user/search`;
                break;
            case 'TEXT_UPDATE':
                reqUrl = reqUrl + `rule/text/update`;
                break;

            case 'CALENDAR_UPDATE':
                reqUrl = reqUrl + `rule/calendar/update`;
                break;

            case 'WORKSPACE_SEARCH':
                reqUrl = reqUrl + `workspace/search`;
                break;

            case 'VISIT_TYPE':
                reqUrl = reqUrl + `visit/type`;
                break;

            case 'DOOR_SEARCH':
                reqUrl = reqUrl + `door/search`;
                break;

        }
        return reqUrl;
    }

    //random id반환
    function uuidv4() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0,
                v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    //규칙정보 컨트롤러(완료)
    function ruleSearchHandler(dataSet) {
        var temp = dataSet;
        var dataSet = temp.msg;
        var dataSet2 = temp.msg2;
        var theadContext = '';
        var append = '';
        var str = '';
        for (var i = 0; i < dataSet2.length; i++) {
            var code_nm = dataSet2[i].code_nm;
            var temp = `<option value=${code_nm}>${code_nm}</option>`
            str = str + temp;
        }

        newTr = `
         <tr class="hide mediaTable mediaTableTbodyTr">
             <td class='mediaTable mediaTableTbodyTd' valueChange = '0'>
                     <input type="checkbox" class="checkbox peer leave resposiveTd mediaTable">
             </td>

             <td class='mediaTable mediaTableTbodyTd'>
                <div class="form-group">
                     <input type="text" class="form-control leave resposiveTd mediaTable" >
                 </div>
             </td>

             <td class='mediaTable mediaTableTbodyTd'>
                 <div class="form-group">
                     <input type="text" class="form-control leave ctphone resposiveTd mediaTable numberValid">
                 </div>
             </td>

             <td class='mediaTable mediaTableTbodyTd'>
                <div class="form-group mediaTable" >
                         <select class="form-control leave resposiveTd resposiveSelect mediaTable carCheck" style='width:130px'>
                                ${str}
                         </select>
                 </div>
             </td>
             <td class='mediaTable mediaTableTbodyTd'><input type="text" class="form-control leave resposiveTd mediaTable " style="background-color:white" readonly></td>
             `

        for (var i = 0; i < dataSet.length; i++) {
            var obj = dataSet[i];
            var type = obj.rule_type;
            var ruleName = obj.rule_name;
            var cnt = i + 1;

            theadContext = theadContext + `<th style="">${ruleName}</th>`;
            ruleList.push(ruleName);

            if (type == '텍스트') {

                append = append + `<td class='mediaTable mediaTableTbodyTd'><input type="text" class="form-control rule-text leave resposiveTd mediaTable is-invalid"  rule=${ruleName}></td>`
            } else if (type == '달력') {

                append = append + `<td class='mediaTable mediaTableTbodyTd'>
                                       <div class="input-group resposiveTd">
                                       <i class="ti-calendar mT-5 p-5"></i>
                                       <input type="text" class="form-control start-date rule-calendar rule datepicker is-invalid" placeholder="달력" name ="inout_sdate"  rule=${ruleName} readonly style="background-color:white">
                                       </div>
                                    </td> `
            } else if (type == '파일') {

                var uuid = 'applyFile' + uuidv4();

                append = append +
                    `<td class='mediaTable mediaTableTbodyTd'>
                        <div class="input-group custom-file resposiveTd">
                            <input id=${uuid} accept="image/*,video/*" type="file" class="leave form-control file rule-file file-upload rule custom-file-input is-invalid"   data-browse-on-zone-click="true" rule=${ruleName}>
                            <label class="custom-file-label " for=${uuid}>파일선택</label>
                        </div>
                         <a href ='' target="_new" class='' hidden>다운로드</a>
                    </td>`
            }
        }

        $('#thead').append(theadContext);
        append = append + `<td class='mediaTable mediaTableTbodyTd'style="visibility:hidden" is-valid="0" is-user="0"></td>`
        newTr = newTr + append + '</tr>';
    }

    //출입신청 컨트롤러(완료)
    function applyHandler(dataSet) {
        $("#alertModal").show();
        $("#modalContent").text('');
        $("#modalContent").text('출입신청이 성공적으로 이뤄졌습니다.');
        $(location).attr('href', '/')


    }

    //신청자조회 컨트롤러(완료)
    function applySearchHandler(dataSet) {
        dataSet = dataSet.msg
        var str = ''
        for (var i = 0; i < dataSet.length; i++) {
            var name = dataSet[i].name;
            var phone = dataSet[i].phone;
            var comp_nm = dataSet[i].comp_nm;
            var biz_no = dataSet[i].biz_no;
            $('#applyTbody').children().remove();
            var temp = `<tr class='applyTtr'>
                                 <th scope="row">${i+1}</th>
                                 <td>${name}</td>
                                 <td>${phone}</td>
                                 <td>${comp_nm}</td>
                                 <td>${biz_no}</td>
                            </tr>`;
            str += temp;
        }

        $('#applyTbody').append(str);
        $('.applyTtr').click(function() {
            $('#applicant_name').val($(this).children('td:eq(0)').text());
            $('#applicant_phone').val($(this).children('td:eq(1)').text());
            $('#applicant_comp_nm').val($(this).children('td:eq(2)').text());
            $('#applicant_biz_no').val($(this).children('td:eq(3)').text());

        });

    }

    //업체조회(HHJ)
    function sccompSearchHandler(dataSet) {
        dataSet = dataSet.msg
        var str = ''
        for (var i = 0; i < dataSet.length; i++) {
            var name = dataSet[i].name;
            var phone = dataSet[i].phone;
            var comp_nm = dataSet[i].comp_nm;
            var biz_no = dataSet[i].biz_no;
            $('#applyTbody2').children().remove();
            var temp = `<tr class='applyTtr2'>
                                 <th scope="row">${i+1}</th>
                                 <td>${name}</td>
                                 <td>${phone}</td>
                                 <td>${comp_nm}</td>
                                 <td>${biz_no}</td>
                            </tr>`;
            str += temp;
        }

        $('#applyTbody2').append(str);
        $('.applyTtr2').click(function() {
            $('#applicant_name').val($(this).children('td:eq(0)').text());
            $('#applicant_phone').val($(this).children('td:eq(1)').text());
            $('#applicant_comp_nm').val($(this).children('td:eq(2)').text());
            $('#applicant_biz_no').val($(this).children('td:eq(3)').text());

        });

    }

    //감독자조회 컨트롤러
    function interViewSearchHandler(dataSet) {
        dataSet = dataSet.msg
        var str = ''
        $('#interviewTbody').children().remove()
        for (var i = 0; i < dataSet.length; i++) {
            var dept_nm = dataSet[i].dept_nm;
            var name = dataSet[i].name;
            var phone = dataSet[i].phone;

            var temp = `<tr class='interviewTtr'>
                                 <th scope="row">${i+1}</th>
                                 <td>${dept_nm}</td>
                                 <td>${name}</td>
                                 <td>${phone}</td>
                            </tr>`;

            str += temp;
        }

        $('#interviewTbody').append(str);
        $('.interviewTtr').click(function() {
            $('#interviewer_dept').val($(this).children('td:eq(0)').text());
            $('#interviewer_name').val($(this).children('td:eq(1)').text());
            $('#interviewer_phone').val($(this).children('td:eq(2)').text());

        });
    }

    //규칙검증 컨트롤러(완료)
    function rulevalidHandler(dataSet, opt) {
        var dataSet = dataSet.msg; //데이터 송신값
        var msg = opt.name+"님의 ";
        var check = false;
        var rule = opt.closest('tr').children();
        var offset = 5;

        for (var i = 0; i < dataSet.length; i++) {
            var rule_name = dataSet[i].rule_name; //규칙이름
            var rule_desc = dataSet[i].rule_desc; //규칙명세
            var rule_type = dataSet[i].rule_type; //규칙유형
            var rule_textDesc = dataSet[i].text_desc; //텍스트 속성
            var rule_sdate = dataSet[i].s_date; //달력 속성
            var rule_bucketUrl = dataSet[i].bucketUrl; //버킷 속성
            var state = dataSet[i].state; //규칙검증상태
            var nextRule = rule.eq(offset + i); //다음 규칙 검색
            var writeCheck = rule.eq(0).attr('valueChange'); //값을 불러왔는지 여부check



            //state 상태체크
            if (!state) { //remove, Rule False(Rule 무효인 상태)
                if (dataSet.length - 1 == i) {
                    msg = msg + rule_name;
                } else {
                    msg = msg + rule_name + " ";
                }
                check = true;
                if (rule_type == '달력') {
                    nextRule.children().children('input').addClass('is-invalid');
                } else if (rule_type == '텍스트') {
                    nextRule.children().addClass('is-invalid');
                } else if (rule_type == '파일') {
                    nextRule.children().next().attr('hidden', true)
                    nextRule.children().children('input').addClass('is-invalid');
                }

            } else { //add, Rule True(Rule이 유효한 상태)
                if (rule_type == '달력') {
                    nextRule.children().children('input').removeClass('is-invalid');
                    if (writeCheck == '0') {
                        var date = rule_sdate.split('-') //달력
                        result = date[1] + "/" + date[2] + "/" + date[0];
                        nextRule.children().children('input').val(result);
                    }
                } else if (rule_type == '텍스트') {
                    nextRule.children().removeClass('is-invalid');
                    if (writeCheck == '0')
                        nextRule.children().val(rule_textDesc); //텍스트

                } else if (rule_type == '파일') {
                    nextRule.children().next().removeAttr('hidden');
                    nextRule.children().children('input').removeClass('is-invalid');

                    if (writeCheck == '0')
                        nextRule.children().next().attr('href', rule_bucketUrl); //버킷 url 매핑
                }
            }
        }

        if (writeCheck == '0') {
            rule.eq(0).attr('valueChange', '1');
        }

        if (check) {
            msg = msg + '의 유효기간이 만료입니다.';
            rule.eq(-1).attr("is-valid", "0"); //0은 검증X
            $('#errorMsg').text(msg);

        } else {
            rule.eq(-1).attr("is-valid", "1"); //1은 검증0
            $('#errorMsg').text('');
        }
    }


    //감독자조회 컨트롤러
    function interviewSearchHandler(dataSet) {
        dataSet = dataSet.msg
        var str = '';
    }

    //차량조회 컨트롤러
    function carSearchHandler(dataSet) {
        dataSet = dataSet.msg
        var str = '';
        for (var i = 0; i < dataSet.length; i++) {
            var code_nm = dataSet[i].code_nm;
            var temp = `<option value=${code_nm}>${code_nm}</option>`
            str = str + temp;
        }
        return str;
    }

    //사용자검색 핸들러
    function userSearchHandler(data, option) {
        var msg = data.msg; //post 결과메시지
        var dataSet = option.dataSet;

        if (msg[0].msg == '-1') {
            $("#alertModal").show();
            $("#modalContent").text('');
            $("#modalContent").text('다른 사용자와 휴대폰번호가 중복됩니다.');
            return;
        }

        if (msg[0].msg == '0') {
            //empty user
            option.closest('tr').children().eq(-1).attr('is-user', '0'); //신규 user

        } else {
            option.closest('tr').children().eq(-1).attr('is-user', '1'); //등록 user
            option.name = dataSet['name'];
            apiCallPost(urlMake('RULE_VALID'), rulevalidHandler, dataSet, option);
        }
    }

    //텍스트업데이트 핸들러
    function textUpdateHandler(data, option) {

    }

    //캘린더업데이트 핸들러
    function calendarUpdateHandler(data, option) {}

    //사업장조회 핸들러
    function workspaceSearchHandler(data) {
        var save = data;
        data = save.msg;
        data2 = save.msg2;

        var str = '';
        for (var i = 0; i < data.length; i++) {
            var code_nm = data[i].code_nm
            var code = data[i].code
            var temp = `<option code = ${code} value=${code_nm}>${code_nm}</option>`
            str = str + temp;
        }

        $('#inout_location').append(str);

        str = '';
        for (var i = 0; i < data2.length; i++) {
            var code_nm = data2[i].code_nm
            var code = data2[i].code
            var temp = `<option code = ${code} value=${code_nm}>${code_nm}</option>`
            str = str + temp;
        }

        $('#inout_location2').append(str);

        $('#inout_location').on('change', function() {
            $('#interviewTbody').children().remove(); //Modal초기화
            var val = $('#inout_location').val() || '';
            var dataSet = {};
            if (val.length == 0)
                return;

            dataSet['code'] = $("#inout_location option:selected").attr('code');
            dataSet['code_nm'] = $("#inout_location option:selected").val();

            //출입문조회
            apiCallPost(urlMake('DOOR_SEARCH'), doorSearchHandler, dataSet);

        });


    }

    //출입문조회 핸들러
    function doorSearchHandler(data) {
        data = data.msg;
        var str = '';
        $('#inout_location2').empty();

        for (var i = 0; i < data.length; i++) {
            var code_nm = data[i].code_nm
            var code = data[i].code
            var temp = `<option code = ${code} value=${code_nm}>${code_nm}</option>`
            str = str + temp;
        }
        $('#inout_location2').append(str);



    }

    //방문유형조회 핸들러
    function visitTypeSearchHandler(data) {
        var data = data.msg;
        var str = '';

        for (var i = 0; i < data.length; i++) {
            var code_nm = data[i].code_nm
            var temp = `<option value=${code_nm}>${code_nm}</option>`
            str = str + temp;
        }
        $('#inout_purpose_type').append(str);

    }



    //event리스너
    function init() {
        const $tableID = $('#table');
        apiCallPost(urlMake('RULE_SEARCH'), ruleSearchHandler);

        $('#appylbtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['applicant_name', 'applicant_phone', 'applicant_biz_no', 'applicant_comp_nm',
                'interviewer_dept', 'interviewer_name', 'interviewer_phone',
                'inout_sdate', 'inout_edate',
                'inout_purpose_type', 'inout_title', 'inout_location', 'inout_location2',
                'inout_purpose_desc', 'visitors'
            ]


            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
                if (key == "visitors")
                    break;

                if (key == 'inout_sdate' || key == 'inout_edate') {
                    var str = $('#' + key).val();
                    var date = str.split('/')
                    var year = date[2]; //년
                    var month = date[0]; //월
                    var day = date[1]; //일
                    dataSet[key] = year + "-" + month + "-" + day;
                    continue;
                }
                var value = $('#' + key).val()
                dataSet[key] = value;
            }

            var lists = [];

            //visitors설정
            $('#tableBody tr').each(function() {
                var cellItem = $(this).find(":input")
                var itemObj = new Object()
                itemObj.name = cellItem.eq(1).val()
                itemObj.phone = cellItem.eq(2).val()
                itemObj.carType = cellItem.eq(3).val()
                itemObj.carNum = cellItem.eq(4).val()
                itemObj.rule = [];
                var ruleClass = ['rule-text', 'rule-calendar', 'rule-file'];

                for (var i = 5; i < cellItem.length; i++) {
                    var current = cellItem.eq(i);
                    var obj = {
                        'ruleName': '',
                        'ruleDesc': '',
                        'ruleType': '',
                        'sDate': dataSet['inout_sdate'],
                        'bucketUrl': ''
                    };
                    obj.ruleName = current.attr('rule');
                    if (current.hasClass('rule-text')) {
                        obj.ruleType = '텍스트';
                        obj.ruleDesc = current.val();

                    } else if (current.hasClass('rule-calendar')) {
                        obj.ruleType = '달력';
                        date = current.val().split('/');
                        gb2 = date
                        obj.sDate = date[2] + "-" + date[0] + "-" + date[1]; //시작날짜

                    } else if (current.hasClass('rule-file')) {
                        obj.ruleType = '파일';
                        obj.bucketUrl = current.parent().next().attr('href');
                    }
                    itemObj.rule.push(obj)
                }

                lists.push(itemObj);
            });



            //출입지역 code
            dataSet["inout_location_code"] = $("#inout_location option:selected").attr('code')
            dataSet["inout_location_code2"] = $("#inout_location2 option:selected").attr('code')
            dataSet["visitors"] = JSON.stringify(lists);

            //신청자 정보 check
            var check = dataSet['applicant_name'];
            var check2 = dataSet['applicant_biz_no'];

            if (check.length == 0 || check2.length == 0) {
                $("#alertModal").show();
                $("#modalContent").text('');
                $("#modalContent").text('신청자 정보를 입력해주세요');
                return;
            }

            //출입 정보 check
            var check = dataSet['inout_title'];

            if (check.length == 0) {
                $("#alertModal").show();
                $("#modalContent").text('');
                $("#modalContent").text('방문목적을 입력해주세요');
                return;
            }

            //접견자 정보 check
            check = dataSet['interviewer_name'];
            if (check.length == 0) {
                $("#alertModal").show();
                $("#modalContent").text('');
                $("#modalContent").text('접견자 정보를 입력해주세요');
                return;
            }

            //출입자 정보 check
            check = $('#tableBody tr').length;
            if (check == 0) {
                $("#alertModal").show();
                $("#modalContent").text('');
                $("#modalContent").text('한 명 이상의 접견자를 추가해주세요');
                return;
            }



            //출입자 정보 check
            check = $('#tableBody tr').length;

            if (check.length == 0) {
                $("#alertModal").show();
                $("#modalContent").text('');
                $("#modalContent").text('한 명 이상의 접견자를 추가해주세요');
                return;
            }


            //출입유효성 check
            $('#tableBody tr').each(function() {
                check = $(this).children().eq(-1).attr('is-valid')
                if (check == '0') {
                    $("#alertModal").show();
                    $("#modalContent").text('');
                    $("#modalContent").text('방문자의 출입유효성을 점검해주세요');
                }
            });

            if (check == '1')
                apiCallPost(urlMake('CREATE'), applyHandler, dataSet);

        });

        $('#addUser').click(function(e) {
            var applicantName = $('#applicant_name').val() || ''; //신청자 이름
            var applicantPhone = $('#applicant_phone').val() || ''; //신청자 휴대폰번호


            if (applicantName.length == 0 || applicantPhone.length == 0) {
                $("#alertModal").show();
                $("#modalContent").text('');
                $("#modalContent").text('신청자 정보를 입력해주세요');
                return;
            }



            const $clone = $tableID.find('tbody tr').last().clone(true).removeClass('hide table-line');
            if ($tableID.find('tbody tr').length === 0) {
                $('#tableBody').append(newTr);

            } else {
                $tableID.find('tbody').last().append(newTr.replace(/applyFile/gi, 'applyFile' + uuidv4()));
            }



            //캘린더 업데이트 컨트롤러
            $('.datepicker').datepicker({
                format: "mm/dd/yyyy", //데이터 포맷 형식(yyyy : 년 mm : 월 dd : 일 )
                endDate: $('#inout_sdate').val(), //달력에서 선택 할 수 있는 가장 느린 날짜. 이후로 선택 불가 ( d : 일 m : 달 y : 년 w : 주)
                autoclose: true, //사용자가 날짜를 클릭하면 자동 캘린더가 닫히는 옵션
                clearBtn: false, //날짜 선택한 값 초기화 해주는 버튼 보여주는 옵션 기본값 false 보여주려면 true
                disableTouchKeyboard: false, //모바일에서 플러그인 작동 여부 기본값 false 가 작동 true가 작동 안함.
                immediateUpdates: false, //사용자가 보는 화면으로 바로바로 날짜를 변경할지 여부 기본값 :false
                templates: {
                    leftArrow: '&laquo;',
                    rightArrow: '&raquo;'
                }, //다음달 이전달로 넘어가는 화살표 모양 커스텀 마이징
                showWeekDays: true, // 위에 요일 보여주는 옵션 기본값 : true
                todayHighlight: true, //오늘 날짜에 하이라이팅 기능 기본값 :false
            }).on("changeDate", function(selected) {
                selected.stopImmediatePropagation();
                var name = $(this).closest('tr').children().eq(1).children().children().val() || ''; //이름
                var phone = $(this).closest('tr').children().eq(2).children().children().val() || ''; //휴대폰번호
                var rule = $(this).attr('rule'); //규칙이름
                var calendar = $(this).val() || ''; //달력

                if (name.length == 0 || phone.length == 0 || calendar.length == 0)
                    return;

                var dataSet = {};
                dataSet['name'] = name;
                dataSet['phone'] = phone;
                dataSet['rule'] = rule;
                dataSet['type'] = '캘린더';
                calendar = calendar.split('/')
                dataSet['calendar'] = calendar[2] + "-" + calendar[0] + "-" + calendar[1];
                apiCallPost(urlMake('CALENDAR_UPDATE'), calendarUpdateHandler, dataSet);
            });

            // 숫자 유효성 판별
            $(".numberValid").on('keydown', function(e) {
                e.stopImmediatePropagation();
                // 숫자만 입력받기
                var trans_num = $(this).val().replace(/-/gi, '');
                var k = e.keyCode;


                if (trans_num.length >= 11 && ((k >= 48 && k <= 126) || (k >= 12592 && k <= 12687 || k == 32 || k == 229 || (k >= 45032 && k <= 55203)))) {
                    e.preventDefault();
                }
            }).on('blur', function(e) { // 포커스를 잃었을때 실행합니다.

                if ($(this).val() == '') return;

                // 기존 번호에서 - 를 삭제합니다.
                var trans_num = $(this).val().replace(/-/gi, '');

                // 입력값이 있을때만 실행합니다.
                if (trans_num != null && trans_num != '') {
                    // 총 핸드폰 자리수는 11글자이거나, 10자여야 합니다.
                    if (trans_num.length == 11 || trans_num.length == 10) {
                        // 유효성 체크
                        var regExp_ctn = /^(01[016789]{1}|02|0[3-9]{1}[0-9]{1})([0-9]{3,4})([0-9]{4})$/;
                        if (regExp_ctn.test(trans_num)) {
                            // 유효성 체크에 성공하면 하이픈을 넣고 값을 바꿔줍니다.
                            trans_num = trans_num.replace(/^(01[016789]{1}|02|0[3-9]{1}[0-9]{1})-?([0-9]{3,4})-?([0-9]{4})$/, "$1-$2-$3");
                            $(this).val(trans_num);
                        } else {
                                $(this).val("");
                                $(this).focus();
                                $("#alertModal").show();
                                $("#modalContent").text('');
                                $("#modalContent").text('유효하지 않은 전화번호 입니다.');
                                validCheck($(this))//HHJ
                        }


                    } else {
                                $(this).val("");
                                $(this).focus();
                                $("#alertModal").show();
                                $("#modalContent").text('');
                                $("#modalContent").text('유효하지 않은 전화번호 입니다.');
                                validCheck($(this))//HHJ
                    }
                }
            });

            //HHJ
            function validCheck(select) {
                var checkSize = ruleList.length + 2; //
                var target = $(select).closest('tr').children().next();
                var offset = 2;
                gb = target;

                for (var i = 0; i < checkSize; i++) {
                    var currentTarget = target.eq(i + offset); //다음 규칙 검색

                    if(i==0){//차량번호
                        currentTarget.children().children().val('차량없음').prop("selected",true);
                    }else if(i==1){//차량종류

                        currentTarget.children('input').attr('readonly',true);
                    }

                    if (currentTarget.children('input').hasClass('rule-text')) {//텍스트
                        currentTarget.children('input').val('');
                        currentTarget.children('input').addClass('is-invalid');//invalid 적용



                    } else if (currentTarget.children().children('input').hasClass('rule-calendar')) {//캘린더
                        currentTarget.children().children('input').val('');
                        currentTarget.children().children('input').addClass('is-invalid');//invalid 적용

                    } else if (currentTarget.children().children('input').hasClass('rule-file')) {//파일
                        currentTarget.children().next().attr('href','');
                        currentTarget.children().next().attr('hidden', true)
                        currentTarget.children().children('input').addClass('is-invalid');//invalid 적용


                    }
                }
                $(select).closest('tr').children().eq(0).attr('valueChange','0');//규칙 값 변경 활상화
                target.eq(-1).attr('is-valid','0');//유효하지 않는 상태
                target.eq(-1).attr('is-user','0');//사용자가 존재하는 상태


            }

                //HHJ
            $('.carCheck').change(function(e){
                e.stopImmediatePropagation();
                var value = $(this).val();
                if(value=='차량없음'){
                   $(this).parent().parent().next().children().attr('readonly',true);
                }else{
                    $(this).parent().parent().next().children().attr('readonly',false);
                }
            })




            $('.leave').blur(function(e) {
                e.stopImmediatePropagation();
                var sdate = $('#inout_sdate').val() || ''; //시작날짜
                var edate = $('#inout_edate').val() || ''; //종료날짜
                var name = $(this).closest('tr').children().eq(1).children().children().val() || ''; //이름
                var phone = $(this).closest('tr').children().eq(2).children().children().val() || ''; //휴대폰번호
                var regExp = /^01(?:0|1|[6-9])-(?:\d{3}|\d{4})-\d{4}$/; //정규표현식
                var check = false; //정규표현식 판별
                var option;
                var dataSet = {};

                if (sdate.length == 0 || edate.length == 0) //날짜가 입력되지 않으면, event가 발생하지 않음
                    return;
                if (name.length == 0 || phone.length == 0) //사용자이름, 핸드폰번호가 입력되지 않으면, event 발생하지 않음
                    return;

                phone = phone.trim().replace(/[^0-9]/g, "");
                if (phone.length != 11) {
                    return;
                }

                phone = phone.trim().replace(/(^02.{0}|^01.{1}|[0-9]{3})([0-9]+)([0-9]{4})/, "$1-$2-$3"); //핸드폰번호 정규표현식 적용
                check = regExp.test(phone); //휴대폰번호에 대한 정규표현식 검증
                if (!check) //정규표현식 결과과 false면, event 발생하지 않음
                    return;

                $(this).closest('tr').children().eq(2).children().children().val(phone); //핸드폰번호에 대한 정규표현식 적용

                var key = {};
                var check = false;
                $('#tableBody tr').each(function() {
                    var cellItem = $(this).find(":input")
                    var itemObj = new Object()
                    itemObj.name = cellItem.eq(1).val()
                    itemObj.phone = cellItem.eq(2).val()

                    if (itemObj.name.length == 0 || itemObj.phone.length == 0)
                        return;

                    var combination = itemObj.name + itemObj.phone;

                    if (key[combination]) {
                        $("#alertModal").show();
                        $("#modalContent").text('');
                        $("#modalContent").text('이미 추가한 사용자 입니다.');
                        $(this).closest('tr').children().eq(1).children().children().val('');
                        $(this).closest('tr').children().eq(2).children().children().val('');
                        check = true;
                        return;
                    } else {
                        key[combination] = true;
                    }
                });

                if (check) {
                    return;
                }
                sdate = sdate.split('/');
                edate = edate.split('/');
                dataSet['sdate'] = sdate[2] + "-" + sdate[0] + "-" + sdate[1]; //시작날짜
                dataSet['edate'] = edate[2] + "-" + edate[0] + "-" + edate[1]; //종료날짜
                dataSet['name'] = name; //사용자
                dataSet['phone'] = phone; //휴대폰번호
                option = $(this);
                option.dataSet = dataSet;
                apiCallPost(urlMake('USER_SEARCH'), userSearchHandler, dataSet, option);

            });

            //텍스트규칙 업데이트
            $('.rule-text').focusout(function(e) {
                e.stopImmediatePropagation();
                var name = $(this).closest('tr').children().eq(1).children().children().val() || ''; //이름
                var phone = $(this).closest('tr').children().eq(2).children().children().val() || ''; //휴대폰번호
                var rule = $(this).attr('rule'); //규칙속성 가져오기
                var ruleText = $(this).val() || ''; //현재 규칙(텍스트)값 가져오기


                if (name.length == 0 || phone.length == 0 || ruleText.length == 0)
                    return;

                var dataSet = {};
                dataSet['name'] = name;
                dataSet['phone'] = phone;
                dataSet['rule'] = rule;
                dataSet['ruleText'] = ruleText;
                dataSet['type'] = '텍스트';

                apiCallPost(urlMake('TEXT_UPDATE'), textUpdateHandler, dataSet);

            });



            //파일업로드 업데이트
            $('.file-upload').change(function(e) {
                e.stopImmediatePropagation();
                var current = $(this);
                var data = new FormData(); //파일객체 생성
                data.append("file", $(this).prop('files')[0]);
                var applicantName = $('#applicant_name').val() || ''; //신청자 이름
                var applicantPhone = $('#applicant_phone').val() || ''; //신청자 휴대폰번호
                var name = $(this).closest('tr').children().eq(1).children().children().val() || ''; //이름
                var phone = $(this).closest('tr').children().eq(2).children().children().val() || ''; //휴대폰번호
                var rule = $(this).attr('rule'); //규칙명

                if (applicantName.length == 0 || applicantPhone.length == 0) {
                    $("#alertModal").show();
                    $("#modalContent").text('');
                    $("#modalContent").text('신청자 정보를 입력해주세요');
                    return;
                }

                if(name.length == 0 || phone.length == 0){
                    $("#alertModal").show();
                    $("#modalContent").text('');
                    $("#modalContent").text('방문자 정보를 입력해주세요');
                    return;

                }

                data.append('applicantName', applicantName);
                data.append('applicantPhone', applicantPhone);
                data.append('name', name);
                data.append('phone', phone);
                data.append('type', '파일');
                data.append('rule', rule);

                $.ajax({
                    type: "POST",
                    enctype: 'multipart/form-data',
                    url: "/inoutApply/rule/file/upload",
                    data: data,
                    processData: false,
                    contentType: false,
                    cache: false,
                    timeout: 600000,
                    success: function(result) {
                        var href = result.msg;
                        current.parent().next().attr('hidden', false);
                        current.parent().next().attr('href', href);
                    },

                    error: function(e) {

                    }
                });
            });

        });

        //삭제버튼
        $('#delUser').click(function(e) {
            var checkbox = $('input.checkbox:checked'); //선택된 사용자

            checkbox.each(function(i) { //선택된 사용자 삭제
                var tr = checkbox.parent().parent().eq(i);
                var td = tr.children();
                setTimeout(function() {
                    tr.remove();
                }, 100);

            });

        });

        //신청자조회 모달
        $('#visitSearchView').click(function(e) {
            var dataSet = {};
            var visitInput = $('#visitInput').val();
            dataSet['visitInput'] = visitInput;

            apiCallPost(urlMake('APPLY_SEARCH'), applySearchHandler, dataSet)
        });

        //업체조회 모달(HHJ)
        $('#visitSearchView2').click(function(e) {
            var dataSet = {};
            var compsearchinput = $('#visitInput2').val();
            dataSet['compSearchInput'] = compsearchinput;

            apiCallPost(urlMake('COMP_SEARCH'), sccompSearchHandler, dataSet)
        });

        //접견자조회 모달
        $('#interviewSearch').click(function(e) {
            var dataSet = {};
            var interviewName = $('#interviewInput').val();
            dataSet['interviewName'] = interviewName;
            dataSet['site_nm'] = $('#inout_location').val();
            apiCallPost(urlMake('INTERVIEW_SEARCH'), interViewSearchHandler, dataSet)

        });


        //신청자정보 테이블 초기화
        $('.visitApply').click(function(e) {
            $('#applyTbody').children().remove();
            $('#visitInput').val('');
        });

        //업체정보 테이블 초기화(HHJ)
        $('.visitApply2').click(function(e) {
            $('#applyTbody2').children().remove();
            $('#visitInput2').val('');
        });

        //접견자정보 테이블 초기화
        $('.interviewInit').click(function(e) {
            $('#interviewTbody').children().remove();
            $('#interviewInput').val('')

        });

        //alert 모달 close 이벤트
        $('#alertModal').click(function(e) {
            $('#alertModal').hide();
        });

        //방문유형
        apiCallPost(urlMake('VISIT_TYPE'), visitTypeSearchHandler)

        //사업장조회
        apiCallPost(urlMake('WORKSPACE_SEARCH'), workspaceSearchHandler)
        // set default dates
        var start = new Date();
        // set end date to max one year period:
        var end = new Date(new Date().setYear(start.getFullYear() + 1));

        //from~to적용
        $('#inout_sdate').datepicker({
            format: "mm/dd/yyyy", //데이터 포맷 형식(yyyy : 년 mm : 월 dd : 일 )
            startDate: '0d', //달력에서 선택 할 수 있는 가장 빠른 날짜. 이전으로는 선택 불가능 ( d : 일 m : 달 y : 년 w : 주)
            autoclose: true, //사용자가 날짜를 클릭하면 자동 캘린더가 닫히는 옵션
            clearBtn: false, //날짜 선택한 값 초기화 해주는 버튼 보여주는 옵션 기본값 false 보여주려면 true
            disableTouchKeyboard: false, //모바일에서 플러그인 작동 여부 기본값 false 가 작동 true가 작동 안함.
            immediateUpdates: false, //사용자가 보는 화면으로 바로바로 날짜를 변경할지 여부 기본값 :false
            templates: {
                leftArrow: '&laquo;',
                rightArrow: '&raquo;'
            }, //다음달 이전달로 넘어가는 화살표 모양 커스텀 마이징
            showWeekDays: true, // 위에 요일 보여주는 옵션 기본값 : true
            todayHighlight: true, //오늘 날짜에 하이라이팅 기능 기본값 :false
        }).on("changeDate", function(selected) {
            startDate = new Date(selected.date.valueOf());
            $('#inout_edate').datepicker('setStartDate', startDate);
            $('.datepicker').datepicker('setEndDate', startDate);
        });

        $('#inout_edate').datepicker({
            format: "mm/dd/yyyy", //데이터 포맷 형식(yyyy : 년 mm : 월 dd : 일 )
            startDate: '0d', //달력에서 선택 할 수 있는 가장 빠른 날짜. 이전으로는 선택 불가능 ( d : 일 m : 달 y : 년 w : 주)
            autoclose: true, //사용자가 날짜를 클릭하면 자동 캘린더가 닫히는 옵션
            clearBtn: false, //날짜 선택한 값 초기화 해주는 버튼 보여주는 옵션 기본값 false 보여주려면 true
            disableTouchKeyboard: false, //모바일에서 플러그인 작동 여부 기본값 false 가 작동 true가 작동 안함.
            immediateUpdates: false, //사용자가 보는 화면으로 바로바로 날짜를 변경할지 여부 기본값 :false
            templates: {
                leftArrow: '&laquo;',
                rightArrow: '&raquo;'
            }, //다음달 이전달로 넘어가는 화살표 모양 커스텀 마이징
            showWeekDays: true, // 위에 요일 보여주는 옵션 기본값 : true
            todayHighlight: true, //오늘 날짜에 하이라이팅 기능 기본값 :false
        }).on("changeDate", function(selected) {
            startDate = new Date(selected.date.valueOf());
            $('#inout_sdate').datepicker('setEndDate', startDate);
        });

    }
    init();
})