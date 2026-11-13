#!/usr/bin/env python3
"""Run the original Python 2 Module System in a private staging directory."""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--python2', default='python2')
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    output = a.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # build_module.bat remains the authoritative processor order.
    order = re.findall(r'^python (process_\w+\.py)',
                       (ROOT / 'build_module.bat').read_text(), re.M)
    assert len(order) == 29, order
    python = str(Path(shutil.which(a.python2) or a.python2).resolve())
    version = subprocess.check_output([python, '-c',
        'import sys; print(sys.version); assert sys.version_info[:2] == (2, 7)'],
        text=True)
    log = [version]
    with tempfile.TemporaryDirectory(prefix='wfas-build-') as tmp:
        stage = Path(tmp)
        for f in list(ROOT.glob('*.py')) + [ROOT / 'variables.txt']:
            shutil.copy2(f, stage / f.name)
        env = dict(os.environ, WFAS_EXPORT_DIR=str(output) + '/')
        for processor in order:
            r = subprocess.run([python, processor], cwd=stage, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, errors='replace')
            log.append('$ ' + processor + '\n' + r.stdout)
            # Old processors sometimes print ERROR then exit zero.
            if r.returncode or re.search(r'(?im)^\s*(error\b|traceback\b)', r.stdout):
                (output / 'build.log').write_text('\n'.join(log))
                print(r.stdout)
                raise SystemExit('FAILED: ' + processor + ' (exit %d)' % r.returncode)
        shutil.copytree(stage, output / 'generated_sources',
                        ignore=shutil.ignore_patterns('*.pyc'), dirs_exist_ok=True)
    (output / 'build.log').write_text('\n'.join(log))
    print('PASS: %d Module System processors (Python 2.7); output: %s' %
          (len(order), output))

if __name__ == '__main__':
    main()
