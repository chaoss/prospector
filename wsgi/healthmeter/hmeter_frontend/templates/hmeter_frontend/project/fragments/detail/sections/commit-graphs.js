{% load url from future %}
{% load jsonify %}

(function () {
    var basecolor = "#EDC240";

    var commits_url = "{% url 'hmeter_frontend:project:commitdata' id=project.id domain='' %}";
    var committers_url = "{% url 'hmeter_frontend:project:committerdata' id=project.id domain='' %}";

    {% if hldomain %}
    var hlcommits_url = "{% url 'hmeter_frontend:project:commitdata' id=project.id domain=hldomain %}";
    var hlcommitters_url = "{% url 'hmeter_frontend:project:committerdata' id=project.id domain=hldomain %}";
    {% else %}
    {% endif %}

    $.when (window.graphready_deferred,
            $.getJSON (commits_url)
            {% if hldomain %}
            , $.getJSON (hlcommits_url)
            {% endif %}
           ).done (plot_commits);

    $.when (window.graphready_deferred,
            $.getJSON (committers_url)
            {% if hldomain %}
            , $.getJSON (hlcommitters_url)
            {% endif %}
           ).done (plot_committers);

    function plot_commits (_, commitdata, hlcommitdata)
    {
        var commit_series = new FrequencySeries ("Commits", commitdata[0],
                                                 basecolor);
        var series_list = hlcommitdata ?
            commit_series.split_by_domain (hlcommitdata[0],
                                           hldomain, hlcolor) :
            [commit_series];

        (new AnnotatedGraph ($("#commit_freq_graph"),
                             series_list,
                             "Commits per @AGGREGATOR@ over time")).draw ();

        var cumulative_series_list = $.map (series_list, function (series) {
            return new CumulativeSeries (series);
        });

        (new AnnotatedGraph ($("#cumulative_commits_graph"),
                             cumulative_series_list,
                             "Total number of commits over time")).draw ();
    }

    function plot_committers (_, committerdata, hlcommitterdata)
    {
        var committer_series = new FrequencySeries (
            "Committers",
            committerdata[0],
            basecolor);

        var series_list = hlcommitterdata ?
            committer_series.split_by_domain (hlcommitterdata[0],
                                              hldomain, hlcolor) :
            [committer_series];

        $.each (series_list, function () {
            mixin (this, BarSeries);
            BarSeries.apply (this);
        });

        (new AnnotatedGraph ($("#committer_freq_graph"),
                             series_list,
                             "Committers per @AGGREGATOR@ over time")).draw ();
    }
}) ();
