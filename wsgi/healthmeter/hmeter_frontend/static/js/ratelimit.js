/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

// Pump this to the event queue, and ignore all consecutive calls to this
// function until we're done.
function coalesce (fn)
{
    var timer = null;

    function wrapper ()
    {
        var args = arguments;

        if (timer)
            clearTimeout (timer);

        timer = setTimeout (function () {
            timer = null;
            fn.apply (this, args);
        }, 10);
    }

    return wrapper;
}
