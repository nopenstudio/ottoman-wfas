"""Check source wiring and fail-closed probe scope under Python 2.7."""
import operator
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from header_operations import *
from header_common import s0, s1, s2
from header_triggers import key_f8, ti_before_mission_start, ti_server_player_joined
from module_fire_orders_poc import (
    fire_orders_poc_enabled, fire_orders_poc_event, fire_orders_poc_request,
    fire_orders_poc_interval_ms, fire_orders_poc_triggers, fire_orders_poc_result_event,
    fire_orders_poc_unsupported_triggers, result_wait_reload, result_wait_bolt,
    native_bayonet_order, native_bayonet_experiment, result_native_sent,
    result_native_refused, result_swap_blocked, fire_orders_poc_dispatch, fire_orders_poc_scripts,
)
from module_mission_templates import mission_templates
from module_scripts import scripts
from test_bolt_operations import parse


class FireOrdersProbeTests(unittest.TestCase):
    def test_opt_in_wiring(self):
        for trigger in fire_orders_poc_triggers:
            hooked = [mission[0] for mission in mission_templates if trigger in mission[5]]
            self.assertEqual(hooked, ["multiplayer_tdm"] if fire_orders_poc_enabled else [])
        dispatch = dict(scripts)["game_receive_network_message"]
        self.assertEqual(dispatch[:2], [
            (store_script_param, ":player_no", 1),
            (store_script_param, ":event_type", 2),
        ])
        event_test = (eq, ":event_type", fire_orders_poc_event)
        self.assertEqual(dispatch.count(event_test), int(fire_orders_poc_enabled))
        names = {name for name, _ in fire_orders_poc_scripts}
        self.assertEqual(names.intersection(dict(scripts)), names if fire_orders_poc_enabled else set())
        if fire_orders_poc_enabled:
            self.assertEqual(dispatch[2], try_begin)
            end = 3 + len(fire_orders_poc_dispatch)
            self.assertEqual(dispatch[3:end], fire_orders_poc_dispatch)
            self.assertEqual(dispatch[end], else_try)

    def test_read_only_assessment_follows_server_and_bot_guards(self):
        ops = fire_orders_poc_request
        writes = [op for op in ops if isinstance(op, tuple) and op[0] in (
            agent_set_wielded_item, agent_equip_item, agent_unequip_item,
            agent_set_ammo, team_give_order, agent_set_division, agent_set_group,
            agent_set_slot, agent_set_animation,
        )]
        self.assertEqual(writes, [])
        guards = [
            multiplayer_is_server,
            (player_is_active, ":player_no"),
            (eq, ":commander_team", ":team"),
            (try_for_agents, ":bot"),
            (agent_is_non_player, ":bot"),
            (eq, ":bot_team", ":team"),
            (agent_get_group, ":owner", ":bot"),
            (eq, ":owner", ":player_no"),
            (neq, ":selected", 0),
            (eq, ":matches", 1),
            (lt, ":now", ":deadline"),
        ]
        positions = [ops.index(op) for op in guards]
        self.assertEqual(positions, sorted(positions))


class RequestModel(object):
    """Execute the probe tuples with two players and one eligible rifle bot."""
    def __init__(self):
        self.slots = {}
        self.scans = self.logs = 0
        self.replies = []
        self.messages = []
        self.strings = {}
        self.server = True
        self.dedicated = True
        self.local_player = 0
        self.commander = 11
        self.selection = [0]
        self.sent = []
        self.players = {1: 11, 2: 12}
        self.owner = 1
        self.agents = [20]
        self.foreign = set()
        self.divisions = {}
        self.password = ""
        self.orders = []
        self.now = 0
        self.deadline = 0
        self.attack_state = 0
        self.wield_changes_mode = True
        self.wield_calls = []
        self.weapon = "itm_canakkale_turk_rifle"

    def request(self, player=1, action=0, mask=1):
        values = {
            ":player_no": player, ":event_type": fire_orders_poc_event,
            "$g_multiplayer_game_type": 1, "$g_multiplayer_is_game_type_captain": 0,
        }
        self.execute(parse(fire_orders_poc_scripts[0][1])[0], values, [player, mask, action])

    def deliver(self, sender, payload):
        values = {":player_no": sender, ":event_type": fire_orders_poc_result_event}
        self.execute(parse(fire_orders_poc_dispatch[6:])[0], values,
                     [sender, fire_orders_poc_result_event] + list(payload))

    def press_f8(self, trigger=fire_orders_poc_triggers[0], host=False):
        self.server = host
        self.dedicated = False
        self.execute(parse(trigger[3] + trigger[4])[0], {}, [])

    def reset(self, event, player=1):
        trigger = next(t for t in fire_orders_poc_triggers if t[0] == event)
        self.execute(parse(trigger[3] + trigger[4])[0], {}, [player])

    def execute(self, nodes, values, params):
        def get(value):
            return values.get(value, value)

        either = False
        for node in nodes:
            kind, operation = node[:2]
            code, args = operation[0], operation[1:]
            if kind == "block":
                branches = node[2]
                if code == try_begin:
                    for branch in branches:
                        if self.execute(branch, values, params):
                            break
                else:
                    if code == try_for_agents:
                        self.scans += 1
                        members = self.agents
                    else:
                        members = range(get(args[1]), get(args[2]))
                    for member in members:
                        values[args[0]] = member
                        self.execute(branches[0], values, params)
                continue

            flagged = code
            code &= ~(neg | this_or_next)
            a = [get(arg) for arg in args]
            result = True
            if code == multiplayer_is_server:
                result = self.server
            elif code == multiplayer_is_dedicated_server:
                result = self.server and self.dedicated
            elif code == multiplayer_get_my_player:
                values[args[0]] = self.local_player
            elif code == call_script:
                if a[0] == "script_cf_ss1914_native_bayonet_order":
                    result = self.execute(parse(native_bayonet_order)[0], dict(values), a[1:])
                elif a[0] == "script_cf_ss1914_fire_order_result":
                    self.execute(parse(fire_orders_poc_scripts[1][1])[0], {}, a[1:])
                else:
                    assert a[0] == "script_game_receive_network_message"
                    self.request(player=a[1], mask=a[3], action=a[4])
            elif code == is_presentation_active:
                result = False
            elif code == key_clicked:
                result = a[0] == key_f8
            elif code == class_is_listening_order:
                result = a[1] in self.selection
            elif code == get_player_agent_no:
                values[args[0]] = self.commander
            elif code in (
                        game_in_multiplayer_mode, agent_is_active, agent_is_alive, agent_is_human):
                pass
            elif code == ge and isinstance(a[0], str) and isinstance(a[1], int):
                # Item names stand in for nonnegative item IDs in this model.
                result = a[1] <= 0
            elif code in (eq, neq, lt, ge, gt):
                result = {eq: operator.eq, neq: operator.ne, lt: operator.lt,
                          ge: operator.ge, gt: operator.gt}[code](*a)
            elif code == is_between:
                result = a[1] <= a[0] < a[2]
            elif code == player_is_active:
                result = a[0] in self.players
            elif code == agent_is_non_player:
                result = a[0] >= 20
            elif code == str_store_server_password:
                self.strings[args[0]] = self.password
            elif code == str_is_empty:
                result = not self.strings.get(args[0], "")
            elif code == team_give_order:
                self.orders.append(tuple(a))
            elif code == get_max_players:
                values[args[0]] = 4
            elif code == agent_get_slot:
                values[args[0]] = self.deadline
            elif code == agent_get_attack_action:
                values[args[0]] = self.attack_state
            elif code == agent_get_division:
                values[args[0]] = self.divisions.get(a[1], 0)
            elif code in (player_get_team_no, agent_get_team,
                          agent_get_ammo, team_get_weapon_usage_order):
                values[args[0]] = 0
            elif code == player_get_agent_id:
                values[args[0]] = self.players[a[1]]
            elif code == store_script_param:
                values[args[0]] = params[a[1] - 1]
            elif code == store_trigger_param_1:
                values[args[0]] = params[0]
            elif code == store_mission_timer_a_msec:
                values[args[0]] = self.now
            elif code == player_get_slot:
                values[args[0]] = self.slots.get(tuple(a[1:]), 0)
            elif code == player_set_slot:
                self.slots[tuple(a[:2])] = a[2]
            elif code in (store_add, store_sub):
                values[args[0]] = a[1] + a[2] if code == store_add else a[1] - a[2]
            elif code in (val_lshift, val_rshift, val_and, val_or, val_add, val_sub):
                values[args[0]] = {val_lshift: operator.lshift, val_rshift: operator.rshift, val_and: operator.and_,
                                  val_or: operator.or_, val_add: operator.add,
                                  val_sub: operator.sub}[code](*a)
            elif code == assign:
                values[args[0]] = a[1]
            elif code == agent_get_group:
                values[args[0]] = -1 if a[1] in self.foreign else self.owner
            elif code == agent_get_troop_id:
                values[args[0]] = "trp_khergit_dismounted_lancer_multiplayer_ai"
            elif code == agent_get_item_slot:
                values[args[0]] = {0: "itm_canakkale_turk_rifle", 1: "itm_canakkale_bullets"}.get(a[2], -1)
            elif code == agent_get_wielded_item:
                values[args[0]] = self.weapon
            elif code == agent_set_wielded_item:
                self.wield_calls.append(a[1])
                if self.wield_changes_mode:
                    self.weapon = a[1]
            elif code == multiplayer_send_2_int_to_server:
                self.sent.append(tuple(a))
            elif code == multiplayer_send_4_int_to_player:
                self.replies.append(tuple(a))
            elif code == str_clear:
                self.strings[args[0]] = ""
            elif code == str_store_string:
                self.strings[args[0]] = a[1].lstrip("@")
            elif code == display_message:
                message = a[0]
                for i, register in enumerate((s0, s1, s2)):
                    message = message.replace("{s%d}" % i, self.strings.get(register, ""))
                self.messages.append(message)
            elif code == server_add_message_to_log:
                self.logs += 1
            else:
                raise AssertionError("Unexpected opcode %r" % (operation,))

            if flagged & neg:
                result = not result
            if flagged & this_or_next:
                either = either or result
                continue
            if not (either or result):
                return False
            either = False
        return True


class RateLimitTests(unittest.TestCase):
    def test_first_request_at_zero_and_interval_boundary(self):
        model = RequestModel()
        model.request(action=1)
        self.assertEqual((model.scans, model.logs), (1, 1))
        model.request(action=2)
        model.now = fire_orders_poc_interval_ms - 1
        model.request(action=2)
        self.assertEqual((model.scans, model.logs), (1, 1))
        model.now += 1
        model.request(action=2)
        self.assertEqual((model.scans, model.logs), (2, 2))

    def test_snapshot_and_wield_requests_share_budget(self):
        model = RequestModel()
        model.request(action=0)
        for action in (0, 1, 2):
            model.request(action=action)
        self.assertEqual((model.scans, model.logs), (1, 1))
        self.assertEqual(model.weapon, "itm_canakkale_turk_rifle")

    def test_player_budgets_and_bot_ownership_are_independent(self):
        model = RequestModel()
        model.request(player=2, action=1)
        self.assertEqual((model.scans, model.logs), (1, 0))
        self.assertEqual(model.weapon, "itm_canakkale_turk_rifle")
        model.request()
        model.request(player=2)
        self.assertEqual((model.scans, model.logs), (2, 1))

    def test_clock_rollback_accepts_and_restarts_throttle(self):
        model = RequestModel()
        model.now = 1000
        model.request()
        model.now = 10
        model.request()
        model.request()
        self.assertEqual((model.scans, model.logs), (2, 2))

    def test_mission_reset_even_when_new_clock_has_caught_up(self):
        model = RequestModel()
        model.now = 5
        model.request()
        model.reset(ti_before_mission_start)
        model.now = 6
        model.request()
        self.assertEqual((model.scans, model.logs), (2, 2))

    def test_rejoin_resets_reused_player_id_only(self):
        model = RequestModel()
        model.request()
        model.request(player=2)
        model.reset(ti_server_player_joined)
        model.request()
        model.request(player=2)
        self.assertEqual((model.scans, model.logs), (3, 2))

    def test_invalid_requests_never_consume_budget_or_scan(self):
        model = RequestModel()
        model.request(player=3)
        model.request(mask=0)
        model.request(mask=512)
        model.request(action=3)
        self.assertEqual((model.scans, model.logs, model.slots), (0, 0, {}))
        model.request()
        self.assertEqual((model.scans, model.logs), (1, 1))


class StatusMessageTests(unittest.TestCase):
    def test_local_feedback_distinguishes_send_and_unavailable_states(self):
        model = RequestModel()
        model.press_f8(fire_orders_poc_unsupported_triggers[0])
        model.commander = -1
        model.press_f8()
        model.commander = 11
        model.selection = []
        model.press_f8()
        self.assertEqual(model.sent, [])
        model.selection = [0]
        model.press_f8()
        self.assertEqual(model.sent, [(fire_orders_poc_event, 1, 0)])
        self.assertEqual(model.messages[0], "@[SS1914] F8 ALGILANDI")
        self.assertIn("Takim Olum Maci", model.messages[1])
        self.assertIn("canli", model.messages[3])
        self.assertIn("bot grubu sec", model.messages[5])
        self.assertIn("gonderildi", model.messages[7])
        for msg in model.messages:
            msg.decode("ascii")


    def test_listen_host_uses_server_validation_with_local_result(self):
        model = RequestModel()
        model.players[0] = 11
        model.owner = 0
        model.request(player=0)  # Dedicated server has no playable host.
        self.assertEqual(model.scans, 0)
        model.press_f8(host=True)
        model.press_f8(host=True)
        self.assertEqual((model.scans, model.logs), (1, 1))
        self.assertEqual(model.sent, [])
        self.assertEqual(model.replies, [])
        self.assertEqual(sum("F8 Kabul" in msg for msg in model.messages), 1)

    def test_reply_is_private_and_limited_to_one_per_admitted_request(self):
        model = RequestModel()
        model.request()
        model.request(action=1)
        model.request(player=2)
        model.request(player=3)
        self.assertEqual(model.replies, [
            (1, fire_orders_poc_result_event, 0, 1, 1, 0),
            (2, fire_orders_poc_result_event, 0, 0, 0, 0),
        ])

    def test_already_in_requested_mode_is_observed_without_a_swap(self):
        model = RequestModel()
        model.request(action=2)
        self.assertEqual(model.replies[-1][2:], (2, 1, 1, 1))
        model.now += fire_orders_poc_interval_ms
        model.request(action=1)
        self.assertEqual(model.replies[-1][2:], (1 | result_swap_blocked, 1, 1, 0))
        self.assertEqual(model.wield_calls, [])

    def test_reports_reload_bolt_and_unavailable_swap_separately(self):
        model = RequestModel()
        model.attack_state = 5
        model.request(action=1)
        self.assertEqual(model.replies[-1][2:], (1 | result_wait_reload, 1, 1, 0))
        model.now += fire_orders_poc_interval_ms
        model.attack_state = 0
        model.deadline = model.now + 1
        model.request(action=1)
        self.assertEqual(model.replies[-1][2:], (1 | result_wait_bolt, 1, 1, 0))
        self.assertEqual(model.wield_calls, [])
        model.now += fire_orders_poc_interval_ms
        model.request(action=1)
        self.assertEqual(model.replies[-1][2:], (1 | result_swap_blocked, 1, 1, 0))
        model.server = False
        for reply in model.replies:
            model.deliver(0, reply[2:])
        self.assertIn("RELOAD DEVAM EDIYOR", model.messages[1])
        self.assertIn("BOLT BEKLEMESI", model.messages[3])
        self.assertIn("GUVENLI SLOT/SARJOR GECISI YOK", model.messages[5])

    def test_reply_display_requires_server_sender_and_client_context(self):
        model = RequestModel()
        model.deliver(0, (0, 1, 1, 0))
        model.server = False
        model.deliver(2, (0, 1, 1, 0))
        model.deliver(0, (3, 1, 1, 0))
        self.assertEqual(model.messages, [])
        for payload in ((0, 0, 0, 0), (0, 1, 1, 0), (1, 1, 1, 0), (2, 1, 1, 1)):
            model.deliver(0, payload)
        self.assertEqual(len(model.messages), 6)
        self.assertIn("Secili canli bot yok", model.messages[0])
        self.assertIn("F8 Kabul", model.messages[1])
        self.assertIn("DENEME: 0", model.messages[2])
        self.assertIn("ISTENEN MODDA", model.messages[5])
        for msg in model.messages:
            self.assertEqual(msg.decode("ascii"), msg)
            self.assertNotIn("BASARILI: 1", msg)


class NativeBayonetGateTests(unittest.TestCase):
    def setUp(self):
        self.model = RequestModel()
        self.model.players = {1: 11}
        self.model.password = "private"

    def run_order(self, mask=1, action=1):
        return self.model.execute(parse(native_bayonet_order)[0],
                                  {"$g_multiplayer_game_type": 1,
                                   "$g_multiplayer_is_game_type_captain": 0},
                                  [1, 0, mask, action, 1000])

    def test_single_owned_division_emits_only_the_requested_native_order(self):
        self.model.agents = [11, 20]
        self.model.divisions[11] = 3
        self.assertTrue(self.run_order())
        self.assertTrue(self.run_order(action=2))
        self.assertEqual(self.model.orders, [(0, 0, 10), (0, 0, 11)])
        self.assertEqual(self.model.wield_calls, [])
        self.assertEqual(self.model.strings[s0], "")

    @unittest.skipUnless(native_bayonet_experiment, "requires experimental build flag")
    def test_dispatch_reports_order_and_refusal_without_claiming_mode_change(self):
        model = self.model
        self.assertIn("cf_ss1914_native_bayonet_order", dict(scripts))
        model.request(action=1)
        self.assertEqual(model.orders, [(0, 0, 10)])
        self.assertTrue(model.replies[-1][2] & result_native_sent)
        model.now += fire_orders_poc_interval_ms
        model.players[2] = -1
        model.request(action=2)
        self.assertEqual(len(model.orders), 1)
        self.assertTrue(model.replies[-1][2] & result_native_refused)
        model.server = False
        for reply in model.replies:
            model.deliver(0, reply[2:])
        self.assertIn("Native emir cagrildi", model.messages[0])
        self.assertIn("RED:", model.messages[1])

    def test_second_active_player_blocks_even_without_an_agent(self):
        self.model.players[2] = -1
        self.assertFalse(self.run_order())
        self.assertEqual(self.model.orders, [])

    def test_human_or_foreign_bot_in_target_division_blocks(self):
        self.model.agents = [11, 20]
        self.assertFalse(self.run_order())
        self.model.agents = [20, 21]
        self.model.foreign.add(21)
        self.assertFalse(self.run_order())
        self.assertEqual(self.model.orders, [])

    def test_public_listen_combined_empty_and_busy_requests_block(self):
        self.model.password = ""
        self.assertFalse(self.run_order())
        self.model.password = "private"
        self.model.dedicated = False
        self.assertFalse(self.run_order())
        self.model.dedicated = True
        self.assertFalse(self.run_order(mask=3))
        self.assertFalse(self.run_order(mask=2))
        self.model.attack_state = 5
        self.assertFalse(self.run_order())
        self.model.attack_state = 0
        self.model.deadline = 1001
        self.assertFalse(self.run_order())
        self.assertEqual(self.model.orders, [])


if __name__ == "__main__":
    unittest.main()
