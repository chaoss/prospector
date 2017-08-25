/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

$.fn.expand = function expand ()
{
    return this.removeClass ("collapsed")
        .each (function () {
            var $this = $(this);

            if (!$this.has_child_rows ())
                return;

            var level = $this.data ("level")

            var descendants = $this.nextUntil ("[data-level=" + level + "]");
            descendants.each (function () {
                var $this = $(this);
                var parent = $this.parent_row ();

                while (parent.length) {
                    if (parent.hasClass ("collapsed"))
                        return;

                    parent = parent.parent_row ();
                }

                // Did not find any ancestors with collaped class, so show
                $this.show ();
            });
        });
}

$.fn.collapse = function collapse ()
{
    return this.each (function () {
        var $this = $(this);

        if (!$this.has_child_rows ())
            return;

        level = $this.data ("level");
        console.log ("collapsing", this,
        $this.nextUntil ("[data-level=" + level + "]").hide ());
        $this.addClass ("collapsed");
    });
}

$.fn.parent_row = function parent_row ()
{
    var level = this.data ("level");
    var parent_row = this.data ("parent-row") ||
        this.prevAll ("[data-level=" + (level-1) + "]").first ();

    // Cache it for future access
    this.data ("parent-row", parent_row);
    return parent_row;
}

$.fn.has_child_rows = function has_child_rows ()
{
    var $this = this.first ();
    if (!$this.length)
        return false;

    var this_level = $this.data ("level");
    var next_level = $this.next ("[data-level]").data ("level");

    return (this_level < next_level);
}

$(function () {
    // hide everything but the first level
    $("tbody.metric-rows tr[data-level]")
        .addClass (function () {
            return $(this).has_child_rows () ? "collapsible" : "";
        })
        .collapse ()
        .click (function () {
            var $this = $(this);
            if ($this.hasClass ("collapsed"))
                $this.expand ();
            else
                $this.collapse ();
        });
    $("tbody.metric-rows tr[data-level=0]").expand ();
});
