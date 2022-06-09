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
module: request_item_info

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
  - servicenow.itsm.request_item_mapping
seealso:
  - module: servicenow.itsm.request_item
"""

EXAMPLES = r"""
- name: Retrieve all request_item
  servicenow.itsm.request_item_info:
  register: result

- name: Retrieve a specific change request by its sys_id
  servicenow.itsm.request_item_info:
    sys_id: 5368c49007401110befff6fd7c1ed01d
  register: result

- name: Retrieve request_item by number
  servicenow.itsm.request_item_info:
    number: RITM0010001
  register: result

- name: Retrieve request_item that contain SAP in its short description
  servicenow.itsm.request_item_info:
    query:
      - short_description: LIKE SOFTWARE
  register: result

- name: Retrieve new request_item assigned to abel.tuter or bertie.luby
  servicenow.itsm.request_item_info:
    query:
      - state: = new
        assigned_to: = abel.tuter
      - state: = new
        assigned_to: = bertie.luby
"""

RETURN = r"""
records:
  - active: 'true'
    activity_due: ''
    additional_assignee_list: ''
    approval: approved
    approval_history: ''
    approval_set: '2022-06-08 11:09:37'
    assigned_to: ''
    assignment_group: ''
    attachments:
      - average_image_color: ''
        chunk_size_bytes: '700000'
        compressed: 'true'
        content_type: application/octet-stream
        download_link: >-
          https://dev96534.service-now.com/api/now/attachment/71c8201407801110befff6fd7c1ed0eb/file
        file_name: drift_stream.npy
        hash: 94f0cf6ff626277c949d4649ef9e46cc525e2c96fd0adbd5451cb6bbd1330f1d
        image_height: ''
        image_width: ''
        size_bytes: '16128'
        size_compressed: '1255'
        state: available
        sys_created_by: admin
        sys_created_on: '2022-06-08 13:30:52'
        sys_id: 71c8201407801110befff6fd7c1ed0eb
        sys_mod_count: '1'
        sys_tags: ''
        sys_updated_by: system
        sys_updated_on: '2022-06-08 13:30:55'
        table_name: sc_req_item
        table_sys_id: 5368c49007401110befff6fd7c1ed01d
    backordered: 'false'
    billable: 'false'
    business_duration: ''
    business_service: ''
    calendar_duration: ''
    cat_item: 10d69689c611227600ffeba41c664824
    close_notes: ''
    closed_at: ''
    closed_by: ''
    cmdb_ci: ''
    comments: ''
    comments_and_work_notes: ''
    company: ''
    configuration_item: ''
    contact_type: ''
    context: ''
    contract: ''
    correlation_display: ''
    correlation_id: ''
    delivery_plan: 982013fdc61122780154f4972935fcb1
    delivery_task: ''
    description: ''
    due_date: '2022-06-10 11:09:31'
    escalation: '0'
    estimated_delivery: ''
    expected_start: ''
    flow_context: ''
    follow_up: ''
    group_list: ''
    impact: low
    knowledge: 'false'
    location: ''
    made_sla: 'true'
    number: RITM0010001
    opened_at: '2022-06-08 11:09:32'
    opened_by: 6816f79cc0a8016401c5a33be04be441
    order: ''
    order_guide: ''
    parent: ''
    price: '0'
    priority: low
    quantity: '1'
    reassignment_count: '0'
    recurring_frequency: ''
    recurring_price: '0'
    request: db68c49007401110befff6fd7c1ed01c
    requested_for: 6816f79cc0a8016401c5a33be04be441
    route_reason: ''
    sc_catalog: ''
    service_offering: ''
    short_description: "Request for software installation service\n\t\t"
    sla_due: ''
    stage: Assess or Scope Task
    state: '1'
    sys_class_name: sc_req_item
    sys_created_by: admin
    sys_created_on: '2022-06-08 11:09:32'
    sys_domain: global
    sys_domain_path: /
    sys_id: 5368c49007401110befff6fd7c1ed01d
    sys_mod_count: '3'
    sys_tags: ''
    sys_updated_by: admin
    sys_updated_on: '2022-06-08 13:30:53'
    task_effective_number: RITM0010001
    time_worked: ''
    universal_request: ''
    upon_approval: proceed
    upon_reject: cancel
    urgency: low
    user_input: ''
    variables:
      - name:
          active: 'true'
          attributes: ''
          cat_item: 10d69689c611227600ffeba41c664824
          category: ''
          choice_direction: ''
          choice_field: ''
          choice_table: ''
          create_roles: ''
          default_html_value: ''
          default_value: ''
          delete_roles: ''
          delivery_plan: ''
          description: ' '
          display_title: 'false'
          do_not_select_first: 'false'
          dynamic_default_value: ''
          dynamic_ref_qual: ''
          enable_also_request_for: 'false'
          example_text: ''
          field: ''
          global: 'false'
          help_tag: ''
          help_text: ''
          hidden: 'false'
          include_none: 'false'
          instructions: ''
          layout: ''
          list_table: ''
          lookup_label: ''
          lookup_price: ''
          lookup_table: ''
          lookup_unique: 'false'
          lookup_value: ''
          macro: ''
          macroponent: ''
          mandatory: 'false'
          map_to_field: 'false'
          mask_use_confirmation: 'false'
          mask_use_encryption: 'false'
          name: software
          order: '100'
          price_if_checked: '0'
          pricing_implications: 'false'
          published_ref: ''
          question_text: What software do you need installed ?
          read_only: 'false'
          read_roles: ''
          read_script: ''
          rec_lookup_price: ''
          rec_price_if_checked: '0'
          record: ''
          record_producer_table: ''
          reference: ''
          reference_qual: ''
          reference_qual_condition: ''
          rich_text: ''
          roles_to_use_also_request_for: ''
          save_script: ''
          scale_max: '5'
          scale_min: '0'
          show_help: 'false'
          show_help_on_load: 'false'
          sp_widget: ''
          summary_macro: ''
          sys_class_name: item_option_new
          sys_created_by: glide.maint
          sys_created_on: '2006-08-09 15:05:24'
          sys_id: f3776a8bc0a8010a003825c7bcb187dd
          sys_mod_count: '0'
          sys_name: What software do you need installed ?
          sys_package: b59122e6a5740110c0a0e1db2cdc956d
          sys_policy: ''
          sys_scope: global
          sys_tags: ''
          sys_update_name: item_option_new_f3776a8bc0a8010a003825c7bcb187dd
          sys_updated_by: system
          sys_updated_on: '2012-11-14 16:49:50'
          table: ''
          tooltip: ''
          type: '6'
          ui_page: ''
          unique: 'false'
          use_dynamic_default: 'false'
          use_reference_qualifier: ''
          validate_regex: ''
          variable_name: ''
          variable_set: ''
          variable_width: ''
          visibility: '1'
          visible_bundle: 'true'
          visible_guide: 'true'
          visible_standalone: 'true'
          visible_summary: 'true'
          write_roles: ''
        value:
          cart_item: ''
          item_option_new: f3776a8bc0a8010a003825c7bcb187dd
          order: '1'
          sc_cat_item_option: ''
          sys_created_by: admin
          sys_created_on: '2022-06-08 11:09:31'
          sys_id: df68c49007401110befff6fd7c1ed01b
          sys_mod_count: '0'
          sys_tags: ''
          sys_updated_by: admin
          sys_updated_on: '2022-06-08 11:09:31'
          value: oracle
    watch_list: ''
    work_end: ''
    work_notes: ''
    work_notes_list: ''
    work_start: ''
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


def merge_two_dicts(x, y):
    z = x.copy()   # start with keys and values of x
    z.update(y)    # modifies z with keys and values of y
    return z


def run(module, table_client, attachment_client, variable_client):
    mapper = get_mapper(module, "request_item_mapping", PAYLOAD_FIELDS_MAPPING)

    if module.params["query"]:
        query = {"sysparm_query": sysparms_query(module, table_client, mapper)}
    else:
        query = utils.filter_dict(module.params, "sys_id", "number")

    retval = []

    for record in table_client.list_records("sc_req_item", query):
        attachments = attachment_client.list_records(
            dict(table_name="sc_req_item", table_sys_id=record["sys_id"]),
        )
        variables = variable_client.list(record["sys_id"])
        retval.append(dict(mapper.to_ansible(record), attachments=attachments, variables=variables['variables'], vars=variables['vars']))

    return retval


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            arguments.get_spec(
                "instance", "sys_id", "number", "query", "request_item_mapping"
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
