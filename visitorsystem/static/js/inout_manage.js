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
		var reqUrl = "/inoutManage/";
		switch (url) {
			case 'SEARCH':
				reqUrl = reqUrl + 'search';
				break;

		}
		return reqUrl;
	}
     function dataToString(data,userAuth) {
        var res = "visit_sdate="+ data.visit_sdate  + "&visit_edate=" + data.visit_edate  +
                                    "&visit_category=" + data.visit_category  + "&visit_purpose=" + data.visit_purpose  + "&visit_dept=" + data.visit_dept +
                                    "&comp_nm=" + data.comp_nm  + "&visit_interviewer=" + data.visit_interviewer  +
                                    "&visit_user=" + data.visit_user  +
                                    "&pages=" + data.pages ;

        //관리자
        if (userAuth == '9990') {
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

//하다말음 - 김동주
	function setSearchFormHandler(data) {
		var dataSet = data.msg;

        //조회 결과에 따른 방문신청정보 Table Set
		if (dataSet.length < 1) {
			$('.applyListTable>tbody').html('<td colspan="12" style="text-align:center"><text> 조회된 내역이 없습니다. </text></td>');
		} else {
			var htmlData = '';
			for (var i = 0; i < dataSet.length; i++) {
				htmlData += '<tr value1="' + dataSet[i].master_id +  '">';
				htmlData += '<td data-title="방문유형">' + dataSet[i].visit_category + '</td>';
				htmlData += '<td data-title="업체명">' + dataSet[i].comp_nm + '</td>';
				htmlData += '<td data-title="방문목적">' + dataSet[i].visit_purpose + '</td>';
				htmlData += '<td data-title="방문자">' + dataSet[i].visit_user + '</td>';
                htmlData += '<td data-title="접견자">' + dataSet[i].visit_interviewr + '</td>';
                htmlData += '<td data-title="접견부서">' + dataSet[i].visit_dept + '</td>';
				htmlData += '<td data-title="방문일시">' + dataSet[i].visit_sdate + '</td>';
				htmlData += '<td data-title="퇴장일시">' + dataSet[i].visit_edate + '</td>';
				htmlData += '<td data-title="신청사업장">' + dataSet[i].site_nm + '</td>';
				htmlData += '<td data-title="신청출입문">' + dataSet[i].site_nm2 + '</td>';
				htmlData += '</tr>';
			}


			$('.applyListTable>tbody').html(htmlData);
		}

        // 조회 결과에 따른 페이지 버튼 Set (endpoint, Pagination 정보 객체, 쿼리 스트링)
        var pageBtnHtml = Paging('inout_manage.index', data.pagination, data.query_string, data.searchCondition, data.userAuth);
        $('#pagination').html(pageBtnHtml);

        init();
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

    var sdate = $('#visit_sdate').val();
    var edate = $('#visit_edate').val();

    if (sdate=="") {
        $('#visit_sdate').val(getFormatDate(new Date(), "sdate"));
    }

    if (edate==""){
        $('#visit_edate').val(getFormatDate(new Date(), "edate"));
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

			if (!sdate || !edate) {
				return;
			}

			sdate = sdate.split('/');
			edate = edate.split('/');
			dataSet['visit_sdate'] = sdate[2] + "-" + sdate[0] + "-" + sdate[1];
			dataSet['visit_edate'] = edate[2] + "-" + edate[0] + "-" + edate[1];
            dataSet['visit_user'] = $('#visit-user').val();
            dataSet['visit_interviewer'] = $('#visit-interviewer').val();
			dataSet['visit_category'] = $('#type').val();
			dataSet['visit_purpose'] = $('#visit-purpose').val();
			dataSet['comp_nm'] = $('#comp-nm').val();
			dataSet['visit_dept'] = $('#visit-dept').val();
			dataSet['page'] = 1;    //Search 버튼 누르면 초기페이지는 1번째로 Set
			dataSet['pages'] = 10;  //한 페이지에 조회되는 개수

            //site_id가 없으면 undefined
			dataSet['site_id'] = $("#location").val();

			apiCallPost(urlMake('SEARCH'), setSearchFormHandler, dataSet);
		});
	}

	init();
});