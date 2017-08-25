/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

$.fn.restore_description = function ()
{
    this.filter (".expanded:visible")
        .each (function ()
               {
                   var $this = $(this);
                   var projid = $this.attr ('data-project-id');
                   var description = descriptions[projid] || 'N/A';

                   var paragraphs = description.split ('\r\n');
                   paragraphs = $.map (paragraphs, function (text) {
                       if (!text) return undefined;

                       return $('<p>').text (text);
                   });

                   var link = $this.find ('a.project-detail-link')
                       .clone ().text ('More details...');

                   // Don't do anything if description row already exists
                   if ($this.next ().hasClass ("description"))
                       return;

                   var placeholder = $("<div>")
                       .append (paragraphs)
                       .append (link);

                   var cell = $("<td>", {
                       'colspan': $this.children ().length,
                       'append': placeholder,
                   });

                   $("<tr>", {'class': 'description child-row'})
                       .append (cell)
                       .insertAfter ($this)
                       .after ($("<tr>", {'class': 'spacer child-row'}));

                   if (!$this.prevAll (":visible").length)
                       $("<tr>", {'class': 'spacer'}).insertBefore ($this);

                   $this.addClass ("expanded");
               });

    return this;
}

$.fn.show_description = function ()
{
    this.filter (":not(.expanded)")
        .addClass ("expanded")
        .restore_description ();

    return this;
}

$.fn.hide_description = function ()
{
    this.filter (".expanded")
        .removeClass ("expanded")
        .nextUntil ("tr.project")
        .remove ();

    this.each (function () {
        var $this = $(this);
        if (!$this.prevAll (":visible:not(.spacer)").length)
            $this.prev (".spacer").remove ();
    });

    return this;
}

$(function () {
    $('.projects-listing')
        .on ("prePageChange sortStart filterStart", function ()
             {
                 $(this).find ("tbody tr:not(.project)").remove ();
             })
        .on ("sortEnd filterEnd", function ()
             {
                 $(this).find ("tr.project").restore_description ();
             })
        .on ("click", "tr.project", function (event)
             {
                 // Ignore clicks on links
                 if ($(event.target).is ("a, button"))
                     return;

                 var tr = $(this).closest ("tr.project");

                 if (tr.hasClass ("expanded"))
                     tr.hide_description ();
                 else
                     tr.show_description ();
             });

    $('.health-scorebar').render_scorebar ('data-health-score');
});
