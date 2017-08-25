/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

$(function () {
    var form = $("#feedback-form");
    var dialog = form.closest (".modal-dialog");

    function submit_form () {form.submit ();}
    function close_form () {dialog.closest (".modal").modal ("hide");}

    function focus_form ()
    {
        form.find ("input[type=text], textarea").first ().focus ();
    }

    function clear_errors ()
    {
        form.find (".has-error")
            .attr ("title", "")
            .removeClass ("has-error")
            .tooltip ("destroy");
    }

    function reset_form ()
    {
        form[0].reset ();
        clear_errors ();
        set_inprogress (false);
    }

    function set_inprogress (inprogress) {
        dialog[inprogress ? 'addClass' : 'removeClass']('in-progress');
    }

    function is_inprogress () {
        return dialog.hasClass ('in-progress');
    }

    form.closest (".modal-content").find ("button[type=submit]")
        .on ("click", submit_form);

    form.on ("submit", function (e) {
        e.preventDefault ();

        if (is_inprogress ())
            return;

        set_inprogress (true);

        $.ajax ({
            data: $(this).serialize (),
            type: $(this).attr ("method"),
            url: $(this).attr ("action"),

            success: close_form,

            error: function (xhr, status, error) {
                if (status == 'timeout')
                    // try again
                    submit_form ();

                else if (status == 'error' && xhr.status == 400) {
                    var response = JSON.parse (xhr.responseText);
                    clear_errors ();

                    for (var field in response.errors) {
                        form.find ("[name=" + field + "]")
                            .closest (".form-group")
                            .addClass ("has-error")
                            .attr ('title', response.errors[field])
                            .tooltip ({'placement': 'right'});
                    }
                } else {
                    alert ("Unknown error while submitting feedback: " +
                           error);
                }
            },

            complete: set_inprogress.bind (null, false)
        });
    });

    dialog.closest (".modal")
        .on ("hidden.bs.modal", reset_form)
        .on ("shown.bs.modal", focus_form);
});
