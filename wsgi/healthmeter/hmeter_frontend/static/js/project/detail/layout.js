/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

function generate_contents_links (elm)
{
    var list = $('<ul/>');

    // looking for links in root
    if (elm == null) {
        elm = $("main");
        list.addClass ("navbar-nav nav");
    } else {
        list.addClass ("dropdown-menu").attr ("role", "menu");
    }

    var headings = elm.find ("> section[id] > h1," +
                             "> .tab-content > section[id] > h1");

    if (headings.length == 0)
        return null;

    for (var i=0; i<headings.length; i++) {
        var heading = $(headings[i]);
        var id = heading.parent ().attr ('id');
        var link = $('<a/>', {href: '#' + id,
                              text: heading.text ()});

        if (heading.is ('[data-custom-color]'))
            link.css ('color', heading.css ('color'));

        var listitem = $('<li/>').append (link);

        var child_list = generate_contents_links (heading.parent ());
        if (child_list != null) {
            listitem.append (child_list);
            link.append ("<span class=caret>");
            link.attr ('data-toggle', 'dropdown')
                .attr ('data-target', ' ')
                .addClass ('dropdown-toggle');
        }

        list.append (listitem);
    }

    return list;
}

function make_collapsible (elements)
{
    for (var i=0; i<elements.length; i++) {
        var element = $(elements[i]);
        var items = element.children ();

        if (items.length < 5)
            continue;

        // Closure needed for cached items and button
        (function (elm) {
            var items = $(elm).children ()
                .slice (5)
                .not (".collapse-button");

            var button = $("<li/>").addClass ("collapse-button")
                .appendTo (elm)
                .click (function () {
                    if ($(this).text() == "Less")
                        collapse ();
                    else
                        expand ();
                });

            function collapse () {
                $(elm).addClass ("collapsed");
                button.text (items.length + " more");
            }

            function expand () {
                $(elm).removeClass ("collapsed");
                button.text ("Less");
            }

            // Set button text for items count here
            button.text (items.length + " more");
        }) (element);
    }
}

// HACK: Offset things so that scrollspy updates at the correct position
function set_tab_content_margins ()
{
    var tab_content_elms = $(".tab-content");
    var navbar = $("#section-heading-links");

    tab_content_elms.each (function () {
        var parent_section = $(this).parent().closest ("section");
        var clearcss = {'margin-top': 0,
                        'padding-top': 0};

        // Clear paddings and margins before looking at their offsets
        $(this)
            .css (clearcss)
            .children ()
            .css (clearcss);

        var offset = $(this).offset ().top - parent_section.offset ().top;

        var css = {'margin-top': -offset + 'px',
                   'padding-top': offset + 'px'};

        $(this)
            .css (css)
            .children ("section")
            .css (css);
    });
}

$(function ()
  {
      make_collapsible ($("ul.collapsible"));

      $("#project-infrastructure-list, .score-breakdown-list")
          .find ("> li > ul")
              .hide ()
          .end ()
          .treeview ();

      var contents_ref_element = $("#section-heading-links").prev ();
      $("#section-heading-links > .container")
          .append (generate_contents_links ())
          .parent ()
          .affix ({
              offset: {
                  top: function () {
                      return contents_ref_element.offset ().top +
                          contents_ref_element.outerHeight (true);
                  }
              }
          })
          .find ("[data-toggle=dropdown]")
          .dropdown ();

      // kick start tabs
      $(".nav-tabs").each (function () {
          var link = $(this).find ("a:first");
          link.tab ("show");
      });

      // Sync submenus in #section-heading-links with tabs
      $("#section-heading-links").on ("click", "a[href]", function (e) {
          var href = $(this).attr ('href');
          $('.nav-tabs a[href="' + href + '"]').tab ("show");
      });

      $(".nav-tabs li a").on ("shown.bs.tab", function (e) {
          var href = $(this).attr ("href");
          $("body").data ("bs.scrollspy").activate (href);
      });

      // hack tab-content margins appropriately
      set_tab_content_margins ();
      $(window).on ("resize", set_tab_content_margins);
      $("#section-heading-links")
          .on ("affixed.bs.affix", set_tab_content_margins);

      // scrollspy
      $("body")
          .attr ({'data-spy': 'scroll'})
          .scrollspy ({'target': '#section-heading-links'});
  });
