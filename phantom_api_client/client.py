#!/usr/bin/env python3.8
"""Phantom API Client
Copyright © 2019 Jerod Gawne <https://github.com/jerodg/>

This program is free software: you can redistribute it and/or modify
it under the terms of the Server Side Public License (SSPL) as
published by MongoDB, Inc., either version 1 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
SSPL for more details.

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

You should have received a copy of the SSPL along with this program.
If not, see <https://www.mongodb.com/licensing/server-side-public-license>."""

import asyncio
import logging
from typing import Any, List, NoReturn, Optional, Tuple, Union
from uuid import uuid4

from base_api_client import BaseApiClient, Results
from phantom_api_client.models import ArtifactRequest, AuditQuery, ContainerQuery, ContainerRequest, InvalidOptionError, Query

logger = logging.getLogger(__name__)


# todo: test_mode (revert any changes made after running)


class PhantomApiClient(BaseApiClient):
    """Phantom API Client"""
    SEM: int = 15  # This defines the number of parallel async requests to make.

    def __init__(self, cfg: Union[str, dict], sem: Optional[int] = None):
        """Initializes Class

        Args:
            cfg (Union[str, dict]): As a str it should contain a full path
                pointing to a configuration file (json/toml). See
                config.* in the examples folder for reference.
            sem (Optional[int]): An integer that defines the number of parallel
                requests to make."""
        BaseApiClient.__init__(self, cfg=cfg, sem=sem or self.SEM)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: None, exc_val: None, exc_tb: None) -> NoReturn:
        await BaseApiClient.__aexit__(self, exc_type, exc_val, exc_tb)

    async def get_artifact_count(self, container_id: Optional[int] = None, query: Optional[Query] = None) -> Results:
        """
        Performs a single page query to get the 'results_count' & 'num_paqges' based on specified Query.
        Args:
            container_id (Optional[int]):
            query (Optional[Query]):

        Returns:
            results (Results)
        """
        if not query:
            query = Query(type='artifact' if not container_id else f'container/{container_id}/artifacts',
                          page_size=1,
                          page=0)

        logger.debug(f'Getting artifact count...')

        tasks = [asyncio.create_task(self.request(method='get',
                                                  end_point=query.type,
                                                  request_id=uuid4().hex,
                                                  params=query.dict()))]

        results = Results(data=await asyncio.gather(*tasks))

        logger.debug('-> Complete.')

        return await self.process_results(results)

    async def get_artifacts(self, artifact_id: Optional[int] = None,
                            container_id: Optional[int] = None,
                            query: Optional[Query] = None) -> Results:
        """
        Can retrieve:
            - All artifacts
            - All artifacts from a single container
            - A single artifact
        Args:
            artifact_id (Optional[int]):
            container_id (Optional[int]):
            query (Optional[Query]):

        Returns:
            results (Results)
        """
        logger.debug(f'Getting artifact(s)...')

        if container_id:
            t = f'container/{container_id}/artifacts'
        elif artifact_id:
            t = f'artifact/{artifact_id}'
        else:
            t = 'artifact'

        if not query:
            query = Query(type=t)
        elif not query.type:
            query.type = t

        if not artifact_id:
            page_limit = (await self.get_artifact_count(container_id=container_id, query=query)).success[0]['num_pages']
        else:  # When we're getting a single artifact we can skip paging
            page_limit = 1

        tasks = [asyncio.create_task(self.request(method='get',
                                                  end_point=query.type,
                                                  request_id=uuid4().hex,
                                                  params={**query.dict(), 'page': i}))
                 for i in range(0, page_limit)]

        results = Results(data=await asyncio.gather(*tasks))

        logger.debug('-> Complete.')

        return await self.process_results(results, 'data' if not artifact_id else None)

    async def create_artifacts(self, containers: Union[List[ContainerRequest], ContainerRequest]) -> Tuple[
        Results, List[ContainerRequest]]:
        # if type(containers) is not list:
        #     containers = [containers]

        # todo: handle failure (already exists?)
        # print('containers:', containers, type(containers))
        # print(containers[0].containers)
        logger.debug('Creating artifact(s)...')
        if type(containers) is not list:
            containers = [containers]

        if type(containers[0]) is ContainerRequest:
            # # We set the last artifact of the last container to run automation.
            # # This will run automation on all newly created objects.
            # try:
            #     containers[-1].artifacts[-1].run_automation = True
            # except IndexError:  # Container doesn't have containers; NBD
            #     pass

            tasks = [asyncio.create_task(self.request(method='post',
                                                      end_point='/artifact',
                                                      request_id=a.data['request_id'],
                                                      json=a.dict())) for x in containers for a in x.artifacts]
            # print('tasks')
            # print(*tasks, sep='\n')
        else:  # ArtifactRequest
            # containers[-1].run_automation = True
            tasks = [asyncio.create_task(self.request(method='post',
                                                      end_point='/artifact',
                                                      request_id=a.data['request_id'],
                                                      json=a.dict())) for a in containers]

        results = await self.process_results(Results(data=await asyncio.gather(*tasks)))
        # print('artifact_results1:', results.data)
        # print('artifact_results1:')
        # print(*results.success, sep='\n')

        # Populate artifact id(s)
        [a.update_id(next((_['id'] for _ in results.success if _['request_id'] == a.data['request_id']), None))
         for x in containers for a in x.artifacts]
        # print('artifact_results2:')
        # print(*results.success, sep='\n')
        logger.debug('-> Complete.')

        for result in results.success:
            result['artifact_id'] = result['id']
            del result['id']

        # print('artifact_results3:')
        # print(*results.success, sep='\n')

        # print('artifacts_done')
        # print(*containers, sep='\n')

        return results, containers

    async def get_container_count(self, container_id: Optional[int] = None, query: Optional[Query] = None) -> Results:
        """
        Performs a single page query to get the 'results_count' & 'num_paqges' based on specified Query.
        Args:
            container_id (Optional[int]):
            query (Optional[Query]):

        Returns:
            results (Results)
        """
        if not query:
            query = Query(type='container' if not container_id else f'container/{container_id}',
                          page_size=1,
                          page=0)

        logger.debug(f'Getting artifact count...')

        tasks = [asyncio.create_task(self.request(method='get',
                                                  end_point=query.type,
                                                  request_id=uuid4().hex,
                                                  params=query.dict()))]

        results = Results(data=await asyncio.gather(*tasks))

        logger.debug('-> Complete.')

        return await self.process_results(results)

    async def get_containers(self, container_id: Optional[int] = None,
                             query: Optional[Union[ContainerQuery, Query]] = None) -> Results:
        """
        Can retrieve:
            - All Containers
            - A single container
        Args:
            container_id (Optional[int]):
            query (Optional[Query]):

        Returns:
            results (Results)
        """
        logger.debug(f'Getting container(s)...')

        try:
            wl = '/permitted_users' if query.whitelist_candidates else ''
        except AttributeError:
            wl = ''

        if container_id:
            t = f'/container/{container_id}{wl}'
        else:
            t = '/container'

        if not query:
            query = ContainerQuery(type=t)
        elif not query.type:
            query.type = t

        if not container_id:
            page_limit = (await self.get_container_count(query=query)).success[0]['num_pages']
        else:  # When we're getting a single container we can skip paging
            page_limit = 1

        tasks = [asyncio.create_task(self.request(method='get',
                                                  end_point=query.type,
                                                  request_id=uuid4().hex,
                                                  params={**query.dict(), 'page': i}))
                 for i in range(0, page_limit)]

        results = Results(data=await asyncio.gather(*tasks))

        logger.debug('-> Complete.')

        if container_id:
            data_key = None
        else:
            data_key = 'data'

        if wl:
            data_key = 'users'

        return await self.process_results(results, data_key)

    async def create_containers(self, containers: Union[List[ContainerRequest], ContainerRequest]) -> Tuple[Results, Any]:
        # todo: handle revert_failure
        # todo: handle failure (already exists)
        # todo: handle update_existing
        if type(containers) is not list:
            containers = [containers]

        # print('containers0:', containers)
        # print('container0:', containers[0])
        # Create Containers
        logger.debug('Creating container(s)...')
        tasks = [asyncio.create_task(self.request(method='post',
                                                  end_point='/container',
                                                  request_id=c.data['request_id'],
                                                  json=c.dict())) for c in containers]

        # print('results1:', results)
        # results = Results()
        container_results = await self.process_results(Results(data=await asyncio.gather(*tasks)))
        # print('container_results1:', container_results)
        logger.debug('-> Complete.')

        # todo: test/finish this
        # if update_existing:
        #     needs_update = []
        #     if results := container_results.failure:
        #         for result in results:
        #             if result['existing_container_id']:
        #                 container = [c for c in containers if c.request_id == result['request_id']]
        #                 needs_update.append(container)
        #
        #     if needs_update:
        #         tasks = [asyncio.create_task(self.request(method='post',
        #                                                   end_point=f'/container/{c.id}',
        #                                                   request_id=uuid4().hex,
        #                                                   json=c.dict())) for c in containers]
        #         container_results = await self.process_results(Results(data=await asyncio.gather(*tasks)))

        # Populate container_id(s)
        [c.update_id(next((_['id'] for _ in container_results.success if _['request_id'] == c.data['request_id']), None))
         for c in containers]

        for result in container_results.success:
            result['container_id'] = result['id']
            del result['id']

        artifact_results, containers = await self.create_artifacts(containers)
        # print('artifact_reulst3:', artifact_results)

        # Combine all results into one response
        container_results.success.extend(artifact_results.success)
        container_results.failure.extend(artifact_results.failure)

        # container_results.cleanup()
        return container_results, containers

    async def get_user_count(self, query: Optional[Query] = None) -> Results:
        if not query:
            query = Query(type='ph_user', filter={'_filter_type__in': '["normal", "automation"]'}, page_size=1, page=0)

        logger.debug('Getting user count...')

        tasks = [asyncio.create_task(self.request(method='get',
                                                  end_point=query.type,
                                                  request_id=uuid4().hex,
                                                  params=query.dict()))]

        results = Results(data=await asyncio.gather(*tasks))

        logger.debug('-> Complete.')

        return await self.process_results(results)

    async def get_users(self, user_id: Optional[int] = None, query: Optional[Query] = None) -> Results:
        logger.debug(f'Getting user(s)...')

        if user_id:
            t = f'/ph_user/{user_id}'
        else:
            t = '/ph_user'

        if not query:
            query = Query(type=t)
        elif not query.type:
            query.type = t

        if not user_id:
            page_limit = (await self.get_user_count(query=query)).success[0]['num_pages']
        else:  # When we're getting a single user we can skip paging
            page_limit = 1

        tasks = [asyncio.create_task(self.request(method='get',
                                                  end_point=query.type,
                                                  request_id=uuid4().hex,
                                                  params={**query.dict(), 'page': i}))
                 for i in range(0, page_limit)]

        results = Results(data=await asyncio.gather(*tasks))

        logger.debug('-> Complete.')

        if user_id:
            data_key = None
        else:
            data_key = 'data'

        return await self.process_results(results, data_key)

    async def get_audit_data(self, query: Optional[AuditQuery] = None) -> Results:
        """
        If no audit data is returned for a valid user then no audit data is
        present. Probably due to the user not having logged in before or a database reset.

        Args:
            query (Optional[Query]):

        Returns:
            results (Results)
        """
        logger.debug(f'Getting audit data...')

        t = '/audit'

        if not query:
            query = AuditQuery(type=t)
        elif not query.type:
            query.type = t

        tasks = [asyncio.create_task(self.request(method='get',
                                                  end_point=query.type,
                                                  request_id=uuid4().hex,
                                                  params=query.dict()))]

        results = Results(data=await asyncio.gather(*tasks))

        logger.debug('-> Complete.')

        return await self.process_results(results)

    async def delete_records(self, ids: Union[List[int], int], query: Optional[Query] = None) -> Results:
        """

        Args:
            ids (Union[List[int], int]):
            query (Optional[Query]):

        Returns:
            results (Results)
        """
        logger.debug(f'Deleting {query.type}, record(s)...')

        if not type(ids) is list:
            ids = [ids]

        tasks = [asyncio.create_task(self.request(method='delete',
                                                  end_point=f'{query.type}/{id}',
                                                  request_id=uuid4().hex)) for id in ids]

        results = Results(data=await asyncio.gather(*tasks))

        logger.debug('-> Complete.')

        return await self.process_results(results)

    async def update_records(self, requests: Union[
        ContainerRequest, ArtifactRequest, List[Union[ContainerRequest, ArtifactRequest]]]) -> Results:
        """

        Args:
            requests (Union[
        ContainerRequest, ArtifactRequest, List[Union[ContainerRequest, ArtifactRequest]]]):

        Returns:
            results (Results)
        """
        logger.debug(f'Updating record(s)...')

        if not type(requests) is list:
            requests = [requests]

        tasks = []
        for request in requests:
            if type(request) is ContainerRequest:
                t = '/container'
            elif type(request) is ArtifactRequest:
                t = '/artifact'
            else:
                raise InvalidOptionError('update_request', ['ArtifactRequest', 'ContainerRequest'])

            tasks.append(asyncio.create_task(self.request(method='post',
                                                          end_point=f'{t}/{request.id}',
                                                          request_id=uuid4().hex,
                                                          json=request.dict())))

        results = Results(data=await asyncio.gather(*tasks))

        logger.debug('-> Complete.')

        return await self.process_results(results)


if __name__ == '__main__':
    print(__doc__)