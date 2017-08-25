# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django import template

register = template.Library()


class IncludeOrNode(template.Node):
    def __init__(self, template_name, nodelist):
        self.template_name = template_name
        self.nodelist = nodelist

    def render(self, context):
        try:
            tmp = template.loader.get_template(
                self.template_name.resolve(context))
        except template.TemplateDoesNotExist:
            if 'commit-activity' in self.template_name.resolve(context):
                raise
            return self.nodelist.render(context)
        else:
            return tmp.render(context)


@register.tag
def includeor(parser, token):
    tag_name, template_name = token.split_contents()
    template_name = parser.compile_filter(template_name)

    nodelist = parser.parse(('endincludeor',))
    parser.delete_first_token()

    return IncludeOrNode(template_name, nodelist)
