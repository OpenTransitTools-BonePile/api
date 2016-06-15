# credit:
# https://github.com/AndrewPashkin/apispec_restful/blob/master/apispec_restful.py

import re
from textwrap import dedent
import yaml


def path_from_resource(spec, api, resource, req_params=None,
                       default_in='query', **kwargs):
    """Extracts swagger spec from `resource` methods."""

    # spec and kwargs parameters, though not use, are required when
    # extending apispec.add_path as this does

    from apispec import Path
    from apispec.ext.marshmallow.swagger import fields2parameters

    assert resource is not None

    for endpoint, view in api.app.view_functions.iteritems():
        if getattr(view, 'view_class', None) == resource:
            break
    else:
        raise RuntimeError

    for rule in api.app.url_map.iter_rules():
        if rule.endpoint == endpoint:
            break
    else:
        raise RuntimeError

    path = re.sub(r'<(?:[^:<>]+:)?([^<>]+)>', r'{\1}', rule.rule)

    operations = {}
    for method in map(str.lower, resource.methods):
        doc = getattr(resource, method).__doc__
        doc = re.sub('^.*---', '', doc, flags=re.DOTALL)
        doc = dedent(doc)
        operations[method] = yaml.load(doc)

        # add request parameters
        if req_params and method == 'get':
            swagger_params = fields2parameters(
                req_params, default_in=default_in)
            operations[method]['parameters'] = swagger_params

    return Path(path=path, operations=operations)


def setup(spec):
    spec.register_path_helper(path_from_resource)
