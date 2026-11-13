# ÇANAKKALE-MVP-001

Implementation for [Issue #6](https://github.com/nopenstudio/ottoman-wfas/issues/6),
starting at `27989be0cad49d55055e44af8bbc293f5ece95d1` on `main`.
PR #5 is neither a dependency nor modified/merged.

## Resulting normal multiplayer roster

| Side | Faction slot / display name | Player troop | AI troop |
|---|---|---|---|
| Turkish | `kingdom_3` / Turkish Forces (1915) | `khergit_veteran_footman_multiplayer` | `khergit_dismounted_lancer_multiplayer_ai` |
| British | `kingdom_4` / British Forces (1915), previously Sweden | `nord_scout_multiplayer` | `nord_scout_multiplayer_ai` |

The Turkish AI uses the existing `janissar` attributes, firearm proficiency,
skills and faces in a record inside the **normal MP AI range**. The Captain
`mp_janissar` record is untouched. British AI/player records replace the Swedish
cavalry records in place and have no horse items, mounted/horse-guarantee flags,
Riding or Horse Archery skills. STR satisfies rifle difficulty.

Each side has one selectable player and one AI template. The other two old
normal player/AI records per side retain their indices but move to
`fac_commoners`, excluding them from the existing faction-filtered selection
and spawn loops. No troops are reordered; Captain records are unchanged. Other
three playable factions remain available. Default teams are Turkish/British.

| Side | Rifle (new item) | Existing uniform item / mesh | New head item / mesh | Existing boots |
|---|---|---|---|---|
| Turkish | `canakkale_turk_rifle` | `yanichar_forma_b` / `janichar2` | `canakkale_turk_cap` / `turk-cap` | `janissary_tapki` |
| British | `canakkale_british_rifle` | `yanichar_forma_a` / `janichar1` | `canakkale_british_helmet` / `ingiliz-cap` | `cavalry_boots` |

Both use `norm_bullets` (stock bolt-type firearm ammunition). A Turkish
Yataghan / British palash occupies the backup weapon slot. There is exactly
one body, one head and one foot item per loadout. Item classes and troop-specific
availability match every default inventory item; the existing server selection
validator and default-item pricing therefore apply. Both player troops classify
as unmounted firearm/crossbow troops, not cavalry/mounted archers.

## Rifle and bolt behavior

The new rifles clone `t_norm_musket` and `norm_musket` meshes, cost, difficulty,
ballistics and weapon capabilities with **max_ammo(7)** and a new attack trigger.
Every old item record/ID stays intact; only the terminal `items_end` sentinel
moves. `itp_next_item_as_melee` is intentionally removed from the clones: the
next list item is not a melee partner. Backup melee weapons remain available.

`rifle_bolt_cycle_2s` is appended to the animation table, preserving all old
animation IDs. It uses a fixed **2.0 s**, priority **90** upper-body action,
without weapon-speed scaling or the aiming/vertical-rotation flags. Death
priority 95 remains higher. `arf_stick_item_to_left_hand` holds the rifle on the
supporting hand while the right hand cycles the bolt.

**Frame convention:** supplied SMD `time 0` is the reference pose; SMD action
times `1..61` import through OpenBRF as BRF indices **`0..60`**. The module action
uses `0, 60`; do not include the reference/T pose in the animation resource.

R1 separates the visual action from its 2000 ms per-agent deadline. A new
accepted shot starts the moving clip **once**. Early callbacks only increment
the diagnostic counter; the tick never restarts the moving clip, including
when the reported animation differs. At expiry, one neutral release clears
owned visual/weapon/deadline state, regardless of the reported action ID.

A wielded-item transition cancels visual ownership immediately on the next
mission tick. Other weapons then animate normally. The original deadline stays
intact. Returning to either rifle before it expires enters a **static frame-60
hold** once per return; it does not play the bolt motion again. That guard is
released at the original deadline. It has no moving frame range or restart flag.

Server message 120 now carries `(agent_id, server_cycle_stamp)`; deploy the
same compiled data to server and clients. Clients deduplicate the positive
opaque stamp even after visual expiry. Owner prediction acknowledgements are
consumed without replay, including late echoes; a real unpredicted server event
can still start playback. Spawn resets the state. No client can change the
server deadline. A server stamp is not interpreted as a client-clock deadline.

**Engine verification still required:** the stock animation priority/static-return
guard is the implemented fire/aim suppression mechanism. `ti_on_weapon_attack`
is post-shot and cannot retract a missile that the engine has already emitted.
Any early attack increments `slot_agent_canakkale_early_shots` (141); a nonzero
value is a failed lock smoke test, not a successfully rejected shot.

Loaded/reserve ammo is never rewritten, refunded, refilled or reconstructed by
these scripts. The engine owns magazine depletion and the normal empty-magazine
reload. Seven real shots, reserve consumption, the seventh-shot transition to
reload, holding aim/fire, interruptions and dedicated-server behavior remain
**NOT RUN** until tested in WFaS. Source/state tests are not evidence of these
engine behaviors.

## Existing local resources

The user explicitly confirmed in this task that the two OBJ models and the SMD
are already imported into the local mod's BRFs and loaded by its `module.ini`.
The code uses the exact confirmed mesh/action names above. This repository does
not include that local `module.ini` or those BRFs, so no invented resource
filenames or duplicate `load_mod_resource` lines were added.

`assets/canakkale/source/` preserves the actual supplied OBJ/SMD sources and
`manifest.json` records hashes and required names. It does not replace the
user's installed resources or prove their texture/material load order.

## Build and apply

Use Python **2.7** for the Module System. The optional isolated runner itself
uses Python 3:

```sh
python3 tools/build_module.py --python2 /path/to/python2 --output build/canakkale
/path/to/python2 -m unittest discover -s tests -p 'test_*.py'
```

The runner stages the source, invokes the original `build_module.bat` processor
order, fails on nonzero exits **or printed ERROR/traceback**, and writes build
logs and generated files under the selected output. It never uses the Steam
export path. `WFAS_EXPORT_DIR` is an optional environment override; without it,
`module_info.py` retains the user's original Windows OTTOMAN path.

Apply compiled module data to matching **client and dedicated server** module
copies. Retain the user's already-loaded BRF/DDS resources and `module.ini`.
Restart the multiplayer mission. In a local host, select Turkish and British
forces, enable bots, and inspect both troops and both player loadouts.

See [CANAKKALE-MVP-001-TESTS.md](CANAKKALE-MVP-001-TESTS.md) for the actual
validation results and the outstanding game smoke checklist.
