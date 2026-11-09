"""입력 경계와 생성 산출물의 일관성을 검사한다."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('render', ROOT / 'plugins/visual-review/skills/agent-map/scripts/render.py')
render = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render)


class AgentMapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'AGENTS.md').write_text('역할 정의\nQA는 verify 필수 호출\n')
        self.data = {'title': '지도', 'scope': '프로젝트 내부', 'summary': '정적 구성',
                     'nodes': [self.node('qa', 'agent'), self.node('verify', 'skill')],
                     'edges': [{'from': 'qa', 'to': 'verify', 'kind': 'required', 'label': '항상 필수 호출', 'source': {'path': 'AGENTS.md', 'line': 2}}],
                     'optional_skills': [], 'notes': []}

    def node(self, key, kind):
        return {'id': key, 'label': key, 'kind': kind, 'description': '역할', 'source': {'path': 'AGENTS.md', 'line': 1}}

    def test_shared_mermaid_and_safe_html(self):
        self.data['title'] = '</script><img src=x onerror=alert(1)>'
        self.data['nodes'][0]['label'] = 'QA " | <test> [팀]'
        out = render.render(self.data, self.root, self.root / 'out')
        mmd = (out / 'map.mmd').read_text()
        page = (out / 'index.html').read_text()
        self.assertIn(mmd.rstrip(), (out / 'map.md').read_text())
        embedded = page.split('id="map-data">', 1)[1].split('</script>', 1)[0]
        self.assertEqual(json.loads(embedded)['mermaid'], mmd)
        self.assertNotIn(self.data['title'], page)
        self.assertNotIn('<test>', mmd)

    def test_unlinked_skill_rejected(self):
        self.data['edges'] = []
        with self.assertRaises(ValueError): render.validate(self.data, self.root)

    def test_source_outside_project_rejected(self):
        self.data['nodes'][0]['source']['path'] = '../outside.md'
        with self.assertRaises(ValueError): render.validate(self.data, self.root)

    def test_external_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / 'external.md'; target.write_text('지침')
            (self.root / 'alias.md').symlink_to(target)
            self.data['nodes'][0]['source']['path'] = 'alias.md'
            with self.assertRaises(ValueError): render.validate(self.data, self.root)

    def test_invalid_evidence_line_rejected(self):
        self.data['edges'][0]['source']['line'] = 99
        with self.assertRaises(ValueError): render.validate(self.data, self.root)

    def test_optional_skill_stays_out_of_diagram(self):
        self.data['optional_skills'] = [{'name': '선택 도구', 'path': 'AGENTS.md', 'reason': '선택 호출'}]
        render.validate(self.data, self.root)
        self.assertNotIn('선택 도구', render.mermaid(self.data))

    def test_empty_project_renders(self):
        self.data['nodes'] = []; self.data['edges'] = []
        render.validate(self.data, self.root)
        self.assertIn('확인된 역할', render.mermaid(self.data))

    def test_required_skill_chain(self):
        self.data['nodes'].append(self.node('audit', 'skill'))
        edge = copy.deepcopy(self.data['edges'][0]);edge.update({'from': 'verify', 'to': 'audit'})
        self.data['edges'].append(edge)
        render.validate(self.data, self.root)
        self.assertIn('n1 -->', render.mermaid(self.data))

    def setting(self, value, line=1):
        return {'value': value, 'source': {'path': 'AGENTS.md', 'line': line}}

    def test_model_and_effort_have_independent_evidence(self):
        self.data['nodes'][0].update(model=self.setting('gpt-example'), effort=self.setting('high', 2))
        out = render.render(self.data, self.root, self.root / 'out')
        diagram = (out / 'map.mmd').read_text()
        document = (out / 'map.md').read_text()
        self.assertIn('model#58; gpt#45;example', diagram)
        self.assertIn('effort#58; high', diagram)
        self.assertIn('stroke-width:3px', diagram)
        self.assertIn('| gpt-example | [AGENTS.md:1]', document)
        self.assertIn('| high | [AGENTS.md:2]', document)
        self.assertNotIn('effort: high', document.split('## 연결 근거')[1])

    def test_colors_distinguish_models_and_effort_independently(self):
        a = self.data['nodes'][0]
        a.update(model=self.setting('sonnet'), effort=self.setting('medium'))
        b = self.node('reviewer', 'agent')
        b.update(model=self.setting('sonnet'), effort=self.setting('ultra'))
        c = self.node('planner', 'agent')
        c.update(model=self.setting('gpt-example'))
        self.data['nodes'] += [b, c]
        colors = render.appearance(self.data)
        self.assertNotEqual(colors['models']['sonnet']['fill'], colors['models']['gpt-example']['fill'])
        self.assertNotEqual(colors['efforts']['medium']['stroke'], colors['efforts']['ultra']['stroke'])
        self.data['nodes'].reverse()
        self.assertEqual(render.appearance(self.data), colors)
        diagram = render.mermaid(self.data)
        self.assertEqual(diagram.count('fill:' + colors['models']['sonnet']['fill']), 2)
        render.validate(self.data, self.root)

    def test_inheritance_unknown_and_partial_settings(self):
        agent = self.data['nodes'][0]
        for value in ('inherit', 'default', 'auto'):
            agent['model'] = self.setting(value)
            self.assertEqual(render.appearance(self.data)['models'][value], render.NEUTRAL)
        agent['effort'] = self.setting('future-level')
        render.validate(self.data, self.root)
        self.assertEqual(render.appearance(self.data)['efforts']['future-level']['stroke'], render.NEUTRAL['stroke'])
        del agent['model']
        self.assertIn('effort#58; future#45;level', render.mermaid(self.data))
        self.assertNotIn('model#58;', render.mermaid(self.data))

    def test_invalid_model_effort_evidence_rejected(self):
        for field in ('model', 'effort'):
            for setting in (self.setting(''), self.setting('medium', 99),
                            {'value': 'medium', 'source': {'path': '../outside', 'line': 1}}, 'medium'):
                with self.subTest(field=field, setting=setting):
                    data = copy.deepcopy(self.data)
                    data['nodes'][0][field] = setting
                    with self.assertRaises(ValueError): render.validate(data, self.root)
            data = copy.deepcopy(self.data)
            data['nodes'][1][field] = self.setting('medium')
            with self.assertRaises(ValueError): render.validate(data, self.root)

    def test_metadata_does_not_inject_markup(self):
        value = '</script><img src=x onerror=alert(1)>|[x]'
        self.data['nodes'][0].update(model=self.setting(value), effort=self.setting(value))
        out = render.render(self.data, self.root, self.root / 'out')
        page = (out / 'index.html').read_text()
        self.assertNotIn(value, page)
        self.assertNotIn('<img', (out / 'map.mmd').read_text())
        embedded = json.loads(page.split('id="map-data">', 1)[1].split('</script>', 1)[0])
        self.assertIn(value, embedded['styles']['models'])
        self.assertEqual(embedded['map']['nodes'][0]['effort']['value'], value)


if __name__ == '__main__':
    unittest.main()
