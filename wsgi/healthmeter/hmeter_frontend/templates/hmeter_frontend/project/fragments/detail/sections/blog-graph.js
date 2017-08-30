(function ()
 {
     $.when (window.graphready_deferred,
             $.getJSON ('{% url "hmeter_frontend:project:blogdata" id=project.id %}'))
         .done (function (_, blogposts_per_day_series)
                {
                    var blogpost_freq = new FrequencySeries (
                        "Blog posts", blogposts_per_day_series[0], "#AB2DEA"
                    );
                    (new AnnotatedGraph ($("#blogposts_freq_graph"),
                                         [blogpost_freq])).draw ();

                    var cumulative_blogposts =
                        new CumulativeSeries (blogpost_freq);
                    (new AnnotatedGraph ($("#cumulative_blogposts_graph"),
                                         [cumulative_blogposts])).draw ();
                });
 }) ();
