import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'court.py'
spec = importlib.util.spec_from_file_location('court', SCRIPT)
court = importlib.util.module_from_spec(spec)
spec.loader.exec_module(court)


class CourtTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old = Path.cwd()
        os.chdir(self.temp.name)
        Path('.court').mkdir()
        Path('.court/case.md').write_text('# Try launching a product\nBudget $500, no customers.', encoding='utf-8')

    def tearDown(self):
        os.chdir(self.old)
        self.temp.cleanup()

    def open(self, *args):
        court.run(['init', '--case-file', '.court/case.md', '--seed', '42', *args])
        return court.state()

    def fill(self, d, s, phase, content):
        for j in court.jobs(d, s, phase):
            j['output'].write_text(content, encoding='utf-8')

    def test_twelve_distinct_jurors(self):
        people = court.jurors()
        self.assertEqual(len(people), 12)
        self.assertEqual(len({p['name'] for p in people}), 12)
        self.assertEqual(len({p['id'] for p in people}), 12)
        self.assertTrue(all(len(p['must_check']) >= 3 and p['decision_test'] for p in people))

    def test_quick_and_seed(self):
        d, s = self.open('--quick')
        self.assertEqual(len(s['jury']), 6)
        selected = s['jury']
        d, s = self.open('--quick')
        self.assertEqual(selected, s['jury'])

    def test_invalid_size(self):
        with self.assertRaises(ValueError):
            self.open('--jury', '2')
        with self.assertRaises(ValueError):
            self.open('--jury', '13')

    def test_parse(self):
        x = court.parse_vote('VOTE: NOT GUILTY\nREASON: yes\nDECIDING FACT: a fact\nWOULD FLIP IF: no budget')
        self.assertEqual(x['vote'], 'NOT GUILTY')
        self.assertEqual(x['flip'], 'no budget')
        self.assertEqual(court.parse_vote('**VOTE:** guilty\nREASON: x')['vote'], 'GUILTY')
        self.assertIsNone(court.parse_vote('VOTE: undecided'))

    def test_prompts_are_written(self):
        d, s = self.open('--jury', '3')
        court.run(['prompts', 'jury'])
        p = court.jobs(d, s, 'jury')[0]['brief'].read_text(encoding='utf-8')
        self.assertIn('VOTE: GUILTY or NOT GUILTY', p)
        self.assertIn('rebuttal/defense.md', p)
        self.assertNotIn('juror-02.md', p)
        self.assertIn('EXPERIMENT:', p)
        self.assertIn('Mandatory checks:', p)

    def test_phase_order(self):
        d, s = self.open('--jury', '3')
        self.assertEqual(len(court.missing(d, s, 'opening')), 2)
        self.fill(d, s, 'opening', 'Some argument')
        self.assertEqual(court.missing(d, s, 'opening'), [])
        self.assertEqual(len(court.missing(d, s, 'rebuttal')), 2)

    def test_majority_and_incomplete(self):
        d, s = self.open('--jury', '5', '--mode', 'simulation')
        self.fill(d, s, 'opening', 'Arguments')
        self.fill(d, s, 'rebuttal', 'Responses')
        for j, v in zip(court.jobs(d, s, 'jury'), ['GUILTY', 'GUILTY', 'NOT GUILTY', 'GUILTY', 'NO VOTE']):
            j['output'].write_text('NO VOTE' if v == 'NO VOTE' else 'VOTE: ' + v + '\nREASON: depends | on data', encoding='utf-8')
        t = court.tally(d, s)
        self.assertEqual((t['verdict'], t['guilty'], t['not_guilty'], t['no_vote']), ('GUILTY', 3, 1, 1))
        with self.assertRaises(ValueError):
            court.render(d, s)
        self.fill(d, s, 'judge', '## The sentence\nRun a pilot.')
        result = court.render(d, s)
        self.assertIn('simulated perspectives', result.lower())
        self.assertIn('depends / on data', result)
        self.assertTrue((d / 'VERDICT.md').exists())

    def test_tie(self):
        d, s = self.open('--jury', '4')
        for j, v in zip(court.jobs(d, s, 'jury'), ['GUILTY', 'NOT GUILTY', 'GUILTY', 'NOT GUILTY']):
            j['output'].write_text('VOTE: ' + v, encoding='utf-8')
        self.assertEqual(court.tally(d, s)['verdict'], 'HUNG JURY')

    def test_no_vote(self):
        d, s = self.open('--jury', '3')
        self.fill(d, s, 'jury', 'NO VOTE')
        t = court.tally(d, s)
        self.assertEqual(t['no_vote'], 3)
        self.assertEqual(t['verdict'], 'HUNG JURY')

    def test_subagent_attestations_gate_complete_render(self):
        d, s = self.open('--jury', '3', '--mode', 'agent')
        self.fill(d, s, 'opening', 'Argument')
        self.fill(d, s, 'rebuttal', 'Rebuttal')
        self.fill(d, s, 'jury', 'VOTE: GUILTY\nREASON: insufficient evidence\nEXPERIMENT: interview buyers\nRISK: HIGH')
        self.fill(d, s, 'judge', '## Decision and uncertainty\nRun a pilot')
        with self.assertRaisesRegex(ValueError, 'subagent IDs'):
            court.render(d, s)
        for phase in court.PHASES:
            for j in court.jobs(d, s, phase):
                court.run(['attest', '--phase', phase, '--job', j['id'], '--agent-id', 'real-agent-' + phase + '-' + j['id']])
        d, s = court.state()
        self.assertEqual(court.tally(d, s)['attested_subagents'], 8)
        self.assertIn('Separate host subagent IDs', court.render(d, s))

    def test_duplicate_attestation_rejected(self):
        d, s = self.open('--jury', '3')
        self.fill(d, s, 'opening', 'Answer')
        court.run(['attest', '--phase', 'opening', '--job', 'prosecution', '--agent-id', 'one'])
        with self.assertRaisesRegex(ValueError, 'cannot be reused'):
            court.run(['attest', '--phase', 'opening', '--job', 'defense', '--agent-id', 'one'])

    def test_attestation_requires_finished_job_and_agent_mode(self):
        d, s = self.open('--jury', '3')
        with self.assertRaisesRegex(ValueError, 'unfinished job'):
            court.run(['attest', '--phase', 'opening', '--job', 'prosecution', '--agent-id', 'x'])
        d, s = self.open('--jury', '3', '--mode', 'simulation')
        self.fill(d, s, 'opening', 'Response')
        with self.assertRaisesRegex(ValueError, 'simulation mode'):
            court.run(['attest', '--phase', 'opening', '--job', 'prosecution', '--agent-id', 'x'])

    def test_specialist_risk_and_experiment(self):
        parsed = court.parse_vote('VOTE: GUILTY\nREASON: weak demand\nEXPERIMENT: preorders\nRISK: HIGH')
        self.assertEqual(parsed['risk'], 'HIGH')
        self.assertEqual(parsed['experiment'], 'preorders')
        parsed = court.parse_vote('VOTE: NOT GUILTY\nRISK: nonsense')
        self.assertEqual(parsed['risk'], 'UNKNOWN')

    def test_missing_case_and_pointer_traversal(self):
        with self.assertRaises(ValueError):
            court.run(['init', '--case-file', 'missing.md'])
        Path('.court/LATEST').write_text('../../outside')
        with self.assertRaises(ValueError):
            court.latest()


if __name__ == '__main__':
    unittest.main()
