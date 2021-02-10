var gb;
var gb2;
var ruleList = [];
$(document).ready(function() {

    //URL에 해당하는 컨트롤러 호출

    function apiCallPost(url, controller, data, opt) {
        $.ajax({
                type: 'POST',
                url: url,
                async: false,
                cache: false,
                data: data
            })
            .success(function(data) {
                controller(data, opt);
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

            case 'COMP_SEARCH':
                reqUrl = reqUrl + `comp/search`;
                break;

            case 'CAR_SEARCH':
                reqUrl = reqUrl + `car/search`;
                break;

        }
        return reqUrl;
    }

    //규칙정보 컨트롤러
    function ruleSearchController(dataSet) {
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
         <tr class="hide">
             <td>
                     <input type="checkbox" id="checkbox" class="peer leave">
             </td>

             <td>
                <div class="form-group">
                     <input type="text" class="form-control leave" id="tvisitor" style="width:80%; float:left" >
                 </div>
             </td>

             <td>
                 <div class="form-group">
                     <input type="text" id="tphone"  class="form-control leave ctphone">
                 </div>
             </td>

             <td>
                <div class="form-group" >
                         <select id="" name="" class="form-control leave">
                                ${str}
                         </select>
                 </div>
             </td>
             <td><input type="text" class="form-control leave"></td>
             `

        for (var i = 0; i < dataSet.length; i++) {
            var obj = dataSet[i];
            var type = obj.rule_type;
            var ruleName = obj.rule_name;
            theadContext = theadContext + `<th style="">${ruleName}</th>`;
            ruleList.push(ruleName);

            if (type == '텍스트') {
                append = append + `<td><input type="text" class="form-control rule-text leave" rule=${ruleName}></td>`
            } else if (type == '달력') {
                append = append + `<td>
                                       <div class="input-group">
                                       <div class="input-group-addon bgc-white bd bdwR-0"><i class="ti-calendar"></i></div>
                                       <input type="text" class="form-control start-date rule-calendar leave rule" placeholder="달력" data-provide="datepicker" name ="inout_sdate" id="inout_sdate" rule=${ruleName}>
                                       </div>
                                    </td> `
            } else if (type == '파일') {
                append = append + `<td><input name="file" id="file" accept="image/*,video/*" type="file" class="file rule-file leave file-upload rule" data-browse-on-zone-click="true" rule=${ruleName}></td>`
            }
        }


        $('#thead').append(theadContext);
        append = append + `<td style="visibility:hidden" is-valid="1"></td>`
        newTr = newTr + append + '</tr>';
    }

    //출입신청 컨트롤러
    function applyController(dataSet) {
        console.log(JSON.stringify(dataSet));
    }

    //감독자조회 컨트롤러
    function interViewSearchController(dataSet) {
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
    function rulevalidController(dataSet, opt) {
        var dataSet = dataSet.msg;
        var msg = '';
        var check = false;
        gb = opt.parent().parent().next().next().next(); //rule1부터 시작
        temp = opt.parent().parent().next().next().next();

        for (var i = 0; i < dataSet.length; i++) {
            var rule_name = dataSet[i].rule_name;
            var rule_desc = dataSet[i].rule_desc;
            var rule_type = dataSet[i].rule_type;
            var state = dataSet[i].state;

            //state 상태체크
            if (!state) {
                msg = msg + rule_name + " ";
                check = true;
                if (rule_type == '달력') {
                    temp.children().children('input').addClass('is-invalid');
                } else {
                    temp.children().addClass('is-invalid');
                }
            } else {
                if (rule_type == '달력') {
                    temp.children().children('input').removeClass('is-invalid');

                } else {
                    temp.children().removeClass('is-invalid');
                }
            }
            temp = temp.next();
        }



        if (check) {
            msg = msg + '의 유효기간이 만료되었습니다.';
            console.log('----------------------------in')
            temp.attr("is-valid", "0"); //0은 검증X
            console.log(temp.attr("is-valid"));
            console.log('----------------------------in')

        } else {
            console.log('----------------------------out')
            temp.attr("is-valid", "1"); //1은 검증0
            console.log(temp.attr("is-valid"));
            console.log('----------------------------out')
        }


        $('#errorMsg').text(msg);
    }



    //업체조회 컨트롤러
    function compSearchController(dataSet) {
        dataSet = dataSet.msg
        var str = ''
        $('#compTbody').children().remove()
        for (var i = 0; i < dataSet.length; i++) {
            var comp_nm = dataSet[i].comp_nm;
            var biz_no = dataSet[i].biz_no;
            var temp = `<tr class='compTtr'>
                                 <th scope="row">${i+1}</th>
                                 <td>${comp_nm}</td>
                                 <td>${biz_no}</td>
                         </tr>`;
            str += temp;
        }

        $('#compTbody').append(str);
        $('.compTtr').click(function() {
            $('#inout_comp_nm').val($(this).children('td:eq(0)').text());
            $('#inout_biz_no').val($(this).children('td:eq(1)').text());

        });
    }

    //감독자조회 컨트롤러
    function interviewSearchController(dataSet) {
        dataSet = dataSet.msg
        var str = '';
    }

    //차량조회 컨트롤러
    function carSearchController(dataSet) {
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
        apiCallPost(urlMake('RULE_SEARCH'), ruleSearchController);

        $('#appylbtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['applicant_name', 'applicant_phone', 'applicant_biz_no',
                'applicant_comp_nm', 'interviewer_name', 'interviewer_phone',
                'inout_biz_no', 'inout_comp_nm', 'inout_sdate',
                'inout_edate', 'inout_comp_nm', 'inout_sdate',
                'inout_purpose_type', 'inout_title', 'inout_location',
                'inout_location_desc', 'inout_purpose_desc'
            ]

            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
                var value = $('#' + key).val()
                dataSet[key] = value;

            }
            apiCallPost(urlMake('CREATE'), applyController, dataSet)
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

                var userName = $(this).parent().parent().first().children().children().children().val() || false;
                var userPhone = $(this).parent().parent().first().children().next().next().children().children().val() || false;
                if (!userName || !userPhone)
                    return;

                dataSet['userName'] = userName;
                dataSet['userPhone'] = userPhone;


                var option = $(this);

                apiCallPost(urlMake('RULE_VALID'), rulevalidController, dataSet, option)
            });

            $('.rule-text').focusout(function(e) {
                var userName = $(this).parent().parent().first().children().children().children().val() || '';
                var userPhone = $(this).parent().parent().first().children().next().next().children().children().val() || '';
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
                $.ajax({
                        type: 'POST',
                        url: "/inoutApply/rule/text/update",
                        async: false,
                        cache: false,
                        data: dataSet
                    })
                    .success(function(data) {
                        alert('성공')
                    });
            });


            $('.rule-calendar').focusout(function(e) {
                gb2 = $(this);
                var userName = $(this).parent().parent().parent().first().children().children().children().val() || '';
                var userPhone = $(this).parent().parent().parent().first().children().next().next().children().children().val() || '';
                var rule = $(this).attr('rule');
                var ruleCalender = $(this).val() || '';

                if (userName.length == 0 || userPhone.length == 0 || ruleCalender.length == 0)
                    return;

                var dataSet = {};
                dataSet['userName'] = userName;
                dataSet['userPhone'] = userPhone;
                dataSet['rule'] = rule;
                dataSet['type'] = '캘린더';
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
                        alert('성공')
                    });

            });


            $('.file-upload').change(function(e) {
                if (confirm('해당 파일을 업로드하시겠습니까?')) {
                    var data = new FormData();
                    data.append("file", $('#file').prop('files')[0]);
                    var applicantName = $('#applicant_name').val() || '';
                    var applicantPhone = $('#applicant_phone').val() || '';
                    var userName = $(this).parent().parent().first().children().children().children().val() || '';
                    var userPhone = $(this).parent().parent().first().children().next().next().children().children().val() || '';

                    var rule = $(this).attr('rule');


                    if (applicantName.length==0 || applicant_phone.length==0 || userName.length == 0 || userPhone.length == 0)
                        return;
                    data.append('applicantName',applicantName);
                    data.append('applicantPhone',applicantPhone);
                    data.append('userName',userName);
                    data.append('phone',userPhone);
                    data.append('type','파일');
                    data.append('rule',rule);



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
                            console.log("SUCCESS : ");
                        },

                        error: function(e) {
                            console.log("ERROR : ", e);
                        }
                    });
                };
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

        $('#interviewSearch').click(function(e) {
            var dataSet = {};
            var interviewName = $('#interviewInput').val();
            dataSet['interviewName'] = interviewName;
            apiCallPost(urlMake('INTERVIEW_SEARCH'), interViewSearchController, dataSet)

        });


        $('#compSearchView').click(function(e) {
            var dataSet = {};
            var compSearchInput = $('#compSearchInput').val();
            dataSet['compSearchInput'] = compSearchInput;
            apiCallPost(urlMake('COMP_SEARCH'), compSearchController, dataSet)

        });


    }
    init();
})