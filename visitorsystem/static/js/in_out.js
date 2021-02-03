$(document).ready(function () {
     //URL에 해당하는 컨트롤러 호출
     function apiCallGet(url, controller, option) {
          $.ajax({
                    url: url,
                    method: "GET"
               })
               .done(function (dataSet) {
                    controller(dataSet, option);
               })
               .fail(function (xhr, status, errorThrown) {
                    console.log(errorThrown);
               })
     }

     function apiCallPost(url, controller, data, option) {
          $.ajax({
                    type: 'POST',
                    url: url,
                    async: false,
                    cache: false,
                    data: data
               })
               .success(function (data) {
                    controller(data);
               });
     }


     //type에 맞는 URL을 반환하는 함수
     function urlMake(url, args) {
          var reqUrl = "/inoutApply/";
          switch (url) {
               case "CAMERA_PLAY":
                    var cameraName = args[0]; //카메라 play reqUrl = `/camera/play?cameraName=${cameraName}`;
                    break;

               case 'CREATE':
                    reqUrl = reqUrl + `create`;
                    break;

               case 'INTERVIEW_SEARCH':
                    reqUrl = reqUrl + `interview/search`;
                    break;

               case 'RULE_SEARCH':
                    reqUrl = reqUrl + `rule/search`;
                    break;

               case 'RULE_SEARCH':
                    reqUrl = reqUrl + `rule/search`;
                    break;

                case 'RULE_VALID':
                    reqUrl = reqUrl + `rule/valid`;
                    break;

          }
          return reqUrl;
     }


     //규칙정보 컨트롤러
     function ruleSearchController(dataSet) {
          var dataSet = dataSet.msg;
          var theadContext = '';
          var append = '';


          newTr = `
         <tr class="hide">
             <td>
                     <input type="checkbox" id="checkbox" class="peer">
             </td>

             <td>
                <div class="form-group">
                     <input type="text" class="form-control" id="tvisitor" style="width:80%; float:left" >
                 </div>
             </td>

             <td>
                 <div class="form-group">
                     <input type="text" id="tphone"  class="form-control">
                 </div>
             </td>

             <td>
                <div class="form-group" >
                         <select id="" name="" class="form-control" disabled>
                             <option selected="selected" value="차량없음">차량없음</option>
                             <option value="승용차">승용차</option>
                             <option value="자동차">자동차</option>
                         </select>
                 </div>
             </td>
             <td><input type="text" class="form-control" disabled></td>
             `

          for (var i = 0; i < dataSet.length; i++) {
               var obj = dataSet[i];
               var type = obj.rule_type;
               var ruleName = obj.rule_name;
               console.log(ruleName)
               theadContext = theadContext+`<th style="">${ruleName}</th>`;

               if (type == '텍스트') {
                    append = append + `<td>
                                                 <div class="input-group">
                                                     <input type="text" class="form-control" disabled>
                                                 </div>
                                    </td>`
               } else if (type == '달력') {
                    append = append + `<td>
                                             <div class="input-group">
                                              <div class="input-group-addon bgc-white bd bdwR-0"><i class="ti-calendar"></i></div>
                                              <input type="text" class="form-control bdc-grey-200 start-date" placeholder="Datepicker" data-provide="datepicker" name ="inout_sdate" id="inout_sdate" disabled>
                                             </div>
                                         </td> `
               } else if (type == '파일') {
                    append = append + `<td><input id="input-b1" name="input-b1" type="file" class="file" data-browse-on-zone-click="true" disabled></td> `
               }
          }

          $('#thead').append(theadContext);
          newTr = newTr + append + '</tr>';

     }

     //출입신청 컨트롤러
     function applyController(dataSet) {

          console.log(JSON.stringify(dataSet));

     }

     //감독자조회 컨트롤러
     function interViewSearchController(dataSet) {

          console.log(JSON.stringify(dataSet));

     }

     //규칙검증 컨트롤러
     function rulevalidController(dataSet){
     }

     //event리스너
     function init() {
          const $tableID = $('#table');

          apiCallPost(urlMake('RULE_SEARCH'), ruleSearchController);


          $('#appylbtn').click(function () {
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

          $('#addUser').click(function (e) {
               const $clone = $tableID.find('tbody tr').last().clone(true).removeClass('hide table-line');
               if ($tableID.find('tbody tr').length === 0) {
                    $('#tableBody').append(newTr);
                    $('#tphone').keydown(function (e) {

                         if (e.keyCode == 13) {
                              $(this).val($(this).val().replace(/[^0-9]/g, "").replace(/(^02|^0505|^1[0-9]{3}|^0[0-9]{2})([0-9]+)?([0-9]{4})$/, "$1-$2-$3").replace("--", "-"));
                              var sdate = $('#inout_sdate').val();
                              var edate = $('#inout_edate').val();
                              var date = [];
                              var year, month, day;
                              var dataSet = {};

                              if (!sdate)
                                   return;

                              sdate = sdate.split('/')
                              year = sdate[2]; //년
                              month = sdate[0]; //월
                              day = sdate[1]; //일
                              dataSet['sdate'] = year+"-"+month+"-"+day;
                              date = [];

                              edate = edate.split('/')
                              year = edate[2]; //년
                              month = edate[0]; //월
                              day = edate[1]; //일
                              dataSet['edate'] = year+"-"+month+"-"+day;
                              data = [];

                              var userName = $(this).parent().parent().prev().children().children().val();
                              var userPhone = $(this).val();
                              dataSet['userName'] = userName;
                              dataSet['userPhone'] = userPhone;
                              console.log("테스트")
                              apiCallPost(urlMake('RULE_VALID'), rulevalidController , dataSet)

                         }
                    });

               }
               $tableID.find('table').append($clone);
          });

          $('#delUser').click(function (e) {
               var checkbox = $('input[id=checkbox]:checked');
               var tdArray = new Array();

               checkbox.each(function (i) {
                    var tr = checkbox.parent().parent().eq(i);
                    var td = tr.children();
                    setTimeout(function () {
                         tr.remove();
                    }, 100);

               });

          });

          $('#interviewSearch').click(function (e) {
               var dataSet = {};
               var interviewName = $('#interviewInput').val();
               dataSet['interviewName'] = interviewName;
               apiCallPost(urlMake('INTERVIEW_SEARCH'), interViewSearchController, dataSet)

          });


          var autoHypenPhone = function (str) {
               str = str.replace(/[^0-9]/g, '');
               var tmp = '';
               if (str.length < 4) {
                    return str;
               } else if (str.length < 7) {
                    tmp += str.substr(0, 3);
                    tmp += '-';
                    tmp += str.substr(3);
                    return tmp;
               } else if (str.length < 11) {
                    tmp += str.substr(0, 3);
                    tmp += '-';
                    tmp += str.substr(3, 3);
                    tmp += '-';
                    tmp += str.substr(6);
                    return tmp;
               } else {
                    tmp += str.substr(0, 3);
                    tmp += '-';
                    tmp += str.substr(3, 4);
                    tmp += '-';
                    tmp += str.substr(7);
                    return tmp;
               }

               return str;
          }


     }

     init();

})