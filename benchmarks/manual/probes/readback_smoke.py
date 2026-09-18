"""Readback-only isolation/config/MCP checks. No model turn or EDA process."""
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import smoke


async def check_packet_values():
    expected = json.loads(Path('/opt/readback-check.json').read_text())
    config = tomllib.loads(Path('/home/robin/.codex/config.toml').read_text())
    server = config['mcp_servers']['TraceWeave']
    params = StdioServerParameters(command=server['command'], args=server['args'],
                                  cwd=server['cwd'], env=dict(os.environ, **server['env']))
    calls = []
    wave = '/opt/experiment/checkpoint/diagnostic.vcd'
    async with stdio_client(params) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()

            async def call(name, arguments):
                result = await session.call_tool(name, arguments)
                calls.append(dict(tool=name, arguments=arguments, result=result.model_dump(mode='json')))
                assert not result.isError, result
                return json.loads('\n'.join(block.text for block in result.content if block.type == 'text'))

            await call('get_formal_paths', dict(formal_root='/opt/experiment/checkpoint',
                formal_tool='jaspergold', formal_log='diagnostic.stdout.log', wave_file='diagnostic.vcd'))
            summary = await call('get_waveform_summary', dict(wave_path=wave))
            assert summary['simulation_duration_ps'] == expected['times_ps'][-1]
            signals = await call('search_signals', dict(wave_path=wave, keyword='', max_results=1024))
            assert not signals.get('truncated')
            assert {row['path'] for row in signals['results']} == {row['path'] for row in expected['signals']}
            for index, at in enumerate(expected['times_ps']):
                for start in range(0, len(expected['signals']), 24):
                    rows = expected['signals'][start:start + 24]
                    values = await call('get_signals_around_time', dict(wave_path=wave,
                        signal_paths=[row['path'] for row in rows], center_time_ps=at,
                        window_ps=0, extra_transitions=0, return_mode='values_only'))
                    assert not values.get('truncated') and not values.get('signal_suggestions'), values
                    for row in rows:
                        value = values['signals'][row['path']]['value_at_center']
                        bits = None if value is None else value['bin'].removeprefix('b').removeprefix('B').lower()
                        assert bits == row['values_bin'][index], (at, row['path'], bits)
    smoke.save('packet_mcp_checks.json', dict(all_values_match=True,
        signal_count=len(expected['signals']), times_ps=expected['times_ps'], calls=calls))


def main():
    smoke.probe_filesystem()
    for path in ['/tools', '/opt/experiment/input_a', '/opt/experiment/input_b',
                 '/opt/experiment/control', '/opt/experiment/input/readback_packet.json']:
        assert not Path(path).exists(), f'Unexpected mount: {path}'
    attachment = Path('/opt/experiment/input/MATERIALS.md')
    try:
        descriptor = os.open(attachment, os.O_WRONLY | os.O_APPEND)
    except OSError:
        pass
    else:
        os.close(descriptor)
        raise AssertionError('Input attachment is writable')
    sys.path.insert(0, '/opt/experiment/runtime')
    from input_read import page
    row, output = page(attachment, 1, 100)
    assert row['path'] == str(attachment) and 'INPUT_PAGE' in output
    for command in ['jg', 'jg-run']:
        result = subprocess.run([command, 'baseline'], capture_output=True, text=True)
        assert result.returncode == 2 and 'DIAGNOSIS_ONLY' in result.stderr
    assert not (smoke.WORK / 'jg_runs.jsonl').exists()
    smoke.save('diagnosis_only_checks.json', dict(vendor_tools_absent=True,
        proof_execution_refused=True, attachment_read_only=True, input_total_lines=row['total_lines']))
    result = subprocess.run(['/opt/codex/bin/codex', 'mcp', 'list', '--json'],
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    servers = json.loads(result.stdout)
    assert len(servers) == 1 and servers[0]['name'] == 'TraceWeave'
    asyncio.run(smoke.probe_client())
    asyncio.run(smoke.probe_mcp())
    asyncio.run(check_packet_values())
    print('PREFLIGHT PASS: immutable equal skill; private attachment; no proof tools; '
          'Codex config/catalog; isolated stdio MCP; every packet value matches raw VCD')


if __name__ == '__main__':
    main()
