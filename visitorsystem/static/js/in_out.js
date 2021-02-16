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

        }
        return reqUrl;
    }

    //규칙정보 컨트롤러
    function ruleSearchhandler(dataSet) {
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
             <td class='mediaTable mediaTableTbodyTd' valueChange = '0' ::before='wow'>
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
                         <select id="" name="" class="form-control leave resposiveTd resposiveSelect mediaTable">
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
            var cnt = i+1;

            theadContext = theadContext + `<th style="">${ruleName}</th>`;
            ruleList.push(ruleName);


            if (type == '텍스트') {
                append = append + `<td class='mediaTable mediaTableTbodyTd'><input type="text" class="form-control rule-text leave resposiveTd mediaTable" rule=${ruleName}></td>`
            } else if (type == '달력') {
                append = append + `<td class='mediaTable mediaTableTbodyTd'>
                                       <div class="input-group resposiveTd">
                                       <div class="input-group-addon bgc-white bd bdwR-0"><i class="ti-calendar"></i></div>
                                       <input type="text" class="form-control start-date rule-calendar leave rule" placeholder="달력" data-provide="datepicker" name ="inout_sdate" id="inout_sdate" rule=${ruleName}>
                                       </div>
                                    </td> `
            } else if (type == '파일') {
                append = append +
                    `<td class='mediaTable mediaTableTbodyTd'><input name="file" id="file" accept="image/*,video/*" type="file" class="file rule-file leave file-upload rule resposiveTd"  data-browse-on-zone-click="true" rule=${ruleName}>
                        <a id='download' href ='' target="_new" class='resposiveTd' download hidden>다운로드</a>
                </td>`
            }
        }


        $('#thead').append(theadContext);
        append = append + `<td class='mediaTable mediaTableTbodyTd'style="visibility:hidden" is-valid="0" is-user="0"></td>`
        newTr = newTr + append + '</tr>';
    }

    //출입신청 컨트롤러
    function applyhandler(dataSet) {

    }

    //신청자조회 컨트롤러
    function applySearchhandler(dataSet) {

        dataSet = dataSet.msg
        var str = ''
        $('#interviewTbody').children().remove()
        for (var i = 0; i < dataSet.length; i++) {
            var name = dataSet[i].name;
            var phone = dataSet[i].phone;
            var comp_nm = dataSet[i].comp_nm;
            var biz_no = dataSet[i].biz_no;

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

    //감독자조회 컨트롤러
    function interViewSearchhandler(dataSet) {
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

    //규칙검증 컨트롤러
    function rulevalidhandler(dataSet, opt) {
        var dataSet = dataSet.msg;
        var msg = '';
        var check = false;
        var rule = opt.closest('tr').children();
        var offset = 5;

        for (var i = 0; i < dataSet.length; i++) {
            var rule_name = dataSet[i].rule_name;
            var rule_desc = dataSet[i].rule_desc;
            var rule_type = dataSet[i].rule_type;
            //추가부분
            var rule_textDesc = dataSet[i].text_desc; //텍스트 속성
            var rule_sdate = dataSet[i].s_date; //달력 속성
            var rule_bucketUrl = dataSet[i].bucketUrl; //버킷 속성

            var state = dataSet[i].state;
            var nextRule = rule.eq(offset + i);
            var writeCheck = rule.eq(0).attr('valueChange');
            console.log(state)


            //state 상태체크
            if (!state) { //remove, Rule False(Rule 무효인 상태)
                msg = msg + rule_name + " ";
                check = true;
                if (rule_type == '달력') {
                    nextRule.children().children('input').addClass('is-invalid');
                } else if (rule_type == '텍스트') {
                    nextRule.children().addClass('is-invalid');
                } else if (rule_type == '파일') {
                    nextRule.children().next().attr('hidden', true)
                }

            } else { //add, Rule True(Rule이 유효한 상태)
                if (rule_type == '달력') {
                    nextRule.children().children('input').removeClass('is-invalid');
                    if(writeCheck=='0'){
                          var date = rule_sdate.split('-')//달력
                          var year = date[0]; //년
                          var month = date[1]; //월
                          var day = date[2]; //일
                          output = month + "/" + day + "/" + year;
                          nextRule.children().children('input').val(output);
                    }


                } else if (rule_type == '텍스트') {
                    nextRule.children().removeClass('is-invalid');
                    if(writeCheck=='0'){
                         nextRule.children().val(rule_textDesc);//텍스트
                    }

                } else if (rule_type == '파일') {
                    nextRule.children().next().removeAttr('hidden');
                    if(writeCheck=='0'){
                        nextRule.children().attr('href', rule_bucketUrl);
                    }
                }
            }
        }

        if(writeCheck =='0'){
                rule.eq(0).attr('valueChange','1');}


        if (check) {
            msg = msg + '의 유효기간이 만료되었습니다.';
            console.log('----------------------------in')
            rule.eq(-1).attr("is-valid", "0"); //0은 검증X
            console.log(rule.eq(-1).attr("is-valid"));
            console.log('----------------------------in')
            $('#errorMsg').text(msg);

        } else {
            console.log('----------------------------out')
            rule.eq(-1).attr("is-valid", "1"); //1은 검증0
            console.log(rule.eq(-1).attr("is-valid"));
            console.log('----------------------------out')
            $('#errorMsg').text('');
        }

    }

    //업체조회 컨트롤러
    function compSearchhandler(dataSet) {
        dataSet = dataSet.msg
        var str = ''
        $('#compTbody').children().remove()
        for (var i = 0; i < dataSet.length; i++) {
            var comp_nm = dataSet[i].comp_nm;
            var biz_no = dataSet[i].biz_no;
            var bizId = dataSet[i].biz_id;
            var temp = `<tr class='compTtr' bizId = ${bizId}>
                                 <th scope="row">${i+1}</th>
                                 <td>${comp_nm}</td>
                                 <td>${biz_no}</td>
                         </tr>`;
            str += temp;
        }

        $('#compTbody').append(str);
        $('.compTtr').click(function() {
            var bizId = $(this).attr("bizId");

            $('#inout_comp_nm').val($(this).children('td:eq(0)').text());
            $('#inout_biz_no').val($(this).children('td:eq(1)').text());
            $('#inout_biz_no').attr('bizId', bizId);

        });
    }

    //감독자조회 컨트롤러
    function interviewSearchhandler(dataSet) {
        dataSet = dataSet.msg
        var str = '';
    }

    //차량조회 컨트롤러
    function carSearchhandler(dataSet) {
        dataSet = dataSet.msg
        var str = '';
        for (var i = 0; i < dataSet.length; i++) {
            var code_nm = dataSet[i].code_nm;
            var temp = `<option value=${code_nm}>${code_nm}</option>`
            str = str + temp;
        }
        return str;
    }

    //event리스너
    function init() {
        const $tableID = $('#table');
        apiCallPost(urlMake('RULE_SEARCH'), ruleSearchhandler);

        $('#appylbtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['applicant_name', 'applicant_phone', 'applicant_biz_no', 'applicant_comp_nm',
                'interviewer_dept', 'interviewer_name', 'interviewer_phone',
                'inout_biz_no', 'inout_comp_nm', 'inout_sdate', 'inout_edate',
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

            //출입신청 아이디
            dataSet['applyId'] = $('#main').attr('name');
            var lists = [];

            //visitors설정
            $('#tableBody tr').each(function() {
                var cellItem = $(this).find(":input")
                var itemObj = new Object()
                itemObj.name = cellItem.eq(1).val()
                itemObj.phone = cellItem.eq(2).val()
                itemObj.carType = cellItem.eq(3).val()
                itemObj.carNum = cellItem.eq(4).val()

                var obj = {
                    "name": itemObj.name,
                    "phone": itemObj.phone,
                    "carType": itemObj.carType,
                    "carNum": itemObj.carNum
                }

                lists.push(obj)

            });

            //사업자번호 설정
            dataSet["inout_biz_id"] = $('#inout_biz_no').attr('bizId');

            //출입지역 code
            dataSet["inout_location_code"] = $("#inout_location option:selected").attr('code')
            dataSet["inout_location_code2"] = $("#inout_location2 option:selected").attr('code')
            dataSet["visitors"] = JSON.stringify(lists);

            //신청자 정보 check
            var check = dataSet['applicant_name'];
            var check2 = dataSet['inout_biz_no'];

            if (check.length == 0 || check2.length == 0) {
                alert('신청자 정보를 입력해주세요');
                return;
            }

            //감독자 정보 check
            check = dataSet['interviewer_name'];
            if (check.length == 0) {
                alert('신청자 정보를 입력해주세요');
                return;
            }

            //출입 정보 check
            check = dataSet['inout_title'];
            if (check.length == 0) {
                alert('출입정보를 입력해주세요');
                return;
            }

            //출입유효성 check
            $('#tableBody tr').each(function() {
                check = $(this).children().eq(-1).attr('is-valid')
                if (check == '0')
                    alert('출입 유효성을 점검해주세요')

            });

            if (check == '1')
                apiCallPost(urlMake('CREATE'), applyhandler, dataSet)

        });

        $('#addUser').click(function(e) {
            const $clone = $tableID.find('tbody tr').last().clone(true).removeClass('hide table-line');
            if ($tableID.find('tbody tr').length === 0) {
                $('#tableBody').append(newTr);

            } else {
                $tableID.find('tbody').last().append(newTr);
                //$tableID.find('table').append($clone);
            }

            $('.leave').focusout(function(e) {
                var sdate = $('#inout_sdate').val();
                var edate = $('#inout_edate').val();
                var date = [];
                var year, month, day;
                var dataSet = {};

                if (!sdate || !edate) {
                    console.log("날짜가 선택되지 않았습니다.")
                    return;
                }

                sdate = sdate.split('/')
                year = sdate[2]; //년
                month = sdate[0]; //월
                day = sdate[1]; //일
                dataSet['sdate'] = year + "-" + month + "-" + day;

                edate = edate.split('/')
                year = edate[2]; //년
                month = edate[0]; //월
                day = edate[1]; //일
                dataSet['edate'] = year + "-" + month + "-" + day;

                var userName = $(this).closest('tr').children().eq(1).children().children().val() || '';
                var userPhone = $(this).closest('tr').children().eq(2).children().children().val() || '';

                console.log(userName);
                console.log(userPhone);

                if (userName.length == 0 || userPhone.length == 0)
                    return;

                var str = userPhone.trim();
                var phone = str.replace(/(^02.{0}|^01.{1}|[0-9]{3})([0-9]+)([0-9]{4})/, "$1-$2-$3");
                var regExp = /^01(?:0|1|[6-9])-(?:\d{3}|\d{4})-\d{4}$/;
                var check = regExp.test(phone);
                if (!check) {
                    console.log("검증에 실패하였습니다.")
                    return;
                }

                $(this).closest('tr').children().eq(2).children().children().val(phone);
                userPhone = phone;
                dataSet['userName'] = userName;
                dataSet['userPhone'] = userPhone;
                dataSet['applyId'] = $('#main').attr('name');
                var option = $(this);

                $.ajax({
                        type: "POST",
                        url: "/inoutApply/user/search",
                        async: false,
                        cache: false,
                        data: dataSet
                    })
                    .success(function(data) {
                        var msg = data.msg;
                        if (msg.length == 0) {
                            //empty user
                            console.log('사용자 없음')
                            option.closest('tr').children().eq(-1).attr('is-user', '0')

                        } else {
                            console.log('사용자 있음')
                            option.closest('tr').children().eq(-1).attr('is-user', '1')
                            apiCallPost(urlMake('RULE_VALID'), rulevalidhandler, dataSet, option)
                        }
                    });


            });

            $('.rule-text').focusout(function(e) {
                var userName = $(this).closest('tr').children().eq(1).children().children().val() || '';
                var userPhone = $(this).closest('tr').children().eq(2).children().children().val() || '';
                var rule = $(this).attr('rule');
                var ruleText = $(this).val() || '';

                if (userName.length == 0 || userPhone.length == 0 || ruleText.length == 0)
                    return;

                var dataSet = {};
                dataSet['userName'] = userName;
                dataSet['userPhone'] = userPhone;
                dataSet['ruleText'] = ruleText;
                dataSet['type'] = '텍스트';
                dataSet['rule'] = rule;
                dataSet['applyId'] = $('#main').attr('name');

                console.log('호출')
                $.ajax({
                        type: 'POST',
                        url: "/inoutApply/rule/text/update",
                        async: false,
                        cache: false,
                        data: dataSet
                    })
                    .success(function(data) {

                    });
            });


            $('.rule-calendar').focusout(function(e) {
                var userName = $(this).closest('tr').children().eq(1).children().children().val() || '';
                var userPhone = $(this).closest('tr').children().eq(2).children().children().val() || '';
                var rule = $(this).attr('rule');
                var ruleCalender = $(this).val() || '';

                if (userName.length == 0 || userPhone.length == 0 || ruleCalender.length == 0)
                    return;

                var dataSet = {};
                dataSet['userName'] = userName;
                dataSet['userPhone'] = userPhone;
                dataSet['rule'] = rule;
                dataSet['type'] = '캘린더';
                dataSet['applyId'] = $('#main').attr('name');
                ruleCalender = ruleCalender.split('/')
                year = ruleCalender[2]; //년
                month = ruleCalender[0]; //월
                day = ruleCalender[1]; //일
                dataSet['ruleCalender'] = year + "-" + month + "-" + day;

                $.ajax({
                        type: 'POST',
                        url: "/inoutApply/rule/calendar/update",
                        async: false,
                        cache: false,
                        data: dataSet
                    })
                    .success(function(data) {

                    });

            });


            $('.file-upload').change(function(e) {
                if (confirm('해당 파일을 업로드하시겠습니까?')) {
                    var current = $(this);
                    var data = new FormData();
                    data.append("file", $(this).prop('files')[0]);
                    var applicantName = $('#applicant_name').val() || '';
                    var applicantPhone = $('#applicant_phone').val() || '';
                    var userName = $(this).closest('tr').children().eq(1).children().children().val() || '';
                    var userPhone = $(this).closest('tr').children().eq(2).children().children().val() || '';
                    var applyId = $('#main').attr('name');
                    var rule = $(this).attr('rule');


                    if (applicantName.length == 0 || applicant_phone.length == 0 || userName.length == 0 || userPhone.length == 0) {
                        console.log(applicant_name)
                        console.log(applicant_phone)
                        console.log(userName)
                        console.log(userPhone)
                        return;
                    }
                    data.append('applicantName', applicantName);
                    data.append('applicantPhone', applicantPhone);
                    data.append('userName', userName);
                    data.append('phone', userPhone);
                    data.append('type', '파일');
                    data.append('rule', rule);
                    data.append('applyId', applyId);

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
                            current.next().removeAttr('hidden');
                            current.next().attr('href', href)
                        },

                        error: function(e) {
                            console.log("ERROR : ", e);
                        }
                    });
                } else {
                    if ($(this).val().length != 0) {
                        $(this).val('');
                    }

                }
            });



        });

        $('#delUser').click(function(e) {
            var checkbox = $('input[id=checkbox]:checked');
            var tdArray = new Array();

            checkbox.each(function(i) {
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

            apiCallPost(urlMake('APPLY_SEARCH'), applySearchhandler, dataSet)
        });

        //감독자조회 모달
        $('#interviewSearch').click(function(e) {
            var dataSet = {};
            var interviewName = $('#interviewInput').val();
            dataSet['interviewName'] = interviewName;
            apiCallPost(urlMake('INTERVIEW_SEARCH'), interViewSearchhandler, dataSet)

        });

        //업체조회 모달
        $('#compSearchView').click(function(e) {
            var dataSet = {};
            var compSearchInput = $('#compSearchInput').val();
            dataSet['compSearchInput'] = compSearchInput;
            apiCallPost(urlMake('COMP_SEARCH'), compSearchhandler, dataSet)

        });


        //방문유형
        $.ajax({
                type: "POST",
                url: "/inoutApply/visit/type",
                async: false,
                cache: false,
                data: ""
            })
            .success(function(data) {
                data = data.msg;
                //                var str = '<option selected="selected">선택</option>';
                var str = '';
                for (var i = 0; i < data.length; i++) {
                    var code_nm = data[i].code_nm
                    var temp = `<option value=${code_nm}>${code_nm}</option>`
                    str = str + temp;
                }
                $('#inout_purpose_type').append(str);

            });

        //방문지역
        $.ajax({
                type: "POST",
                url: "/inoutApply/door/search",
                async: false,
                cache: false,
                data: ""
            })
            .success(function(dataSet) {
                data = dataSet.msg;
                var str = '';
                for (var i = 0; i < data.length; i++) {
                    var code_nm = data[i].code_nm
                    var code = data[i].code
                    var temp = `<option code = ${code} value=${code_nm}>${code_nm}</option>`
                    str = str + temp;
                }

                data = dataSet.msg2;
                $('#inout_location').append(str);
                str = '';
                for (var i = 0; i < data.length; i++) {
                    var code_nm = data[i].code_nm
                    var code = data[i].code
                    var temp = `<option code = ${code} value=${code_nm}>${code_nm}</option>`
                    str = str + temp;
                }
                $('#inout_location2').append(str);
            });

        var date = new Date();
        var year = date.getFullYear();
        var month = new String(date.getMonth() + 1);
        var day = new String(date.getDate());
        if (month.length == 1)
            month = '0' + month;

        var thisYear = month + "/" + day + "/" + year;
        $('#inout_sdate').val(thisYear);
        $('#inout_edate').val(thisYear);

    }
    init();
})