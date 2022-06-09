#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule

from ..module_utils import (arguments, attachment, client, errors, table,
                            utils, validation, variable)
from ..module_utils.request_item import PAYLOAD_FIELDS_MAPPING
from ..module_utils.utils import get_mapper

__metaclass__ = type


DOCUMENTATION = r"""
module: request_item

author:
  - Manca Bizjak (@mancabizjak)
  - Miha Dolinar (@mdolin)
  - Tadej Borovsak (@tadeboro)
  - Matej Pevec (@mysteriouswolf)

short_description: Manage ServiceNow change requests

description:
  - Create, delete or update a ServiceNow change request.
  - For more information, refer to the ServiceNow change management documentation at
    U(https://docs.servicenow.com/bundle/paris-it-service-management/page/product/change-management/concept/c_ITILChangeManagement.html).
version_added: 1.0.0
extends_documentation_fragment:
  - servicenow.itsm.instance
  - servicenow.itsm.sys_id
  - servicenow.itsm.number
  - servicenow.itsm.attachments
  - servicenow.itsm.request_item_mapping
seealso:
  - module: servicenow.itsm.request_item_info

options:
  state:
    description:
      - The state of the item request.
      - If I(state) value is C(assess) or C(authorize) or C(scheduled) or
        C(implement) or C(review) or C(closed),
        I(assignment_group) parameter must be filled in.
      - For more information on state model and transition,
        refere to the ServiceNow documentation at
        U(https://docs.servicenow.com/bundle/paris-it-service-management/page/product/change-management/concept/c_ChangeStateModel.html)
      - Default choices are C(new), C(assess), C(authorize), C(scheduled), C(implement), C(review), C(closed), C(canceled), C(absent).
        One can override them by setting I(request_item_mapping.state).
    type: str
  assignment_group:
    description:
      - The group that the change request is assigned to.
      - Required if I(state) value is C(assess) or C(authorize) or
        C(scheduled) or C(implement) or C(review) or C(closed).
    type: str
  priority:
    description:
      - Priority is based on impact and urgency, and it identifies how quickly
        the service desk should address the task.
      - Default choices are C(critical), C(high), C(moderate), C(low).
        One can override them by setting I(request_item_mapping.priority).
    type: str
  impact:
    description:
      - Impact is a measure of the effect of an incident, problem,
        or change on business processes.
      - Default choices are C(high), C(medium), C(low).
        One can override them by setting I(request_item_mapping.impact).
    type: str
  urgency:
    description:
      - The extent to which resolution of an change request can bear delay.
      - Default choices are C(high), C(medium), C(low).
        One can override them by setting I(request_item_mapping.urgency).
    type: str
  short_description:
    description:
      - A summary of the change request.
    type: str
  description:
    description:
      - A detailed description of the change request.
    type: str
  close_notes:
    description:
      - Resolution notes added by the user who closed the change request.
      - The change request must have this parameter set prior to
        transitioning to the C(closed) state.
    type: str
  other:
    description:
      - Optional remaining parameters.
      - For more information on optional parameters, refer to the ServiceNow
        change request documentation at
        U(https://docs.servicenow.com/bundle/sandiego-field-service-management/page/product/planning-and-policy/task/t_CreateARequestThroughTheCatalog.html).
    type: dict
"""

EXAMPLES = """
- name: Create change request
  servicenow.itsm.request_item:
    instance:
      host: https://instance_id.service-now.com
      username: user
      password: pass

    type: standard
    state: Open
    requested_by: some.user
    short_description: Install new Cisco
    description: Please install new Cat. 6500 in Data center 01
    attachments:
      - path: path/to/attachment.txt
    priority: moderate
    impact: low
    other:
      expected_start: 2021-02-12

- name: Change state of the change request
  servicenow.itsm.request_item:
    instance:
      host: https://instance_id.service-now.com
      username: user
      password: pass

    state: assess
    assignment_group: some.group
    number: RITM0010001

- name: Close request_item
  servicenow.itsm.request_item:
    instance:
      host: https://instance_id.service-now.com
      username: user
      password: pass

    state: "Closed Complete"
    close_notes: "Closed Note"
    number: RITM0010001

- name: Delete request_item
  servicenow.itsm.request_item:
    instance:
      host: https://instance_id.service-now.com
      username: user
      password: pass

    state: absent
    number: RITM0010001
"""


DIRECT_PAYLOAD_FIELDS = (
    "state",
    "assignment_group",
    "priority",
    "impact",
    "short_description",
    "description",
    "close_notes",
)


def ensure_absent(module, table_client, attachment_client, variable_client):
    mapper = get_mapper(module, "request_item_mapping", PAYLOAD_FIELDS_MAPPING)
    query = utils.filter_dict(module.params, "sys_id", "number")
    change = table_client.get_record("sc_req_item", query)

    if change:
        attachment_client.delete_attached_records(
            "sc_req_item",
            change["sys_id"],
            module.check_mode,
        )
        table_client.delete_record("sc_req_item", change, module.check_mode)
        return True, None, dict(before=mapper.to_ansible(change), after=None)

    return False, None, dict(before=None, after=None)


def validate_params(params, change_request=None):
    missing = []
    if params["state"] == "closed":
        missing.extend(
            validation.missing_from_params_and_remote(
                ("close_notes"), params, change_request
            )
        )

    if missing:
        raise errors.ServiceNowError(
            "Missing required parameters {0}".format(", ".join(missing))
        )


def ensure_present(module, table_client, attachment_client, variable_client):
    mapper = get_mapper(module, "request_item_mapping", PAYLOAD_FIELDS_MAPPING)
    query = utils.filter_dict(module.params, "sys_id", "number")
    payload = build_payload(module, table_client)
    attachments = attachment.transform_metadata_list(
        module.params["attachments"], module.sha256
    )

    if not query:
        # User did not specify existing change request, so we need to create a new one.
        validate_params(module.params)
        new = mapper.to_ansible(
            table_client.create_record(
                "sc_req_item", mapper.to_snow(payload), module.check_mode
            )
        )

        # When we execute in check mode, new["sys_id"] is not defined.
        # In order to give users back as much info as possible, we fake the sys_id in the
        # next call.
        new["attachments"] = attachment_client.upload_records(
            "sc_req_item",
            new.get("sys_id", "N/A"),
            attachments,
            module.check_mode,
        )
        return True, new, dict(before=None, after=new)

    old = mapper.to_ansible(
        table_client.get_record("sc_req_item", query, must_exist=True)
    )

    old["attachments"] = attachment_client.list_records(
        dict(table_name="sc_req_item", table_sys_id=old["sys_id"])
    )

    variables = variable_client.list(old["sys_id"])

    old["variables"] = variables["variables"]
    old["vars"] = variables["vars"]

    if utils.is_superset(old, payload) and not any(
        attachment.are_changed(old["attachments"], attachments)
    ):
        # No change in parameters we are interested in - nothing to do.
        return False, old, dict(before=old, after=old)

    validate_params(module.params, old)
    new = mapper.to_ansible(
        table_client.update_record(
            "sc_req_item",
            mapper.to_snow(old),
            mapper.to_snow(payload),
            module.check_mode,
        )
    )
    new["attachments"] = attachment_client.update_records(
        "sc_req_item",
        old["sys_id"],
        attachments,
        old["attachments"],
        module.check_mode,
    )
    # is not posible to make variable changes yet
    new["variables"] = variables["variables"]
    new["vars"] = variables["vars"]

    return True, new, dict(before=old, after=new)


def build_payload(module, table_client):
    payload = (module.params["other"] or {}).copy()
    payload.update(utils.filter_dict(module.params, *DIRECT_PAYLOAD_FIELDS))

    # The change model is set to the same value as the change type
    # as the standard change request requires the model to be set.
    # For that reason change model is set for every type of change request.
    if module.params["assignment_group"]:
        assignment_group = table.find_assignment_group(
            table_client, module.params["assignment_group"]
        )
        payload["assignment_group"] = assignment_group["sys_id"]

    return payload


def run(module, table_client, attachment_client, variable_client):
    if module.params["state"] == "absent":
        return ensure_absent(module, table_client, attachment_client)
    return ensure_present(module, table_client, attachment_client, variable_client)


def main():
    module_args = dict(
        arguments.get_spec(
            "instance", "sys_id", "number", "attachments", "request_item_mapping"
        ),
        state=dict(
            type="str",
        ),
        assignment_group=dict(
            type="str",
        ),
        priority=dict(
            type="str",
        ),
        impact=dict(
            type="str",
        ),
        urgency=dict(
            type="str",
        ),
        short_description=dict(
            type="str",
        ),
        description=dict(
            type="str",
        ),
        close_notes=dict(
            type="str",
        ),
        other=dict(
            type="dict",
        ),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ("state", "absent", ("sys_id", "number"), True),
        ],
    )

    try:
        snow_client = client.Client(**module.params["instance"])
        table_client = table.TableClient(snow_client)
        attachment_client = attachment.AttachmentClient(snow_client)
        variable_client = variable.VariableClient(snow_client)
        changed, record, diff = run(module, table_client, attachment_client, variable_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ServiceNowError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
