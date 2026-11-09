# dol-agent-map

프로젝트에 설정된 에이전트와 스킬을 사람이 검토할 수 있도록 시각화하는 돌마켓 플러그인이다. Claude Code와 Codex가 같은 `agent-map` 스킬 본문을 사용한다.

명시된 위임, 필수 스킬 호출, 지침 적용 관계를 Mermaid 구성도로 표현한다. 조건이 있는 필수 호출은 조건을 연결선에 표시한다. 선택적으로 사용 가능한 스킬은 별도 목록에 정리한다. 에이전트 이름이나 스킬 설명만으로 연결을 추측하지 않는다.

전역 에이전트, 개인 홈의 스킬, 설치 캐시, 프로젝트 밖의 링크 대상은 조사하지 않는다. 저장소에서 배포하는 플러그인도 해당 프로젝트의 활성 설정과 구분한다. 결과는 설정 문서의 구조이며 실제 실행 기록이나 도구 호출 순서를 의미하지 않는다.

## 호출

Claude Code에서 플러그인을 설치한 뒤:

```text
/agent-map
```

프로젝트나 출력 위치를 덧붙일 수도 있다. 다른 명령과 `agent-map` 이름이 겹칠 때만 `/dol-agent-map:agent-map`으로 구분한다. 플러그인 설치 이름은 `dol-agent-map@dol-market`으로 유지한다.

Codex 앱에서는 `agent-map` 스킬을 선택한다. Codex CLI·IDE에서는 `$agent-map` 또는 `/skills`에서 선택한다. `/agent-map`을 Codex의 공통 슬래시 명령으로 등록하는 기능은 제공하지 않는다.

호출 방식 근거: [Claude Code의 스킬 명령 이름](https://code.claude.com/docs/en/slash-commands#how-a-skill-gets-its-command-name), [Codex 스킬 호출](https://learn.chatgpt.com/docs/build-skills).

## 결과

기본 출력 위치는 프로젝트의 `docs/agent-map/`이다.

- `map.json`: 프로젝트 내부 근거를 확인한 노드와 연결
- `map.md`: GitHub에서 볼 수 있는 Mermaid와 근거 목록
- `map.mmd`: 다른 Mermaid 도구에서도 사용할 수 있는 원본
- `index.html`: 같은 Mermaid를 렌더링하는 로컬 뷰어

HTML은 브라우저에서 열 수 있다. 브라우저가 제공되는 환경에서는 스킬이 열어 렌더링 상태를 확인한다. 사용할 브라우저가 없으면 파일 경로와 열기 방법을 제공하고 렌더링 확인 여부를 밝힌다.

뷰어는 고정 버전의 Mermaid를 CDN에서 불러오므로 최초 로딩에 네트워크 연결이 필요하다. 다이어그램 데이터는 HTML 안에 있으며 외부 다이어그램 생성 서비스에 업로드하지 않는다. 오프라인에서는 Markdown과 Mermaid 원본을 사용할 수 있다. 생성 도구는 Python 3.9 이상 표준 라이브러리로 실행되며 Node.js 설치는 요구하지 않는다.

## 변경과 제거

이 스킬은 에이전트 설정을 수정하거나 활성화하지 않는다. 생성된 결과를 갱신할 때만 지정된 출력 파일을 변경한다. 결과를 없애려면 생성된 파일만 제거한다. 기존 문서와 다른 사용자의 파일은 유지한다.

라이선스는 MIT다. 설치 절차는 돌마켓 루트 README를 참고한다.

## 개발 검증과 참고

버전 0.1.0. `/plugin marketplace add newrecord/dol-market`, `/plugin install dol-agent-map@dol-market`로 설치한다.

pstack의 [how 설명 방식](https://github.com/cursor/plugins/tree/main/pstack/skills/how)을 참고해 구조·관계·파일 근거를 분리했다. pstack 코드나 프롬프트를 복제하지 않고 프로젝트 구성 분석에 맞게 작성했다.
