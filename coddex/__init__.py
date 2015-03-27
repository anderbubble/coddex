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
    config.add_route('create_table_put',           '/{schema}/{table}', request_method='PUT')
    config.add_route('create_table_post',          '/{schema}/{table}', request_method='POST', request_param='method=PUT')
    config.add_route('drop_table_delete',          '/{schema}/{table}', request_method='DELETE')
    config.add_route('drop_table_post',            '/{schema}/{table}', request_method='POST', request_param='method=DELETE')
    config.add_route('table',                      '/{schema}/{table}', request_method='GET')
    config.add_route('global_table_list',          '/',                 request_method='GET')
    config.add_route('create_table_helper',        '/',                 request_method='POST')
    config.scan()
    return config.make_wsgi_app()
