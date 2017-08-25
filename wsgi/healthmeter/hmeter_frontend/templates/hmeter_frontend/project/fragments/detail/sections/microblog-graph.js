{% load url from future %}

(function ()
 {
     $.when (window.graphready_deferred,
             $.getJSON ('{% url "hmeter_frontend:project:microblogdata" id=project.id %}'))
         .done (function (_, microblogposts_per_day_series)
                {
                    var microblogpost_freq = new FrequencySeries (
                        "Microblog posts", microblogposts_per_day_series[0],
                        "#AB2DEA"
                    );
                    (new AnnotatedGraph ($("#microblogposts_freq_graph"),
                                         [microblogpost_freq])).draw ();

                    var cumulative_microblogposts =
                        new CumulativeSeries (microblogpost_freq);
                    (new AnnotatedGraph ($("#cumulative_microblogposts_graph"),
                                         [cumulative_microblogposts])).draw ();
                });
 }) ();
