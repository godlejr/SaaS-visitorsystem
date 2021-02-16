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
        var reqUrl = "/commonCode/";
        switch (url) {
            case 'SAVE':
                reqUrl = reqUrl + args + `/save`;
                break;
            case 'EDIT':
                reqUrl = reqUrl + args + `/edit`;
                break;
            case 'DELETE':
                reqUrl = reqUrl + args+ `/delete`;
                break;

        }
        return reqUrl;
    }


    //규칙생성 및 저장 컨트롤러
    function saveController(dataSet) {
        $('#modalContent').text(dataSet.msg);
        console.log(dataSet.msg);
        $('#alertModal').show();

    }

    //규칙수정 컨트롤러
    function editController(dataSet) {

        $('#site_name').val(dataSet.msg.site_name);
        $('#site_type').val(dataSet.msg.site_type);
        $('#site_duedate').val(dataSet.msg.site_duedate);
        $('#site_desc').val(dataSet.msg.site_desc);
    }

    //규칙삭제 컨트롤러
    function deleteController(dataSet) {
        location.reload();
    }

    //event리스너
    function init() {
        $('#confirmModal').click(function() {
            $('#alertModal').hide();
            setTimeout('location.reload()', 500);

        });

        //사업장
        $('#siteCreteBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['site_name']

            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
                $('#' + key).val('');

                $('#' + key).attr('disabled', false);
            }

        });

        $('.siteEditBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            $('#site_name').attr('disabled', true);
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('EDIT','site'), editController, dataSet);

        });

        $('.siteDelBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('DELETE','site'), deleteController, dataSet);
        });

        $('#siteSaveBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['site_name']


            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
                var value = $('#' + key).val()
                dataSet[key] = value;
            }

            apiCallPost(urlMake('SAVE','site'), saveController, dataSet)
        });


        //정문
         $('#gateCreteBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['gate_name']

            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];

                 $('#' + key).val('');

                $('#' + key).attr('disabled', false);
            }

        });

        $('.gateEditBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            $('#gate_name').attr('disabled', true);
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('EDIT','gate'), editController, dataSet);

        });

        $('.gateDelBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('DELETE','gate'), deleteController, dataSet);
        });

        $('#gateSaveBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['gate_name', 'site_type']


            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
                var value = $('#' + key).val()
//                if (key == 'site_type' && value == '선택')
//                    value = 'text';

                dataSet[key] = value;
            }

            apiCallPost(urlMake('SAVE','gate'), saveController, dataSet)
        });

        //코드
          $('#codeCreteBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['code_name']

            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
//                if (key == 'site_duedate' || key == 'site_type')
//                    $('#' + key).val('선택');
//                else
                $('#' + key).val('');

                $('#' + key).attr('disabled', false);
            }

        });

        $('.codeEditBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            $('#code_name').attr('disabled', true);
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('EDIT','code'), editController, dataSet);

        });

        $('.codeDelBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('DELETE','code'), deleteController, dataSet);
        });

        $('#codeSaveBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['code_name', 'code_type']


            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
                var value = $('#' + key).val()
//                if (key == 'site_type' && value == '선택')
//                    value = 'text';

                dataSet[key] = value;
            }

            apiCallPost(urlMake('SAVE','code'), saveController, dataSet)
        });
    }

    init();

});