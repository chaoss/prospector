/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

function health_score_to_colour (score)
{
    var hue = score * 1.2;
    return "hsl(" + hue + ",100%,40%)";
}

// Render health score bars as progressbars
$.fn.render_scorebar = function (attrname, colourize)
{
    // default to colourizing the bar.
    colourize = (colourize === undefined) ? true : colourize;

    return this.each (function ()
                      {
                          var $this = $(this);
                          var value = +$this.attr (attrname);

                          // not rendered yet. render now!
                          if (!$this.hasClass ("progress")) {
                              $this.addClass ("progress")
                                  .append ($("<div>", {
                                      'class': 'progress-bar',
                                      'role': 'progressbar',
                                      'aria-valuemin': 0,
                                      'aria-valuemax': 100
                                  }));
                          }

                          $this.find (".progress-bar")
                              .css ('width', value + '%')
                              .attr ('aria-value', value)

                              .css ('background',
                                    colourize ?
                                    health_score_to_colour (value) :
                                    '#857979');
                      });
};
