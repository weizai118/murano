#    Copyright (c) 2013 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import eventlet
from webob import exc
from muranoapi.common import config
from muranoapi.db.session import get_session
from muranoapi.db.models import Environment
from muranoapi.db.services.environments import EnvironmentServices
from muranoapi.db.services.systemservices import SystemServices
from muranoapi.openstack.common import wsgi
from muranoapi.openstack.common import log as logging

amqp = eventlet.patcher.import_patched('amqplib.client_0_8')
rabbitmq = config.CONF.rabbitmq

log = logging.getLogger(__name__)


class Controller(object):
    def index(self, request):
        log.debug(_('Environments:List'))

        #Only environments from same tenant as user should be returned
        filters = {'tenant_id': request.context.tenant}
        environments = EnvironmentServices.get_environments_by(filters)
        environments = [env.to_dict() for env in environments]

        return {"environments": environments}

    def create(self, request, body):
        log.debug(_('Environments:Create <Body {0}>'.format(body)))

        environment = EnvironmentServices.create(body.copy(),
                                                 request.context.tenant)

        return environment.to_dict()

    def show(self, request, environment_id):
        log.debug(_('Environments:Show <Id: {0}>'.format(environment_id)))

        session = get_session()
        environment = session.query(Environment).get(environment_id)

        if environment.tenant_id != request.context.tenant:
            log.info('User is not authorized to access this tenant resources.')
            raise exc.HTTPUnauthorized

        env = environment.to_dict()
        env['status'] = EnvironmentServices.get_status(env['id'])

        session_id = None
        if hasattr(request, 'context') and request.context.session:
            session_id = request.context.session

        #add services to env
        get = SystemServices.get_services

        ad = get(environment_id, 'activeDirectories', session_id)
        webServers = get(environment_id, 'webServers', session_id)
        aspNetApps = get(environment_id, 'aspNetApps', session_id)
        webServerFarms = get(environment_id, 'webServerFarms', session_id)
        aspNetAppFarms = get(environment_id, 'aspNetAppFarms', session_id)

        env['services'] = {
            'activeDirectories': ad,
            'webServers': webServers,
            'aspNetApps': aspNetApps,
            'webServerFarms': webServerFarms,
            'aspNetAppFarms': aspNetAppFarms
        }

        return env

    def update(self, request, environment_id, body):
        log.debug(_('Environments:Update <Id: {0}, '
                    'Body: {1}>'.format(environment_id, body)))

        session = get_session()
        environment = session.query(Environment).get(environment_id)

        if environment.tenant_id != request.context.tenant:
            log.info('User is not authorized to access this tenant resources.')
            raise exc.HTTPUnauthorized

        environment.update(body)
        environment.save(session)

        return environment.to_dict()

    def delete(self, request, environment_id):
        log.debug(_('Environments:Delete <Id: {0}>'.format(environment_id)))

        unit = get_session()
        environment = unit.query(Environment).get(environment_id)

        if environment.tenant_id != request.context.tenant:
            log.info('User is not authorized to access this tenant resources.')
            raise exc.HTTPUnauthorized

        EnvironmentServices.delete(environment_id, request.context.auth_token)


def create_resource():
    return wsgi.Resource(Controller())
