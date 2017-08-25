/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

$.expr[":"].icontains = $.expr.createPseudo (function (arg) {
    return function (elem) {
        return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});
