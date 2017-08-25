{% load url from future %}
{% load jsonify %}

(function ()
 {
     $.when (window.graphready_deferred,
             $.getJSON ("{% url "hmeter_frontend:project:btdata" id=project.id domain='' %}")
             {% if hldomain %},
             $.getJSON ("{% url "hmeter_frontend:project:btdata" id=project.id domain=hldomain %}")
             {% endif %})
         .done (plot_bugs);

     $.when (window.graphready_deferred,
             $.getJSON ("{% url "hmeter_frontend:project:btreporterdata" id=project.id domain='' %}")
             {% if hldomain %},
             $.getJSON ("{% url "hmeter_frontend:project:btreporterdata" id=project.id domain=hldomain %}")
             {% endif %})
         .done (plot_bugreporters);

     function plot_bugs (_, btdata, hlbtdata)
     {
         btdata = btdata && btdata[0]
         hlbtdata = hlbtdata && hlbtdata[0];

         plot_series ($("#bugs_opened_freq_graph"),
                      "Bugs opened",
                      btdata.bugs_opened_series,
                      hlbtdata ? hlbtdata.bugs_opened_series : null,
                      false);
         plot_series ($("#bugs_closed_freq_graph"),
                      "Bugs closed",
                      btdata.bugs_closed_series,
                      hlbtdata ? hlbtdata.bugs_closed_series : null,
                      false);
     }

     function plot_bugreporters (_, brdata, hlbrdata)
     {
         brdata = brdata && brdata[0]
         hlbrdata = hlbrdata && hlbrdata[0];

         plot_series ($("#bug_reporter_freq_graph"),
                      "Bug reporters",
                      brdata, hlbrdata,
                      true);
     }

     function plot_series (graph_target, label_base, data, hldata, bar)
     {
         var series = new FrequencySeries (label_base, data, "#40EDEB");
         var series_list = hldata ?
             series.split_by_domain (hldata, hldomain, hlcolor) :
             [series];

         if (bar)
             $.each (series_list,
                     function () {
                         mixin (this, BarSeries);
                         BarSeries.apply (this);
                     });

         new AnnotatedGraph (graph_target, series_list,
                             series.label + "over time").draw ();
     }

 }) ();
