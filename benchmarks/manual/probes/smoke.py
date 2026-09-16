"""Real stdio MCP and JG preflight, without any model call or benchmark proof."""
import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.path.insert(0, '/opt/experiment/runtime')
from jg_run import execute, run_completed, JG

WORK = Path('/work')
REPO = '/home/robin/Projects/awesome-formal-verification-skill'
TW = '/home/robin/Projects/mcp/TraceWeave'
CASE = json.loads(Path('/opt/experiment/common/case.json').read_text())['case_path']
FORBIDDEN = [
    REPO + '/benchmarks', REPO + '/.git',
    REPO + '/test/.epoch_return_control',
    REPO + '/test/.reservation_journal_control',
    REPO + '/test/.reservation_journal_control/CALIBRATION.md',
    REPO + '/test/.reservation_journal_control/setup.tcl',
    REPO + '/test/reservation_journal_isolated_ab_gpt55_01/control',
    REPO + '/test/reservation_journal_isolated_ab_gpt55_01/blind/arm_a',
    REPO + '/test/reservation_journal_isolated_ab_gpt55_01/blind/arm_b',
    REPO + '/test/resource_settlement_isolated_ab_gpt55_02',
    REPO + '/test/resource_settlement_routing_ab/blind/arm_a/FINAL_REPORT.md',
    REPO + '/test/resource_settlement_routing_ab/blind/arm_b/FINAL_REPORT.md',
    REPO + '/test/resource_settlement_orig/.ab_control',
    REPO + '/knowledge', REPO + '/adapters',
    REPO + '/test/resource_settlement_isolated_ab/control/pins.json',
    '/home/robin/.claude', '/home/robin/.codex/hooks.json',
    '/home/robin/.codex/sessions', '/home/robin/.codex/memories',
    TW + '/docs', TW + '/.git', '/run/user/1000/codex.sock',
]


def save(name, value):
    (WORK / name).write_text(json.dumps(value, indent=2) + '\n')


def probe_filesystem():
    checks = []
    for path in FORBIDDEN:
        assert not Path(path).exists(), f'Forbidden host data visible: {path}'
        checks.append(dict(path=path, visible=False))
    first = Path('/home/robin/.codex/skills/formal-verification').resolve()
    second = Path('/home/robin/.agents/skills/formal-verification').resolve()
    assert first == second == Path('/opt/formal-snapshot/adapters/claude-code')
    checks.append(dict(skill_aliases_equal=True, target=str(first)))
    # No peer snapshot or evaluator directories are mounted, even if guessed.
    assert not Path('/opt/formal-snapshot/.git').exists()
    for path in [first / 'SKILL.md', Path(CASE) / 'baseline.tcl',
                 Path('/home/robin/.codex/config.toml')]:
        try:
            fd = os.open(path, os.O_WRONLY | os.O_APPEND)
        except OSError:
            checks.append(dict(path=str(path), write_denied=True))
        else:
            os.close(fd)
            raise AssertionError(f'Frozen file writable: {path}')
    # Newly mounted procfs cannot expose host ancestors through /proc/PID/root.
    assert os.readlink('/proc/self/ns/pid')
    save('filesystem_checks.json', checks)


async def probe_mcp():
    shutil.copyfile('/opt/preflight/smoke.vcd', WORK / 'smoke.vcd')
    hidden_wave = REPO + '/test/.reservation_journal_control/runs/physical_small_01.artifacts/physical_candidate.vcd'
    (WORK / 'escape.vcd').symlink_to(hidden_wave)
    config = tomllib.loads(Path('/home/robin/.codex/config.toml').read_text())
    assert set(config['mcp_servers']) == {'TraceWeave'}
    server = config['mcp_servers']['TraceWeave']
    params = StdioServerParameters(command=server['command'], args=server['args'],
                                   cwd=server['cwd'], env=dict(os.environ, **server['env']))
    calls = []
    async with stdio_client(params) as streams:
        async with ClientSession(*streams) as session:
            init = await session.initialize()
            tools = await session.list_tools()
            assert {'get_formal_paths', 'get_waveform_summary', 'get_signals_around_time'} <= {
                tool.name for tool in tools.tools}

            async def call(name, arguments):
                result = await session.call_tool(name, arguments)
                calls.append(dict(tool=name, arguments=arguments, result=result.model_dump(mode='json')))
                texts = [c.text for c in result.content if c.type == 'text']
                try:
                    payload = json.loads('\n'.join(texts))
                except json.JSONDecodeError:
                    payload = {'text': '\n'.join(texts)}
                return result, payload

            result, _ = await call('get_formal_paths', dict(formal_root='/work', formal_tool='jaspergold',
                                                            project_dir='/work/jgproject', wave_file='/work/smoke.vcd'))
            assert not result.isError
            result, _ = await call('get_waveform_summary', dict(wave_path='/work/smoke.vcd'))
            assert not result.isError
            result, _ = await call('search_signals', dict(wave_path='/work/smoke.vcd', keyword=['q'], max_results=5))
            assert not result.isError
            for at, expected in [(0, 0), (10000, 1)]:
                result, values = await call('get_signals_around_time', dict(wave_path='/work/smoke.vcd',
                    signal_paths=['smoke.q'], center_time_ps=at, window_ps=0, extra_transitions=0,
                    return_mode='values_only'))
                assert not result.isError
                assert values['signals']['smoke.q']['value_at_center']['dec'] == expected, values
            for path in [hidden_wave, '/work/escape.vcd']:
                result, payload = await call('get_waveform_summary', dict(wave_path=path))
                assert result.isError or payload.get('error'), payload
            result, payload = await call('get_formal_paths', dict(
                formal_root=REPO + '/test/resource_settlement_routing_ab/blind/arm_a', formal_tool='jaspergold'))
            assert result.isError or payload.get('error'), payload
            for root in [REPO + '/test/.epoch_return_control',
                         REPO + '/test/.reservation_journal_control/runs',
                         REPO + '/test/reservation_journal_isolated_ab_gpt55_01/blind/arm_a',
                         REPO + '/test/reservation_journal_isolated_ab_gpt55_01/blind/arm_b']:
                result, payload = await call('get_formal_paths', dict(formal_root=root, formal_tool='jaspergold'))
                assert result.isError or payload.get('error'), payload
    save('mcp_checks.json', dict(server=init.serverInfo.model_dump(mode='json'), calls=calls))


async def probe_client():
    """Check native discovery/config through app-server, without starting a turn."""
    with (WORK / 'codex_app_server.stderr.log').open('wb') as err:
        proc = await asyncio.create_subprocess_exec('/opt/codex/bin/codex', 'app-server',
            '--strict-config', '--stdio', stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=err)
        messages = []

        async def request(index, method, params):
            proc.stdin.write((json.dumps(dict(id=index, method=method, params=params)) + '\n').encode())
            await proc.stdin.drain()
            while True:
                line = await asyncio.wait_for(proc.stdout.readline(), timeout=15)
                assert line, 'app-server exited before reply'
                item = json.loads(line)
                messages.append(item)
                if item.get('id') == index:
                    assert 'error' not in item, item
                    return item['result']
        try:
            await request(1, 'initialize', dict(clientInfo=dict(name='isolation-preflight', version='1'),
                                                capabilities=dict(experimentalApi=True)))
            proc.stdin.write(b'{"method":"initialized","params":{}}\n')
            await proc.stdin.drain()
            config = await request(2, 'config/read', dict(includeLayers=False))
            effective = config['config']
            assert effective['model'] == 'gpt-5.5'
            assert effective['model_reasoning_effort'] == 'medium'
            assert effective['sandbox_mode'] == 'danger-full-access'
            assert effective['approval_policy'] == 'never'
            assert effective['features']['hooks'] is False and effective['features']['memories'] is False
            skills = await request(3, 'skills/list', dict(cwds=['/work'], forceReload=True))
            found = [skill for group in skills['data'] for skill in group['skills']
                     if skill['name'] == 'formal-verification']
            assert found, skills
            for skill in found:
                assert Path(skill['path']).resolve() == Path('/opt/formal-snapshot/adapters/claude-code/SKILL.md'), skill
            models = await request(4, 'model/list', dict(includeHidden=True))
            selected = [model for model in models['data'] if model.get('model') == effective['model']]
            save('codex_client_checks.json', dict(config=config, skills=skills, models=models,
                                                 selected_model=selected, messages=messages))
            assert selected, 'Configured model has no native catalog entry; do not accept fallback metadata'
            assert any(effort['reasoningEffort'] == 'medium'
                       for effort in selected[0]['supportedReasoningEfforts']), selected
        finally:
            proc.terminate()
            await asyncio.wait_for(proc.wait(), timeout=10)


def main():
    probe_filesystem()
    assert shutil.which('rg') == '/opt/codex/codex-path/rg'
    subprocess.run(['rg', '--version'], check=True, stdout=subprocess.DEVNULL)
    gate = subprocess.run(['jg-run', 'baseline'], capture_output=True, text=True)
    assert gate.returncode == 2 and 'No skill delivery receipt' in gate.stderr
    assert not (WORK / 'jg_runs.jsonl').exists()
    (WORK / 'missing_skill_gate.log').write_text(gate.stdout + gate.stderr)
    # Check the actual client parses this clean config; no model request.
    proc = subprocess.run(['/opt/codex/bin/codex', 'mcp', 'list', '--json'],
                          capture_output=True, text=True, timeout=15)
    (WORK / 'codex_mcp_list.log').write_text(proc.stdout + proc.stderr)
    assert proc.returncode == 0, proc.stderr
    servers = json.loads(proc.stdout)
    assert len(servers) == 1 and servers[0]['name'] == 'TraceWeave', servers
    asyncio.run(probe_client())
    row = execute([JG, '-fpv', '-batch', '-proj', '/work/jgproject',
                   '-tcl', '/opt/preflight/smoke.tcl'], WORK / 'jg.stdout.log', limit=20.0)
    save('jg_preflight.json', row)
    assert run_completed(row), row
    output = (WORK / 'jg.stdout.log').read_text()
    assert 'ENVIRONMENT_ASSERT_STATUS proven' in output
    assert 'ENVIRONMENT_COVER_STATUS covered' in output
    asyncio.run(probe_mcp())
    print('PREFLIGHT PASS: isolated files; immutable inputs; Codex config; JG license/proof/cover; stdio MCP values and denied cross-reads')


if __name__ == '__main__':
    main()
