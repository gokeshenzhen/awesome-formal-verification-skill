"""Model-free checks of optional feedback and proof-disabled mounts."""
import asyncio
import json
from pathlib import Path
import subprocess
import smoke
from readback_smoke import check_packet_values


def main():
    smoke.probe_filesystem()
    assert not Path('/tools').exists()
    assert not Path('/opt/experiment/checkpoint/diagnostic.vcd').exists()
    for command in ['jg', 'jg-run']:
        result = subprocess.run([command, 'baseline'], capture_output=True, text=True)
        assert result.returncode == 2 and 'DIAGNOSIS_ONLY' in result.stderr
    result = subprocess.run(['/opt/codex/bin/codex', 'mcp', 'list', '--json'],
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    assert [s['name'] for s in json.loads(result.stdout)] == ['TraceWeave']
    asyncio.run(smoke.probe_client())
    asyncio.run(smoke.probe_mcp())
    has_feedback = Path('/opt/experiment/input/diagnostic.vcd').exists()
    if has_feedback:
        asyncio.run(check_packet_values('/opt/experiment/input'))
    else:
        assert {p.name for p in Path('/opt/experiment/input').iterdir()} == {'MATERIALS.md'}
    smoke.save('feedback_mount_checks.json', dict(vendor_tools_absent=True,
               optional_feedback_mounted=has_feedback, common_checkpoint_has_no_diagnostic=True))
    print('PREFLIGHT PASS: same skill aliases; selected input only; no proof tools; '
          'Codex catalog; isolated MCP; supplied feedback values checked when present')


if __name__ == '__main__':
    main()
