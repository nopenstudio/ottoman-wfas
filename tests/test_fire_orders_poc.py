"""Check source wiring and fail-closed probe scope under Python 2.7."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from header_operations import *
from module_fire_orders_poc import (
    fire_orders_poc_enabled, fire_orders_poc_event, fire_orders_poc_receive,
    fire_orders_poc_trigger,
)
from module_mission_templates import mission_templates
from module_scripts import scripts


class FireOrdersProbeTests(unittest.TestCase):
    def test_opt_in_wiring(self):
        hooked = [mission[0] for mission in mission_templates
                  if fire_orders_poc_trigger in mission[5]]
        self.assertEqual(hooked, ["multiplayer_tdm"] if fire_orders_poc_enabled else [])
        dispatch = dict(scripts)["game_receive_network_message"]
        self.assertEqual(dispatch[:2], [
            (store_script_param, ":player_no", 1),
            (store_script_param, ":event_type", 2),
        ])
        event_test = (eq, ":event_type", fire_orders_poc_event)
        self.assertEqual(dispatch.count(event_test), int(fire_orders_poc_enabled))
        if fire_orders_poc_enabled:
            self.assertEqual(dispatch[2], try_begin)
            end = 3 + len(fire_orders_poc_receive)
            self.assertEqual(dispatch[3:end], fire_orders_poc_receive)
            self.assertEqual(dispatch[end], else_try)

    def test_mutation_follows_server_and_bot_guards(self):
        ops = fire_orders_poc_receive
        writes = [op for op in ops if isinstance(op, tuple) and op[0] in (
            agent_set_wielded_item, agent_equip_item, agent_unequip_item,
            agent_set_ammo, team_give_order, agent_set_division, agent_set_group,
            agent_set_slot, agent_set_animation,
        )]
        self.assertEqual(writes, [(agent_set_wielded_item, ":bot", ":requested")])
        guards = [
            multiplayer_is_dedicated_server,
            (player_is_active, ":player_no"),
            (eq, ":commander_team", ":team"),
            (try_for_agents, ":bot"),
            (agent_is_non_player, ":bot"),
            (eq, ":bot_team", ":team"),
            (agent_get_group, ":owner", ":bot"),
            (eq, ":owner", ":player_no"),
            (neq, ":selected", 0),
            (eq, ":matches", 1),
            (ge, ":now", ":deadline"),
            writes[0],
        ]
        positions = [ops.index(op) for op in guards]
        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
