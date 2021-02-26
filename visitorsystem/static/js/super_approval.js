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
		var reqUrl = "/superApproval/";
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
		}
		return reqUrl;
	}

	//목록 페이징
	function Paging(endpoint, pagination, query_string) {
        var pageBtnHtml = '';
        pageBtnHtml += '<div class="custom-pagination btn-group mr-1" style="display: flex">';
        pageBtnHtml += '<div class="custom-pagination-center" style="margin: 0 auto">';

        if(pagination.page > 1) {
            pageBtnHtml += '<button type="button" class="btn btn-primary mr-1" onclick="javascript:url_for(' + (parseInt(pagination.page) - 1) + ')" ';

            if (query_string) {
                pageBtnHtml += query_string;
            }
            pageBtnHtml += '>&#8592;</a></button>';
        }

        for (var page in pagination.iter_pages) {
            var idx = (page*1) + 1
            if (page) {
                if(idx != pagination.page) {
                    pageBtnHtml += '<button type="button" class="btn btn-primary mr-1" onclick="javascript:url_for('+ idx + ')" ';
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
            pageBtnHtml += '<button type="button" class="btn btn-primary" onclick="javascript:url_for(' + (parseInt(pagination.page) + 1) + ')" ';

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

        //조회 결과에 따른 출입신청정보 Table Set
		if (dataSet.length < 1) {
			$('.applyListTable>tbody').html('<td colspan="12" style="text-align:center"><text> 조회된 내역이 없습니다. </text></td>');
		} else {
			var htmlData = '';
			for (var i = 0; i < dataSet.length; i++) {
				htmlData += '<tr>';
				htmlData += '<td data-title="선택"><input type="checkbox" name="chk" value1=' + dataSet[i].id + ' value2=' + dataSet[i].approval_state + '></td>';
				htmlData += '<td data-title="방문유형">' + dataSet[i].visit_category + '</td>';
				htmlData += '<td data-title="업체명">' + dataSet[i].comp_nm + '</td>';
				htmlData += '<td data-title="방문목적">' + dataSet[i].visit_purpose + '</td>';
				htmlData += '<td data-title="신청자">' + dataSet[i].applicant + '</td>';
				htmlData += '<td data-title="방문자 정보" style="text-decoration: underline;" data-toggle="modal" class="guestInfo" name="guestInfo" value=' + dataSet[i].id + '>방문자 정보</td>';
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
        var pageBtnHtml = Paging('super_approval.index', data.pagination, data.query_string);
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

    //출입신청 건에 포함된 방문자 및 규칙 정보리스트 Modal
	function searchApplyMasterDetailHandler(dataSet) {
		//작업에 대한 작업자 상세 정보 Modal에 띄어야 함.
		console.log(dataSet.users);
		console.log(dataSet.userRuleInfoList);
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
        //출입상세정보 중 1명 row 선택시, 선택한 사람의 Rule 정보를 보임.
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

    //체크 개수, 승인, 반려 Modal 창에 값 전달하는 부분
    function modalOpen(val) {
        var cnt = $("input:checkbox[name=chk]:checked").length;

        $(".appr-name").html(val);
        $(".chkCnt").html(cnt);

        if (cnt == 0) {
            alert(val + " 진행할 건을 체크해주세요.");
            return false;
        } else {
            $('#signModal').modal({
                backdrop: 'static',
                keyboard: false
            });
            $('#signModal').modal('show');
        }
    }

	//event리스너
	function init() {
	    //Modal 닫기
	    $('.exitModal').unbind('click').click(function() {
	        var modalName = '#'+$(this).val();
            $(modalName).hide();
        });

		//체크박스 전체 선택,해제
		$("#checkall").unbind('click').click(function() {
			if ($("#checkall").prop("checked")) {
				$("input[name=chk]").prop("checked", true);
			} else {
				$("input[name=chk]").prop("checked", false);
			}
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

			//권한별 추가

			apiCallPost(urlMake('SEARCH'), setSearchFormHandler, dataSet);
		});

		$("#agree").unbind('click').click(function() {
			$('#status').val("승인");
			modalOpen($("#agree").html());
		});

		$("#reject").unbind('click').click(function() {
			$('#status').val("반려");
			modalOpen($("#reject").html());
		});

		//승인 및 반려 버튼 눌렀을 때, 체크된 작업ID에 대해 승인 및 반려
		$("#okBtn").unbind('click').click(function() {
			$('#signModal').modal('hide');

			var obj = $("[name=chk]");
			var chkArray = []; // 배열 선언
			var exit = false;

			// 체크된 체크박스의 value 값을 가지고 온다. value1 : ID , value2 : 승인상태
			$('input:checkbox[name=chk]:checked').each(function() {
				chkArray.push($(this).attr("value1"));

				if ($(this).attr("value2") != "대기") {
					alert("이미 승인 및 반려된 건은 수정할 수 없습니다.");
					exit = true;
				}
			});

			if (exit) {
				$(".modal-backdrop").hide();
				return false;
			}

			var dataSet = {};
			approval_date = getFormatDate(new Date(), "");
			approval_date = approval_date.split('/');
			dataSet['approval_date'] = approval_date[2] + "-" + approval_date[0] + "-" + approval_date[1];
			console.log(dataSet['approval_date']);
			dataSet['approval_state'] = $('#status').val();
			dataSet['lists'] = chkArray;

			apiCallPost(urlMake('SAVE'), updateApprovalStateHandler, dataSet);
		});

        //출입신청내역 중 출입상세정보 출력
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