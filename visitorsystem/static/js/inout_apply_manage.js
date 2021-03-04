$(document).ready(function() {

	function apiCallPost(url, handler, data, opt) {
		$.ajax({
			type: 'POST',
			url: url,
			cache: false,
			data: data,
			dataType: 'json',
//			async : false,
			success: function(data) {
				handler(data);
			},
			error: function(e) {
				alert("처리중 에러 발생");
				return;
			}
		});
	}

	//type에 맞는 URL을 반환하는 함수
	function urlMake(url, args) {
		var reqUrl = "/inoutApplyManage/";
		switch (url) {
			case 'SEARCH':
				reqUrl = reqUrl + 'search';
				break;
			case 'DETAIL':
				reqUrl = reqUrl + 'detail';
				break;
			case 'SAVE':
				reqUrl = reqUrl + 'save';
				break;
			case 'APPLICANT_SEARCH':
				reqUrl = reqUrl + 'applicant/search';
				break;
		}
		return reqUrl;
	}

    function dataToString(data, userAuth) {
        var res = 'applicant_name=' + data.applicant_name + '&applicant_phone=' + data.applicant_phone +
                  'visit_sdate=' + data.visit_sdate + '&visit_edate=' + data.visit_edate +
                  '&visit_category=' + data.visit_category + '&visit_purpose=' + data.visit_purpose +
                  '&comp_nm=' + data.comp_nm + '&approval_state=' + data.approval_state + '&pages=' + data.pages;

        if (userAuth == '9990' || userAuth == '2000') {
            res += '&site_id=' + data.site_id;
        }
        res = '\'?' + res + '\'';
        return res;
    }

	//목록 페이징
	function Paging(endpoint, pagination, query_string, data, userAuth) {
        searchCondition = dataToString(data, userAuth);

        var pageBtnHtml = '';
        pageBtnHtml += '<div class="custom-pagination btn-group mr-1" style="display: flex">';
        pageBtnHtml += '<div class="custom-pagination-center" style="margin: 0 auto">';

        if(pagination.page > 1) {
            pageBtnHtml += '<button type="button" class="btn btn-primary mr-1" onclick="javascript:url_for(' + (parseInt(pagination.page) - 1) + ',' + searchCondition + ')" ';

            if (query_string) {
                pageBtnHtml += query_string;
            }
            pageBtnHtml += '>&#8592;</a></button>';
        }

        for (var page in pagination.iter_pages) {
            var idx = (page*1) + 1
            if (page) {
                if(idx != pagination.page) {
                    pageBtnHtml += '<button type="button" class="btn btn-primary mr-1" onclick="javascript:url_for('+ idx + ',' + searchCondition + ')" ';
                    if (query_string) {
                        pageBtnHtml += query_string;
                    }
                    pageBtnHtml += '><div>' + idx + '</div></a></button>';
                }
                else {
                    pageBtnHtml += '<button type="button" class="btn mr-1"> <div class="active"> ' + idx + '</div></button>';
                }
            }
            else {
                pageBtnHtml += '<span>...</span>';
            }
        }

        if(pagination.page < pagination.p_pages) {
            pageBtnHtml += '<button type="button" class="btn btn-primary" onclick="javascript:url_for(' + (parseInt(pagination.page) + 1) + ',' + searchCondition + ')" ';

            if (query_string) {
                pageBtnHtml += query_string;
            }
            pageBtnHtml += '> <div>&#8594;</div></button>';
        }
        pageBtnHtml += '</div></div>';
        return pageBtnHtml;
	}

	function setSearchFormHandler(data) {
		var dataSet = data.msg;

        //조회 결과에 따른 방문신청정보 Table Set
		if (dataSet.length < 1) {
			$('.applyListTable>tbody').html('<td colspan="12" style="text-align:center"><text> 조회된 내역이 없습니다. </text></td>');
		} else {
			var htmlData = '';
			for (var i = 0; i < dataSet.length; i++) {
				htmlData += '<tr style="cursor:pointer;" onclick="document.location.href="/inoutApply/edit/' + dataSet[i].id + '">';
				htmlData += '<td data-title="방문유형">' + dataSet[i].visit_category + '</td>';
				htmlData += '<td data-title="업체명">' + dataSet[i].comp_nm + '</td>';
				htmlData += '<td data-title="방문목적">' + dataSet[i].visit_purpose + '</td>';
				htmlData += '<td data-title="신청자">' + dataSet[i].applicant + '</td>';
				htmlData += '<td data-title="방문자 정보" style=" cursor:pointer; text-decoration: underline;" data-toggle="modal" class="guestInfo" name="guestInfo" value=' + dataSet[i].id + '>방문자 정보</td>';
				htmlData += '<td data-title="시작일">' + dataSet[i].visit_sdate + '</td>';
				htmlData += '<td data-title="종료일">' + dataSet[i].visit_edate + '</td>';
				htmlData += '<td data-title="신청사업장">' + dataSet[i].site_nm + '</td>';
				htmlData += '<td data-title="신청출입문">' + dataSet[i].site_nm2 + '</td>';
				htmlData += '<td data-title="진행단계">' + dataSet[i].approval_state + '</td>';
				htmlData += '</tr>';
			}
			$('.applyListTable>tbody').html(htmlData);
		}

        // 조회 결과에 따른 페이지 버튼 Set (endpoint, Pagination 정보 객체, 쿼리 스트링)
        var pageBtnHtml = Paging('super_approval.index', data.pagination, data.query_string, data.searchCondition, data.userAuth);
        $('#pagination').html(pageBtnHtml);

        init();
	}

	//승인, 반려 건에 대한 상태값 update
	function updateApprovalStateHandler(dataSet) {
		$('input:checkbox[name=chk]:checked').each(function() {
		    $(this).attr("value2", dataSet.approval_state);
		    $(this).closest("tr").children().eq(-1).text(dataSet.approval_state);
		});

        //결재 이후, 체크 박스 해제
        $("input[name=checkall]").prop("checked", false);
        $("input[name=chk]").prop("checked", false);

        //성공 모달 띄우기
		$('#modalContent').text(dataSet.msg);
		$('#alertModal').show();
	}

    //선택한 사용자의 Rule 정보 출력
    function userRuleInfoDetail(idx, users, userRuleInfoList) {
        $('.userName').text(users[idx].name);

        var userRuleInfoHtml = '';
        var no = 0;
		for (var i = 0; i < userRuleInfoList.length; i++) {
            if( users[idx].name != userRuleInfoList[i].name || (users[idx].phone != userRuleInfoList[i].phone) ) {
                continue;
            }
            no += 1;
            userRuleInfoHtml += '<tr>';
            userRuleInfoHtml += '<td>' + no + '</td>';
            userRuleInfoHtml += '<td>' + userRuleInfoList[i].name + '</td>';
            userRuleInfoHtml += '<td>' + userRuleInfoList[i].rule_name + '</td>';
            userRuleInfoHtml += '<td>' + userRuleInfoList[i].rule_type + '</td>';

            type = userRuleInfoList[i].rule_type
            if(type=='텍스트'){
                userRuleInfoHtml += '<td>' + userRuleInfoList[i].ruleDesc + '</td>';
            }
            else if (type=='달력'){
                userRuleInfoHtml += '<td>' + userRuleInfoList[i].s_date + '</td>';
            }
            else if (type=='파일'){
                userRuleInfoHtml += '<td><a href=' + userRuleInfoList[i].ruleDesc + ' target="_new">다운로드</a></td>';
            }
            userRuleInfoHtml += '<td>' + userRuleInfoList[i].ruleRes + '</td>';
            userRuleInfoHtml += '</tr>';
		}
		return userRuleInfoHtml;
    }

    //방문신청 건에 포함된 방문자 및 규칙 정보리스트 Modal
	function searchApplyMasterDetailHandler(dataSet) {
		//작업에 대한 작업자 상세 정보 Modal에 띄어야 함.
		users = dataSet.users;
		userRuleInfoList = dataSet.userRuleInfoList;

		$('#visitantDocModal').show();
		users = dataSet.users;

		//방문자 리스트 출력
		userInfoHtml = '';
		for (var i = 0; i < users.length; i++) {
		    userInfoHtml += '<tr>';
            userInfoHtml += '<td value1=' + users[i].id + ' value2='+ users[i].apply_id + '>' + (parseInt(i)+1) + '</td>';
            userInfoHtml += '<td>' + users[i].name + '</td>';
            userInfoHtml += '<td>' + users[i].phone + '</td>';

            var isTure = true;
            for(var j=0;j<userRuleInfoList.length; j++){
                //해당 Uesr의 모든 규칙이 가능하면 총 결과는 가능. 아니면 불가
                if(userRuleInfoList[j].id == users.id){
                    if(userRuleInfoList[j].ruleRes == '불가') {
                        userInfoHtml += '<td>' + '불가' + '</td>';
                        isTure = false;
                        break;
                    }
                }
            }
            if(isTure) {
                userInfoHtml += '<td>' + '가능' + '</td>';
            }
            userInfoHtml += '</tr>';
		}
		$('#userInfoTable > tbody').html(userInfoHtml);

        //방문자별 상세 규칙 리스트 출력
        //방문상세정보 중 1명 row 선택시, 선택한 사람의 Rule 정보를 보임.
		userRuleInfoHtml = userRuleInfoDetail(0, users, userRuleInfoList);
		$('#userRuleTable > tbody').html(userRuleInfoHtml);

		$(".userInfomodalBody tr").unbind('click').click(function() {
            var idx = $(this).children().eq(0).text();
            idx = (parseInt(idx)-1);
            userRuleInfoHtml = userRuleInfoDetail(idx, users, userRuleInfoList);
		    $('#userRuleTable > tbody').html(userRuleInfoHtml);
		});
	}

    //날짜 초기값 세팅
	function getFormatDate(date, op) {
        //조회기간 오늘 ~ 오늘+7
        if (op == "sdate")
            date.setDate(date.getDate() - 7);

        var y = date.getFullYear();
        var m = (1 + date.getMonth());
        m = m >= 10 ? m : '0' + m;
        var d = date.getDate();
        d = d >= 10 ? d : '0' + d;
        date = m + '/' + d + '/' + y;
        return date;
    }
    $('#visit_sdate').val(getFormatDate(new Date(), "sdate"));
    $('#visit_edate').val(getFormatDate(new Date(), "edate"));

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

	//event리스너
	function init() {
	    //Modal 닫기
	    $('.exitModal').unbind('click').click(function() {
	        var modalName = '#'+$(this).val();
            $(modalName).hide();
        });

        //조회시, 달력 포맷 수정
		$("#searchBtn").unbind('click').click(function() {
			var sdate = $('#visit_sdate').val();
			var edate = $('#visit_edate').val();
			var dataSet = {};

			if (sdate=="" || edate=="" ) {
                $("#nullChkModal").modal('show');
				return;
			}

			sdate = sdate.split('/');
			edate = edate.split('/');
			dataSet['visit_sdate'] = sdate[2] + "-" + sdate[0] + "-" + sdate[1];
			dataSet['visit_edate'] = edate[2] + "-" + edate[0] + "-" + edate[1];
			dataSet['visit_category'] = $('#type').val();
			dataSet['visit_purpose'] = $('#visit-purpose').val();
			dataSet['comp_nm'] = $('#comp-nm').val();
			dataSet['approval_state'] = $('#inputState').val();
			dataSet['page'] = 1;    //Search 버튼 누르면 초기페이지는 1번째로 Set
			dataSet['pages'] = 10;  //한 페이지에 조회되는 개수

            //site_id가 없으면 undefined
			dataSet['site_id'] = $("#location").val();

            //신청자 정보
			dataSet['applicant_name'] = $("#applicant_name").val();
            dataSet['applicant_phone'] = $("#applicant_phone").val();

			//권한별 추가
			apiCallPost(urlMake('SEARCH'), setSearchFormHandler, dataSet);
		});



		//신청자조회 모달
        $('#visitSearchView').unbind('click').click(function() {
            var dataSet = {};
            var visitInput = $('#visitInput').val();
            dataSet['visitInput'] = visitInput;

            apiCallPost(urlMake('APPLICANT_SEARCH'), applySearchHandler, dataSet);
        });

        //방문신청내역 중 방문상세정보 출력
		$("[name=guestInfo]").unbind('click').click(function() {
			var id = $(this).attr('value');
			var dataSet = {};
			dataSet['id'] = id;

			dataSet['sdate'] = $(this).closest("tr").children("[data-title=시작일]").text();
			dataSet['edate'] = $(this).closest("tr").children("[data-title=종료일]").text();

			apiCallPost(urlMake('DETAIL'), searchApplyMasterDetailHandler, dataSet);
		});
	}

	init();
});