# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django import forms


class FeedbackForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
