"""One-shot bolt visuals, with an independent 2000 ms rifle cooldown.

No tick or early-attack path restarts the moving clip. Weapon changes cancel
its visual ownership, not the deadline. Re-equipping a rifle during the lock
uses one STATIC end-frame hold, released at the original deadline. These stock
animation controls still require WFaS verification for actual fire/aim denial;
the post-projectile attack trigger cannot retract an already emitted missile.
"""
from module_canakkale_assets import custom_magazine_reload
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
            (le, ":until", ":now"),
            # The only moving-clip start in the whole bolt implementation.
            (store_add, ":until", ":now", canakkale_bolt_duration_ms),
            (agent_set_slot, ":agent", slot_agent_canakkale_bolt_until, ":until"),
            (agent_set_slot, ":agent", slot_agent_canakkale_bolt_visual, 0),
            (agent_get_wielded_item, ":weapon", ":agent", 0),
            (agent_set_slot, ":agent", slot_agent_canakkale_bolt_weapon, ":weapon"),
            (try_begin),
                (this_or_next|eq, ":weapon", "itm_canakkale_turk_rifle"),
                (eq, ":weapon", "itm_canakkale_british_rifle"),
                (agent_set_animation, ":agent", "anim_rifle_bolt_cycle_2s", 1),
                (agent_set_slot, ":agent", slot_agent_canakkale_bolt_visual, 1),
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
                    # Positive, monotonically increasing per-agent cycle token.
                    # It is an opaque dedupe token, NOT a client-clock deadline.
                    (store_add, ":stamp", ":now", 1),
                    (get_max_players, ":players"),
                    (try_for_range, ":player", 1, ":players"),
                        (player_is_active, ":player"),
                        (multiplayer_send_2_int_to_player, ":player",
                         multiplayer_event_canakkale_bolt, ":agent", ":stamp"),
                    (try_end),
                (else_try),
                    # Diagnostics only: do not restart/extend or refund ammo.
                    (agent_get_slot, ":early", ":agent", slot_agent_canakkale_early_shots),
                    (val_add, ":early", 1),
                    (agent_set_slot, ":agent", slot_agent_canakkale_early_shots, ":early"),
                (try_end),
            (else_try),
                (get_player_agent_no, ":local_agent"),
                (eq, ":agent", ":local_agent"),
                (store_mission_timer_a_msec, ":now"),
                (agent_get_slot, ":until", ":agent", slot_agent_canakkale_bolt_until),
                (le, ":until", ":now"),
                # Retain pending prediction acknowledgements after expiry, so
                # a first late server echo cannot replay an already-ended shot.
                (agent_get_slot, ":predictions", ":agent", slot_agent_canakkale_bolt_predictions),
                (val_add, ":predictions", 1),
                (agent_set_slot, ":agent", slot_agent_canakkale_bolt_predictions, ":predictions"),
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
            (agent_get_slot, ":visual", ":agent", slot_agent_canakkale_bolt_visual),
            (agent_get_wielded_item, ":weapon", ":agent", 0),
            (try_begin),
                (ge, ":now", ":until"),
                # One unconditional release of our owned action, even when
                # agent_get_animation reports a transient/different action.
                (try_begin),
                    (gt, ":visual", 0),
                    (agent_set_animation, ":agent", "anim_stand", 1),
                (try_end),
                (agent_set_slot, ":agent", slot_agent_canakkale_bolt_until, 0),
                (agent_set_slot, ":agent", slot_agent_canakkale_bolt_visual, 0),
                (agent_set_slot, ":agent", slot_agent_canakkale_bolt_weapon, -1),
                # Keep last_event after expiry: late duplicates cannot replay.
            (else_try),
                (agent_get_slot, ":previous_weapon", ":agent", slot_agent_canakkale_bolt_weapon),
                (try_begin),
                    (neq, ":weapon", ":previous_weapon"),
                    (try_begin),
                        (gt, ":visual", 0),
                        (agent_set_animation, ":agent", "anim_stand", 1),
                    (try_end),
                    (assign, ":visual", 0),
                    (agent_set_slot, ":agent", slot_agent_canakkale_bolt_visual, 0),
                    (agent_set_slot, ":agent", slot_agent_canakkale_bolt_weapon, ":weapon"),
                (try_end),
                (try_begin),
                    # Returning to either rifle cannot clear the lock, but
                    # must never replay its moving bolt sequence.
                    (eq, ":visual", 0),
                    (this_or_next|eq, ":weapon", "itm_canakkale_turk_rifle"),
                    (eq, ":weapon", "itm_canakkale_british_rifle"),
                    (agent_set_animation, ":agent", "anim_canakkale_bolt_hold", 1),
                    (agent_set_slot, ":agent", slot_agent_canakkale_bolt_visual, 2),
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
        (agent_set_slot, ":agent", slot_agent_canakkale_bolt_visual, 0),
        (agent_set_slot, ":agent", slot_agent_canakkale_bolt_last_event, 0),
        (agent_set_slot, ":agent", slot_agent_canakkale_bolt_weapon, -1),
        (agent_set_slot, ":agent", slot_agent_canakkale_bolt_predictions, 0),
    ]),
    # Poll transitions/deadlines each frame; never replay an action per frame.
    (0, 0, 0, [], [(call_script, "script_canakkale_bolt_tick")]),
]

if custom_magazine_reload:
    # Latch the native reload transition before overriding its upper-body clip.
    canakkale_mission_triggers.append((0, 0, 0, [], [
        (try_for_agents, ":agent"),
            (agent_is_alive, ":agent"),
            (agent_is_human, ":agent"),
            (agent_get_attack_action, ":action", ":agent"),
            (try_begin),
                (neq, ":action", 5),
                (agent_set_slot, ":agent", slot_agent_canakkale_reload_seen, 0),
            (else_try),
                (agent_slot_eq, ":agent", slot_agent_canakkale_reload_seen, 0),
                (agent_get_wielded_item, ":weapon", ":agent", 0),
                (this_or_next|eq, ":weapon", "itm_canakkale_turk_rifle"),
                (eq, ":weapon", "itm_canakkale_british_rifle"),
                (agent_slot_eq, ":agent", slot_agent_canakkale_bolt_until, 0),
                (agent_set_slot, ":agent", slot_agent_canakkale_reload_seen, 1),
                (agent_set_animation, ":agent", "anim_rifle_magazine_reload_7", 1),
            (try_end),
        (try_end),
    ]))
