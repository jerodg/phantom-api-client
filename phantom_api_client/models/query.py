#!/usr/bin/env python3.8
"""Phantom API Client: Models.Filter
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

from dataclasses import dataclass
from typing import List, Optional, Union

import re

from base_api_client.models.record import Record

CARE = re.compile(r'container/\d+/artifacts')


@dataclass
class Query(Record):
    """
    Attributes:
        type (str): action_run|artifact|asset|app|app_run|container|playbook_run|cluster_node|ph_user
        page (int): page number to retrieve
        page_size (int): how many results per page
        pretty (bool): pretty format results
        filter (dict): {'_filter_name__icontains': 'test'}
        include_expensive (bool): return all fields
        sort (str): field_name to sort on
        order (str): asc|desc; default desc

    References:
        https://my.phantom.us/4.1/docs/rest/query
    """
    type: Optional[str] = None
    page: Optional[int] = None
    page_size: Optional[int] = 1000  # Optimal page size (depends on semaphore)
    pretty: Optional[Union[bool, int]] = None
    filter: Optional[Union[dict, None]] = None  # Gets converted to standard Phantom filters in __post_init__
    include_expensive: Optional[Union[bool, int]] = None
    sort: Optional[str] = None
    order: Optional[str] = None

    def __post_init__(self):
        # todo: regex matching
        # type_opts = ['ph_user', 'artifact']
        # if self.type not in type_opts:
        #     raise InvalidOptionError

        if self.include_expensive or self.pretty:
            self.page_size = 500

        if self.pretty:
            self.pretty = 1

        if self.include_expensive:
            self.include_expensive = 1

        if self.filter:
            self.load(**self.filter)
            del self.filter

        if self.type and not self.type.startswith('/'):
            self.type = f'/{self.type}'


@dataclass
class ContainerQuery(Query):
    _annotation_whitelist_users: Optional[Union[bool, int]] = None
    whitelist_candidates: Optional[Union[bool, int]] = None

    def __post_init__(self):
        super().__post_init__()
        if self._annotation_whitelist_users:
            self._annotation_whitelist_users = 1

        if self.whitelist_candidates:
            self.whitelist_candidates = 1


@dataclass
class AuditQuery(Query):
    format: Optional[str] = None  # default json
    start: Optional[str] = None  # ISO 8601 Date|Date-Time; Default 30 days prior
    end: Optional[str] = None  # ISO 8601 Date|Date-Time; Default now
    user: Optional[Union[int, str, List[Union[int, str]]]] = None
    role: Optional[Union[int, str, List[Union[int, str]]]] = None
    authentication: Optional[str] = None
    administration: Optional[str] = None
    playbook: Optional[Union[int, str, List[Union[int, str]]]] = None
    container: Optional[Union[int, str, List[Union[int, str]]]] = None

    def __post_init__(self):
        super().__post_init__()
        if self.user and type(self.user) is list:
            self.user = [str(u) for u in self.user]
            self.user = '%1E'.join(self.user)

        if self.role and type(self.role) is list:
            self.role = [str(r) for r in self.role]
            self.role = '%1E'.join(self.role)

        if self.playbook and type(self.playbook) is list:
            self.playbook = [str(p) for p in self.playbook]
            self.playbook = '%1E'.join(self.playbook)

        if self.container and type(self.container) is list:
            self.container = [str(c) for c in self.container]
            self.container = '%1E'.join(self.container)


if __name__ == '__main__':
    print(__doc__)