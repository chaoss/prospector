/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

// Custom parsers for sorting health-bar and date columns
$.tablesorter.addParser ({
    id: 'health-bar',
    is: function () {return false;},
    format: function (value, table, node)
    {
        return +$(node).attr ("data-health-score");
    },
    type: 'numeric'
});

// Copied from datejs, but hacked for firefox's crappy datejs support
$.tablesorter.addParser ({
    id: 'timestamp',
    is: function () {return false;},
    format: function (value, table, node) {
        return +$(node).attr ("data-timestamp");
    },
    type: 'numeric'
});


$(function () {
    var pagesize = 20;

    $('.projects-listing').each (function () {
        var table = $(this);
        var pager = $('<div class="paginator">')
            .append ('<div class="pagecount">')
            .insertAfter (table);

	var form = $('<form class="project-search">')
            .insertBefore (table);

        $('<label>')
            .append ('<span>Search projects:</span>')
            .append ($('<input type="search" data-column="1" />')
                     .addClass ('form-control'))
            .appendTo (form);

        $.tablesorter.customPagerControls ({
            table: table,
            pager: pager,
            addKeyboard: true,
            currentPage: '.page',
            link: '<span class="page" data-page="{page}">{page}</span>',
            ends: 0,
            aroundCurrent: 999,
            adjacentSpacer: ', '
        });

        table
            .tablesorter ({
                debug: true,
                selectorSort: 'th.sortable',
                selectorRemove: 'tbody > tr:not(.project)',
                widgets: ['filter'],
                widgetOptions: {
                    filter_external: form.find ('input'),
                    filter_columnFilters: false
                }
            })
            .tablesorterPager ({
                container: pager,
                size: pagesize,
                savePages: false
            })
            .on ("pagerComplete", function (element, config) {
                var pagenum = config.page;
                var start = pagenum * pagesize;
                table.css ('counter-reset', 'projects ' + start);
            });

    });
});
