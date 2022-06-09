#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import (arguments, attachment, client, errors, query,
                            table, utils)
from ..module_utils.request_item import PAYLOAD_FIELDS_MAPPING
from ..module_utils.utils import get_mapper

__metaclass__ = type


DOCUMENTATION = r"""
module: request_info

author:
  - Manca Bizjak (@mancabizjak)
  - Miha Dolinar (@mdolin)
  - Tadej Borovsak (@tadeboro)
  - Matej Pevec (@mysteriouswolf)
short_description: List ServiceNow change requests
description:
  - Retrieve information about ServiceNow change requests.
  - For more information, refer to the ServiceNow change management documentation at
    U(https://docs.servicenow.com/bundle/rome-it-service-management/page/product/planning-and-policy/concept/request-management-architecture.html).
version_added: 1.0.0
extends_documentation_fragment:
  - servicenow.itsm.instance
  - servicenow.itsm.sys_id.info
  - servicenow.itsm.number.info
  - servicenow.itsm.query
  - servicenow.itsm.change_request_mapping
seealso:
  - module: servicenow.itsm.change_request
"""

EXAMPLES = r"""
- name: Retrieve all change requests
  servicenow.itsm.request_info:
  register: result

- name: Retrieve a specific change request by its sys_id
  servicenow.itsm.request_info:
    sys_id: 5368c49007401110befff6fd7c1ed01d
  register: result

- name: Retrieve change requests by number
  servicenow.itsm.request_info:
    number: PRB0007601
  register: result

- name: Retrieve change requests that contain SAP in its short description
  servicenow.itsm.request_info:
    query:
      - short_description: LIKE SAP
  register: result

- name: Retrieve new change requests assigned to abel.tuter or bertie.luby
  servicenow.itsm.request_info:
    query:
      - state: = new
        assigned_to: = abel.tuter
      - state: = new
        assigned_to: = bertie.luby
"""

RETURN = r"""

"""


def remap_params(query, table_client):
    query_load = []

    for item in query:
        q = dict()
        for k, v in item.items():
            if k == "type":
                q["chg_model"] = (v[0], v[1])

            elif k == "hold_reason":
                q["on_hold_reason"] = (v[0], v[1])

            elif k == "requested_by":
                user = table.find_user(table_client, v[1])
                q["requested_by"] = (v[0], user["sys_id"])

            elif k == "assignment_group":
                assignment_group = table.find_assignment_group(table_client, v[1])
                q["assignment_group"] = (v[0], assignment_group["sys_id"])

            elif k == "template":
                standard_change_template = table.find_standard_change_template(
                    table_client, v[1]
                )
                q["std_change_producer_version"] = (
                    v[0],
                    standard_change_template["sys_id"],
                )

            else:
                q[k] = v

        query_load.append(q)

    return query_load


def sysparms_query(module, table_client, mapper):
    parsed, err = query.parse_query(module.params["query"])
    if err:
        raise errors.ServiceNowError(err)

    remap_query = remap_params(parsed, table_client)

    return query.serialize_query(query.map_query_values(remap_query, mapper))


def run(module, table_client, attachment_client):
    mapper = get_mapper(module, "change_request_mapping", PAYLOAD_FIELDS_MAPPING)

    if module.params["query"]:
        query = {"sysparm_query": sysparms_query(module, table_client, mapper)}
    else:
        query = utils.filter_dict(module.params, "sys_id", "number")

    return [
        dict(
            mapper.to_ansible(record),
            attachments=attachment_client.list_records(
                dict(table_name="sc_request", table_sys_id=record["sys_id"]),
            ),
        )
        for record in table_client.list_records("sc_request", query)
    ]


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec(
                "instance", "sys_id", "number", "query", "change_request_mapping"
            ),
        ),
        mutually_exclusive=[("sys_id", "query"), ("number", "query")],
    )

    try:
        snow_client = client.Client(**module.params["instance"])
        table_client = table.TableClient(snow_client)
        attachment_client = attachment.AttachmentClient(snow_client)
        records = run(module, table_client, attachment_client)
        module.exit_json(changed=False, records=records)
    except errors.ServiceNowError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
