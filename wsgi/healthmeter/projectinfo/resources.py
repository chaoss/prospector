# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

resource_registry = set()


def register_resource(resource_model):
    resource_registry.add(resource_model)


def get_resource_models():
    return resource_registry
