/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

function MetricNode (treenode, data, parent)
{
    this.id = treenode.id;
    this.children = [];
    this.data = data;
    this.pinned = false;
    this.legend = data.legend[this.id];
    this.weight = this.legend.weight;
    this.parent = parent;
    this.is_root = (parent == null);

    var score_series = data.metric_series[this.id];
    if (typeof score_series != "number")
        this.series = new Series (this.legend.title,
                                  data.metric_series[this.id],
                                  this.legend.colour);
    else
        this.score = score_series;

    var self = this;
    var recalc_all = coalesce (this.recalc_all_scores.bind (this));
    function handle_score_change (event, timestamp)
    {
        if (timestamp == null)
            recalc_all ();
        else
            self.recalc_score (timestamp);
    }

    for (var i=0; i<treenode.children.length; i++) {
        var child = new MetricNode (treenode.children[i], data, this);

        $(child).on ("score_changed", handle_score_change)
            .on ("weight_changed", recalc_all);

        this.children.push (child);
    }
}

MetricNode.prototype.get_siblings = function get_siblings ()
{
    return this.parent ? this.parent.children : null;
}

MetricNode.prototype.get_display_score = function get_display_score ()
{
    var score = this.get_score ();

    if (score == null)
        return "N/A";

    return score.toFixed (2);
}

MetricNode.prototype.set_weight = function set_weight (new_weight)
{
    if (this.weight == new_weight)
        return;

    this.weight = new_weight;
    $(this).trigger ("weight_changed");
}

MetricNode.prototype.reset_weights = function reset_weights ()
{
    for (var i=0; i<this.children.length; i++)
        this.children[i].reset_weights ();

    this.set_weight (this.legend.weight);
}

MetricNode.prototype.update_weight = function (new_weight)
{
    if (this.pinned)
        return false;

    var delta = new_weight - this.weight;
    var siblings = this.get_siblings ();

    var free_siblings = [];
    var pinned_siblings = [];

    for (var i=0; i<siblings.length; i++) {
        var sibling = siblings[i];

        if (sibling == this)
            continue;

        (sibling.pinned ? pinned_siblings : free_siblings).push (sibling);
    }

    var free_weight = sum_weight (free_siblings);
    var pinned_weight = sum_weight (pinned_siblings);
    var free_space = free_siblings.length ?
        100 - pinned_weight - free_weight : 0;

    // we cannot add more weight to this than free_weight
    var new_delta = Math.min (delta, free_weight);

    // and we cannot subtract more weight from this than free_space
    new_delta = Math.max (new_delta, -free_space);
    new_weight = this.weight + new_delta;

    this.set_weight (new_weight);

    for (var i=0; i<free_siblings.length; i++) {
        var sibling = free_siblings[i];
        var sibling_delta = (free_weight == 0) ?
            -new_delta / free_siblings.length :
            -new_delta * sibling.weight / free_weight;

        sibling.set_weight (sibling.weight + sibling_delta);
    }

    // Obstruct the slider if our delta differs from the original delta
    return (delta == new_delta);

    function sum_weight (list)
    {
        var sum = 0;
        for (var i=0; i<list.length; i++)
            sum += list[i].weight;

        return sum;
    }
}

MetricNode.prototype.get_score = function get_score (timestamp)
{
    // static score, so don't bother checking timestamp
    if (this.series == null)
        return this.score;

    // Return last value for null timestamp
    return (timestamp == null) ?
        this.series.data[this.series.data.length - 1][1] :
        this.series.get_value (timestamp);
}

MetricNode.prototype.set_score = function set_score (timestamp, score)
{
    if (this.series == null) {
        if (this.score == score)
            return;

        this.score = score;
        $(this).trigger ("score_changed", timestamp);
    } else {
        this.series.set_value (timestamp, score);
        $(this).trigger ("score_changed", timestamp);
    }
 }

// recalculate weighted average for this particular timestamp
MetricNode.prototype.recalc_score = function recalc_score (timestamp)
{
    // Recalculate entire series if timestamp isn't provided
    if (timestamp == null && this.series != null) {
        this.recalc_all_scores ();
        return;
    }

    // If we're drawing a graph, then send the recalculating trigger on this
    // series to show the working message.
    if (this.series)
        $(this.series).trigger ("recalculating");

    // Weighted average for this timestamp
    var numerator = 0;

    for (var i=0; i<this.children.length; i++) {
        var child = this.children[i];
        var value = child.get_score (timestamp);

        numerator += value * child.weight;
    }

    // Assume total weight = 100
    this.set_score (timestamp, numerator / 100.0);
}

// iterate through all timestamps and recalculate their scores
MetricNode.prototype.recalc_all_scores = function recalc_all_scores ()
{
    if (this.series == null) {
        this.recalc_score ();
        return;
    }

    var rawdata = this.series.data;
    for (var i=0; i<rawdata.length; i++) {
        var timestamp = rawdata[i][0];
        this.recalc_score (timestamp);
    }
}

MetricNode.prototype.draw_graph = function draw_graph (element)
{
    var graph = new Graph (element, [this.series]);
    graph.draw ();

    // We don't want captions for this -- we already have <h1>'s for that.
    element.find (".graph-caption").remove ();
}

MetricNode.prototype.toggle_pin = function ()
{
    this.pinned = !this.pinned;
    $(this).trigger ("pin_changed");
}

MetricNode.prototype.render_widgets = function render_widgets ()
{
    this.render_graphs ();
    this.render_sliders ();
    this.render_scorebars ();
    this.attach_pinbuttons ();
    this.render_labels ();

    // Do the same for children
    for (var i=0; i<this.children.length; i++)
        this.children[i].render_widgets ();

}

MetricNode.prototype.render_graphs = function render_graphs ()
{
    var self = this;

    $(".graph[data-metric-id=" + this.id + "]").each (function () {
        self.draw_graph ($(this));
    });
}

MetricNode.prototype.render_sliders = function render_sliders ()
{
    var self = this;
    var sliders = $(".weight-slider[data-metric-id=" + this.id + "]");
    sliders.slider ({
        selection: 'before',
        min: 0,
        max: 100,
        precision: 1,
        value: this.weight,
        tooltip: 'hide',
    });

    sliders
        .on ("slide slideStop", function (event) {
            self.update_weight ($(this).slider ("getValue"));
        })
        .prevAll ('.slider')
        .children ('.slider-track')
        .append ("<span class=watermark>Weight</span>");

    update_slider_handle ();
    $(this).on ("weight_changed",
                function (event) {
                    sliders.slider ("setValue", self.weight);
                    update_slider_handle ();
                });

    function update_slider_handle ()
    {
        var weight_text = self.weight == 100 ? '100' : self.weight.toFixed (1);

        sliders
            .prevAll ('.slider')
            .find (".slider-handle")
            .text (weight_text)
            .attr ('title', self.weight.toFixed (2));
    }
}

MetricNode.prototype.render_scorebars = function render_scorebars ()
{
    var self = this;
    var scorebars = $(".health-scorebar[data-metric-id=" + this.id + "]");

    update_scorebars ();
    $(this).on ("score_changed", update_scorebars);

    function update_scorebars ()
    {
        scorebars
            .attr ("data-health-score", self.get_score ())
            .render_scorebar ("data-health-score");
    }
}

MetricNode.prototype.attach_pinbuttons = function attach_pinbuttons ()
{
    var self = this;
    var pinbuttons = $(".weight-pinbutton[data-metric-id=" + this.id + "]")
        .click (function (event) {
            self.toggle_pin ();
        });

    update_pinbuttons ();
    $(this).on ("pin_changed", update_pinbuttons);

    function update_pinbuttons ()
    {
        if (self.pinned)
            pinbuttons.removeClass ('unpinned').addClass ('pinned');
        else
            pinbuttons.removeClass ('pinned').addClass ('unpinned');
    }
}

MetricNode.prototype.render_labels = function render_labels ()
{
    var self = this;
    var score_labels = $(".metric-score[data-metric-id=" + this.id + "]");
    var weight_labels = $(".metric-weight[data-metric-id=" + this.id + "]");
    var weight_normalized_score_labels =
        $(".weight-normalized-score[data-metric-id=" + this.id + "]");

    update_labels ();
    $(this).on ("score_changed weight_changed", update_labels);

    function update_labels ()
    {
        var score = self.get_score ();
        var weight = self.weight;
        var display_weight = weight.toFixed (2);

        score_labels.text (self.get_display_score ())
            .css ('color', health_score_to_colour (score));
        weight_labels.text (display_weight);

        var weight_normalized_score = score / 100 * weight;
        weight_normalized_score_labels
            .text ([weight_normalized_score.toFixed (1),
                    ' / ',
                    weight].join (''));
    }
}

$.when (domready_deferred,
        $.getJSON (Urls['hmeter_frontend:project:metricdata'] (
            window.project_id)))
    .done (function (_, data) {
        data = data[0];
        window.score_tree = new MetricNode (data.tree, data);
        score_tree.render_widgets ();

        $("#score-tree .score-breakdown-list").treeview ();

        $(".reset-score-tree").click (function () {
            score_tree.reset_weights ();
        });

        $("#score-breakdown > .score-breakdown-list")
            .find ("li > ul")
                .hide ()
            .end ()
            .treeview ();
    });
