#!/usr/bin/env python3.8
"""Phantom API Client: Models.Custom Fields
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

import logging
from dataclasses import dataclass
from typing import Optional, Union

from base_api_client.models import Record, sort_dict

logger = logging.getLogger(__name__)


@dataclass
class CustomFields(Record):
    """
    References:
        https://soflokydcphat01.info53.com/admin/product_settings/eventsettings/global"""
    alert_source: Union[str, None] = None
    resolution_summary: Union[str, None] = None
    incident_level: Union[str, None] = None
    incident_category: Union[str, None] = None
    true_resolution: Union[str, None] = None
    analysis_completed: Union[str, None] = None
    true_detect_time: Union[str, None] = None
    analysis_started: Union[str, None] = None
    compliance_contacted: Union[str, None] = None
    contain_time: Union[str, None] = None
    vendor_ticket_number: Union[str, None] = None
    mitigated: Union[str, None] = None
    disposition: Union[str, None] = None
    true_event_time: Union[str, None] = None
    customer_exposure: Union[str, None] = None

    def dict(self, cleanup: Optional[bool] = True, dct: Optional[dict] = None, sort_order: Optional[str] = 'asc') -> dict:
        """
        Args:
            cleanup (Optional[bool]):
            dct (Optional[dict]):
            sort_order (Optional[str]): ASC | DESC

        Returns:
            dict (dict):"""
        if not dct:
            dct = {'Alert Source':         self.alert_source,
                   'Resolution Summary':   self.resolution_summary,
                   'Incident Level':       self.incident_level,
                   'Incident Category':    self.incident_category,
                   'True Resolution':      self.true_resolution,
                   'Analysis Completed':   self.analysis_completed,
                   'True Detect Time':     self.true_detect_time,
                   'Analysis Started':     self.analysis_started,
                   'Compliance Contacted': self.compliance_contacted,
                   'Contain Time':         self.contain_time,
                   'Vendor Ticket Number': self.vendor_ticket_number,
                   'Mitigated':            self.mitigated,
                   'Disposition':          self.disposition,
                   'True Event Time':      self.true_event_time,
                   'Customer Exposure':    self.customer_exposure}

        if cleanup:
            dct = {k: v for k, v in dct.items() if v is not None}

        if sort_order:
            dct = sort_dict(dct, reverse=True if sort_order.lower() == 'desc' else False)

        return dct


if __name__ == '__main__':
    print(__doc__)
