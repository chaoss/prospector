/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

// Utilities
/**
 * Aggregate data in form of [[x,y], [x,y], ..]. Requires map_x(x) to be sorted
 * in the same order as x.
 *
 * @arg map_x function(x) -> groupby_value
 * @arg combine_y function(y1, y2) -> combined value.
 * @return aggregated data
 */
function aggregate (data, map_x, combine_y)
{
    var newdata = [];
    var current_x;
    var current_y = [];

    for (var i=0; i<data.length; i++) {
        var x = data[i][0];
        var y = data[i][1];
        var new_x = map_x (x);

        if (i == 0)
            current_x = new_x;

        if (new_x == current_x) {
            current_y.push (y);

        } else {
            newdata.push ([current_x, combine_y (current_y)]);
            current_y = [y]
            current_x = new_x;
        }
    }

    if (data.length)
        newdata.push ([current_x, combine_y (current_y)]);

    return newdata;
}

/**
 * Sum all values in `list'. This can be used as `combine_y' for `aggregate()'
 *
 * @arg list values to sum
 * @return Sum of all values in `list'
 */
function sum(list)
{
    return list.reduce (function (a, b) {return a + b;}, 0);
}


/**
 * Shows a tooltip with the contents specified at (x,y). Function copied out of
 * the interactive flot example
 *
 * @arg x X coordinate of mouse point
 * @arg y Y coordinate of mouse point
 * @arg contents String containing innerHTML of tooltip
 */
function show_tooltip (x, y, contents)
{
    var tooltip = $("#tooltip")

    if (tooltip.length != 0) {
        tooltip.stop ()
        tooltip.html (contents)
        tooltip.animate ({top: y + 5, left: x + 5}, 50, null, null)
        return;
    }

    $('<div id="tooltip">' + contents + '</div>').css ({
        position: 'absolute',
        top: y + 5,
        left: x + 5,
        border: '2px solid #aa0000',
        'border-radius': '3px',
        padding: '2px',
        'background-color': '#fff',
        opacity: 0.90,
        width: 'auto'
    }).appendTo("body");
}

/**
  * Clamps timestamp to ticksize and formats it as a user-visible string
  *
  * @arg timestamp_usecs Microseconds from epoch
  * @arg ticksize array in form of [number, "day"|"week"|"month"|"year"]
  * @return User-presentable string
  */
function format_clamped_date (timestamp_usecs, ticksize)
{
    timestamp_usecs = map_functions[ticksize[1]] (ticksize[0], timestamp_usecs);
    var date = new Date (timestamp_usecs)

    var stringify_functions = {
        'year': function (date) {
            return "" + date.getUTCFullYear ();
        },

        'month': function (date) {
            var months = ["January", "February", "March", "April", "May",
                          "June", "July", "August", "September", "October",
                          "November", "December"];

            return months[date.getUTCMonth()] + " " +
                stringify_functions['year'] (date);
        },

        'day': function (date) {
            var month_string = stringify_functions['month'] (date);

            var split_values = month_string.split (" ")
            split_values[2] = split_values[1]
            split_values[1] = "" + date.getUTCDate ();

            return split_values.join (" ");
        }
    }

    return stringify_functions[ticksize[1]] (date);
}


function Graph (element, all_series, caption_text)
{
    this.element = element;
    this.all_series = all_series;
    this.caption_text = caption_text;

    var self = this;
    function replot ()
    {
        // Swallow data_changed triggers before graph is first drawn
        if (self.plot != null)
            self.replot ();
    }

    function update_trendmarker ()
    {
        if (self.plot != null)
            self.update_trendmarker ();
    }

    var show_working_label = this.show_working_label.bind (this);

    $.each (all_series, function ()
            {
                $(this)
                    .on ("enabled disabled data_changed label_changed " +
                         "options_changed",
                         coalesce (replot))
                    .on ("recalculating", show_working_label);

                if (this.is_aggregated)
                    this.set_aggregator (self.get_aggregator ());

                // Only show one trend marker
                if (!self.trend_series && this.show_trend) {
                    $(this).on ("data_changed",
                                update_trendmarker);
                    self.trend_series = this;
                }
            });
}

Graph.prototype.get_enabled_series = function ()
{
    return $.grep (this.all_series,
                   function (v) {return v.is_enabled;});
}

Graph.prototype.get_flot_series = function ()
{
    return $.map (this.all_series,
                  function (v) {
                      return v.is_enabled ? v.to_flot_series () : undefined;
                  });
}

Graph.prototype.get_options = function ()
{
    var options = {
        xaxis: {mode: "time",
                min: this.min_x,
                max: this.max_x,
                ticks: Math.round ($(this.element).width () / 90)} ,
        selection: {mode: "x"},
        grid: {hoverable: true,
               mouseActiveRadius: 20}
    };

    $.each (this.all_series, function ()
            {
                this.contribute_graph_options (options);
            });

    this.options = options;

    return options;
}

Graph.prototype.draw = function ()
{
    var $element = $(this.element).append (this.get_caption ());

    var trendmarker = this.get_trendmarker ();
    if (trendmarker)
        $element.append (trendmarker);

    $element.append (this.get_canvas (),
                     this.get_legend (),
                     this.get_working_label ());

    // if we're hidden due to being a tab, hook onto tab showing to replot
    var tab_content = $element.closest (".tab-content");
    if (tab_content.length > 0) {
        var id = $element.closest ("section[id]").attr ('id');
        var tab = tab_content.prev ('.nav-tabs').find ('a[href="#' + id + '"]');

        tab.on ("shown.bs.tab.graph", this.replot.bind (this));

        // plot anyway if we're already active
        if (tab.closest ('li').hasClass ('active'))
            this.replot ();
    } else {
        this.replot ();
    }
}

Graph.prototype.get_trendmarker = function ()
{
    if (this.trendmarker)
        return this.trendmarker;

    if (!this.trend_series)
        return null;

    this.trendmarker = $("<img>", {'class': 'trend-icon'});
    this.update_trendmarker ();

    return this.trendmarker;
}

Graph.prototype.update_trendmarker = function ()
{
    var icons = {
        '-1': 'trending-graph-down',
        '0': 'trending-graph-equals',
        '1': 'trending-graph-up',
    }

    this.trendmarker.attr ('src',
                           '/static/' + icons[this.trend_series.get_trend ()] +
                           '.png');
}

Graph.prototype.get_aggregator = function ()
{
    return this.aggregator = (this.aggregator || new Aggregator ());
}

Graph.prototype.get_caption = function ()
{
    if (this.caption)
        return this.caption;

    var first_series = this.get_enabled_series ()[0];

    // Don't use Series.get_label() here because get_label() auto-formats it
    var template = this.caption_text || (first_series.label + " over time");
    this.caption = this.get_aggregator ().make_graph_caption (template);

    return this.caption;
}

Graph.prototype.get_canvas = function ()
{
    if (!this.canvas)
        this.canvas = $("<div>", {'class': 'graph-canvas'});

    return this.canvas;
}

Graph.prototype.get_legend = function ()
{
    if (!this.legend) {
        this.legend = $("<form>").addClass ('graph-selectable-layers');
        var list = $("<ul>").appendTo (this.legend)

        $.each (this.all_series,
                function ()
                {
                    if (this.legend)
                        list.append (this.legend.get_widget ());
                });
    }

    return this.legend;
}

Graph.prototype.get_working_label = function ()
{
    this.working_label = $("<div>", {'class': 'working-msg',
                                     'text': 'Working...'});

    return this.working_label;
}

Graph.prototype.show_working_label = function ()
{
    if (!this.working_label)
        return;

    this.working_label.show ();
}

Graph.prototype.hide_working_label = function ()
{
    if (!this.working_label)
        return;

    this.working_label.hide ();
}

Graph.prototype.replot = function ()
{
    var options = this.get_options ();
    this.plot = $.plot (this.canvas, this.get_flot_series (), options);

    this.canvas
        .on ("plotselected.graph", this._plotselected.bind (this))
        .on ("plothover.graph", this._plothover.bind (this))
        .on ("dblclick.graph", this.zoom.bind (this, null, null));


    var self = this;
    this.plot.hooks.shutdown.push (function ()
                                   {
                                       self.canvas.unbind (".graph");
                                   });

    this.hide_working_label ();
}

Graph.prototype.zoom = function (from_x, to_x)
{
    this.min_x = from_x;
    this.max_x = to_x;

    this.replot ();
}

Graph.prototype._plotselected = function (event, ranges)
{
    this.plot.clearSelection (true);
    this.zoom (ranges.xaxis.from, ranges.xaxis.to);
}

/**
  * Round a date into a multiple of ticksize
  *
  * @arg ticksize: [number, unit], where unit = (day|week|month|year)
  * @arg timestamp_usecs: Microseconds from epoch
  */
function round_date (ticksize, timestamp_usecs)
{
    var round_functions = {
        day: function (number, value)
        {
            if (number <= 1)
                return value;

            // Floor by number * day
            value -= value % (number * 24 * 3600 * 1000);
            return value;
        },

        week: function (number, value)
        {
            var refpoint = -345600000; // Sunday before epoch
            var offset = value - refpoint;
            offset -= offset % (number * 7 * 24 * 60 * 60 * 1000);

            return refpoint + offset;
        },

        month: function (number, value)
        {
            var date = new Date (value);

            var total_months = date.getUTCMonth () +
                (date.getUTCFullYear () - 1970)* 12;
            total_months -= total_months % number;

            var years = 1970 + total_months / 12;
            var months = total_months % 12

            return new Date (Date.UTC (years, months, 1)).getTime ();
        },

        year: function (number, value)
        {
            var date = new Date (value);

            var year = date.getUTCFullYear ();
            var year_offset = year - 1970;
            year_offset -= year_offset % number;

            return new Date (Date.UTC (1970 + year_offset, 0, 1));
        }
    };

    return round_functions[ticksize[1]] (ticksize[0], timestamp_usecs);
}

/**
  * Clamps timestamp to ticksize and formats it as a user-visible string
  *
  * @arg timestamp_usecs Microseconds from epoch
  * @arg ticksize array in form of [number, "day"|"week"|"month"|"year"]
  * @return User-presentable string
  */
function format_clamped_date (timestamp_usecs, ticksize)
{
    if (ticksize[1] == 'week') {
        ticksize[0] *= 7;
        ticksize[1] = 'day';
    }

    timestamp_usecs = round_date (ticksize, timestamp_usecs);
    var date = new Date (timestamp_usecs)

    var stringify_functions = {
        'year': function (date) {
            return "" + date.getUTCFullYear ();
        },

        'month': function (date) {
            var months = ["January", "February", "March", "April", "May",
                          "June", "July", "August", "September", "October",
                          "November", "December"];

            return months[date.getUTCMonth()] + " " +
                stringify_functions['year'] (date);
        },

        'day': function (date) {
            var month_string = stringify_functions['month'] (date);

            var split_values = month_string.split (" ")
            split_values[2] = split_values[1]
            split_values[1] = "" + date.getUTCDate ();

            return split_values.join (" ");
        }
    }

    return stringify_functions[ticksize[1]] (date);
}

Graph.prototype._plothover = function (event, pos, item)
{
    // Not hovering over item. End here.
    if (!item) {
        this.plot.previous_datapoint = null;
        $("#tooltip").remove ();
        return;
    }

    // Tooltip is up to date, so stop here
    if (this.plot.previous_datapoint != null &&
        item.datapoint[0] == this.plot.previous_datapoint[0] &&
        item.datapoint[1] == this.plot.previous_datapoint[1])
        return;

    var ticksize = (this.options.xaxis.minTickSize !== undefined) ?
        this.options.xaxis.minTickSize : [1, "day"];

    var delta_str = "";
    if (item.dataIndex > 0) {
        var delta = item.datapoint[1] - item.series.data[item.dataIndex - 1][1];
        delta_str = ((delta > 0) ? " (+" : "(") + delta.toFixed (1) + ")";
    }

    // Add a new tooltip
    var label = ["<b>", format_clamped_date (item.datapoint[0], ticksize),
                 "</b><br />",
                 "<span style=\"color: ", item.series.color, ";",
                 "font-weight: bold;", "\">",
                 item.series.label,
                 "</span> = ",
                 item.datapoint[1],
                 delta_str].join ("");

    // Check if we have any ranges to show
    var ranges = this.plot.findRanges ({x: pos.x, y: pos.y});

    for (var i=0; i<ranges.length; i++) {
        var range = ranges[i];
        if (range.series.tooltip_prefix != null) {
            label += ['<br />',
                      '<span style="color: ', range.series.color, ';',
                      'font-weight: bold;">',
                      range.series.tooltip_prefix,
                      '</span>'].join ("");

            function format_date (date) {
                return format_clamped_date (date, [1, "day"]);
            }

            var formatted_date =
                (range.datapoint[0] == range.datapoint[2]) ?
                format_date (range.datapoint[0]) :
                (format_date (range.datapoint[0]) + ' &mdash; ' +
                 format_date(range.datapoint[2]));

            if (range.series.labels)
                label += (range.series.labels[range.dataIndex] + ' (' +
                          formatted_date + ')');
            else
                label += formatted_date;
        }
    }

    show_tooltip (item.pageX, item.pageY, label);

    this.plot.previous_datapoint = item.datapoint;
}

/**
  * Graph that is annotated with appropriate EventMarkerSeries
  */
function AnnotatedGraph (element, all_series, caption_text)
{
    var full_series = all_series.concat ([
        new EventMarkerSeries ("Event", event_series, "#12FF00",
                               event_labels),
        new EventMarkerSeries ("Release", release_series, "#E700FF",
                               release_labels),
        new EventMarkerSeries ("Blog post", blog_series, "#00A7FF",
                               blog_labels)
    ]);

    Graph.call (this, element, full_series, caption_text);
}

make_derived (AnnotatedGraph, Graph);


function Series (label, data, color, options)
{
    this.label = label;
    this.data = data;
    this.color = color;
    this.options = options;
}

Series.prototype.get_trend = function ()
{
    var data = this.orig_data ? this.orig_data : this.data;
    if (!data.length)
        return 0;

    var earlier_sum = 0, later_sum = 0;
    var latest_ts = data[data.length-1][0];

    var step = Math.min (6 * 30 * 24 * 3600 * 1000, // 6 months
                         (latest_ts - data[0][0]) / 2);

    var cutoff = latest_ts - step;

    for (var i=data.length-1; i>=0; i--) {
        var current = data[i];
        if (current[0] < cutoff)
            break;

        later_sum += current[1];
    }

    cutoff -= step;
    for (; i>= 0; i--) {
        var current = data[i];
        if (current[0] < cutoff)
            break;
        earlier_sum += current[1];
    }

    var difference = later_sum - earlier_sum;

    // Consider it to a non-flat trend only if difference > 10%
    if (Math.abs (difference) / later_sum <= 0.1)
        return 0;

    return difference / Math.abs (difference); // reduce to -1, 0, or 1
}

Series.prototype.is_enabled = true;
Series.prototype.is_aggregated = false;
Series.prototype.show_trend = false;

Series.prototype.enable = function ()
{
    this.is_enabled = true;
    $(this).trigger ("enabled");
}

Series.prototype.disable = function ()
{
    this.is_enabled = false;
    $(this).trigger ("disabled");
}

Series.prototype.to_flot_series = function ()
{
    return $.extend ({label: this.get_label (),
                      data: this.data,
                      color: this.color,
                      series_obj: this},
                     this.options);
}

Series.prototype.set_label = function (label)
{
    this.label = label;
    $(this).trigger ("label_changed");
}

Series.prototype.get_label = function ()
{
    return this.label;
}

Series.prototype.set_data = function (data)
{
    this.data = data;
    $(this).trigger ("data_changed");
}

Series.prototype.get_caption = function ()
{
    if (!this.caption) {
        this.caption = $("<div>", {text: this.get_label () + " over time",
                                   'class': "graph-caption"});
        var self = this;
        $(this).on ("label_changed", function ()
                    {
                        self.caption.text (self.label);
                    });
    }

    return this.caption;
}

Series.prototype.index_datapoints = function ()
{
    this.data_index = {};

    for (var i=0; i<this.data.length; i++)
        this.data_index[this.data[i][0]] = i;
}

Series.prototype.get_datapoint = function (timestamp)
{
    if (!this.data_index)
        this.index_datapoints ();

    return this.data[this.data_index[timestamp]];
}

Series.prototype.get_value = function (timestamp)
{
    var dp = this.get_datapoint (timestamp);
    return dp[1];
}

Series.prototype.set_value = function (timestamp, value)
{
    var dp = this.get_datapoint (timestamp);
    dp[1] = value;
    $(this).trigger ("data_changed");
}

Series.prototype.contribute_graph_options = function (options) {}


function EventMarkerSeries (label, data, color, event_labels, options)
{
    options = $.extend ({ranges: {show: true},
                         labels: event_labels},
                        options);
    if (label)
        options.tooltip_prefix = label + ': ';

    Series.call (this, label, data, color, options);
    this.legend = new LegendItem (this.label, this.color);

    var self = this;
    $(this.legend).on ('toggled',
                       function (event, enabled) {
                           if (enabled)
                               self.enable ();
                           else
                               self.disable ();
                       });
}

make_derived (EventMarkerSeries, Series);

EventMarkerSeries.prototype.is_enabled = false;

EventMarkerSeries.prototype.to_flot_series = function ()
{
    var flot_series = $.extend (Series.prototype.to_flot_series.call (this),
                                {ranges: {show: true}});

    // We've got a proper legend outside the graph, so drop this attribute
    delete flot_series['label'];

    return flot_series;
}


function LegendItem (label, color)
{
    this.label = label;
    this.color = color;
}

LegendItem.prototype.get_widget = function ()
{
    if (this.widget !== undefined)
        return this.widget;

    var self = this;

    this.checkbox = $("<input>", {type: 'checkbox'})
        .change (function ()
                 {
                     var checked = $(this).is (":checked");
                     var color = checked ? self.color : '';

                     self.widget.css ({color: color});
                     $(self).trigger ("toggled", [checked]);
                 });

    this.widget = $("<li>")
        .append (this.checkbox, this.label);

    return this.widget;
}


function FrequencySeries (label_base, data, color, options)
{
    var label = label_base + " per @AGGREGATOR@";
    Series.call (this, label, data, color, options);

    this.label_base = label_base;
    this.orig_data = this.data;
}

make_derived (FrequencySeries, Series);

FrequencySeries.prototype.is_aggregated = true;
FrequencySeries.prototype.show_trend = true;

FrequencySeries.prototype.set_aggregator = function (aggregator)
{
    var self = this;

    this.aggregator = aggregator;
    $(aggregator).on ("change", function ()
                      {
                          self.update_data ();
                          $(self).trigger ("label_changed");
                      });
    $(this).trigger ("aggregator_changed");
    this.update_data ();
}

FrequencySeries.prototype.update_data = function ()
{
    $(this).trigger ("recalculating");
    this.set_data (this.aggregator.apply (this.orig_data));
}

FrequencySeries.prototype.get_label = function ()
{
    return this.aggregator.make_series_label (this.label);
}

FrequencySeries.prototype.contribute_graph_options = function (options)
{
    Series.prototype.contribute_graph_options.call (this, options);

    if (options.xaxis === undefined)
        options.xaxis = {}

    options.xaxis.minTickSize = this.aggregator.get_denominator ().slice (0, 2);
}

FrequencySeries.prototype.split_by_domain = function (hldata, hldomain, hlcolor)
{
    var hlseries = new FrequencySeries (
        hldomain + " " + this.label_base.toLowerCase (),
        hldata,
        hlcolor,
        {
            stack: true,
            lines: {fill: true}
        });

    var otherseries = new CompositeSeries (
        [this, hlseries],
        function (all, hl) {return (all || 0) - (hl || 0);},
        "Other " + this.label_base.toLowerCase (),
        this.color,
        {
            stack: true,
            lines: {fill: true}
        });

    return [hlseries, otherseries];
}


function CumulativeSeries (base_series, label_base, color, options)
{
    var cumulative_counter = 0;
    function cumulative_sum (counts)
    {
        return cumulative_counter += sum (counts);
    }

    var cumdata = aggregate (base_series.data, function (x) {return x;},
                             cumulative_sum);

    label_base = label_base ||
        (base_series.label_base || base_series.label).toLowerCase ();
    color = color || base_series.color;
    options = options || base_series.options;

    Series.call (this, "Total number of " + label_base,
                 cumdata, color, options);
}

make_derived (CumulativeSeries, Series);


function BarSeries ()
{
    this.options = this.options || {};
    $.extend (this.options, {
        bars: {show: true}
    })

    var self = this;
    $(this).on ("aggregator_changed", function ()
                {
                    $(self.aggregator).on ("change",
                                           function () {
                                               self.update_barwidth ();
                                               $(self)
                                                   .trigger ("options_changed");
                                           });
                    self.update_barwidth ();
                });
}

BarSeries.prototype.update_barwidth = function ()
{
    var bases = {
        day: 24,
        week: 7 * 24,
        month: 30 * 24,
        year: 365 * 24
    };

    var denominator = this.aggregator.get_denominator ();
    var denominator_msecs = bases[denominator[1]] * denominator[0] * 3600000;

    this.options.bars.barWidth = denominator_msecs * 0.8;
}


function CompositeSeries (subseries, translatefn, label, color, options)
{
    Series.call (this, label, [], color, options);

    this.subseries = subseries;
    this.translatefn = translatefn;

    var self = this;

    $.each (subseries, function ()
            {
                $(this).on ("data_changed", function ()
                           {
                               $(self).trigger ("recalculating");
                               self.recalculate ();
                               $(self).trigger ("data_changed");
                           });
            });

    this.recalculate ();
}

make_derived (CompositeSeries, Series);

CompositeSeries.prototype.is_aggregated = true;

CompositeSeries.prototype.set_aggregator = function (aggregator)
{
    var self = this;
    this.aggregator = aggregator;

    $.each (this.subseries, function ()
            {
                if (this.is_aggregated)
                    this.set_aggregator (aggregator);
            });

    $(aggregator).on ("change", function ()
                      {
                          $(self).trigger ("label_changed");
                      });
    $(this).trigger ("aggregator_changed");
}

CompositeSeries.prototype.recalculate = function ()
{
    // Collate data so we have collated_data[timestamp] = arrays of values in
    // order from the series
    var collated_data = {};

    for (var i=0; i<this.subseries.length; i++) {
        var series = this.subseries[i];
        var data = series.data;

        for (var j=0; j<data.length; j++) {
            var timestamp = data[j][0];
            var value = data[j][1];

            var collated_datapoint = collated_data[timestamp];
            if (collated_datapoint === undefined)
                collated_data[timestamp] = collated_datapoint = [];

            for (var k=collated_datapoint.length; k<i; k++)
                collated_datapoint[k] = 0;

            collated_datapoint[i] = value;
        }
    }

    // collect sorted list of timestamps
    var timestamps = [];
    for (var timestamp in collated_data)
        timestamps.push (timestamp);

    timestamps = timestamps.sort (function (a, b) {return a - b;});

    // Generate data
    this.data = [];
    for (var i=0; i<timestamps.length; i++) {
        var timestamp = timestamps[i];

        var value = this.translatefn.apply (this, collated_data[timestamp]);

        this.data.push ([timestamp, value]);
    }
}


function Aggregator (default_base)
{
    if (default_base != null)
        this.default_base = default_base;
}

Aggregator.prototype.default_base = 2;

Aggregator.prototype.get_widget = function ()
{
    if (this.widget !== undefined)
        return this.widget;

    this.widget = $("<select>")
        .on ("change", function () {$(self).trigger ("change");});

    var self = this;
    $.each (this.bases,
            function (index) {
                var option = $("<option>", {text: this[2]})
                    .data ("value", this)
                    .appendTo (self.widget);

                if (index == self.default_base)
                    option.attr ("selected", "selected");
            });

    return this.widget;
}

Aggregator.prototype.get_denominator = function ()
{
    return this.get_widget ().children (":selected").data ("value");
}

Aggregator.prototype.apply = function (data)
{
    var denom = this.get_denominator ();

    return aggregate (data, round_date.bind (null, denom), sum);
}

Aggregator.prototype.bases = [
    [1, 'day', 'day'],
    [1, 'week', 'week'],
    [1, 'month', 'month'],
    [3, 'month', 'quartile'],
    [1, 'year', 'year']
];

Aggregator.prototype.token = "@AGGREGATOR@";

Aggregator.prototype.parse_template = function (template)
{
    var result = template.split (this.token, 2);

    if (result.length > 2)
        throw "More than one occurrence of " + this.token;

    return result;
}

Aggregator.prototype.make_graph_caption = function (label)
{
    var caption = $("<div>", {'class': 'graph-caption'});
    var parsed_result = this.parse_template (label);

    if (parsed_result.length <= 1)
        caption.text (label);
    else
        caption.text (parsed_result[0])
            .append (this.get_widget (), parsed_result[1]);

    return caption;
}

Aggregator.prototype.make_series_label = function (label)
{
    var parsed_result = this.parse_template (label);

    if (parsed_result.length <= 1)
        return label;

    parsed_result.splice (1, 0, this.get_denominator ()[2]);
    return parsed_result.join ("");
}
