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
            .success(function(data) {
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


                     <input type="checkbox" id="checkbox" class="peer leave resposiveTd mediaTable">
             </td>

             <td class='mediaTable mediaTableTbodyTd'>
                <div class="form-group">
                     <input type="text" class="form-control leave resposiveTd mediaTable" id="tvisitor"  >
                 </div>
             </td>

             <td class='mediaTable mediaTableTbodyTd'>
                 <div class="form-group">
                     <input type="text" id="tphone"  class="form-control leave ctphone resposiveTd mediaTable">
                 </div>
             </td>

             <td class='mediaTable mediaTableTbodyTd'>
                <div class="form-group mediaTable" >
                         <select id="" name="" class="form-control leave resposiveTd resposiveSelect mediaTable" style='width:130px'>
                                ${str}
                         </select>
                 </div>
             </td>
             <td class='mediaTable mediaTableTbodyTd'><input type="text" class="form-control leave resposiveTd mediaTable"></td>
             `

        for (var i = 0; i < dataSet.length; i++) {
            var obj = dataSet[i];
            var type = obj.rule_type;
            var ruleName = obj.rule_name;
            var cnt = i + 1;

            theadContext = theadContext + `<th style="">${ruleName}</th>`;
            ruleList.push(ruleName);


            if (type == '텍스트') {
                append = append + `<td class='mediaTable mediaTableTbodyTd'><input type="text" class="form-control rule-text leave resposiveTd mediaTable" rule=${ruleName}></td>`
            } else if (type == '달력') {
                append = append + `<td class='mediaTable mediaTableTbodyTd'>
                                       <div class="input-group resposiveTd">
                                       <i class="ti-calendar mT-5 p-5"></i>
                                       <input type="text" class="form-control start-date rule-calendar leave rule" placeholder="달력" data-provide="datepicker" name ="inout_sdate"  rule=${ruleName} readonly style="background-color:white">
                                       </div>
                                    </td> `
            } else if (type == '파일') {
               var uuid = 'applyFile'+uuidv4();

                append = append +
                    `<td class='mediaTable mediaTableTbodyTd'>
                        <div class="input-group custom-file resposiveTd">
                            <input id=${uuid} accept="image/*,video/*" type="file" class="form-control file rule-file leave file-upload rule custom-file-input"  data-browse-on-zone-click="true" rule=${ruleName}>
                            <label class="custom-file-label" for=${uuid}>파일선택</label>
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
    function sccompSearchHandler(dataSet){
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
        var msg = '';
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
                if(dataSet.length-1==i){
                    msg = msg + rule_name;
                }else{
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
            msg = msg + '의 유효기간이 만료되었습니다.';
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

         if(msg[0].msg=='-1'){
                 $("#alertModal").show();
                 $("#modalContent").text('');
                 $("#modalContent").text('다른 사용자와 휴대폰번호가 중복됩니다.');
                return;
            }

        if (msg[0].msg=='0') {
            //empty user
//            console.log('------userSearchHandler(사용자없음)----------------------')
            option.closest('tr').children().eq(-1).attr('is-user', '0'); //신규 user
//            console.log('------userSearchHandler----------------------')
        } else {
//            console.log('------userSearchHandler(사용자 있음)----------------------')
            option.closest('tr').children().eq(-1).attr('is-user', '1'); //등록 user
            apiCallPost(urlMake('RULE_VALID'), rulevalidHandler, dataSet, option);
//            console.log('------userSearchHandler----------------------')
        }
    }

    //텍스트업데이트 핸들러
    function textUpdateHandler(data, option) {

    }

    //캘린더업데이트 핸들러
    function calendarUpdateHandler(data, option) {}

    //사업장조회 핸들러
    function workspaceSearchHandler(data){
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

        $('#inout_location').on('change',function(){
            $('#interviewTbody').children().remove(); //Modal초기화
            var val = $('#inout_location').val()||'';
            var dataSet = {};
            if(val.length == 0)
                return;

            dataSet['code'] =$("#inout_location option:selected").attr('code');
            dataSet['code_nm'] =$("#inout_location option:selected").val();

            //출입문조회
            apiCallPost(urlMake('DOOR_SEARCH'), doorSearchHandler, dataSet);

        });


    }

    //출입문조회 핸들러
    function doorSearchHandler(data){
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
    function visitTypeSearchHandler(data){
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
                var ruleClass = ['rule-text','rule-calendar','rule-file'];

                for(var i=5; i<cellItem.length; i++){
                    var current = cellItem.eq(i);
                    var obj = {'ruleName':'','ruleDesc':'', 'ruleType':'', 'sDate': dataSet['inout_sdate'],'bucketUrl': ''};
                    obj.ruleName = current.attr('rule');
                    if(current.hasClass('rule-text')){
                        obj.ruleType = '텍스트';
                        obj.ruleDesc = current.val();

                    }else if(current.hasClass('rule-calendar')){
                        obj.ruleType = '달력';
                        date = current.val().split('/');
                        gb2 = date
                        obj.sDate = date[2] + "-" + date[0] + "-" + date[1]; //시작날짜

                    }else if(current.hasClass('rule-file')){
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
            console.log(check)
               if (check.length == 0) {
                $("#alertModal").show();
                $("#modalContent").text('');
                $("#modalContent").text('한 명 이상의 접견자를 추가해주세요');
                return;
            }


            //출입유효성 check
            $('#tableBody tr').each(function() {
                check = $(this).children().eq(-1).attr('is-valid')
                if (check == '0'){
                    $("#alertModal").show();
                    $("#modalContent").text('');
                    $("#modalContent").text('방문자의 출입유효성을 점검해주세요');
                }

            });

            if (check == '1')
                apiCallPost(urlMake('CREATE'), applyHandler, dataSet);

        });

        $('#addUser').click(function(e) {
            const $clone = $tableID.find('tbody tr').last().clone(true).removeClass('hide table-line');
            if ($tableID.find('tbody tr').length === 0) {
                $('#tableBody').append(newTr);

            } else {
                $tableID.find('tbody').last().append(newTr.replace(/applyFile/gi, 'applyFile'+uuidv4()));
            }

            $('.leave').focusout(function(e) {
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

                phone = phone.trim().replace(/[^0-9]/g,"");
                if(phone.length!=11){
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

                    if(itemObj.name.length==0 || itemObj.phone.length ==0)
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

                if (check){

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

            //캘린더규칙 업데이트
            $('.rule-calendar').focusout(function(e) {
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

            //파일업로드 업데이트
            $('.file-upload').change(function(e) {
                var current = $(this);
                var data = new FormData(); //파일객체 생성
                data.append("file", $(this).prop('files')[0]);
                var applicantName = $('#applicant_name').val() || ''; //신청자 이름
                var applicantPhone = $('#applicant_phone').val() || ''; //신청자 휴대폰번호
                var name = $(this).closest('tr').children().eq(1).children().children().val() || ''; //이름
                var phone = $(this).closest('tr').children().eq(2).children().children().val() || ''; //휴대폰번호
                var rule = $(this).attr('rule'); //규칙명

                if (applicantName.length == 0 || applicantPhone.length == 0 || name.length == 0 || phone.length == 0){
                   $("#alertModal").show();
                   $("#modalContent").text('');
                   $("#modalContent").text('신청자 정보를 입력해주세요');
                   return;
                }

                data.append('applicantName', applicantName);
                data.append('applicantPhone', applicantPhone);
                data.append('name', name);
                data.append('phone', phone);
                data.append('type', '파일');
                data.append('rule', rule);
                console.log('upload')
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
//                        console.log("ERROR : ", e);
                    }
                });
            });

        });

        $('#delUser').click(function(e) {
            var checkbox = $('input[id=checkbox]:checked'); //선택된 사용자

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
        $('.visitApply').click(function(e){
            $('#applyTbody').children().remove();
            $('#visitInput').val('');
        });

        //업체정보 테이블 초기화(HHJ)
        $('.visitApply2').click(function(e){
            $('#applyTbody2').children().remove();
            $('#visitInput2').val('');
        });



        //접견자정보 테이블 초기화
        $('.interviewInit').click(function(e){
            $('#interviewTbody').children().remove();
            $('#interviewInput').val('')

        });


        //alert 모달 close 이벤트
        $('#alertModal').click(function(e){
            $('#alertModal').hide();
        });


        //방문유형
        apiCallPost(urlMake('VISIT_TYPE'), visitTypeSearchHandler)

        //사업장조회
        apiCallPost(urlMake('WORKSPACE_SEARCH'), workspaceSearchHandler)


        var date = new Date();
        var year = date.getFullYear();
        var month = new String(date.getMonth()+1);
        var day = new String(date.getDate());


        var date2 = new Date();
        date2.setDate(date2.getDate() + 7);
        var year2 = date2.getFullYear();
        var month2 = new String(date2.getMonth()+1);
        var day2 = new String(date2.getDate());

        if (month.length == 1)
            month = '0' + month;

        if (day.length == 1)
            day = '0' + day;

        if (month2.length == 1)
            month2 = '0' + month2;

        if (day2.length == 1)
            day2 = '0' + day2;

        var sdate = month + "/" + day + "/" + year;
        var edate = month2 + "/" + day2 + "/" + year2;

        $('#inout_sdate').val(sdate);
        $('#inout_edate').val(edate);
    }

    init();
})