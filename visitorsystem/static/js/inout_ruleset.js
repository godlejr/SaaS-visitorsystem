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
        var reqUrl = "/inoutRuleset/";
        switch (url) {
            case 'SAVE':
                reqUrl = reqUrl + `save`;
                break;
            case 'EDIT':
                reqUrl = reqUrl + `edit`;
                break;
            case 'DELETE':
                reqUrl = reqUrl + `delete`;
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

        $('#rule_name').val(dataSet.msg.rule_name);
        $('#rule_type').val(dataSet.msg.rule_type);
        $('#rule_duedate').val(dataSet.msg.rule_duedate);
        $('#rule_desc').val(dataSet.msg.rule_desc);
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

        $('#creteBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['rule_name', 'rule_type', 'rule_duedate', 'rule_desc']

            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
                if (key == 'rule_duedate' || key == 'rule_type')
                    $('#' + key).val('선택');
                else
                    $('#' + key).val('');

                $('#' + key).attr('disabled', false);
            }

        });

        $('.editBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            $('#rule_name').attr('disabled', true);
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('EDIT'), editController, dataSet);

        });

        $('.delBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            dataSet['id'] = $(this).parents("li").attr('id');
            apiCallPost(urlMake('DELETE'), deleteController, dataSet);
        });

        $('#saveBtn').click(function() {
            var htmlIdList = [];
            var dataSet = {};
            htmlIdList = ['rule_name', 'rule_type', 'rule_duedate', 'rule_desc']


            for (var i = 0; i < htmlIdList.length; i++) {
                var key = htmlIdList[i];
                var value = $('#' + key).val()
                if (key == 'rule_type' && value == '선택')
                    value = 'text';

                dataSet[key] = value;
            }

            apiCallPost(urlMake('SAVE'), saveController, dataSet)
        });
    }

    init();

});