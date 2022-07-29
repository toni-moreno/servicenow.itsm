# -*- coding: utf-8 -*-
# Copyright: (c) 2021, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from . import table
from .utils import get_mapper


def by_order_full(ele):
    return int(ele['value']['order'])


def by_order_simple(ele):
    return int(ele['order'])


# https://docs.servicenow.com/bundle/sandiego-application-development/page/administer/flow-designer/reference/supported-service-catalog-types.html


var_type = [
    ("", ""),
    ("1", "Yes/No"),
    ("2", "Multi_Line_Text"),
    ("3", "Multiple_Choice"),
    ("4", "Numeric_cale"),
    ("5", "Select_Box"),
    ("6", "Single_Line_Text"),
    ("7", "CheckBox"),
    ("8", "Reference"),
    ("9", "Date"),
    ("10", "Date/Time"),
    ("11", "Label"),
    ("12", "Break"),
    ("14", "Custom"),
    ("15", "UI_Page"),
    ("16", "Wide Single Line Text"),
    ("17", "Custom_with_Label"),
    ("18", "Lookup_Select_Box"),
    ("19", "Container Start"),
    ("20", "Container End"),
    ("21", "List_Collector"),
    ("22", "Lookup_Multiple_Choice"),
    ("23", "HTML"),
    ("24", "Container Split"),
    ("25", "Masked"),
    ("26", "Email"),
    ("27", "URL"),
    ("28", "IP_Address"),
    ("29", "Duration"),
    ("30", "Time"),
    ("31", "Requested_For"),
    ("32", "Rich_Text_Label"),
    ("33", "Attachment"),
]


def map_type(type_):
    if type_ in [i[0] for i in var_type]:
        for i in var_type:
            if type_ == i[0]:
                return i[1]
    else:
        return "unknown"


class VariableClient:
    def __init__(self, client):
        self.client = client
        self.table_client = table.TableClient(client)

    # list variables in the ticket with sysid
    def list(self, sys_id):
        vars = []
        vars_full = []
        for v in self.table_client.list_records("sc_item_option_mtom", {'request_item': sys_id}):
            value = self.table_client.get_record("sc_item_option", {'sys_id': v["sc_item_option"]})
            name = self.table_client.get_record("item_option_new", {'sys_id': value["item_option_new"]})
            # print(name)
            vars.append(dict(
                order=value['order'],
                active=name['active'],
                name=name['name'],
                type=map_type(name['type']),
                mandatory=name['mandatory'],
                read_only=name['read_only'],
                question_text=name['question_text'],
                description=name['description'],
                value=value['value']))
            vars_full.append(dict(name=name, value=value))
        vars_full.sort(key=by_order_full)
        vars.sort(key=by_order_simple)
        return dict(variables=vars_full, vars=vars)

    # def create(self, sys_id, key, value):

    # def delete(self, sys_id, key):

    # def update(self, sys_id, key, value):
