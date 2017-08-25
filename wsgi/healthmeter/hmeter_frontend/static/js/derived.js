/* Copyright 2017 Red Hat, Inc.
 License: GPLv3 or any later version */

/**
  * Make derived_class a child of base_class by setting up the prototype chain
  *
  * @arg derived_class Derived class
  * @arg base_class Base class
  */
function make_derived (derived_class, base_class)
{
    derived_class.prototype = Object.create (base_class.prototype);
    derived_class.prototype.constructor = derived_class;
}


/**
 * Mixes mixin into cls_or_obj
 */
function mixin (cls_or_obj, mixin)
{
    if (cls_or_obj instanceof Function) {
        // it's a class, so extend its prototype
        $.extend (cls_or_obj.prototype, mixin.prototype);
        cls_or_obj.prototype.constructor = cls_or_obj;

    } else {
        // it's an object, so just dynamically mix things in
        $.extend (cls_or_obj, mixin.prototype);
    }
}
