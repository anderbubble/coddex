import migrate.changeset

import pyramid.renderers
from pyramid.response import Response
from pyramid.view import view_config


import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.types

from .models import (
    DBSession,
    )


class DeferredRouteURL (object):

    def __init__ (self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __json__ (self, request):
        return request.route_url(*self.args, **self.kwargs)


@view_config(route_name='root_get', renderer='templates/root.pt')
def root (request):
    schema_tables = {}
    schema_views = {}
    inspector = sqlalchemy.inspect(DBSession.bind)
    for schema in inspector.get_schema_names():
        schema_tables[schema] = inspector.get_table_names(schema=schema)
        schema_views[schema] = inspector.get_view_names(schema=schema)
    return {
        'engine': DBSession.bind,
        'schema_tables': schema_tables,
        'schema_views': schema_views,
    }


@view_config(route_name='schema_get', renderer='templates/schema.pt')
def retrieve_schema (request):
    schema = request.matchdict['schema']
    inspector = sqlalchemy.inspect(DBSession.bind)
    return {
        'engine': DBSession.bind,
        'schema': schema,
        'tables': inspector.get_table_names(schema=schema),
        'views': inspector.get_view_names(schema=schema),
    }


@view_config(context=sqlalchemy.exc.ProgrammingError)
def sqlalchemy_programming_error (exc, request):
    response = pyramid.renderers.render_to_response('json', {'message': exc.message})
    response.status_int = 500
    return response


@view_config(route_name='root_tables_post', renderer='json')
@view_config(route_name='schema_tables_post', renderer='json')
def create_table (request):
    try:
        schema = request.matchdict['schema']
    except KeyError:
        schema = request.params['schema']
    try:
        table_name = request.matchdict['table']
    except KeyError:
        table_name = request.params['table']
    uri = DeferredRouteURL('table_get', schema=schema, table=table_name)

    metadata = sqlalchemy.MetaData()
    metadata.bind = DBSession.bind
    table = sqlalchemy.Table(
        table_name, metadata,
        schema=schema
    )
    table.create()
    return {'schema': schema, 'table': table_name, 'uri': uri}


# @view_config(route_name='table_delete', renderer='json')
@view_config(route_name='table_post_delete', renderer='json')
def drop_table (request):
    schema_name = request.matchdict['schema']
    table_name = request.matchdict['table']

    metadata = sqlalchemy.MetaData()
    metadata.bind = DBSession.bind
    table = sqlalchemy.Table(
        table_name, metadata,
        schema=schema_name
    )
    table.drop()
    return {'schema': schema_name, 'table': table_name}


types = [
    'integer',
    'string',
    'boolean',
    'date',
    'datetime',
]


@view_config(route_name='table_get', renderer='templates/table.pt')
def retrieve_table (request):
    schema_name = request.matchdict['schema']
    table_name = request.matchdict['table']

    metadata = sqlalchemy.MetaData()
    metadata.bind = DBSession.bind
    table = sqlalchemy.Table(
        table_name, metadata,
        schema=schema_name,
        autoload=True)

    if table.c:
        query = sqlalchemy.select([table])
        return {'schema': schema_name, 'table': table_name, 'columns': table.c, 'result_set': DBSession.execute(query), 'types': types}
    else:
        return {'schema': schema_name, 'table': table_name, 'columns': None, 'result_set': None, 'types': types}


#@view_config(route_name='create_column_helper', renderer='json')
#def create_column (request):
#    try:
#        schema = request.matchdict['schema']
#    except KeyError:
#        schema = request.params['schema']
#    try:
#        table_name = request.matchdict['table']
#    except KeyError:
#        table_name = request.params['table']
#    try:
#        column_type = request.matchdict['type']
#    except KeyError:
#        column_type = request.params['type']
#    try:
#        column_name = request.matchdict['name']
#    except KeyError:
#        column_name = request.params['name']
#    uri = DeferredRouteURL('column', schema=schema, table=table_name, column=column_name)
#
#    metadata = sqlalchemy.MetaData()
#    metadata.bind = DBSession.bind
#    table = sqlalchemy.Table(
#        table_name, metadata,
#        schema=schema
#    )
#    table.create()
#    return {'schema': schema, 'table': table_name, 'column': column_name, 'type': column_type, 'uri': uri}
