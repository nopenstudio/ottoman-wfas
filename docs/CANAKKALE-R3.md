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

## Official module location: Seddulbahir 1914

The WFaS launcher module name and Windows directory are **exactly** `Seddulbahir 1914`, **not** `OTTOMAN` and not `Seddulbahir 1915`. Keep the existing installed `module.ini`, BRF, DDS and other assets in this directory. The repository does not contain the user's local `module.ini` or BRF files; do not invent or overwrite them.

With the default Windows Steam library, the install directory is:

    C:\Program Files (x86)\Steam\steamapps\common\Mount & Blade With Fire and Sword\Modules\Seddulbahir 1914

If Steam is on another drive, locate the game's actual `Modules` directory and use that instead. The original `module_info.py` fallback no longer refers to `OTTOMAN` and defaults to `Seddulbahir 1914`; it supports `WFAS_MODULES_ROOT` (containing the `Modules` directory) and still honors `WFAS_EXPORT_DIR` for the full destination. The isolated `tools/build_module.py --output` option always exports to the staging folder supplied and must be deployed manually.

Example after the R3 opt-in build in PowerShell (edit `$modulesRoot` to the real Steam library):

    $modulesRoot = 'C:\Program Files (x86)\Steam\steamapps\common\Mount & Blade With Fire and Sword\Modules'
    $target = Join-Path $modulesRoot 'Seddulbahir 1914'
    if (!(Test-Path (Join-Path $target 'module.ini'))) { throw "Module missing at $target; check your Steam install directory" }
    # Back up the installed module before replacing compiled files.
    Copy-Item -Path '.\build-r3-on\*.txt' -Destination $target -Force

Use the WFaS launcher entry `Seddulbahir 1914`. For multiplayer, every client and server must use the same newly compiled .txt output; do not mix option-0 and option-1 builds.
