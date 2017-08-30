$(function ()
  {
     $.when (window.graphready_deferred,
             $.getJSON ("{% url "hmeter_frontend:project:btdata" id=project.id domain='' %}")
             {% if hldomain %},
             $.getJSON ("{% url "hmeter_frontend:project:btdata" id=project.id domain=hldomain %}")
             {% endif %})
         .done (plot_bugs);

      function plot_bugs (_, btdata, hlbtdata)
      {
          btdata = btdata[0];
          hlbtdata = hlbtdata && hlbtdata[0];

          var bugs_opened = new FrequencySeries (
              "Bugs opened",
              btdata.bugs_opened_series
          );

          var bugs_closed = new FrequencySeries (
              "Bugs closed",
              btdata.bugs_closed_series
          );

          var series_list = [];

          if (hlbtdata) {
              bugs_opened =
                  bugs_opened.split_by_domain (hlbtdata.bugs_opened_series,
                                               hldomain, hlcolor);
              bugs_closed =
                  bugs_closed.split_by_domain (hlbtdata.bugs_closed_series,
                                               hldomain, hlcolor);
          } else {
              bugs_opened = [bugs_opened];
              bugs_closed = [bugs_closed];
          }

          var colors = [hlcolor, "#108D17"];
          var labels = ["Outstanding " + hldomain + " bugs",
                       "Outstanding other bugs"];

          for (var i=0; i<bugs_opened.length; i++) {
              var counter = new BugCounter ();
              var series = new CompositeSeries (
                  [bugs_opened[i], bugs_closed[i]],
                  counter.translatefn.bind (counter),
                  labels[i],
                  colors[i],
                  {stack: true, lines: {fill: true}}
              );
              $(series).on ("data_changed", counter.reset.bind (counter));

              series_list.push (series);
          }

          (new AnnotatedGraph ($("#outstanding_bugs_graph"), series_list,
                               "Outstanding bugs over time")).draw ();
      }

      function BugCounter () {}
      BugCounter.prototype.counter = 0;
      BugCounter.prototype.translatefn = function (add, subtract)
      {
          add = add || 0;
          subtract = subtract || 0;
          return this.counter += add - subtract;
      };
      BugCounter.prototype.reset = function () {this.counter = 0;}
  });
