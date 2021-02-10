$(document).ready(function(){

//    $("#visit_sdate").datepicker('setDate', new Date())
//    $("#visit_edate").datepicker('setDate', new Date())
//
//    $("#visit_sdate").setDefaults({
//        dateFormat: 'yy-mm-dd' //Input Display Format 변경
//    });

    //체크박스 전체 선택,해제
    $("#checkall").click(function(){
        if($("#checkall").prop("checked")){
            $("input[name=chk]").prop("checked",true);
        }else{
            $("input[name=chk]").prop("checked",false);
        }
    })

    //체크 개수, 승인, 반려 Modal 창에 값 전달하는 부분
    function modalOpen(val) {
        var cnt = $("input:checkbox[name=chk]:checked").length
        $(".appr-name").html(val)
        $(".chkCnt").html(cnt)
    }

    $("#agree").click(function () {
        modalOpen($("#agree").html())
    })

    $("#reject").click(function () {
        modalOpen($("#reject").html())
    })

    //승인 및 반려 버튼 눌렀을 때, 체크된 작업ID에 대해 승인 및 반려
    $("#okBtn").click(function (){
		var obj = $("[name=chk]");
        var chkArray = new Array(); // 배열 선언

        //// 체크된 체크박스의 value 값을 가지고 온다.
        $('input:checkbox[name=chk]:checked').each(function() {
            chkArray.push(this.value);
        });
    })

//    //조회시, 달령 포맷 수정
//    $("#searchBtn").click(function(){
//        var sdate = $('#visit_sdate').val();
//        var edate = $('#visit_edate').val();
//
//        var year, month, day;
//        var dataSet = {};
//
//        if (!sdate || !edate){
//            alert('날짜를 입력해주세요')
//            return;
//        }
//
//        sdate = sdate.split('/')
//        year = sdate[2]; month = sdate[0]; day = sdate[1];
//        dataSet['sdate'] = year + "-" + month + "-" + day;
//
//        edate = edate.split('/')
//        year = edate[2]; month = edate[0]; day = edate[1]; //일
//        dataSet['edate'] = year + "-" + month + "-" + day;
//
//        return dataSet;
//    })

})
