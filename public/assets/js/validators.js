'use strict';
$.validator.addMethod("validemail", function (value, element) {
    return this.optional(element) || /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/.test(value);
}, "Email is invalid.");

$.validator.addMethod("alphaNumeric", function (value, element) {
    return this.optional(element) || /^[0-9a-zA-Z\s,.]+$/.test(value); //[A-za-z0-9_\-\s]
}, "Special character is not allowed.");

$.validator.addMethod("couponCode", function (value, element) {
    return this.optional(element) || /^[0-9A-Z_]+$/.test(value);
}, "Coupon is invalid.");

$.validator.addMethod("onlyNumber", function (value, element) {
    return this.optional(element) || /^[0-9]+$/.test(value);
}, "Only number is allowed.");

$.validator.addMethod("billingName", function (value, element) {
    return this.optional(element) || /^[a-zA-Z\s.]+$/.test(value); //[A-za-z0-9_\-\s]
}, "Special character is not allowed.");

$.validator.addMethod("withouSpace", function (value, element) {
    return value.indexOf(" ") < 0 && value !== "";
}, "Space is not allowed.");
