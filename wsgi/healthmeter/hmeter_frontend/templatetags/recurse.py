# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

from django import template

register = template.Library()
TemplateSyntaxError = template.TemplateSyntaxError


class RecurseNode(template.Node):
    def __init__(self, params):
        self.params = params

    def render(self, context):
        try:
            recurse_ctx = context['_recurse_ctx']
        except KeyError:
            raise TemplateSyntaxError("{0} found outside recursion context")

        args = [param.resolve(context) for param in self.params]
        return recurse_ctx._render(context, *args)


class RecurseDefinitionNode(template.Node):
    def __init__(self, params, nodelist):
        self.params = params
        self.nodelist = nodelist

    def _render(self, context, *args):
        context.push()

        context['level'] = context.get('level', -1) + 1
        context['_recurse_ctx'] = self

        try:
            if args and len(args) != len(self.params):
                raise IndexError

            for i, arg in enumerate(args):
                context[self.params[i]] = arg

        except IndexError:
            raise TemplateSyntaxError("Number of arguments passed to recurse "
                                      "do not match defrecurse")

        output = self.nodelist.render(context)

        context.pop()

        return output

    def render(self, context):
        return self._render(context)


@register.tag
def defrecurse(parser, token):
    """
    Recursively render things in Django templates.

    Usage:
    {% defrecurse param1 param2... %}
    <ul>
    {% for x in param.children %}
    <li>{{ x }}
    {% recurse param1 param2... %}
    </li>
    {% endfor %}
    </ul>
    {% enddefrecurse %}
    """
    params = token.split_contents()
    tag_name = params.pop(0)

    nodelist = parser.parse(('enddefrecurse',))
    parser.delete_first_token()

    return RecurseDefinitionNode(params, nodelist)


@register.tag
def recurse(parser, token):
    params = token.split_contents()
    tag_name = params.pop(0)

    params = [parser.compile_filter(param) for param in params]

    return RecurseNode(params)
