# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django import forms
from django.db import models

from south.modelsinspector import add_introspection_rules


class PlaintextPasswordField(models.CharField):
    def formfield(self, form_class=forms.CharField, **kwargs):
        kwargs['widget'] = forms.PasswordInput

        return super(PlaintextPasswordField,
                     self).formfield(form_class=form_class, **kwargs)

add_introspection_rules([], ["^healthmeter\.fields\.PlaintextPasswordField"])
