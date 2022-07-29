#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import (arguments, attachment, client, errors, query,
                            table, utils, variable)
from ..module_utils.request_item import PAYLOAD_FIELDS_MAPPING
from ..module_utils.utils import get_mapper

__metaclass__ = type


DOCUMENTATION = r"""
module: request_task_info

author:
  - Manca Bizjak (@mancabizjak)
  - Miha Dolinar (@mdolin)
  - Tadej Borovsak (@tadeboro)
  - Matej Pevec (@mysteriouswolf)
  - Toni Moreno (@toni-moreno)
short_description: List ServiceNow Request Item
description:
  - Retrieve information about ServiceNow Request Item.
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
- name: Retrieve all request_task
  servicenow.itsm.request_task_info:
  register: result

- name: Retrieve a specific change request by its sys_id
  servicenow.itsm.request_task_info:
    sys_id: 5368c49007401110befff6fd7c1ed01d
  register: result

- name: Retrieve request_task by number
  servicenow.itsm.request_task_info:
    number: RITM0010001
  register: result

- name: Retrieve request_task that contain SAP in its short description
  servicenow.itsm.request_task_info:
    query:
      - short_description: LIKE SOFTWARE
  register: result

- name: Retrieve new request_task assigned to abel.tuter or bertie.luby
  servicenow.itsm.request_task_info:
    query:
      - state: = new
        assigned_to: = abel.tuter
      - state: = new
        assigned_to: = bertie.luby
"""

RETURN = r"""
records:
  - active: 'false'
    activity_due: ''
    additional_assignee_list: ''
    approval: not requested
    approval_history: ''
    approval_set: ''
    assigned_to: ''
    assignment_group: 74ad1ff3c611227d01d25feac2af603f
    attachments: []
    business_duration: '1970-01-01 08:00:00'
    business_service: ''
    calendar_duration: ''
    calendar_stc: ''
    close_notes: ''
    closed_at: '2022-06-09 11:34:15'
    closed_by: 6816f79cc0a8016401c5a33be04be441
    cmdb_ci: ''
    comments: ''
    comments_and_work_notes: ''
    company: ''
    contact_type: ''
    contract: ''
    correlation_display: ''
    correlation_id: ''
    delivery_plan: ''
    delivery_task: 982086afc611227801df50a33779081e
    description: Assess or Scope Task. Modify Due Date if neccessary
    due_date: '2022-06-09 11:09:32'
    escalation: '0'
    expected_start: '2022-06-08 11:09:32'
    follow_up: ''
    group_list: ''
    impact: low
    knowledge: 'false'
    location: ''
    made_sla: 'true'
    number: SCTASK0010001
    opened_at: '2022-06-08 11:09:32'
    opened_by: 6816f79cc0a8016401c5a33be04be441
    order: '100'
    parent: 5368c49007401110befff6fd7c1ed01d
    priority: low
    reassignment_count: '0'
    request: db68c49007401110befff6fd7c1ed01c
    request_item: 5368c49007401110befff6fd7c1ed01d
    route_reason: ''
    sc_catalog: ''
    service_offering: ''
    short_description: Assess or Scope Task
    sla_due: ''
    state: Closed Complete
    sys_class_name: sc_task
    sys_created_by: admin
    sys_created_on: '2022-06-08 11:09:32'
    sys_domain: global
    sys_domain_path: /
    sys_id: 2b68c49007401110befff6fd7c1ed024
    sys_mod_count: '7'
    sys_tags: ''
    sys_updated_by: admin
    sys_updated_on: '2022-06-09 11:36:44'
    task_effective_number: SCTASK0010001
    time_worked: ''
    universal_request: ''
    upon_approval: proceed
    upon_reject: cancel
    urgency: low
    user_input: ''
    variables: []
    vars: []
    watch_list: ''
    work_end: '2022-06-09 11:36:44'
    work_notes: ''
    work_notes_list: ''
    work_start: '2022-06-08 11:09:37'
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


def by_order(ele):
    return int(ele['value']['order'])


def run(module, table_client, attachment_client, variable_client):
    mapper = get_mapper(module, "change_request_mapping", PAYLOAD_FIELDS_MAPPING)

    if module.params["query"]:
        query = {"sysparm_query": sysparms_query(module, table_client, mapper)}
    else:
        query = utils.filter_dict(module.params, "sys_id", "number")

    retval = []

    for record in table_client.list_records("sc_task", query):
        attachments = attachment_client.list_records(
            dict(table_name="sc_task", table_sys_id=record["sys_id"]),
        )
        variables = variable_client.list(record["sys_id"])
        retval.append(dict(mapper.to_ansible(record), attachments=attachments, variables=variables['variables'], vars=variables['vars']))

    return retval


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
        variable_client = variable.VariableClient(snow_client)
        records = run(module, table_client, attachment_client, variable_client)
        module.exit_json(changed=False, records=records)
    except errors.ServiceNowError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
