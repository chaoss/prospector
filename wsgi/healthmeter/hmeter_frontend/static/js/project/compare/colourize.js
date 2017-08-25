/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

$(function ()
  {
      $("td:not(.metric)").css ('color',
                                function () {
                                    var score = +$(this)
                                        .attr ("data-health-score");

                                    return health_score_to_colour (score);
                                });
  });
