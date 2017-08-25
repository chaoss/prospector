{% load url from future %}

(function ()
 {
     $.when (window.graphready_deferred,
             $.getJSON ("{% url 'hmeter_frontend:project:jamiqdata' id=project.id %}"))
         .done (plot_jamiq);

     function plot_jamiq (_, jamiqdata)
     {
         jamiqdata = jamiqdata[0];

         var series_list = [];
         var cum_series_list = [];
         var cat = ['positive', 'neutral', 'negative'];

         $.each (cat, function ()
                 {
                     var capitalized_cat = this.charAt (0).toUpperCase () +
                         this.substr (1);

                     var series = new FrequencySeries (
                         capitalized_cat + ' posts',
                         jamiqdata[this]
                     );

                     series_list.push (series);
                 });

         function compose_ppi (positive, neutral, negative)
         {
             var total = positive + neutral + negative;
             var difference = positive - negative;

             if (!total)
                 return 0;

             return difference / total;
         }

         var ppi_series = new CompositeSeries (series_list,
                                               compose_ppi,
                                               "Posts Positivity Index");

         (new AnnotatedGraph (
             $("#jamiq_freq_graph"), [ppi_series],
             "Posts Positivity Index by @AGGREGATOR@ over time"
         )).draw ();
     }
 }) ();
