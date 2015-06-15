# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from superdesk import get_resource_service
from superdesk.resource import Resource
from superdesk.services import BaseService

logger = logging.getLogger(__name__)


class PublishFilterResource(Resource):
    schema = {
        'publish_filter': {
            'type': 'list',
            'schema': {
                'type': 'list',
                'schema': Resource.rel('filter_condition', True)
            }
        },
        'name': {
            'type': 'string',
            'nullable': False,
        }
    }

    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'name'
    }

    datasource = {'default_sort': [('_created', -1)]}
    privileges = {'POST': 'publish_queue', 'PATCH': 'publish_queue'}


class PublishFilterService(BaseService):
    def on_create(self, docs):
        pass

    def build_mongo_query(self, doc):
        filter_condition_service = get_resource_service('filter_condition')
        expressions = []
        for expression in doc.get('publish_filter', []):
            filter_conditions = []
            for filter_condition_id in expression:
                filter_condition = filter_condition_service.find_one(req=None, _id=filter_condition_id)
                mongo_query = filter_condition_service.get_mongo_query(filter_condition)
                filter_conditions.append(mongo_query)

            if len(filter_conditions) > 1:
                expressions.append({'$and': filter_conditions})
            else:
                expressions.extend(filter_conditions)

        if len(expressions) > 1:
            return {'$or': expressions}
        else:
            return expressions[0]

    def build_elastic_query(self, doc):
        query = {'source': {'query': 'x'}}
        filter_condition_service = get_resource_service('filter_condition')
        for expression in doc.get('publish_filter', []):
            filter_conditions = {'query': {}}
            for filter_condition_id in expression:
                filter_condition = filter_condition_service.find_one(req=None, _id=filter_condition_id)
                elastic_query = filter_condition_service.get_elastic_query(filter_condition)

                if 'filtered' in elastic_query:
                    if 'filtered' in filter_conditions['query']:
                        filter_conditions['query']['filtered']['filter']['bool']['should'].\
                            extend(elastic_query['filtered']['filter']['bool']['should'])
                    else:
                        filter_conditions['query']['filtered']['filter']['bool']['should'] = \
                            elastic_query['filtered']['filter']['bool']['should']