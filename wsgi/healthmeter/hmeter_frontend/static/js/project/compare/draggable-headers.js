/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

function DragManager (table)
{
    this.table = table;
    this.projects = this.get_projid_order ();
    this.annotate_tbody_cols ();
    this.savestate (false);
}

DragManager.prototype.get_projid_order = function ()
{
    var projids = this.table
        .find ("thead tr th + th")
        .map (function () {return $(this).attr ("data-project-id");});

    return $.makeArray (projids);
}

DragManager.prototype.annotate_tbody_cols = function ()
{
    var self = this;

    this.table
        .find ("tbody tr td + td")
        .each (function ()
               {
                   var $this = $(this);
                   $this.attr ("data-project-id",
                               self.projects[$this.index () - 1]);
               });
}

DragManager.prototype.update_projects = function (projects)
{
    this.projects = projects;
    this.reorder_tbody_cols ();
}

DragManager.prototype.drop = function ()
{
    this.update_projects (this.get_projid_order ());
    this.savestate (true);
}

DragManager.prototype.savestate = function (push)
{
    var url = this.projects.join (",");

    if (push)
        history.pushState (this.projects, document.title, url);
    else
        history.replaceState (this.projects, document.title, url);
}

DragManager.prototype.popstate = function (event)
{
    var projects = event.originalEvent.state;

    if (projects) {
        this.update_projects (projects);
        this.reorder_thead_cols ();
    }
}

DragManager.prototype.reorder_cols = function (section, element)
{
    var self = this;

    this.table
        .find (section + " tr")
        .each (function ()
               {
                   var row = $(this);
                   $.each (self.projects, function ()
                           {
                               row
                                   .children (element + "[data-project-id=" +
                                              this + "]")
                                   .appendTo (row);
                           });
               });
}

DragManager.prototype.reorder_tbody_cols = function ()
{
    this.reorder_cols ("tbody", "td");
}

DragManager.prototype.reorder_thead_cols = function ()
{
    this.reorder_cols ("thead", "th");
}

$(function () {
    var dmgr = new DragManager ($("#project-comparison"));
    $(window).on ("popstate", dmgr.popstate.bind (dmgr));

    $("#project-comparison thead tr")
        .sortable ({
            itemSelector: 'th + th',
            placeholder: '<th class="placeholder"/>',
            vertical: false,
            onDrop: drop_handler
        });

    function drop_handler ($item, container, _super)
    {
        dmgr.drop ();
        _super ($item, container);
    }
});
