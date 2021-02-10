


$(document).ready(function() {


  // 포인트 숫자만 입력, comma 찍기
  $(function() {
    $('#userCount').on('keyup', function() {
      if ($(this).val() != null && $(this).val() != '') {
        var tmps = parseInt($(this).val().replace(/[^0-9]/g, '')) || '0';
        var tmps2 = tmps.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1,');
        $(this).val(tmps2);

        var sum = 0,
        userCount = parseInt($('#userCount').val().replace(/,/g, '') || '0');

        if(userCount <= 100){
            basicPrice = 1.2 * userCount
            var _result_basicPrice = Math.ceil(basicPrice).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1,'); //소수점 반올림 하고 comma 찍기
            $('#basicPrice').text(_result_basicPrice);
            $('#basicPriceBox').css({"border": "2px #ea9b95 solid"});
            $('#standardPriceBox').css({"border": "0"});
            $('#enterprisePriceBox').css({"border": "0"});

        }else if(userCount <= 500){
            standardPrice = 1 * userCount
            var _result_standardPrice = Math.ceil(standardPrice).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1,'); //소수점 반올림 하고 comma 찍기
            $('#standardPrice').text(_result_standardPrice);
            $('#basicPriceBox').css({"border": "0"});
            $('#standardPriceBox').css({"border": "2px #ea9b95 solid"});
            $('#enterprisePriceBox').css({"border": "0"});

        }else{
            enterprisePrice = 0.8 * userCount
            var _result_enterprisePrice = Math.ceil(enterprisePrice).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1,'); //소수점 반올림 하고 comma 찍기
            $('#enterprisePrice').text(_result_enterprisePrice);
            $('#basicPriceBox').css({"border": "0"});
            $('#standardPriceBox').css({"border": "0"});
            $('#enterprisePriceBox').css({"border": "2px #ea9b95 solid"});
        }
      }
    });
  });
});