$(document).ready(function() {

    function apiCallPost(url, Handler, data, option) {
          $.ajax({
                    type: 'POST',
                    url: url,
                    async: false,
                    cache: false,
                    data: data
               }).success(function (data) {
                    Handler(data);

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


    function saveHandler(dataSet) {
        $('#modalContent').text(dataSet.msg);
        $('#alertModal').show();

    }

    //규칙삭제 컨트롤러
    function deleteHandler(dataSet) {
        $('#modalContent').text(dataSet.msg);
        $('#alertModal').show();
    }

    //규칙수정 컨트롤러
    function siteEditHandler(dataSet) {
        $('#site_id').val(dataSet.msg.site_id);
        $('#site_name').val(dataSet.msg.site_name);
    }

    function gateEditHandler(dataSet) {
        $('#gate_id').val(dataSet.msg.gate_id);
        $('#gate_name').val(dataSet.msg.gate_name);
        $('#site_type').val(dataSet.msg.site_type);
    }

    function codeEditHandler(dataSet) {
        $('#code_id').val(dataSet.msg.code_id);
        $('#code_name').val(dataSet.msg.code_name);
        $('#code_type').val(dataSet.msg.code_type);
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
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('EDIT','site'), siteEditHandler, dataSet);

        });

        $('.siteDelBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('DELETE','site'), deleteHandler, dataSet);
        });

        $('#siteSaveBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['site_name','site_id']


            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
                var value = $('#' + key).val()
                dataSet[key] = value;
            }

            apiCallPost(urlMake('SAVE','site'), saveHandler, dataSet)
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
            dataSet['id'] = $(this).parents("li").attr('id');

            apiCallPost(urlMake('EDIT','gate'), gateEditHandler, dataSet);

        });

        $('.gateDelBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('DELETE','gate'), deleteHandler, dataSet);
        });

        $('#gateSaveBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['gate_name', 'site_type','gate_id']


            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
                var value = $('#' + key).val()
//                if (key == 'site_type' && value == '선택')
//                    value = 'text';

                dataSet[key] = value;
            }

            apiCallPost(urlMake('SAVE','gate'), saveHandler, dataSet)
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
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('EDIT','code'), codeEditHandler, dataSet);

        });

        $('.codeDelBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('DELETE','code'), deleteHandler, dataSet);
        });

        $('#codeSaveBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['code_name', 'code_type', 'code_id']


            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
                var value = $('#' + key).val()
//                if (key == 'site_type' && value == '선택')
//                    value = 'text';

                dataSet[key] = value;
            }

            apiCallPost(urlMake('SAVE','code'), saveHandler, dataSet)
        });
    }

    init();

});