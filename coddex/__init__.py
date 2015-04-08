from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('root_get',           '/',       request_method='GET')
    config.add_route('root_tables_post',   '/tables', request_method='POST')
    config.add_route('root_views_post',    '/views',  request_method='POST')

    config.add_route('schema_get',         '/schemas/{schema}',        request_method='GET')
    config.add_route('schema_tables_post', '/schemas/{schema}/tables', request_method='POST')

    config.add_route('table_get',          '/schemas/{schema}/tables/{table}', request_method='GET')
    config.add_route('table_post_delete',  '/schemas/{schema}/tables/{table}', request_method='POST', request_param='method=DELETE')

    config.scan()
    return config.make_wsgi_app()
