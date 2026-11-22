"""Opt-in WFaS 1.143 paired-item probe for Team Deathmatch."""
import os

from header_mission_templates import *
from module_constants import (slot_agent_canakkale_bolt_until,
                              slot_player_captain_bot_data_end)

fire_orders_poc_enabled = os.environ.get("WFAS_FIRE_ORDERS_POC") == "1"
fire_orders_poc_event = 121
fire_orders_poc_result_event = 122
fire_orders_poc_interval_ms = 350
# Result packet action occupies the low two bits. These flags share the field.
result_wait_reload = 4
result_wait_bolt = 8
result_swap_blocked = 16
# Player slot 52. Stock Captain data uses the half-open range [40, 52).
slot_player_fire_orders_stamp = slot_player_captain_bot_data_end
fire_orders_poc_keys = (
    (key_f8, 0),  # read-only mode snapshot
    (key_f9, 1),  # assess bayonet mode
    (key_f10, 2),  # assess rifle mode
)

# Poll only the three debug keys; never capture input or open a presentation.
fire_orders_poc_key_conditions = [
    (neg|multiplayer_is_dedicated_server),
    (neg|is_presentation_active, "prsnt_multiplayer_escape_menu"),
    (neg|is_presentation_active, "prsnt_multiplayer_poll_menu"),
]

def key_triggers(operations, request=False):
    return [
        (0, 0, 0.35, fire_orders_poc_key_conditions + [(key_clicked, key)], [
            (display_message, "@[SS1914] F%d ALGILANDI" % (8 + action)),
        ] + ([(assign, ":action", action)] if request else []) + operations)
        for key, action in fire_orders_poc_keys
    ]


fire_orders_poc_unsupported_triggers = key_triggers([
    (display_message, "@SS1914: Test yalniz Takim Olum Maci icin."),
])

fire_orders_poc_triggers = key_triggers([
    (get_player_agent_no, ":commander"),
    (assign, ":alive", 0),
    (try_begin),
        (ge, ":commander", 0),
        (agent_is_alive, ":commander"),
        (assign, ":alive", 1),
    (try_end),
    (try_begin),
        (eq, ":alive", 0),
        (display_message, "@SS1914: Once canli olarak oyuna gir."),
    (else_try),
        (agent_get_team, ":team", ":commander"),
        (is_between, ":team", 0, 2),
        (assign, ":mask", 0),
        (try_for_range, ":division", 0, grc_everyone),
            (class_is_listening_order, ":team", ":division"),
            (assign, ":bit", 1),
            (val_lshift, ":bit", ":division"),
            (val_or, ":mask", ":bit"),
        (try_end),
        (try_begin),
            (eq, ":mask", 0),
            (display_message, "@SS1914: Once bir bot grubu sec."),
        (else_try),
            (try_begin),
                (multiplayer_is_server),
                (multiplayer_get_my_player, ":host"),
                (display_message, "@SS1914: Istek yerel sunucuya iletildi."),
                (call_script, "script_game_receive_network_message", ":host",
                 fire_orders_poc_event, ":mask", ":action"),
            (else_try),
                (multiplayer_send_2_int_to_server, fire_orders_poc_event, ":mask", ":action"),
                (display_message, "@SS1914: Istek sunucuya gonderildi."),
            (try_end),
        (try_end),
    (try_end),
], request=True) + [
    (ti_after_mission_start, 0, 0, [neg|multiplayer_is_dedicated_server], [
        (display_message, "@SS1914 TEST AKTIF - F8 Durum / F9 Sungu / F10 Tufek"),
    ]),
    (ti_before_mission_start, 0, 0, [multiplayer_is_server], [
        (get_max_players, ":player_limit"),
        (try_for_range, ":player_no", 0, ":player_limit"),
            (player_is_active, ":player_no"),
            (player_set_slot, ":player_no", slot_player_fire_orders_stamp, 0),
        (try_end),
    ]),
    (ti_server_player_joined, 0, 0, [multiplayer_is_server], [
        (store_trigger_param_1, ":player_no"),
        (player_set_slot, ":player_no", slot_player_fire_orders_stamp, 0),
    ]),
]

fire_orders_poc_request = [
    (store_script_param, ":player_no", 1),
    (store_script_param, ":mask", 2),
    (store_script_param, ":action", 3),
    (multiplayer_is_server),
    (game_in_multiplayer_mode),
    (eq, "$g_multiplayer_game_type", multiplayer_game_type_team_deathmatch),
    (eq, "$g_multiplayer_is_game_type_captain", 0),
    (get_max_players, ":player_limit"),
    (is_between, ":player_no", 0, ":player_limit"),
    (assign, ":host", -1),
    (try_begin),
        (neg|multiplayer_is_dedicated_server),
        (multiplayer_get_my_player, ":host"),
    (try_end),
    (this_or_next|gt, ":player_no", 0),
    (eq, ":player_no", ":host"),
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
    (assign, ":selected_count", 0),
    (assign, ":target_count", 0),
    (assign, ":observed_count", 0),
    (assign, ":result_flags", 0),
    (assign, ":rifle_count", 0),
    (assign, ":melee_count", 0),
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
        (val_add, ":selected_count", 1),
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
        (val_add, ":target_count", 1),
        (try_begin),
            (eq, ":before", ":rifle"),
            (val_add, ":rifle_count", 1),
        (else_try),
            (eq, ":before", ":melee"),
            (val_add, ":melee_count", 1),
        (try_end),
        (agent_get_slot, ":deadline", ":bot", slot_agent_canakkale_bolt_until),
        (agent_get_attack_action, ":attack_state", ":bot"),
        (try_begin),
            (gt, ":action", 0),
            (assign, ":desired", ":rifle"),
            (try_begin),
                (eq, ":action", 1),
                (assign, ":desired", ":melee"),
            (try_end),
            (try_begin),
                (eq, ":before", ":desired"),
                (val_add, ":observed_count", 1),
            (else_try),
                (eq, ":attack_state", 5),
                (val_or, ":result_flags", result_wait_reload),
            (else_try),
                (lt, ":now", ":deadline"),
                (val_or, ":result_flags", result_wait_bolt),
            (else_try),
                # Stock equips cannot target a slot or restore its magazine.
                (val_or, ":result_flags", result_swap_blocked),
            (try_end),
        (try_end),
        (team_get_weapon_usage_order, reg9, ":team", ":division"),
        (assign, reg0, ":player_no"),
        (assign, reg1, ":bot"),
        (assign, reg2, ":division"),
        (assign, reg3, ":action"),
        (assign, reg4, ":before"),
        (assign, reg7, ":deadline"),
        (assign, reg11, ":attack_state"),
        (server_add_message_to_log, "@SS1914 owner={reg0} bot={reg1} division={reg2} action={reg3} before={reg4} deadline={reg7} attack_state={reg11} native_usage={reg9}"),
    (try_end),
]

fire_orders_poc_display = [
    (assign, reg0, ":selected_count"),
    (assign, reg1, ":count_a"),
    (assign, reg2, ":count_b"),
    (try_begin),
        (eq, reg0, 0),
        (display_message, "@SS1914 Sunucu: Secili canli bot yok."),
    (else_try),
        (eq, ":action", 0),
        (store_sub, reg3, reg0, reg1),
        (val_sub, reg3, reg2),
        (display_message, "@SS1914 F8 Kabul: Bot {reg0}, tufek {reg1}, sungu {reg2}, diger {reg3}."),
    (else_try),
        (eq, reg1, 0),
        (display_message, "@SS1914 Sunucu: Secimde uygun tufekli bot yok."),
    (else_try),
        (assign, reg3, ":count_b"),
        (store_sub, reg4, reg1, reg3),
        (display_message, "@[SS1914] HEDEF: {reg1} | DENEME: 0 | BASARILI: 0 | BASARISIZ: 0"),
        (assign, ":reload_flag", ":result_flags"),
        (val_and, ":reload_flag", result_wait_reload),
        (assign, ":bolt_flag", ":result_flags"),
        (val_and, ":bolt_flag", result_wait_bolt),
        (assign, ":failed_flag", ":result_flags"),
        (val_and, ":failed_flag", result_swap_blocked),
        (str_clear, s0),
        (str_clear, s1),
        (str_clear, s2),
        (try_begin),
            (neq, ":failed_flag", 0),
            (str_store_string, s0, "@GUVENLI SLOT/SARJOR GECISI YOK. "),
        (try_end),
        (try_begin),
            (neq, ":reload_flag", 0),
            (str_store_string, s1, "@RELOAD DEVAM EDIYOR. "),
        (try_end),
        (try_begin),
            (neq, ":bolt_flag", 0),
            (str_store_string, s2, "@BOLT BEKLEMESI."),
        (try_end),
        (display_message, "@[SS1914] ISTENEN MODDA: {reg3} | ATLANDI: {reg4}. {s0}{s1}{s2}"),
    (try_end),
]

# The listen host displays its own result locally. Remote players get one reply.
fire_orders_poc_request += [
    (assign, ":result_action", ":action"),
    (val_or, ":result_action", ":result_flags"),
    (assign, ":count_a", ":target_count"),
    (assign, ":count_b", ":observed_count"),
    (try_begin),
        (eq, ":action", 0),
        (assign, ":count_a", ":rifle_count"),
        (assign, ":count_b", ":melee_count"),
    (try_end),
    (try_begin),
        (eq, ":player_no", ":host"),
] + fire_orders_poc_display + [
    (else_try),
        (multiplayer_send_4_int_to_player, ":player_no", fire_orders_poc_result_event,
         ":result_action", ":selected_count", ":count_a", ":count_b"),
    (try_end),
]

fire_orders_poc_result = [
    (store_script_param, ":action", 1),
    (store_script_param, ":selected_count", 2),
    (store_script_param, ":count_a", 3),
    (store_script_param, ":count_b", 4),
    (is_between, ":action", 0, 32),
    (assign, ":result_flags", ":action"),
    (val_and, ":result_flags", result_wait_reload | result_wait_bolt | result_swap_blocked),
    (val_and, ":action", 3),
    (is_between, ":action", 0, 3),
] + fire_orders_poc_display

# Keep the engine callback below the WFaS per-script local-variable limit.
fire_orders_poc_scripts = [
    ("cf_ss1914_fire_order_request", fire_orders_poc_request),
    ("cf_ss1914_fire_order_result", fire_orders_poc_result),
]

fire_orders_poc_dispatch = [
    (eq, ":event_type", fire_orders_poc_event),
    (multiplayer_is_server),
    (store_script_param, ":value", 3),
    (store_script_param, ":value_2", 4),
    (call_script, "script_cf_ss1914_fire_order_request", ":player_no", ":value", ":value_2"),
    (else_try),
    (eq, ":event_type", fire_orders_poc_result_event),
    (neg|multiplayer_is_server),
    (eq, ":player_no", 0),
    (store_script_param, ":value", 3),
    (store_script_param, ":value_2", 4),
    (store_script_param, ":value_3", 5),
    (store_script_param, ":value_4", 6),
    (call_script, "script_cf_ss1914_fire_order_result", ":value", ":value_2", ":value_3", ":value_4"),
]
