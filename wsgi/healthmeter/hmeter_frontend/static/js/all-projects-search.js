/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

$(function () {
    var search_field = $(".search-form input[type=search]");
    var target = search_field.closest ('form').next ('ol');
    var orig_text = search_field.attr ('value');

    search_field
        .on ("focus", function () {
            if ($(this).val () == orig_text)
                $(this).val ('').removeClass ('inactive');
        })
        .on ("blur", function () {
            if ($(this).val () == '')
                $(this).val (orig_text).addClass ('inactive');
        })
        .on ("keyup change", filter_projects);

    function filter_projects ()
    {
        var term = search_field.val ();
        term = (term == orig_text) ? '' : term;

        if (!term)
            target.children ().show ();

        else {
            var terms = term.split (/[^a-zA-Z0-9]/);
            var selector = target.children ();

            for (var i=0; i<terms.length; i++) {
                if (!terms[i])
                    continue;

                selector = selector.filter (':icontains(' + terms[i] + ')');
            }

            target.children ().hide ();
            selector.show ();
        }
    }
});
