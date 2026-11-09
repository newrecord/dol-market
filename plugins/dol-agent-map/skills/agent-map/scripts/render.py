#!/usr/bin/env python3
"""근거가 있는 프로젝트 구성 JSON을 Mermaid·Markdown·HTML로 변환한다."""
import argparse
import html
import json
import os
import textwrap
from pathlib import Path, PurePosixPath
from urllib.parse import quote

KINDS = {'instruction': '적용 지침', 'agent': '에이전트', 'skill': '필수 스킬'}
RELATIONS = {'instruction': '지침 적용', 'delegate': '위임', 'required': '필수 호출'}


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('빈 문자열 대신 설명을 입력하세요.')
    return value


def validate(data, root):
    root = Path(root).resolve()
    for field in ('title', 'scope', 'summary'):
        text(data[field])
    def source(s):
        p = PurePosixPath(text(s['path']))
        if p.is_absolute() or '..' in p.parts or '\\' in str(p) or ':' in str(p):
            raise ValueError('근거는 프로젝트 내부 상대 경로여야 합니다.')
        resolved = (root / str(p)).resolve()
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise ValueError(f'프로젝트 밖 또는 존재하지 않는 근거: {p}')
        line = s['line']
        if type(line) is not int or not 1 <= line <= len(resolved.read_text(encoding='utf-8').splitlines()):
            raise ValueError(f'근거 줄 번호를 확인하세요: {p}')
    nodes = {}
    for n in data['nodes']:
        key = text(n['id'])
        if key in nodes or n['kind'] not in KINDS:
            raise ValueError('중복 노드 또는 지원하지 않는 종류입니다.')
        text(n['label']); text(n['description']); source(n['source'])
        nodes[key] = n
    for e in data['edges']:
        a, b = nodes[e['from']], nodes[e['to']]
        valid = {'delegate': a['kind'] == b['kind'] == 'agent',
                 'required': a['kind'] in ('agent', 'skill') and b['kind'] == 'skill',
                 'instruction': a['kind'] == 'instruction' and b['kind'] in ('agent', 'skill', 'instruction')}
        if not valid.get(e['kind']):
            raise ValueError('관계와 노드 종류가 맞지 않습니다.')
        text(e['label']); source(e['source'])
    required = {e['to'] for e in data['edges'] if e['kind'] == 'required'}
    if any(n['kind'] == 'skill' and n['id'] not in required for n in nodes.values()):
        raise ValueError('필수 호출 근거 없는 스킬은 optional_skills 표로 옮기세요.')
    for s in data.get('optional_skills', []):
        text(s['name']); text(s['reason']); source({'path': s['path'], 'line': 1})
    for note in data.get('notes', []):
        text(note)
    return data


def label(value):
    # Mermaid 문법과 HTML을 입력 텍스트가 바꾸지 않도록 문자 엔티티로 표현한다.
    return ''.join(c if c.isalnum() or c == ' ' else f'#{ord(c)};' for c in ' '.join(value.split()))


def mermaid(data):
    lines = ['flowchart LR']
    ids = {n['id']: f'n{i}' for i, n in enumerate(data['nodes'])}
    for kind, title in KINDS.items():
        group = [n for n in data['nodes'] if n['kind'] == kind]
        if not group:
            continue
        lines.append(f'  subgraph g_{kind}["{title}"]')
        for n in group:
            lines.append(f'    {ids[n["id"]]}["{label(n["label"])}"]:::{kind}')
        lines.append('  end')
    if not data['nodes']:
        lines.append('  empty["프로젝트 내부에 확인된 역할·지침이 없습니다"]')
    for e in data['edges']:
        arrow = '-.->' if e['kind'] == 'instruction' else '-->'
        caption = '<br/>'.join(label(part) for part in textwrap.wrap(e['label'], width=16))
        if e['kind'] == 'instruction' and e['label'] in ('지침 적용', '프로젝트 지침 적용'):
            lines.append(f'  {ids[e["from"]]} {arrow} {ids[e["to"]]}')
        else:
            lines.append(f'  {ids[e["from"]]} {arrow}|"{caption}"| {ids[e["to"]]}')
    lines += ['  classDef instruction fill:#f0f3f8,stroke:#95a0b4,color:#34425c',
              '  classDef agent fill:#edf3ff,stroke:#637dea,color:#1e3475',
              '  classDef skill fill:#e4f5ec,stroke:#40966b,color:#205c3e']
    return '\n'.join(lines) + '\n'


def md(value):
    return html.escape(str(value), quote=False).replace('|', '&#124;').replace('`', '&#96;').replace('[', '&#91;').replace(']', '&#93;').replace('\n', ' ')


def markdown(data, diagram, root, out):
    def link(s):
        rel = os.path.relpath(root / s['path'], out).replace(os.sep, '/')
        return f'[{md(s["path"])}:{s["line"]}]({quote(rel, safe="/.")}#L{s["line"]})'
    lines = [f'# {md(data["title"])}', '', md(data['summary']), '',
             f'범위: {md(data["scope"])}. 프로젝트 설정의 정적 관계이며 실제 실행 기록이 아닙니다.', '',
             '```mermaid', diagram.rstrip(), '```', '',
             '실선: 위임·필수 호출 / 점선: 지침 적용. 조건부 호출은 연결선의 조건을 읽으세요.', '',
             '## 역할과 근거', '', '| 이름 | 종류 | 설명 | 근거 |', '| --- | --- | --- | --- |']
    for n in data['nodes']:
        lines.append(f'| {md(n["label"])} | {KINDS[n["kind"]]} | {md(n["description"])} | {link(n["source"])} |')
    lines += ['', '## 연결 근거', '', '| 연결 | 의미·조건 | 근거 |', '| --- | --- | --- |']
    names = {n['id']: n['label'] for n in data['nodes']}
    for e in data['edges']:
        lines.append(f'| {md(names[e["from"]])} → {md(names[e["to"]])} | {md(e["label"])} | {link(e["source"])} |')
    lines += ['', '## 선택·미연결 스킬', '', '| 스킬 | 경로 | 연결하지 않은 이유 |', '| --- | --- | --- |']
    for s in data.get('optional_skills', []):
        lines.append(f'| {md(s["name"])} | {md(s["path"])} | {md(s["reason"])} |')
    if not data.get('optional_skills'):
        lines.append('| 없음 | — | 확인된 선택·미연결 스킬 없음 |')
    lines += ['', '## 확인이 필요한 사항', '']
    lines += [f'- {md(n)}' for n in data.get('notes', [])] or ['- 없음']
    return '\n'.join(lines) + '\n'


def render(data, root, out):
    root, out = Path(root).resolve(), Path(out).resolve()
    validate(data, root)
    diagram = mermaid(data)
    document = markdown(data, diagram, root, out)
    template = (Path(__file__).resolve().parent.parent / 'assets/viewer.html').read_text()
    payload = json.dumps({'map': data, 'mermaid': diagram, 'markdown': document}, ensure_ascii=False)
    payload = payload.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    page = template.replace('<!--MAP_DATA-->', payload)
    out.mkdir(parents=True, exist_ok=True)
    for name, content in [('map.mmd', diagram), ('map.md', document), ('index.html', page)]:
        (out / name).write_text(content, encoding='utf-8')
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--project-root', type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        render(json.loads(args.input.read_text()), args.project_root, args.output)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f'생성 실패: {exc}\n')
    print('생성 완료: map.md / map.mmd / index.html')


if __name__ == '__main__':
    main()
