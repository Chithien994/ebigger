'use strict';
function setPlanHeight() {
    var maxHeight = 0;
    $('.plan-description').removeAttr('style');
    $('.plan-description').each(function () {
        if ($(this).height() > maxHeight) {
            maxHeight = $(this).height();
        }
    });
    $('.plan-description').height(maxHeight);
}
var source = $("#failed-monthly-template").html();
var template = Handlebars.compile(source);
var context = {};
var failed_html = template();

function showLoading() {
    $('.loading_place').removeClass('hide');

}
function hideLoading() {
    $('.loading_place').addClass('hide');
}
function showCustomPopup(html, buttons) {
    bootbox.dialog({
        message: html,
        closeButton: false,
        buttons: buttons
    });
}

function failedPaymentPopup(planId) {
  bootbox.dialog({
      message: 'Your monthly charge failed. Please check your credit card information again to make sure it works fine on next charge.',
      closeButton: true,
      buttons: {
          "success": {
              "label": "Update Credit Card Info",
              "className": "btn-sm btn-primary",
              callback: function () {
                if (planId) {
                  window.location.href = CONSTANTS.creditcardInfoUrl + '?plan_id=' + planId;
                }
                else {
                  window.location.href = CONSTANTS.creditcardInfoUrl;
                }
              }
          },
      },
  });
}

function showFreePlanMessage() {
    bootbox.dialog({
        message: 'Users subscribed to a Free Plan may only use 1 collection. Please reconcile your leads, and then delete all collections but 1 before downgrading to our Free Plan.',
        closeButton: true,
        className: "error-modal",
        buttons: {},
    });
}

function showConfirmUpdatePlan(html, planId) {
  if ( html && planId ) {
    bootbox.dialog({
        message: html,
        closeButton: false,
        buttons: {
            "cancel": {
                "label": "No",
                "className": "btn-sm btn-danger",
                callback: function () {
                }
            },
            "success": {
                "label": "Yes",
                "className": "btn-sm btn-primary",
                callback: function () {
                    showLoading();
                    $.post(CONSTANTS.updatePlanUrl + planId).done(function (data) {
                        hideLoading();
                        // window.location.href = '{% url 'frontend:home' %}';
                        toastr.success(data.msg);
                        setTimeout(function () {
                            window.location.href = CONSTANTS.homeUrl;
                        }, 1000);

                    }).fail(function (data) {
                        hideLoading();
                        failedPaymentPopup(planId);
                        // toastr.error(data.responseJSON.msg);
                    }).always(function () {
                        // toastr.clear();
                    });
                }
            },
        },
    });
  }
}

$(function () {
    $('input, textarea').placeholder({customClass: 'custom-placeholder'});
    $('.logout-btn a, #logout-btn').on('click', function (e) {
        e.preventDefault();
        bootbox.dialog({
            message: "Are you sure you want to log out?",
            closeButton: false,
            buttons: {
                "cancel": {
                    "label": "No",
                    "className": "btn-sm btn-danger",
                    callback: function () {
                    }
                },
                "success": {
                    "label": "Yes",
                    "className": "btn-sm btn-primary",
                    callback: function () {
                        window.location.href = CONSTANTS.logoutUrl;
                    }
                }
            }
        });
        return false;
    })
});
