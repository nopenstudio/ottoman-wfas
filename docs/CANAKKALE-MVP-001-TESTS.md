# Validation — ÇANAKKALE-MVP-001

Validated using PyPy **2.7.18 / 7.3.17**, downloaded from the official PyPy
Python distribution. Python 3.12 runs the isolated build orchestrator.

| Check | Actual result |
|---|---|
| Changed Module System/test Python 2 syntax | PASS |
| Original Module System processor chain | PASS — all 29 processors, exit 0, no ERROR/traceback, **zero compiler warnings** |
| Source regression suite | PASS — 8 tests |
| Script operation host/client state harness | PASS — 19 tests after R1; not an engine simulation |
| Old items/IDs, animations/IDs and troop ordering | PASS — compared with base commit |
| Captain troop records and missions | PASS — unchanged against base commit |
| Normal faction-filtered AI/player ranges | PASS — one Turkish and one British template each |
| Exact uniforms/head meshes, boots, ammo/default inventories | PASS — source references and slot counts |
| Availability, item classes, classifier and STR/horse skills | PASS — source and actual classifier operations |
| Rifle capacity encoded in item records | PASS — 7 for both clones; originals remain 1 |
| SMD → BRF → SMD private tooling round-trip | PASS — 20 bones, 61 action poses, BRF indices 0–60; maximum equivalent rotation error 1.137e-6 rad; position error 0 |
| User's installed BRF/material/DDS/module.ini inspection | NOT RUN — local files not accessible here; installation confirmed by user |
| WFaS client / dedicated-server smoke test | R0 user reported repeated animation/swap failure; R1 local retest NOT RUN — no WFaS client, server or Wine here |
| Seven real shots, ammo consumption, seventh-shot full reload | NOT RUN — engine acceptance pending |
| Effective 2 s fire AND aim suppression, AI, interruption and network latency | NOT RUN — script implementation/state tests pass; engine acceptance pending |

Commands actually run from the repository:

```sh
../.tools/pypy2.7-v7.3.17-linux64/bin/pypy tests/test_canakkale.py
../.tools/pypy2.7-v7.3.17-linux64/bin/pypy tests/test_bolt_operations.py
python3 tools/build_module.py --python2 ../.tools/pypy2.7-v7.3.17-linux64/bin/pypy --output build/canakkale
git -c core.whitespace=cr-at-eol diff --check
```

The actual build log is generated as `build/canakkale/build.log`. The committed
build runner reconstructs it from the original processor order. Changed Python 2 source/test files were checked with `py_compile`; tests themselves were executed by Python 2.
An additional all-root syntax sweep encountered the unchanged baseline
`ID_scene_props.py:1131` identifier `spr_!oim_maple_big` (invalid Python).
That unrelated generated file was not modified. The actual 29-processor build
and all changed-file syntax checks pass.

The private SMD round-trip used a locally compiled OpenBRF-derived CLI,
`markpryk/brf_sync_tools` commit `567fd4172006a30da0152e42f9182ec797446ba2`.
It imported the supplied SMD, wrote a temporary validation BRF, exported it
again, and compared bone hierarchy, frame times, translation and equivalent
rotation matrices. The fixture skeleton/BRF are **not game assets**, are not
installed, and are not committed. This does not inspect or replace the user's
local game BRF.

## Remaining real-game acceptance

1. Host normal Team Deathmatch or Battle with Turkish and British teams and
   both bots and players. Confirm the actual body/head models and one head/body/
   foot slot, both sides on foot, and correct selection/purchase options.
2. For each rifle, fire seven times without full reload. Inspect reserve ammo
   consumption and full reload after the seventh shot. Compare client and server.
3. Hold fire and aim after every shot. Measure the actual approximately 2 s
   lock. Inspect rapid repeated input and the server's agent slot 141; it must
   stay zero. A post-shot counter cannot retract an emitted projectile.
4. Attempt weapon swaps, interrupted animations, dying/respawning, reconnecting
   and shooting under latency. Confirm cooldown state does not bypass or stick.
5. Repeat with dedicated server, a remote client and an AI shooter. Confirm
   action playback and ammo agree on all peers. Confirm Captain/other factions
   retain their original behavior.

**Delivery status:** source implementation is REVIEW_READY. Runtime acceptance
is pending; this document does not claim the full playable MVP is proven PASS.

## Runtime rework R1

The reported R0 gameplay failure supersedes the earlier source-only acceptance
for bolt playback. See [R1 changes and regression evidence](CANAKKALE-R1.md).
Current regressions: 8 source tests + 19 operation/state tests = **27 PASS**.
The 29-processor build was rerun with zero compiler warnings.
R1 in-engine playback, swap cancellation and true fire/aim suppression are
**NOT RUN / BLOCKED pending the user's recompiled playtest**.
