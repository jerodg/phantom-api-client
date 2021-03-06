#!/usr/bin/env python3.8
"""Phantom API Client: Models.Init
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

from phantom_api_client.models.artifact import ArtifactRequest
from phantom_api_client.models.attachment import Attachment
from phantom_api_client.models.cef import Cef
from phantom_api_client.models.comment import Comment
from phantom_api_client.models.container import ContainerRequest
from phantom_api_client.models.custom_fields import CustomFields
from phantom_api_client.models.exceptions import InvalidCombinationError, InvalidOptionError
from phantom_api_client.models.note import Note
from phantom_api_client.models.pin import Pin
from phantom_api_client.models.query import ArtifactQuery, AuditQuery, ContainerQuery, Query, UserQuery
