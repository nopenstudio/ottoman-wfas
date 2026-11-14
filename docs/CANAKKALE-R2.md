# PR 9 R2 runtime handoff

Default builds use stock reload. Import the supplied skeletal animation into an already loaded module BRF as rifle_magazine_reload_7. For a new BRF add load_mod_resource = <actual BRF basename> to the installed module.ini. Verify frames 0..90 for 3 seconds in OpenBRF, or adjust the sequence endpoints to match the supplied clip. Build and deploy the same opt-in output to host and clients.

    WFAS_MAGAZINE_BRF=1 python3 tools/build_module.py --python2 /path/to/pypy --output /tmp/wfas-optin

The upper-body override observes native reload state 5, after bolt expiry. Game testing must establish that overriding the clip preserves native reload completion and interruption after switching. No ammunition is written. Stock phased reload definitions remain intact. Optional action ID is appended (672).

The melee records use stock polearm thrust and no musket-specific offset/bayonet flags. Verify both grips and forward contact in game. X switches between adjacent records with the same world mesh.

The launch callback supplies shooter, weapon and position. The hit callback supplies impact. The bundled operation list exposes no live missile handle or position iterator. Separate cartridges reuse the native flying_missile flight mesh on the engine projectile and retain stock impact operations and stats. This is an in-flight mesh experiment, not an emitted spark trail. Cartridges follow the ammunition item if picked up and reused in another compatible gun. Test both players, bots and a remote observer, including impact/despawn, before accepting visuals.

Verification for each mode (0 and 1):

    WFAS_MAGAZINE_BRF=$mode pypy -m unittest discover -s tests -v
    WFAS_MAGAZINE_BRF=$mode python3 tools/build_module.py --python2 /path/to/pypy --output /tmp/wfas-r2-$mode

R2-tests-*.log and R2-build-*.log contain the actual output. An initial smoke assertion counted offsets shared with historical rifles across the entire callback. The corrected assertion checks the complete body of each rifle branch. No muzzle code changed.
