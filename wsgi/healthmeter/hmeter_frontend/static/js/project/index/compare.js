/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

function Project (name, id)
{
    this.id = id;
    this.name = name;
}

function TooManyProjects () {}
TooManyProjects.prototype.name = "TooManyProjects";
TooManyProjects.prototype.message = 'Too many projects. ' +
    'Please remove one or more projects before adding another.';

function CompareOverlay (max_projects)
{
    this.project_ids = [];
    this.project_names = [];
    this.max_projects = max_projects;
}

CompareOverlay.prototype.find_project = function (id)
{
    return this.project_ids.indexOf (id);
}

CompareOverlay.prototype.add_project = function (project)
{
    if (this.find_project (project.id) != -1)
        return;

    if (this.project_ids.length >= this.max_projects)
        throw new TooManyProjects ();

    this.project_ids.push (project.id);
    this.project_names.push (project.name);
    this.update_widget ();
}

CompareOverlay.prototype.remove_project = function (project)
{
    var idx = this.find_project (project.id);

    if (idx == -1)
        return;

    this.project_ids.splice (idx, 1);
    this.project_names.splice (idx, 1);
    this.update_widget ();
}

CompareOverlay.prototype.get_widget = function ()
{
    if (this.widget != null)
        return this.widget;

    this.widget = $("<div>", {id: "compare-overlay"});
    this.update_widget ();

    return this.widget;
}

CompareOverlay.prototype.update_widget = function ()
{
    var widget = this.get_widget ();

    if (!this.project_ids.length)
        widget.remove ();

    else {
        var text_widget = $("<div>", {'class': 'ellipsize'})
            .text (this.project_ids.length + ' ' +
                   (this.project_ids.length == 1 ? 'project' : 'projects') +
                   ' selected: ' +
                   this.project_names.join (", "));

        // Construct compare widget...
        widget
            .children ().remove ().end ()
            .appendTo ($("body"))
            .append (text_widget);

        // Add a compare link if >1 project
        if (this.project_ids.length > 1) {
            $("<a>")
                .text ("Compare projects")
                .addClass ("btn btn-sm btn-default pull-right")
                .attr ('href',
                       Urls['hmeter_frontend:project:compare'] (
                           this.project_ids.join (",")))
                .prependTo (widget);
        }
    }
}


$(function () {
    var overlay = new CompareOverlay (7);

    $("button.compare-btn").on ("click", function (e) {
        var $this = $(this);

        var row = $this.closest ("tr.project");

        var projid = +row.attr ("data-project-id");
        var projname = $.trim (row.find ("td.project-name").text ());

        var project = new Project (projname, projid);

        if ($this.hasClass ("selected")) {
            overlay.remove_project (project);
            $this.removeClass ("selected");

        } else {
            try {
                overlay.add_project (project);
                $this.addClass ("selected");

            } catch (exception) {
                alert ("Could not add project to be compared: " +
                       exception.message);
            }

        }
    });
});
