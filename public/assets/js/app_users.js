'use strict';
$(function(){
  toastr.options = {
              "closeButton": true,
              "debug": false,
              "newestOnTop": false,
              "progressBar": false,
              "positionClass": "toast-top-right",
              "preventDuplicates": false,
              "onclick": null,
              "showDuration": "300",
              "hideDuration": "1000",
              "timeOut": "5000",
              "extendedTimeOut": "1000",
              "showEasing": "swing",
              "hideEasing": "linear",
              "showMethod": "fadeIn",
              "hideMethod": "fadeOut"
  };

  $('#expired_on').datepicker({
      format: 'yyyy-mm-dd',
      container: '#bonusForm',
      startDate: '1d'
  });

  $('#bonus_credit').keypress(function(e) {
      var verified = (e.which === 8 || e.which === undefined || e.which === 0) ? null : String.fromCharCode(e.which).match(/[^0-9]/);
      if (verified) {e.preventDefault();}
  });

  $.fn.dataTableExt.oApi.fnSetFilteringDelay = function ( oSettings, iDelay ) {
        var _that = this;

        if ( iDelay === undefined ) {
            iDelay = 250;
        }

        this.each( function ( i ) {
            $.fn.dataTableExt.iApiIndex = i;
            var
                oTimerId = null,
                sPreviousSearch = null,
                anControl = $( 'input', _that.fnSettings().aanFeatures.f );

            anControl.unbind( 'keyup search input' ).bind( 'keyup search input', function() {
                  if ((anControl.val().trim().length === 0 || anControl.val().trim().length >= 2) && (sPreviousSearch === null || sPreviousSearch !== anControl.val())) {

                    window.clearTimeout(oTimerId);
                    sPreviousSearch = anControl.val();
                    oTimerId = window.setTimeout(function() {
                        $.fn.dataTableExt.iApiIndex = i;
                        _that.fnFilter( anControl.val() );
                    }, iDelay);
                }
            });

            return this;
        } );
        return this;
    };

    $.extend( $.fn.dataTable.defaults, {
        searching: true,
        ordering:  true
    } );

    var tableData = $('#example').dataTable( {
        "processing": false,
        "serverSide": true,
        "ajax": API.appUsers,
        "oLanguage": {
                "sEmptyTable": "No record found."
                },
        "aoColumnDefs": [
            {
                "aTargets": [5],
                "mRender": function (data, type, full) {
                    if (data){
                        return '<label class="btn btn-success" style="cursor: default;">Paid</label>';
                    }
                    else{
                        return '<label class="btn btn-warning" style="cursor: default;">Failed</label>';
                    }
                },
            },
             {  "aTargets": [6],
                   "bSearchable": false,
                   "sType": 'date',
                    "mRender": function (data, type, full) {
                        return "<div class= date>" + moment.tz(data, "America/Chicago").format('MM-DD-YYYY LTS') + "<div>";
                    }
            },
            {

                "aTargets": [7],
                "mRender": function (data, type, full) {
                    return '<div class="action-buttons">' +
                        '<a class="blue edit_user" href="javascript:void(0)" title="Edit User"><input type="hidden" value="'+data+'"><i class="fa fa-pencil-square-o bigger-130"></i> </a>' +
                        '<a class="remove_user" href="javascript:void(0)" title="Delete User" data-first_name="'+full[0]+'" data-last_name="'+full[1]+'"><input type="hidden" value="'+data+'"><i class="ace-icon glyphicon glyphicon-remove bigger-130 red"></i> </a>' +
                        '<a class="change_plan" href="javascript:void(0)" title="Change Plan" data-id="'+data+'"><i class="ace-icon fa fa-usd bigger-130 green"></i> </a>' +
                        '<a class="add_bonus" href="javascript:void(0)" title="Add Bonus" data-id="'+data+'"><i class="ace-icon glyphicon glyphicon-plus bigger-130 orange"></i> </a>' +
                        '<a class="add_coupon" href="javascript:void(0)" title="Add Coupon" data-id="'+data+'"><i class="ace-icon glyphicon glyphicon-tag bigger-130 purple"></i> </a>' +
                        '<a class="request_leads" href="javascript:void(0)" title="Request Leads" data-id="'+data+'"><i class="ace-icon request-leads-icon bigger-130"></i> </a></div>';
                },
            }
        ],
        "aoColumns": [
                 null, null, null, null, null, null, null, { "bSortable": false }
                ],
        "iDisplayLength": 25,
        "bInfo": true,
        "aaSorting": [[ 6, "desc" ]],
        "bLengthChange": false,
        "pagingType": "full_numbers",
        "fnPreDrawCallback": function() {
            // gather info to compose a message
            showLoading();
            return true;
        },
        "fnDrawCallback": function() {
            // in case your overlay needs to be put away automatically you can put it here
            hideLoading();
        }
    }).fnSetFilteringDelay();
        $('a.add_user').on('click',function(){
        $("#signupForm").validate().resetForm();
        $("#email").prop('disabled', false);
        $('.btn-edit').addClass('hide');
        $('.btn-save').removeClass('hide');
        $('#myModalLabel').html('<i class="fa fa-user-plus white"></i>Add User');
        $('#userModal').modal({ keyboard: true });

    });

    $("#bonusForm").validate({
        rules: {
            bonus_credit: {
                required:true,
                maxlength: 6,
                onlyNumber:true
            },
            expired_on: {
                required:true
            }
        },
        messages: {
            bonus_credit:{
                required: "Number of bonus credits is required.",
                maxlength: "Please use between 1 and 6 characters."

            } ,
            expired_on: {
                required: "Expiry Date is required."
            }
        }
    });

    $("#signupForm").validate({
        rules: {
            firstname: {
                required:true,
                maxlength: 50
            },
            lastname: {
                required:true,
                maxlength: 50
            },
            email: {
                required: true,
                validemail: true,
                remote:{
                    url: API.checkMail,
                    data: { email: function() {
                            return $( "#email" ).val();
                          },
                     },
                    beforeSend: function(){
                        $('.btn-save').prop('disabled',true);
                    },
                    complete: function(){
                        $('.btn-save').prop('disabled',false);
                    },
                }
            }
        },
        messages: {
            firstname:{
                required: "First Name is required.",
                maxlength: "Please use between 0 and 50 characters."
            } ,
            lastname: {
                required: "Last Name is required.",
                maxlength: "Please use between 0 and 50 characters."
            } ,
            email: {
                required:"Email is required.",
                validemail: "Email is invalid.",
                remote: "This user has already been added to system."
            }
        }
    });
    $( '#email, #first_name, #last_name' ).keypress(function( event ) {
      if ( event.which === 13 ) {
         event.preventDefault();

      }

    });

    $('.btn-save').on('click',function(e){
        if(!$("#signupForm").valid()){
            return false;
        }else{
            $('#userModal').modal('hide');
            showLoading();
            $.ajax({
                url: API.addUserURL,
                type: 'POST',
                 headers: {
                                "Authorization":"Token " + USER.token
                            },
                data:{
                      first_name: $('#first_name').val(),
                      last_name: $('#last_name').val(),
                      email: $('#email').val()
                    },
                success: function(result) {
                    hideLoading();
                    toastr.clear();
                    toastr.success("You have invited user successfully.");
                    tableData.fnSort( [ [6,'desc'] ] );

                },
                error: function(result){
                    hideLoading();
                    toastr.clear();
                    toastr.error("You have failed to add new user. Please try again.");
                    tableData.fnSort( [ [6,'desc'] ] );


                }
            });
        }
        return false;
    });

    function changePlan(){
        showLoading();
        $.ajax({
            url: API.updatePlan + '?plan_id=' + $('#plans option:selected').data('id'),
            type: 'POST',
             headers: {
                            "Authorization":"Token " + USER.token
                        },
            data:{ user_id: $('#changePlanForm #user_id').val() },
            success: function(result) {
                hideLoading();
                toastr.clear();
                var message = "You’ve just updated " + $('#user_first_name').val() + " " + $('#user_last_name').val() +  "‘s pricing plan successfully.";
                toastr.success(message);
                tableData.fnSort( [ [6,'desc'] ] );
                $('#changePlanModal').modal('hide');
            },
            error: function(result){
                hideLoading();
                toastr.clear();
                toastr.error("There is a problem of charging user " + $('#user_first_name').val() + " " + $('#user_last_name').val() +  " for the first month. Please try later.");
                tableData.fnSort( [ [6,'desc'] ] );


            }
        });
    }

    $('#change_plan').on('click',function(e){
        var userId = $(this).closest('#changePlanForm').find('#user_id').val();
        if(!$("#changePlanForm").valid()){
            return false;
        }
        else{
            if ($('#plans option:selected').val() === 'free-plan') {
                $.post(API.checkUserPlan + '?user_id=' + userId).done(function(data){
                  showFreePlanMessage();
                }).fail(function(data) {
                    changePlan();
                }).always(function(){
                });
            }
            else {
                changePlan();
            }
        }
        return false;
    });

      $('#add_bonus').on('click',function(e){
        if(!$("#bonusForm").valid()){
            return false;
        }
        else{
            showLoading();
            $.ajax({
                url: API.addBonus,
                type: 'POST',
                 headers: {
                                "Authorization":"Token " + USER.token
                            },
                data:{
                    bonus_credit:$('#bonus_credit').val(),
                    expired_on:$('#expired_on').val(),
                    user_id:$('#bonusForm #user_id').val()
                },
                success: function(result) {
                    toastr.clear();
                    toastr.success("You've just updated " + $('#user_first_name').val() + " " + $('#user_last_name').val() +  "'s bonus credits successfully");
                    tableData.fnSort( [ [6,'desc'] ] );
                    $('#bonusModal').modal('hide');


                },
                error: function(result){
                    toastr.clear();
                    toastr.error("Oops, something went wrong! Please try again!");
                    tableData.fnSort( [ [6,'desc'] ] );


                }
            });
        }
        return false;
    });

    $('.btn-close').on('click',function(e){
        $("#signupForm").validate().resetForm();
    });
    $('#userModal').on('hidden.bs.modal', function () {
          $("#signupForm").validate().resetForm();
      });
    $('.btn-edit').on('click',function(e){
        if(!$("#signupForm").valid()){
            return false;
        }else{
            $('#userModal').modal('hide');
            $.ajax({
                url: API.users + $('#user_id').val() +'/',
                type: 'PUT',
                 headers: {
                                "Authorization":"Token " + USER.token
                            },
                data:{
                    first_name:$('#first_name').val(),
                    last_name:$('#last_name').val(),
                    company: $('#company').val()
                },
                success: function(result) {
                    toastr.clear();
                    toastr.success("User has been edited successfully.");
                    tableData.fnSort( [ [6,'desc'] ] );

                },
                error: function(result){
                    toastr.clear();
                    toastr.error("Oops, something went wrong! Please try again!");
                    tableData.fnSort( [ [6,'desc'] ] );


                }
            });
        }
        return false;
    });

    $(document).on('click','.edit_user', function(e){
        var id = $(this).find('input').val();

        $.get(API.users + id).done(function(data){

            $('#user_id').val(id);
            $('#first_name').val(data.first_name);
            $('#last_name').val(data.last_name);
            $('#company').val(data.company);
            $('#email').val(data.email);
            $('#token').val(data.token);
            $('.btn-save').addClass('hide');
            $('.btn-edit').removeClass('hide');
            $('#email').prop('disabled',true);
            $('#myModalLabel').html('<i class="fa fa-user-plus white"></i>Edit User');
            $('#userModal').modal({ keyboard: false });
        });
    });

    $(document).on('click','.add_bonus', function(e){
        var id = $(this).data('id');

        $.get(API.users + id).done(function(data){
            $('#bonusForm #user_id').val(id);
            $('#user_first_name').val(data.first_name);
            $('#user_last_name').val(data.last_name);
            $('#bonus_credit').val(data.bonus_credit);
            $('#expired_on').val(data.expired_on);
            $('#bonusModal').modal({ keyboard: false });
        });
    });

    $(document).on('click','.change_plan', function(e){
        var id = $(this).data('id');
        $('#changePlanForm #user_id').val(id);

        $.get(API.users + id).done(function(data){
            $('#user_first_name').val(data.first_name);
            $('#user_last_name').val(data.last_name);
            var plan = data.plan;
            if (plan !== '') {
                $('#current_plan').val(plan.chargify_id);
            }
            $.ajax({
                url: API.products + '?limit=4',
                type: 'GET',
                headers: {
                    "Authorization":"Token " + USER.token
                },
                success: function(result) {
                    var options = '';
                    for (var i = result.results.length - 1; i >= 0; i--) {
                        var option = result.results[i];
                        var selected = '';
                        if (plan != '' && plan.handle == option.handle) {
                            selected = ' selected ';
                            $('#monthly_leads').val(option.credit);
                            $('#monthly_charge').val(option.price);
                        }
                        options += '<option data-price="'+ option.price +'" data-id="'+ option.chargify_id +'" ' + selected + ' data-credit="'+ option.credit +'" value="'+ option.handle +'">' + option.name + '</option>';
                    }
                    if(plan == ''){
                        $('#monthly_leads').val($('#plans option:selected').data('credit'));
                        $('#monthly_charge').val($('#plans option:selected').data('price'));
                    }
                    $('#plans').html(options);
                    $('#change_plan').addClass('hide');
                    $('#changePlanModal').modal({ keyboard: false });
                },
                error: function(result){
                }
            });

        });
    });

    $(document).on('click','.add_coupon', function(e){
        var id = $(this).data('id');
        $('#updateCouponForm #user_id').val(id);

        $.get(API.users + id).done(function(data){
            $('#couponModal').modal({ keyboard: false });
            $("#updateCouponForm").validate().resetForm();
            $('.coupon-form').addClass('hide');
            if (data.coupon_code && data.coupon_code !== '' && data.coupon_code !== null) {
              $('.coupon-code').text(data.coupon_code);
              $('#remove_coupon').parent().removeClass('hide');
            } else {
              $('.coupon-code').text('NONE');
              $('#remove_coupon').parent().addClass('hide');
            }

            $('#coupon_code').val(data.coupon_code);

        });
    });

    $(document).on('change','#plans', function(){
        if ($(this).find('option:selected').data('id') !== $('#current_plan').val()) {
            $('#change_plan').removeClass('hide');
        }
        else{
            $('#change_plan').addClass('hide');
        }
        $('#monthly_leads').val($(this).find('option:selected').data('credit'));
        $('#monthly_charge').val($(this).find('option:selected').data('price'));
    });

    function showFreePlanMessage(){
            bootbox.dialog({
              message: 'This user has more than one collection. So please ask user to remove some collections and remain only one before downgrading to Free Plan.',
              closeButton: true,
              className: "error-modal",
              buttons: {}
          });
        }

    function deleteUserModal(id){
        var message = "Are you sure you want to delete user " + $('#user_first_name').val() + " " + $('#user_last_name').val() +  " from our system?";
        var success_message = "You’ve just deleted user " + $('#user_first_name').val() + " " + $('#user_last_name').val() +  " from system. All their data including leads and collections are removed from database.";
         bootbox.dialog({
            message: message,
            closeButton: false,
            buttons: {

                "cancel" : {
                    "label" : "No",
                    "className" : "btn-sm btn-danger",
                    callback: function() {
                    }
                },
                "success" : {
                    "label" : "Yes",
                    "className" : "btn-sm btn-primary",
                    callback: function() {
                         $.ajax({
                            url: API.users + id + '/',
                            type: 'DELETE',
                            headers: {
                                "Authorization":"Token " + USER.token
                            },
                            success: function(result) {
                                toastr.clear();
                                toastr.success(success_message);
                                tableData.fnSort( [ [6,'desc'] ] );
                            },
                            error: function(result){
                                toastr.clear();
                                toastr.error("Oops, something went wrong! Please try again!");
                                tableData.fnSort( [ [6,'desc'] ] );
                            }
                        });

                    }
                },
            },
          });
    }


    $(document).on('click','.remove_user', function(e){
        var id = $(this).find('input').val();
        $('#user_first_name').val($(this).data('first_name'));
        $('#user_last_name').val($(this).data('last_name'));
        deleteUserModal(id);
        return false;
    });

    /*******************/
    /* Update Coupon   */
    /*******************/

    $("#updateCouponForm").validate({
      submitHandler: function(form) {
            if ($("#coupon_code").val() !== '') {
                bootbox.hideAll();
                updateCouponConfirmation();
            }

            return false;
      },
      rules: {
        coupon_code: {
          required: true,
          couponCode: true
        }
      },
      messages: {
          coupon_code: {
            required: "Coupon Code is required.",
          }
        }
    });

    /* Update Coupon Modal */
    function updateCouponConfirmation(){
      bootbox.dialog({
            message: 'Are you sure you want to use this coupon code?',
            closeButton: false,
            buttons: {
                "cancel" : {
                    "label" : "No",
                    "className" : "btn-sm btn-danger",
                    callback: function() {
                    }
                },
                "success" : {
                    "label" : "Yes",
                    "className" : "btn-sm btn-primary",
                    callback: function() {
                        showLoading();
                        $.post(API.updateUserCoupon, $( "#updateCouponForm" ).serialize()).done(function(data){
                          toastr.success('Coupon has been applied to user.');
                          setTimeout(function(){
                            window.location.href = FRONTEND.appUsers;
                          }, 1000);
                          hideLoading();
                        }).fail(function(data) {
                          hideLoading();
                          toastr.error('Coupon is invalid.');
                        }).always(function(){
                          // toastr.clear();
                        }).fail(function(data) {
                            hideLoading();
                        }).always(function(){
                            // toastr.clear();
                        });
                    }
                },
            },
            });
    }

    /* Request Leads Modal */
    function requestLeadsModal(userId){
      bootbox.dialog({
            message: 'All transcribed leads will be delivered via email. ' +
                     'Are you sure you want to request the list of transcribed leads of this user?',
            closeButton: false,
            buttons: {
                "cancel" : {
                    "label" : "No",
                    "className" : "btn-sm btn-danger",
                    callback: function() {
                    }
                },
                "success" : {
                    "label" : "Yes",
                    "className" : "btn-sm btn-primary",
                    callback: function() {
                        showLoading();
                        $.post(API.requestLeads, {user_id: userId}).done(function(data){
                          toastr.success('Lead request successful. You will receive an email with transcribed leads shortly.');
                          setTimeout(function(){
                            window.location.href = FRONTEND.appUsers;
                          }, 1000);
                          hideLoading();
                        }).fail(function(data) {
                          hideLoading();
                          toastr.info('There are no transcribed leads to request');
                        }).always(function(){
                          // toastr.clear();
                        }).fail(function(data) {
                            hideLoading();
                        }).always(function(){
                            // toastr.clear();
                        });
                    }
                },
            },
            });
    }

    function removeCouponConfirmation(){
      bootbox.dialog({
            message: 'Are you sure you want to remove existing coupon code?',
            closeButton: false,
            buttons: {
                "cancel" : {
                    "label" : "No",
                    "className" : "btn-sm btn-danger",
                    callback: function() {
                    }
                },
                "success" : {
                    "label" : "Yes",
                    "className" : "btn-sm btn-primary",
                    callback: function() {
                        showLoading();
                        $.post(API.removeUserCoupon, $( "#updateCouponForm" ).serialize()).done(function(data){
                          toastr.success('Coupon has been deleted successfully.');
                          setTimeout(function(){
                            window.location.href = FRONTEND.appUsers;
                          }, 1000);
                            hideLoading();
                          }).fail(function(data) {
                            hideLoading();
                        }).always(function(){
                          // toastr.clear();
                        }).fail(function(data) {
                            hideLoading();
                        }).always(function(){
                            // toastr.clear();
                        });
                    }
                },
            },
            });
    }

    $(document).on('click', '#show_update_coupon', function(e){
      e.preventDefault();
      $('.coupon-form').toggleClass('hide');
    });

    $(document).on('click', '#remove_coupon', function(e){
      e.preventDefault();
      removeCouponConfirmation();
    });

    $(document).on('click', '.request_leads', function(e){
      e.preventDefault();
      var userId = $(this).data('id');
      if (userId) {
        requestLeadsModal(userId);
      }

    });

});
