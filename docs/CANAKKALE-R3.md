# R3 magazine reload trial

The R2 field run used the management-requested mode 0, which omits the magazine animation. R2 also retained native speed ratings 36 and 37 in both modes. Mode 1 now exports speed rating 100 for the two seven-shot ranged weapons only. This is a calibration point, not a measured time. Mode 0 still exports 36/37 and the old reload behavior.

The engine selects the action for crossbow-type items with shoot_musket. Native crossbow (2.5 s), musket (4.4 s) and phased musket sequences use weapon-speed scaling. Neither the active native action ID for these rifles nor the scaling formula is specified by the module sources. Attack state 5 identifies reloading, not the action ID. The module operation table has no weapon-specific setter for native reload completion time. The clip has a fixed 3 s duration; neither that duration nor changing the speed rating proves when the eighth projectile can launch. If the native cycle consists of multiple state-5 intervals the current latch can re-arm between intervals. Native action selection, interruptions and timing require runtime verification.

## Windows (PowerShell)

Run in this source checkout. Python 3 runs the staging wrapper and PyPy2 runs the 29 processors. Substitute your actual PyPy2 executable path.

    $env:WFAS_MAGAZINE_BRF = '1'
    py -3 tools/build_module.py --python2 'C:\PyPy2\pypy.exe' --output '.\build-r3-on'
    Select-String '^\s*rifle_magazine_reload_7\s' .\build-r3-on\actions.txt

Ensure the installed module.ini loads the actual BRF containing the skeleton animation named rifle_magazine_reload_7, frames 0 through 90. Open the loaded BRF in OpenBRF to check the skeleton/action name and endpoints. The user's BRF and installed module.ini are not in the checkout. Deploy the generated top-level game TXT files to the module on server and every client; keep the installed BRFs and module.ini. For the old powder fallback use option 0 and a separate output directory.

## Acceptance

Record each faction emptying a fresh seven-round magazine with reserve ammo. Confirm shots 1–6 play only the R1 bolt. Show the seventh muzzle flash, first reload frame, last reload frame and eighth muzzle flash in one recording. Attempt the eighth shot as soon as possible and record both seventh-to-eighth and reload-start-to-eighth elapsed times, plus reserve before and after. Target about 3 seconds for the reload, one magazine clip, no remaining powder sequence. Repeat with bot and remote observer; interrupt by switching to melee and back, and by death/respawn. Check R1 cannot be bypassed by switching. No in-engine times collected here.
