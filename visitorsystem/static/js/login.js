$(document).ready(function() {
    function apiCallPost(url, controller, data, option) {
          $.ajax({
                    type: 'POST',
                    url: url,
                    async: false,
                    cache: false,
                    data: data
               }).success(function (data) {
                    controller(data);

               });
     }

    //type에 맞는 URL을 반환하는 함수
    function urlMake(url, args) {
        var reqUrl = "";
        switch (url) {
            case 'COMP':
                reqUrl = reqUrl + `/compsearch`;
                break;
            case 'JOIN':
                reqUrl = reqUrl + `/join`;
                break;
            case 'CHECK':
                reqUrl = reqUrl + `/check`;
                break;
        }
        return reqUrl;
    }

    //회사정보 조회 컨트롤러
    function compSearchController(dataSet) {
        dataSet = dataSet.msg
        //console.log(JSON.stringify(dataSet));

        //데이터가 있는 경우
        if(dataSet.biz_id != 0) {
           //조회된 정보 입력
            $('#inputBizId').val(dataSet.biz_id);
            $('#inputBizNo').val(dataSet.biz_no);
            $('#inputCompName').val(dataSet.comp_nm);
            $('#inputAddress').val(dataSet.addr_1);
            $('#inputAddress2').val(dataSet.addr_2);
            $('#inputTel').val(dataSet.tel_no);
            //ID로 포커스
            $('#lblComp').text("조회 되었습니다.");
            $('#inputID').focus();
        }else {
            $('#lblComp').text("등록되어 있지 않은 사업자 등록 번호 입니다.");
            $('#inputBizNo').focus();
            $('#inputBizId').val("0");
        }
    }

    //ID 중복 체크 컨트롤러
    function idCheckController(dataSet) {
        dataSet = dataSet.msg
        //console.log(JSON.stringify(dataSet));
        //데이터가 있는 경우
        if(dataSet.check == "true") {
            $('#lblcheckID').text("  이미 사용중인 ID 입니다");
        }else{
            //사용할 수 있는 ID
            $('#chkDuplicate').val("Y");
            $('#lblcheckID').text("  사용가능 한 ID 입니다.");
        }
    }

    //회원가입 컨트롤러
    function joinController(dataSet) {
        dataSet = dataSet.msg
        //console.log(JSON.stringify(dataSet));
        //가입완료 메시지, ID 넣어줌
        alert ("회원가입이 완료되었습니다.");
        
        //log id를 넣어준다.
        $('#login_id').val($('#inputID').val());
        
        //데이터 초기화
        $('#inputBizId').val     ("");
        $('#inputBizNo').val     ("");
        $('#inputCompName').val  ("");
        $('#inputAddress').val   ("");
        $('#inputAddress2').val  ("");
        $('#inputTel').val       ("");
        $('#inputID').val        ("");
        $('#inputName').val      ("");
        $('#inputBizId').val     ("");
        $('#inputPassword').val  ("");
        $('#inputPasswordCfm').val  ("");
        $('#inputEmail').val     ("");
        $('#inputPhone').val     ("");

        $('#chkDuplicate').val("");
        $('#lblcheckID').text("");
        $('#lblComp').text("");

        //닫기 클릭
        $('#btnClose').trigger("click");
    }

    //event리스너
    function init() {
        $('#confirmModal').click(function() {
            $('#alertModal').hide();
            setTimeout('location.reload()', 500);
        });

        //업체정보조회
        $('#btnCompSearch').click(function(e) {
            var dataSet = {};
            var bizNo = $('#inputBizNo').val();
            dataSet['biz_no'] = bizNo;
            apiCallPost(urlMake('COMP'), compSearchController, dataSet)
        });

        //ID 중복 조회
        $('#btnChechID').click(function(e) {
            var dataSet = {};
            var loginID = $('#inputID').val();
            if(!loginID){
                //값이 없음. ID를 넣어주세요
                $('#chkDuplicate').val("");
                $('#lblcheckID').text("ID를 넣어주세요");
                $('#inputID').focus();
                return
            }
            if(loginID.length < 4){
                $('#lblcheckID').text("ID는 4자리 이상 입력해주세요.");
                $('#chkDuplicate').val("");
                $('#inputID').focus();
                return ;
            }
            dataSet['login_id'] = loginID;
            apiCallPost(urlMake('CHECK'), idCheckController, dataSet)
        });

        //회원가입 & 회사정보 입력
        $('#btnJoin').click(function(e) {

            //중복확인 했는지 확인
            var checkDup = $('#chkDuplicate').val();

            if(!checkDup){
                //중복체크 확인
                $('#lblcheckID').text("ID중복 체크를 해주세요");
                $('#inputID').focus();
                return
            }
            //pw값이 같은지 확인
            if($('#inputPassword').val()!=$('#inputPasswordCfm').val()){
                $('#lblcheckID').text("패스워드 확인과 다릅니다. 확인 해 주세요.");
                $('#inputPassword').focus();
                return
            }
            //값들이 다 들어가 있는지 확인
            if(!$('#inputBizNo').val()){
                $('#lblComp').text("회사정보를 검색하거나 입력해주세요");
                $('#inputBizNo').focus();
                return
            }
            if(!$('#inputCompName').val()){
                $('#lblComp').text("회사정보를 검색하거나 입력해주세요");
                $('#inputCompName').focus();
                return
            }

            var id= $('#inputID').val();
            if(!id){
                $('#lblcheckID').text("ID를 넣어주세요");
                $('#inputID').focus();
                return
            }

            if(!$('#inputName').val()){
                $('#lblcheckID').text("성명을 넣어주세요");
                $('#inputName').focus();
                return
            }
            var password = $("#inputPassword").val();
            if(!password){
                $('#lblcheckID').text("패스워드를 넣어주세요");
                $('#inputPassword').focus();
                return
            }

            //비밀번호 유효성 체크
            var num = password.search(/[0-9]/g);
            var eng = password.search(/[a-z]/ig);
            var spe = password.search(/[`~!@@#$%^&*|₩₩₩'₩";:₩/?]/gi);
            if(password.length < 8 || password.length > 20){
              $('#lblcheckID').text("8자리~20자리 이내로 입력해주세요.");
              $('#inputPassword').focus();
              return ;
            }else if(num < 0 || eng < 0){
              $('#lblcheckID').text("영문,숫자를 혼합하여 입력해주세요.");
              $('#inputPassword').focus();
              return ;
            }

            if(!$('#inputEmail').val()){
                $('#lblcheckID').text("이메일을 넣어주세요");
                $('#inputEmail').focus();
                return
            }
            if(!$('#inputPhone').val()){
                $('#lblcheckID').text("핸드폰 번호를 넣어주세요");
                $('#inputPhone').focus();
                return
            }
            // 정규식 - 이메일 유효성 검사
            var regEmail = /([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
            if (!regEmail.test($('#inputEmail').val())){
                $('#lblcheckID').text("이메일 형식(abc@abc.com)이 아닙니다.");
                $('#inputEmail').focus();
                return
            }
            // 정규식 -전화번호 유효성 검사
            //var regPhone = /^((01[1|6|7|8|9])[1-9]+[0-9]{6,7})|(010[1-9][0-9]{7})$/;
            var regPhone = /^01(?:0|1|[6-9])-(?:\d{3}|\d{4})-\d{4}$/;
            if (!regPhone.test($('#inputPhone').val())){
                $('#lblcheckID').text("전화번호 형식(000-0000-0000)이 아닙니다.");
                $('#inputPhone').focus();
                return
            }

            var dataSet = {};
            dataSet['biz_id'] = $('#inputBizId').val();
            
            var bizid = $('#inputBizId').val();
            //console.log(JSON.stringify(dataSet));
            //console.log(bizid);

            dataSet['biz_no'] = $('#inputBizNo').val();
            dataSet['comp_nm'] = $('#inputCompName').val();
            dataSet['addr_1'] = $('#inputAddress').val();
            dataSet['addr_2'] = $('#inputAddress2').val();
            dataSet['tel_no'] = $('#inputTel').val();

            dataSet['login_id']  = $('#inputID').val();
            dataSet['login_pwd'] = $('#inputPassword').val();
            dataSet['name']      = $('#inputName').val();
            dataSet['phone']     = $('#inputPhone').val();
            dataSet['email']     = $('#inputEmail').val();

            //console.log(JSON.stringify(dataSet));

            apiCallPost(urlMake('JOIN'), joinController, dataSet)
        });
    }
    init();

});