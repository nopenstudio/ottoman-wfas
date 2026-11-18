"""Opt-in WFaS 1.143 paired-item probe for dedicated Team Deathmatch."""
import os

from header_mission_templates import *
from module_constants import (slot_agent_canakkale_bolt_until,
                              slot_player_captain_bot_data_end)

fire_orders_poc_enabled = os.environ.get("WFAS_FIRE_ORDERS_POC") == "1"
fire_orders_poc_event = 121
fire_orders_poc_interval_ms = 350
# Player slot 52. Stock Captain data uses the half-open range [40, 52).
slot_player_fire_orders_stamp = slot_player_captain_bot_data_end
fire_orders_poc_keys = (
    (key_f8, 0),  # read-only snapshot, including for the native-order control
    (key_f9, 1),  # request paired melee item
    (key_f10, 2),  # request original ranged item
)

fire_orders_poc_trigger = (0, 0, 0, [], [
    (neg|multiplayer_is_server),
    (neg|is_presentation_active, "prsnt_multiplayer_escape_menu"),
    (get_player_agent_no, ":commander"),
    (ge, ":commander", 0),
    (agent_is_alive, ":commander"),
    (agent_get_team, ":team", ":commander"),
    (is_between, ":team", 0, 2),
    (assign, ":action", -1),
] + [
    op for key, action in fire_orders_poc_keys for op in [
        (try_begin),
            (key_clicked, key),
            (assign, ":action", action),
        (try_end),
    ]
] + [
    (ge, ":action", 0),
    (assign, ":mask", 0),
    (try_for_range, ":division", 0, grc_everyone),
        (class_is_listening_order, ":team", ":division"),
        (assign, ":bit", 1),
        (val_lshift, ":bit", ":division"),
        (val_or, ":mask", ":bit"),
    (try_end),
    (gt, ":mask", 0),
    (multiplayer_send_2_int_to_server, fire_orders_poc_event, ":mask", ":action"),
])

fire_orders_poc_triggers = [
    fire_orders_poc_trigger,
    (ti_before_mission_start, 0, 0, [multiplayer_is_dedicated_server], [
        (get_max_players, ":player_limit"),
        (try_for_range, ":player_no", 1, ":player_limit"),
            (player_is_active, ":player_no"),
            (player_set_slot, ":player_no", slot_player_fire_orders_stamp, 0),
        (try_end),
    ]),
    (ti_server_player_joined, 0, 0, [multiplayer_is_dedicated_server], [
        (store_trigger_param_1, ":player_no"),
        (player_set_slot, ":player_no", slot_player_fire_orders_stamp, 0),
    ]),
]

fire_orders_poc_receive = [
    (eq, ":event_type", fire_orders_poc_event),
    (multiplayer_is_server),
    (multiplayer_is_dedicated_server),
    (game_in_multiplayer_mode),
    (eq, "$g_multiplayer_game_type", multiplayer_game_type_team_deathmatch),
    (eq, "$g_multiplayer_is_game_type_captain", 0),
    (get_max_players, ":player_limit"),
    (is_between, ":player_no", 1, ":player_limit"),
    (player_is_active, ":player_no"),
    (player_get_team_no, ":team", ":player_no"),
    (is_between, ":team", 0, 2),
    (player_get_agent_id, ":commander", ":player_no"),
    (ge, ":commander", 0),
    (agent_is_active, ":commander"),
    (agent_is_alive, ":commander"),
    (agent_is_human, ":commander"),
    (neg|agent_is_non_player, ":commander"),
    (agent_get_team, ":commander_team", ":commander"),
    (eq, ":commander_team", ":team"),
    (store_script_param, ":mask", 3),
    (store_script_param, ":action", 4),
    (is_between, ":mask", 1, 1 << grc_everyone),
    (is_between, ":action", 0, 3),
    (store_mission_timer_a_msec, ":now"),
    # Store time + 1 so a request at mission time zero still consumes its turn.
    (player_get_slot, ":last_stamp", ":player_no", slot_player_fire_orders_stamp),
    (store_sub, ":last_time", ":last_stamp", 1),
    (store_add, ":next_time", ":last_time", fire_orders_poc_interval_ms),
    (this_or_next|eq, ":last_stamp", 0),
    (this_or_next|lt, ":now", ":last_time"),
    (ge, ":now", ":next_time"),
    (store_add, ":stamp", ":now", 1),
    (player_set_slot, ":player_no", slot_player_fire_orders_stamp, ":stamp"),
    (try_for_agents, ":bot"),
        (agent_is_active, ":bot"),
        (agent_is_alive, ":bot"),
        (agent_is_human, ":bot"),
        (agent_is_non_player, ":bot"),
        (agent_get_team, ":bot_team", ":bot"),
        (eq, ":bot_team", ":team"),
        (agent_get_group, ":owner", ":bot"),
        (eq, ":owner", ":player_no"),
        (agent_get_division, ":division", ":bot"),
        (is_between, ":division", 0, grc_everyone),
        (assign, ":selected", 1),
        (val_lshift, ":selected", ":division"),
        (val_and, ":selected", ":mask"),
        (neq, ":selected", 0),
        (agent_get_troop_id, ":troop", ":bot"),
        (assign, ":rifle", -1),
        (try_begin),
            (eq, ":troop", "trp_khergit_dismounted_lancer_multiplayer_ai"),
            (assign, ":rifle", "itm_canakkale_turk_rifle"),
            (assign, ":melee", "itm_canakkale_turk_rifle_melee"),
        (else_try),
            (eq, ":troop", "trp_nord_scout_multiplayer_ai"),
            (assign, ":rifle", "itm_canakkale_british_rifle"),
            (assign, ":melee", "itm_canakkale_british_rifle_melee"),
        (try_end),
        (ge, ":rifle", 0),
        # The paired ID can appear in the slot if the engine is already in
        # alternate mode. Require exactly one matching physical weapon slot.
        (assign, ":matches", 0),
        (try_for_range, ":slot", 0, 4),
            (agent_get_item_slot, ":item", ":bot", ":slot"),
            (this_or_next|eq, ":item", ":rifle"),
            (eq, ":item", ":melee"),
            (val_add, ":matches", 1),
        (try_end),
        (eq, ":matches", 1),
        (agent_get_wielded_item, ":before", ":bot", 0),
        (agent_get_ammo, reg10, ":bot", 1),
        (agent_get_slot, ":deadline", ":bot", slot_agent_canakkale_bolt_until),
        (assign, ":requested", -1),
        (try_begin),
            (gt, ":action", 0),
            (ge, ":now", ":deadline"),
            (assign, ":requested", ":rifle"),
            (try_begin),
                (eq, ":action", 1),
                (eq, ":before", ":rifle"),
                (assign, ":requested", ":melee"),
            (try_end),
            # If the rifle is stowed, first wield it. F9 again tests its
            # companion. If already in melee mode, F9 leaves it alone.
            (neq, ":before", ":requested"),
            (this_or_next|neq, ":action", 1),
            (neq, ":before", ":melee"),
            (agent_set_wielded_item, ":bot", ":requested"),
        (try_end),
        (agent_get_wielded_item, ":after", ":bot", 0),
        (agent_get_ammo, reg8, ":bot", 1),
        (team_get_weapon_usage_order, reg9, ":team", ":division"),
        (assign, reg0, ":player_no"),
        (assign, reg1, ":bot"),
        (assign, reg2, ":division"),
        (assign, reg3, ":action"),
        (assign, reg4, ":before"),
        (assign, reg5, ":requested"),
        (assign, reg6, ":after"),
        (assign, reg7, ":deadline"),
        (server_add_message_to_log, "@SS1914 owner={reg0} bot={reg1} division={reg2} action={reg3} before={reg4} request={reg5} after={reg6} deadline={reg7} ammo_before={reg10} ammo_after={reg8} native_usage={reg9}"),
    (try_end),
]
