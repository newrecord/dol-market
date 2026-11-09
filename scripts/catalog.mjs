import { readdirSync, readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';

const root = fileURLToPath(new URL('../', import.meta.url));
const check = process.argv.includes('--check');
const read = p => JSON.parse(readFileSync(path.join(root, p), 'utf8'));
const emit = (p, value) => {
  const target = path.join(root, p);
  const content = JSON.stringify(value, null, 2) + '\n';
  if (check) assert.equal(readFileSync(target, 'utf8'), content, `${p}: 재생성 필요`);
  else { mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, content); }
};
const manifests = readdirSync(path.join(root, 'plugins'), { withFileTypes: true })
  .filter(d => d.isDirectory()).map(d => {
    const p = `plugins/${d.name}`;
    const m = read(`${p}/plugin.json`);
    assert.match(m.name, /^[a-z][a-z0-9-]*$/);
    assert.equal(m.name, d.name, '폴더명과 플러그인 이름이 달라요');
    assert.match(m.version, /^\d+\.\d+\.\d+$/);
    assert.ok(m.description && m.author?.name);
    const skills = readdirSync(path.join(root, p, 'skills'), { withFileTypes: true }).filter(s => s.isDirectory());
    assert.ok(skills.length, `${p}: 스킬이 필요해요`);
    for (const s of skills) {
      const file = path.join(root, p, 'skills', s.name, 'SKILL.md');
      assert.ok(existsSync(file), `${file}: 누락`);
      const text = readFileSync(file, 'utf8');
      const front = text.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/)?.[1];
      assert.ok(front, `${file}: frontmatter 누락`);
      assert.match(front, new RegExp(`^name: ${s.name}$`, 'm'));
      assert.match(front, /^description: .+/m);
    }
    return m;
  }).sort((a, b) => a.name.localeCompare(b.name));
for (const m of manifests) {
  const { $schema, ...claude } = m;
  emit(`plugins/${m.name}/.claude-plugin/plugin.json`, claude);
}
emit('.claude-plugin/marketplace.json', {
  name: 'dol-market', owner: { name: '돌마켓' }, description: 'Claude Code와 Codex를 위한 돌마켓',
  plugins: manifests.map(m => ({ name: m.name, source: `./plugins/${m.name}`, description: m.description }))
});
emit('.agents/plugins/marketplace.json', {
  name: 'dol-market', interface: { displayName: '돌마켓' },
  plugins: manifests.map(m => ({ name: m.name, source: { source: 'local', path: `./plugins/${m.name}` },
    policy: { installation: 'AVAILABLE', authentication: 'ON_INSTALL' }, category: 'Productivity' }))
});
console.log(`${check ? '검증' : '생성'} 완료: 플러그인 ${manifests.length}개`);
