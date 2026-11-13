# PR #7 runtime rework R1

Baseline: `daf3e5c950ca7a3b4954491daedecd0272027016`.
Order: [RUNTIME REWORK R1](https://github.com/nopenstudio/ottoman-wfas/pull/7#issuecomment-6861907716).

User observed roughly four bolt cycles after one shot, continuation after a
weapon swap and a duration exceeding two seconds. R0 had explicit moving-clip
restart paths in both the early-shot callback and a per-frame animation-ID
comparison. Those paths are removed; this is a source-backed explanation,
not a claim that every engine/BRF cause was reproduced here.

## Narrow changes

- `canakkale_start_bolt` is the **only** moving-clip start site. It opens one
  fixed 2000 ms deadline. An active deadline rejects another start.
- An early attack only increments diagnostic slot 141. No replay, extension,
  ammo rewrite/refund, or additional broadcast occurs.
- `canakkale_bolt_tick` observes wielded-item transitions and expiry. It never
  starts the moving clip or compares action IDs to decide to replay it.
- A weapon change issues one neutral upper-body release, then leaves unrelated
  weapon actions alone. It preserves the deadline. Changing directly between
  the two rifles also cancels the moving clip.
- Re-equipping either rifle before the deadline starts the new **static**
  `canakkale_bolt_hold` action once per return. It uses frame 60 of the existing
  BRF resource (no new mesh/SMD), priority 90 and `amf_keep`, not a moving loop.
  The original deadline releases it; it cannot extend or reset the timer.
- At deadline, owned visual state is released once even if the engine reports
  a transient/different action. Deadline/visual/weapon state is cleared.
  Event dedupe and pending prediction acknowledgements survive expiry.
- Server event 120 now sends agent ID **and a positive cycle stamp**. Old,
  repeated and late duplicate messages are ignored. Owner prediction is
  acknowledged without replay even if the first echo arrives after expiry;
  multiple delayed acknowledgements and unpredicted owner events are covered.
  Server/client must both receive the updated compiled module.
- Spawn resets visual, wielded-item, deadline, dedupe and prediction state.

Slots 140–141 retain their meanings. New dedicated R1 slots are 142 (visual
ownership), 143 (last accepted network stamp), 144 (last wielded weapon), and
145 (pending owner prediction acknowledgements). The stamp is only a dedupe
token; client/server mission clocks are not compared.

Troops, factions, items, defaults, availability assignments, headgear/uniform
meshes, source OBJ/SMD assets, music and PR #5 are unchanged from the R1 baseline.
The original action remains 2.0 seconds, BRF frames 0–60. Only a static hold
record is appended; all old animation IDs, including the moving clip, stay fixed.

## Actual validation

```sh
../.tools/pypy2.7-v7.3.17-linux64/bin/pypy -m unittest discover -s tests -p 'test_*.py'
python3 tools/build_module.py --python2 ../.tools/pypy2.7-v7.3.17-linux64/bin/pypy --output build/canakkale-r1
git -c core.whitespace=cr-at-eol diff --check
```

- **PASS:** 27 tests (8 source + 19 actual-operation state regressions).
- **PASS:** Python 2.7 syntax for changed source/test files.
- **PASS:** all 29 Module System processors, zero compiler errors/warnings.
- **PASS:** one moving start across 200 ticks; four rapid attack/event attempts;
  weapon swap and empty hands; swap back and rifle-to-rifle change; late and
  out-of-order messages; owner prediction/acknowledgements; remote observer;
  expiry with a mismatched reported animation; spawn reset and existing scope.
- **NOT RUN:** WFaS playback, actual cancellation/render timing, AI, remote
  client/dedicated-server input and latency tests.
- **BLOCKED:** proof of real fire/aim denial. The retained cooldown and static
  hold prevent the *script state* from being reset by swapping, but the harness
  cannot prove the engine refuses a shot. `ti_on_weapon_attack` is post-shot;
  slot 141 detects an early emission and does not retract it.

Recompile and retest the reported one-shot/one-cycle case, switch to a sword
mid-cycle, return before the deadline, hold fire/aim, and repeat with AI and a
remote client. Measure cancellation at the next mission frame and termination
at the two-second deadline. A late first event on a remote observer is received
on that client's clock; network latency behavior still needs a real playtest.
No runtime PASS or merge is claimed.
