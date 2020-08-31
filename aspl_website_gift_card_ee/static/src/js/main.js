odoo.define('aspl_website_gift_card.aspl_website_gift_card', function (require) {
    "use strict";


    function notification(type, message){
        var types = ['success','warning','info', 'danger'];
        if($.inArray(type.toLowerCase(),types) != -1){
        $('div.span4').remove();
        var newMessage = '';
        switch(type){
        case 'success' :
        newMessage = '<i class="fa fa-check" aria-hidden="true"></i> '+message;
        break;
        case 'warning' :
        newMessage = '<i class="fa fa-exclamation-triangle" aria-hidden="true"></i> '+message;
        break;
        case 'info' :
        newMessage = '<i class="fa fa-info" aria-hidden="true"></i> '+message;
        break;
        case 'danger' :
        newMessage = '<i class="fa fa-ban" aria-hidden="true"></i> '+message;
        break;
        }
        $('body').append('<div class="span4 pull-right" style="width: 20%;position: absolute;top: 15%;right: 1%;">' +
                   '<div class="alert alert-'+type+' fade">' +
                   newMessage+
                  '</div>'+
                '</div>');
           $(document).find(".alert").css('opacity',1).show();
           $(document).find(".alert").delay(2000).addClass("in").fadeOut(10000);
        }
    }

    $(document).ready(function () {
        var ajax = require('web.ajax');
        $('#giftcard_pin_form').validate({
            rules: {
                pin_no: {
                    required: true,
                    digits: true,
                },
                cfm_pin_no: {
                    required: true,
                    digits: true,
                    equalTo: "#pin_no"
                }
            }
        });
        $("#pin").keypress(function (event) {
            return isNumber(event, this)
        });
        $("#card_number").keypress(function (event) {
            return isNumber(event, this)
        });
        $("#gift_card_amount_pay #amount").keypress(function (event) {
            return isNumber(event, this)
        });
        function isNumber(evt, element) {
            var charCode = (evt.which) ? evt.which : event.keyCode;
            if (charCode == 13) {
                return true
            }
            if (charCode != 8 && charCode != 0 && (charCode < 48 || charCode > 57) && charCode != 46) {
                $("#errmsg").html("Enter Digits Only !!!").show().fadeOut("slow");
                return false;
            }

        };
        $("#set_pin").on('click', function (e) {
            var pin = $(this).parents('.modal-body').find("#pin_no").val();
            var confirmpin = $(this).parents('.modal-body').find("#cfm_pin_no").val();
            var card_id = $(this).parents('.modal-body').find("#card_id").val();
            if (pin && confirmpin) {
                if (pin != confirmpin) {
                    e.preventDefault();
                    $(this).parents('.modal-body').find("#error-set-pin").html("").html("Pin and confirm pin does not match");
                    return false;
                } else {
                    ajax.jsonRpc("/shop/set/pin", 'call', {'card_id': card_id, 'pin': pin})
                    .then(function (data) {
                        $('#SetPinModel').find("#pin_no").val('')
                        $('#SetPinModel').find("#cfm_pin_no").val('')
                        $('#SetPinModel').modal('hide');
                        notification('success','Successfully Pin Changed, Please login again..')
                        setTimeout(function(){
                        location.replace('/gift_card');
                        },3000)

                    });
                }
            }
            else {
                 $(this).parents('.modal-body').find("#pin_no").addClass('error-new');
                 $(this).parents('.modal-body').find("#cfm_pin_no").addClass('error-new');
            }
        });

        $("#set_pin_new").on('click', function (e) {
            var pin = $("#pin_no").val();
            var confirmpin = $("#cfm_pin_no").val();
            if (pin && confirmpin) {
                if (pin != confirmpin) {
                $("#error-set-pin").html("").html("Pin and confirm pin does not match");
                return false;
                } else {
                e.preventDefault();
                $('#SetPinModel').modal('show');
                $("#close_pin_model").on('click', function () {
                $('#giftcard_pin_form').submit();
                })
                }
            }
            else {
                $("#pin_no").addClass('error-new');
                $("#cfm_pin_no").addClass('error-new');
            }
        });

        $('#Section2 input').keydown(function (event) {
            var keyCode = (event.keyCode ? event.keyCode : event.which);
            if (keyCode == 13) {
                $('#check_card_details').trigger('click');
            }
        });
        $('#recharge_history input').keydown(function (event) {
            var keyCode = (event.keyCode ? event.keyCode : event.which);
            if (keyCode == 13) {
                $('#recharge_submit').trigger('click');
            }
        });
        $('#change_pin_form input').keydown(function (event) {
            var keyCode = (event.keyCode ? event.keyCode : event.which);
            if (keyCode == 13) {
                $('#change_pin').trigger('click');
            }
        });
        $('#gift_card_apply_form input').keydown(function (event) {
            var keyCode = (event.keyCode ? event.keyCode : event.which);
            if (keyCode == 13) {
                $('#gift_card_pay_form').trigger('click');
            }
        });
        $('#gift_card_amount_pay input').keydown(function (event) {
            var keyCode = (event.keyCode ? event.keyCode : event.which);
            if (keyCode == 13) {
                $('#gift_card_amount_pay_apply').trigger('click');
            }
        });
//        $("#check_card_details").on('click', function (e) {
//            e.preventDefault();
//            var card_number = $('#card_number').val();
//            var pin = $('#pin').val();
//            if (card_number && pin) {
//                ajax.jsonRpc("/card_details", 'call', {'card_number': card_number, 'pin': pin})
//                    .then(function (data) {
//                        var data = JSON.parse(data);
//                        if (data) {
//                            $('#balance').html("<h4>Current Balance  " + data.balance + data.symbol + "</h4>");
//                            $('#recharge_card_number').val(data.id);
//                            $('#change_pin_id').val(data.id);
//                            if (data.usage_history.length > 0) {
//                                for (var i = 0; i < data.usage_history.length; i++) {
//                                    $('#usage_history_table').append("<tr><td>" + data.usage_history[i].order_date + "</td>" + "<td>" + data.usage_history[i].order_name + "</td>" + "<td>" + data.usage_history[i].amount + data.symbol + "</td></tr>")
//                                }
//                            } else {
//                                $('#usage_history').html("<h4>No usage history found</h4>")
//                            }
//                            if (data.recharge_history.length > 0) {
//                                for (var i = 0; i < data.recharge_history.length; i++) {
//                                    $('#recharge_history_table').append("<tr><td>" + data.recharge_history[i].recharge_date + "</td>" + "<td>" + data.recharge_history[i].amount + data.symbol + "</td></tr>")
//                                }
//                            } else {
//                                $('#recharge_history_tab').html("<h4>No recharge history found</h4>")
//                            }
//                            $("#error-new").html("");
//                            $("#Section2 input").val("").removeClass('error-new');
//                            $('#CardDetails').modal('show');
//                            $("#close_model").on('click', function () {
//                                $('#CardDetails').modal('hide');
//                                location.reload();
//                            });
//                        }
//                        else {
//                            $("#card_number").addClass('error-new');
//                            $("#pin").addClass('error-new');
//                            $("#error-new").html("").html("Wrong card number or pin");
//                        }
//                    });
//            } else {
//                $("#card_number").addClass('error-new');
//                $("#pin").addClass('error-new');
//                $("#error-new").html("").html("Please enter card number and pin");
//            }
//        });
        $("#gift_card_pay").on('click', function () {
            $("#addgiftcard").modal('show');
        });
        $("#cancel_pay").on('click', function () {
            $("#addgiftcard").modal('hide');
            $('#gift_card_amount_pay input').val("");
            $('#gift_card_apply_form input').val("");
        });
        $("#gift_card_pay_form").on('click', function (e) {
            e.preventDefault();
            var card_number = $('#card_number').val();
            var pin = $('#pin').val();
            if (card_number && pin) {
                ajax.jsonRpc("/card_details", 'call', {'card_number': card_number, 'pin': pin})
                    .then(function (data) {
                        var data = JSON.parse(data);
                        if (data) {
                            $('#gift_card_apply_form').hide();
                            $('#gift_card_amount_pay').show();
                            $('#card_amount').val(data.balance);
                            $('#id').val(data.id);
                        }
                        else {
                            $("#error-gift-apply").html("").html("Wrong card number or pin");
                        }
                    });
            } else {
                $("#card_number").addClass('error-new');
                $("#pin").addClass('error-new');
                $("#error-gift-apply").html("").html("Enter card number or pin");
            }
        });
        $('#gift_card_amount_pay_apply').on('click', function () {
            var id = $('#id').val();
            var amount = $('#amount').val();
            if (amount && id) {
                ajax.jsonRpc("/apply_gift_card", 'call', {'id': id, 'amount': amount})
                    .then(function (data) {
                        var data = JSON.parse(data);
                        if (data.success) {
                            location.reload();
                        } else if (data.error) {
                            $("#error-gift-amount").html("").html("You can not enter amount higher than total amount");
                        } else {
                            $("#error-gift-amount").html("").html("Not enough balance available");
                        }
                    });
            }
            else {
                $("#amount").addClass('error-new');
                $("#error-gift-amount").html("").html("Enter amount");
            }
        });
        $("#cancel_amount_pay").on('click', function () {
            $('#gift_card_amount_pay').hide();
            $('#gift_card_apply_form').show();
            $('#gift_card_amount_pay input').val("");
            $('#gift_card_apply_form input').val("");
            $("#addgiftcard").modal('hide');

        });
        $("#recharge_submit").on('click', function () {
            var id = $('#card_id').val();
            var amount = $('#recharge_amount').val();
            if (amount && id) {
                ajax.jsonRpc("/recharge_gift_card", 'call', {'id': id, 'amount': amount})
                    .then(function (data) {
                        if (data) {
                            location.replace('/shop/cart');
                        }
                    });
            }
            else {
                $("#recharge_amount").addClass('error-new');
                $("#error-recharge").html("").html("Enter Amount");
            }
        });

        $('#card_details_tab').on('click', function () {
            $('#Section1 input').val("");
        });
        $('#buy_card_tab').on('click', function () {
            $('#Section2 input').val("");
        });
//        $('#change_pin').on('click', function () {
//            var current_pin = $('#change_pin_form #pin').val();
//            var pin = $('#change_pin_form #pin_no').val();
//            var cfm_pin = $('#change_pin_form #cfm_pin_no').val();
//            var id = $('#change_pin_form #change_pin_id').val();
//            if (current_pin && pin && cfm_pin && id) {
//                if (pin != cfm_pin) {
//                    $("#error-set-pin").html("").html("Pin and confirm pin does not match");
//                    return false;
//                } else {
//                    ajax.jsonRpc("/change_pin", 'call', {'id': id, 'current_pin': current_pin, 'pin': pin})
//                        .then(function (data) {
//                            if (data) {
//                                $("#error-set-pin").html("");
//                                $("#change_pin_form input").val("").removeClass('error-new');
//                                $("#success-set-pin").html("").html("pin successfully changed").css('color', 'green');
//                            }
//                            else {
//                                $("#error-set-pin").html("").html("Pin does not match");
//                                $("#change_pin_form #current_pin").addClass('error-new');
//                            }
//                        });
//                }
//            }
//            else {
//                $("#success-set-pin").html("");
//                $("#change_pin_form input").addClass('error-new');
//                $("#error-set-pin").html("").html("Enter required fields");
//            }
//        });
        var applied_card = $('#applied_card');
        var applied_card_counter;
        applied_card.popover({
            trigger: 'auto',
            animation: true,
            html: true,
            title: function () {
                return ("Applied Card");
            },
            container: 'body',
            placement: 'auto',
            template: '<div class="popover mycart-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
        }).on("mouseenter", function () {
            var self = this;
            clearTimeout(applied_card_counter);
            applied_card.not(self).popover('hide');
            applied_card_counter = setTimeout(function () {
                if ($(self).is(':hover') && !$(".mycart-popover:visible").length) {
                    $.get("/shop/applied_card", {'type': 'popover'})
                        .then(function (data) {
                           $(self).data("bs.popover").config.content = data;
                            $(self).popover("show");
                            $(".popover").on("mouseleave", function () {
                                $(self).trigger('mouseleave');
                            });
                        });
                }
            }, 100);
        }).on("mouseleave", function () {
            var self = this;
            setTimeout(function () {
                if (!$(".popover:hover").length) {
                    if (!$(self).is(':hover')) {
                        $(self).popover('hide');
                    }
                }
            }, 1000);
        });


//    Table Pagination

        $.fn.pageMe = function(opts){
            var $this = this,
                defaults = {
                    perPage: 7,
                    showPrevNext: false,
                    hidePageNumbers: false
                },
                settings = $.extend(defaults, opts);

            var listElement = $this;
            var perPage = settings.perPage;
            var children = listElement.children();
            var pager = $('.pager');

            if (typeof settings.childSelector!="undefined") {
                children = listElement.find(settings.childSelector);
            }

            if (typeof settings.pagerSelector!="undefined") {
                pager = $(settings.pagerSelector);
            }

            var numItems = children.size();
            var numPages = Math.ceil(numItems/perPage);

            pager.data("curr",0);

            if (settings.showPrevNext){
                $('<li><a href="#" class="prev_link">«</a></li>').appendTo(pager);
            }

            var curr = 0;
            while(numPages > curr && (settings.hidePageNumbers==false)){
                $('<li><a href="#" class="page_link">'+(curr+1)+'</a></li>').appendTo(pager);
                curr++;
            }

            if (settings.showPrevNext){
                $('<li><a href="#" class="next_link">»</a></li>').appendTo(pager);
            }

            pager.find('.page_link:first').addClass('active');
            pager.find('.prev_link').hide();
            if (numPages<=1) {
                pager.find('.next_link').hide();
            }
              pager.children().eq(1).addClass("active");

            children.hide();
            children.slice(0, perPage).show();

            pager.find('li .page_link').click(function(){
                var clickedPage = $(this).html().valueOf()-1;
                goTo(clickedPage,perPage);
                return false;
            });
            pager.find('li .prev_link').click(function(){
                previous();
                return false;
            });
            pager.find('li .next_link').click(function(){
                next();
                return false;
            });

            function previous(){
                var goToPage = parseInt(pager.data("curr")) - 1;
                goTo(goToPage);
            }

            function next(){
                goToPage = parseInt(pager.data("curr")) + 1;
                goTo(goToPage);
            }

            function goTo(page){
                var startAt = page * perPage,
                    endOn = startAt + perPage;

                children.css('display','none').slice(startAt, endOn).show();

                if (page>=1) {
                    pager.find('.prev_link').show();
                }
                else {
                    pager.find('.prev_link').hide();
                }

                if (page<(numPages-1)) {
                    pager.find('.next_link').show();
                }
                else {
                    pager.find('.next_link').hide();
                }

                pager.data("curr",page);
                pager.children().removeClass("active");
                pager.children().eq(page+1).addClass("active");

            }
            if (numPages<=1) {
                pager.hide();
            }
        };

        $(document).ready(function(){
          $('#recharge_history_table_body').pageMe({pagerSelector:'#recharge_history_page',showPrevNext:true,hidePageNumbers:false,perPage:10});
          $('#usage_history_table_body').pageMe({pagerSelector:'#usage_history_page',showPrevNext:true,hidePageNumbers:false,perPage:10});
        });
    });
});