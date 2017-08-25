{% load url from future %}

(function ()
 {
     $.when (window.graphready_deferred,
             $.getJSON ("{% url 'hmeter_frontend:project:mldata' id=project.id domain='' %}")
             {% if hldomain %},
             $.getJSON ("{% url 'hmeter_frontend:project:mldata' id=project.id domain=hldomain %}")
             {% endif %})
         .done (plot_emails);
     $.when (window.graphready_deferred,
             $.getJSON ("{% url 'hmeter_frontend:project:mlposterdata' id=project.id domain='' %}")
             {% if hldomain %},
             $.getJSON ("{% url 'hmeter_frontend:project:mlposterdata' id=project.id domain=hldomain %}")
             {% endif %})
         .done(plot_emailers);

     function plot_emails (_, mldata, hlmldata)
     {
         mldata = mldata[0];
         hlmldata = hlmldata && hlmldata[0];

         var email_freq = new FrequencySeries ("Emails", mldata, "#4069ED");

         var series_list = hlmldata ?
             email_freq.split_by_domain (hlmldata, hldomain, hlcolor) :
             [email_freq];

         (new AnnotatedGraph ($("#email_freq_graph"),
                              series_list,
                              "Emails per @AGGREGATOR@ over time")).draw ();

         var cumulative_series = $.map (series_list, function (x) {
             return new CumulativeSeries (x);
         });

         (new AnnotatedGraph ($("#cumulative_emails_graph"),
                              cumulative_series,
                              "Total number of emails over time")).draw ();
     }

     function plot_emailers (_, emailers, hlemailers)
     {
         emailers = emailers[0];
         hlemailers = hlemailers && hlemailers[0];

         var poster_freq = new FrequencySeries ("Email posters", emailers,
                                                "#4069ED");
         var series_list = hlemailers ?
             poster_freq.split_by_domain (hlemailers, hldomain, hlcolor) :
             [poster_freq];

         $.each (series_list, function ()
                 {
                     mixin (this, BarSeries);
                     BarSeries.apply (this);
                 });

         (new AnnotatedGraph ($("#poster_freq_graph"),
                              series_list,
                              "Posters per @AGGREGATOR@ over time")).draw ();
     }
 }) ();
