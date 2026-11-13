"""Normal multiplayer bolt-cycle operations (WFaS 1.143, Python 2.7).

No loaded/reserve ammo is written here: the engine owns the seven-shot magazine
and the normal empty-magazine reload. Animation priority plus a per-frame guard
is the available stock-engine fire/aim lock. It needs a real client/server test;
ti_on_weapon_attack is POST-shot and cannot retract an already emitted missile.
"""
from header_common import *
from header_operations import *
from header_triggers import *
from module_constants import *

canakkale_scripts = [
    ("canakkale_start_bolt", [
        (store_script_param_1, ":agent"),
        (try_begin),
            (agent_is_active, ":agent"),
            (agent_is_human, ":agent"),
            (agent_is_alive, ":agent"),
            (eq, "$g_multiplayer_is_game_type_captain", 0),
            (store_mission_timer_a_msec, ":now"),
            (agent_get_slot, ":until", ":agent", slot_agent_canakkale_bolt_until),
            # A predicted owner cycle / duplicate event must not restart the timer.
            (try_begin),
                (le, ":until", ":now"),
                (store_add, ":until", ":now", canakkale_bolt_duration_ms),
                (agent_set_slot, ":agent", slot_agent_canakkale_bolt_until, ":until"),
                (agent_set_animation, ":agent", "anim_rifle_bolt_cycle_2s", 1),
            (try_end),
        (try_end),
    ]),
    ("canakkale_rifle_fired", [
        (store_script_param_1, ":agent"),
        (try_begin),
            (agent_is_active, ":agent"),
            (agent_is_human, ":agent"),
            (agent_is_alive, ":agent"),
            (eq, "$g_multiplayer_is_game_type_captain", 0),
            (try_begin),
                (multiplayer_is_server),
                (store_mission_timer_a_msec, ":now"),
                (agent_get_slot, ":until", ":agent", slot_agent_canakkale_bolt_until),
                (try_begin),
                    (le, ":until", ":now"),
                    (call_script, "script_canakkale_start_bolt", ":agent"),
                    (get_max_players, ":players"),
                    (try_for_range, ":player", 1, ":players"),
                        (player_is_active, ":player"),
                        (multiplayer_send_int_to_player, ":player",
                         multiplayer_event_canakkale_bolt, ":agent"),
                    (try_end),
                (else_try),
                    # Diagnostic ONLY, never claim this retracts a projectile/ammo.
                    # A nonzero counter is a failed engine lock smoke test.
                    (agent_get_slot, ":early", ":agent", slot_agent_canakkale_early_shots),
                    (val_add, ":early", 1),
                    (agent_set_slot, ":agent", slot_agent_canakkale_early_shots, ":early"),
                    (agent_set_animation, ":agent", "anim_rifle_bolt_cycle_2s", 1),
                (try_end),
            (else_try),
                # Predict only the locally controlled shooter, not remote agents.
                (get_player_agent_no, ":local_agent"),
                (eq, ":agent", ":local_agent"),
                (call_script, "script_canakkale_start_bolt", ":agent"),
            (try_end),
        (try_end),
    ]),
    ("canakkale_bolt_tick", [
        (store_mission_timer_a_msec, ":now"),
        (try_for_agents, ":agent"),
            (agent_is_human, ":agent"),
            (agent_is_alive, ":agent"),
            (agent_get_slot, ":until", ":agent", slot_agent_canakkale_bolt_until),
            (gt, ":until", 0),
            (agent_get_animation, ":animation", ":agent", 1),
            (try_begin),
                (lt, ":now", ":until"),
                # Weapon swap, ready/aim or an animation interruption cannot
                # clear the timer. Priority 90 beats ready/fire/equip/struck;
                # death (95) still wins. Do not scale by proficiency/weapon speed.
                (neq, ":animation", "anim_rifle_bolt_cycle_2s"),
                (agent_set_animation, ":agent", "anim_rifle_bolt_cycle_2s", 1),
            (else_try),
                (ge, ":now", ":until"),
                (agent_set_slot, ":agent", slot_agent_canakkale_bolt_until, 0),
                (try_begin),
                    # A restarted/interrupted clip must not extend the lock.
                    (eq, ":animation", "anim_rifle_bolt_cycle_2s"),
                    (agent_set_animation, ":agent", "anim_stand_crossbow", 1),
                (try_end),
            (try_end),
        (try_end),
    ]),
]

canakkale_mission_triggers = [
    (ti_on_agent_spawn, 0, 0, [], [
        (store_trigger_param_1, ":agent"),
        (agent_set_slot, ":agent", slot_agent_canakkale_bolt_until, 0),
        (agent_set_slot, ":agent", slot_agent_canakkale_early_shots, 0),
    ]),
    (0, 0, 0, [], [
        (call_script, "script_canakkale_bolt_tick"),
    ]),
]
