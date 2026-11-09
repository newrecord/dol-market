# visual-review

프로젝트 구성과 작업 결과를 사람이 시각적으로 검토할 수 있도록 하는 돌마켓 플러그인이다. 현재 프로젝트 에이전트 지도를 제공한다. Claude Code와 Codex가 같은 `agent-map` 스킬 본문을 사용한다.

명시된 위임, 필수 스킬 호출, 지침 적용 관계를 Mermaid 구성도로 표현한다. 조건이 있는 필수 호출은 조건을 연결선에 표시한다. 선택적으로 사용 가능한 스킬은 별도 목록에 정리한다. 에이전트 이름이나 스킬 설명만으로 연결을 추측하지 않는다.

에이전트에 명시된 LLM 모델과 effort도 표시한다. 모델은 노드 배경색, effort는 테두리색으로 구분하며 값도 텍스트로 보여준다. HTML 뷰어에는 배지, 색상 범례와 각 값의 파일 근거가 함께 나온다. 지정하지 않은 값은 생략하고, `inherit`·`default`·`auto` 또는 알 수 없는 effort는 원문을 유지한 중립색으로 표시한다. 조건부 변경은 조건과 근거를 별도 설명에 남긴다.

전역 에이전트, 개인 홈의 스킬, 설치 캐시, 프로젝트 밖의 링크 대상은 조사하지 않는다. 저장소에서 배포하는 플러그인도 해당 프로젝트의 활성 설정과 구분한다. 결과는 설정 문서의 구조이며 실제 실행 기록이나 도구 호출 순서를 의미하지 않는다.

## 호출

Claude Code에서 플러그인을 설치한 뒤:

```text
/agent-map
```

프로젝트나 출력 위치를 덧붙일 수도 있다. 다른 명령과 `agent-map` 이름이 겹칠 때만 `/visual-review:agent-map`으로 구분한다. 플러그인 설치 이름은 `visual-review@dol-market`으로 유지한다.

Codex 앱에서는 `visual-review`의 `agent-map` 스킬을 선택한다. Codex CLI·IDE에서는 `$agent-map`, 이름이 겹치면 `$visual-review:agent-map`을 사용하거나 `/skills`에서 선택한다. `/agent-map`을 Codex의 공통 슬래시 명령으로 등록하는 기능은 제공하지 않는다.

호출 방식 근거: [Claude Code의 스킬 명령 이름](https://code.claude.com/docs/en/slash-commands#how-a-skill-gets-its-command-name), [Codex 스킬 호출](https://learn.chatgpt.com/docs/build-skills).

## 결과

기본 출력 위치는 프로젝트의 `docs/agent-map/`이다.

- `map.json`: 프로젝트 내부 근거를 확인한 노드와 연결, 선택적인 모델·effort 선언
- `map.md`: GitHub에서 볼 수 있는 Mermaid와 근거 목록
- `map.mmd`: 다른 Mermaid 도구에서도 사용할 수 있는 원본
- `index.html`: 같은 Mermaid를 렌더링하는 로컬 뷰어

HTML은 브라우저에서 열 수 있다. 브라우저가 제공되는 환경에서는 스킬이 열어 렌더링 상태를 확인한다. 사용할 브라우저가 없으면 파일 경로와 열기 방법을 제공하고 렌더링 확인 여부를 밝힌다.

모델과 effort는 프로젝트에 선언된 값이며 호스트의 실제 실행 설정을 보장하지 않는다. 별칭을 실제 모델 버전으로 바꾸거나 전역 기본값을 채워 넣지 않는다. 해당 필드가 없는 기존 `map.json`도 계속 사용할 수 있다.

뷰어는 고정 버전의 Mermaid를 CDN에서 불러오므로 최초 로딩에 네트워크 연결이 필요하다. 다이어그램 데이터는 HTML 안에 있으며 외부 다이어그램 생성 서비스에 업로드하지 않는다. 오프라인에서는 Markdown과 Mermaid 원본을 사용할 수 있다. 생성 도구는 Python 3.9 이상 표준 라이브러리로 실행되며 Node.js 설치는 요구하지 않는다.

## 변경과 제거

이 스킬은 에이전트 설정을 수정하거나 활성화하지 않는다. 생성된 결과를 갱신할 때만 지정된 출력 파일을 변경한다. 결과를 없애려면 생성된 파일만 제거한다. 기존 문서와 다른 사용자의 파일은 유지한다.

라이선스는 MIT다. 설치 절차는 돌마켓 루트 README를 참고한다.

## 개발 검증과 참고

버전 0.2.0. `/plugin marketplace add newrecord/dol-market`, `/plugin install visual-review@dol-market`로 설치한다.

pstack의 [how 설명 방식](https://github.com/cursor/plugins/tree/main/pstack/skills/how)을 참고해 구조·관계·파일 근거를 분리했다. pstack 코드나 프롬프트를 복제하지 않고 프로젝트 구성 분석에 맞게 작성했다.

## 스킬 구성

| 스킬 | Codex 전체 호출명 | Claude Code 전체 호출명 | 상태 |
| --- | --- | --- | --- |
| agent-map | `$visual-review:agent-map` | `/visual-review:agent-map` | 구현됨 |
| pr | `$visual-review:pr` | `/visual-review:pr` | 향후 예정, 현재 호출 불가 |

`name: agent-map`은 스킬 자체의 이름이다. 플러그인이 호스트에 로드될 때 `visual-review` 네임스페이스가 붙는다. 스킬 본문이나 폴더 이름에 접두사를 중복해서 넣지 않는다.

## 이전 설치에서 전환

이름 변경은 기존 플러그인의 자동 업데이트로 처리되지 않는다. 아래 순서로 새 플러그인을 설치하고, 정상 로딩을 확인한 다음 이전 이름을 제거한다.

```sh
claude plugin marketplace update dol-market
claude plugin install visual-review@dol-market
codex plugin marketplace upgrade dol-market
codex plugin add visual-review@dol-market
```

Claude Code와 Codex의 새 세션에서 각각 `/visual-review:agent-map`, `$visual-review:agent-map` 로딩을 확인한다. 전환 기간에는 두 플러그인에 같은 스킬 이름이 있으므로 전체 이름을 사용한다. 확인을 마친 후:

```sh
claude plugin uninstall dol-agent-map@dol-market
codex plugin remove dol-agent-map@dol-market
```

새 설치에 문제가 있으면 이전 설치를 유지하고 새 이름의 플러그인만 제거한다. 마켓플레이스 등록과 프로젝트 산출물은 보존한다.
