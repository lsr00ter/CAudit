from copy import copy

import urllib3
from ldap3 import LEVEL, BASE

from plugins.Exchange import PluginExchangeScanBase
from utils.consts import AllPluginTypes

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PluginExchangeNoSenderID(PluginExchangeScanBase):
    """未启用 SenderID 代理"""

    display = "未启用 SenderID 代理"
    alias = "ex_no_sender_id"
    p_type = AllPluginTypes.Scan

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run_script(self, args) -> dict:
        result = copy(self.result)
        instance_list = []
        query = "(objectClass=*)"
        attributes = ["cn"]
        ldap_cli = (
            "CN=Microsoft Exchange,CN=Services,CN=Configuration,"
            + self.ldap_cli.domain_dn
        )
        entry_generator = self.ldap_cli.con.extend.standard.paged_search(
            search_base=ldap_cli,
            search_filter=query,
            search_scope=LEVEL,
            get_operational_attributes=True,
            attributes=attributes,
            paged_size=1000,
            generator=True,
        )

        for entry1 in entry_generator:
            ldap_cli1 = (
                "CN=SenderIdConfig,CN=Message Hygiene,CN=Transport Settings,CN="
                + entry1["attributes"]["cn"]
                + ","
                + ldap_cli
            )

            attributes = ["msExchAgentsFlags", "cn"]
            entry_generator2 = self.ldap_cli.con.extend.standard.paged_search(
                search_base=ldap_cli1,
                search_filter=query,
                search_scope=BASE,
                get_operational_attributes=True,
                attributes=attributes,
                paged_size=1000,
                generator=True,
            )
            for entry2 in entry_generator2:
                # print(entry2["attributes"]['msExchAgentsFlags'])
                if entry2["attributes"]["msExchAgentsFlags"] & int("0b0001", 2) == 0:
                    result["status"] = 1
                    instance = {}
                    instance["msExchAgentsFlags"] = entry2["attributes"][
                        "msExchAgentsFlags"
                    ]
                    instance_list.append(instance)
        result["data"] = {"instance_list": instance_list}
        return result
