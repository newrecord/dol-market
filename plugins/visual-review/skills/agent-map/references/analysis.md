# 분석 기준

## 프로젝트 경계와 탐색

`rg --files --hidden` 등 호스트의 파일 검색 도구로 경로를 먼저 좁힌다. `.git`, 의존성 폴더, 빌드 결과, 생성한 `docs/agent-map`은 조사에서 제외한다. 파일을 읽기 전에 symlink를 해석한 실제 경로가 프로젝트 안인지 확인한다.

| 시작점 | 확인할 내용 |
| --- | --- |
| 프로젝트 루트와 하위의 `AGENTS.md`, `AGENTS.override.md`, `CLAUDE.md`, `CLAUDE.local.md` | 해당 경로에 적용되는 역할, 위임, 검토 절차, 필수 스킬과 로컬 참조 |
| `.claude/agents/`, `.claude/skills/` | 프로젝트에 정의된 에이전트와 스킬. 에이전트 frontmatter에 명시된 `model`, `effort` |
| `.agents/skills/` | 프로젝트의 공통 스킬 |
| `.codex/agents/*.toml` | 프로젝트 에이전트의 `name`, `description`, `developer_instructions`, 명시된 `model`, `model_reasoning_effort`와 스킬 비활성화 설정 |
| `.codex/config.toml`, `.claude/settings.json`, `.claude/settings.local.json` | 프로젝트에서 선언한 에이전트·로컬 정의 참조·플러그인 활성 설정. 자격증명은 제외 |
| 위 파일이 명시적으로 가리키는 프로젝트 내부 문서·설정 | 에이전트 역할, 스킬 본문, 위임 조건의 근거 |

표준 설정 경로는 gitignore로 숨겨져 있어도 프로젝트 안에 있는지 개별 확인한다. 존재하지 않는 경로는 건너뛴다.

설정 파일 전체를 결과물에 복사하지 않는다. 필요한 역할명, 로컬 경로, 관계, 모델·effort만 취한다. 개인 계정, 토큰, API key, 비공개 URL은 수집·인용하지 않는다.

`plugins/`나 템플릿·예제 폴더에 있는 에이전트·스킬은 배포할 원본일 수 있다. 프로젝트의 활성 지침이나 설정에서 사용하도록 연결한 근거가 없다면 현재 프로젝트에 적용되는 것으로 표시하지 않는다. 마켓플레이스 목록에 있다는 사실만으로 설치·활성화를 확정하지 않는다. 이 구분을 결정할 수 없으면 `notes`에 남긴다.

비활성화 설정이 있는 역할·스킬을 활성 상태라고 표현하지 않는다. 필수 호출 지침과 비활성화 설정이 충돌하면 notes에 양쪽 근거를 적고 해당 연결을 활성 호출로 그리지 않는다. 프로젝트의 AGENTS.override.md가 같은 경로 AGENTS.md를 대체하는 경우에도 대체된 내용을 현재 관계로 합치지 않는다.

같은 에이전트의 정의가 여러 호스트에 있다면 파일과 적용 범위를 확인한다. 이름만 같다고 합치지 않고, 동일한 역할임이 명확할 때만 통합한다. 하위 `AGENTS.md`의 적용 범위를 프로젝트 전체로 확대하지 않는다. 선언만 확인된 설정과 실제 호스트에서 활성화됨을 확인한 상태도 구분한다.

## 무엇을 연결하는가

| 근거의 의미 | 결과 |
| --- | --- |
| “개발자는 QA 에이전트에게 검증을 맡긴다” | 개발자 → QA, `delegate` |
| “QA는 항상 verify 스킬을 실행한다” | QA → verify, `required` |
| “UI 변경이면 디자이너는 accessibility 스킬을 반드시 사용한다” | 디자이너 → accessibility, `required`, 라벨에 UI 변경 조건 |
| “개발자는 필요할 때 benchmark 스킬을 사용할 수 있다” | benchmark를 선택 스킬 목록에 기록, 간선 없음 |
| “리뷰 가능”처럼 능력만 설명하거나 스킬 이름만 나열 | 위임·호출 관계로 해석하지 않음 |
| 특정 지침이 특정 역할에 적용됨을 명시 | 지침 → 역할, `instruction` |
| 스킬이 다른 프로젝트 내부 스킬을 반드시 읽거나 호출 | 스킬 → 스킬, `required`, 읽기/호출 구분을 라벨에 기록 |

명시된 조건부 위임은 `delegate`로 두되 조건을 라벨에 기록한다. 단순히 메인 에이전트가 해당 서브 에이전트를 호출할 수 있는 기능이 있다는 이유로 연결하지 않는다. 위임과 검토는 호출 방향만 표현한다. 결과 반환이나 시간 순서는 근거에 있을 때만 설명하며 반대 방향 화살표를 자동으로 추가하지 않는다. 현재 데이터 계약에 없는 결과 보고·반환 관계는 `notes`에서 근거와 함께 설명하며 `delegate`로 바꾸지 않는다.

프로젝트 밖의 스킬을 필수로 요구하더라도 이번 그림에 외부 노드를 만들지 않는다. `notes`에 “프로젝트 밖의 필수 스킬 참조가 있어 이 지도에서는 제외했다”라고 남긴다. 대상 파일이 없는 경우에는 “로컬 대상 정의를 찾지 못함”으로 구분한다.

## 모델과 effort

에이전트의 직접 선언을 우선하고, 각 값에 선언 파일과 줄 번호를 붙인다. Claude 에이전트 Markdown의 YAML frontmatter에서 `model`, `effort`, Codex 에이전트 TOML에서 `model`, `model_reasoning_effort`처럼 실제로 존재하는 필드를 확인한다. 명시적인 프로젝트 지침도 해당 에이전트와 적용 범위를 확인할 수 있으면 근거가 된다. 필드가 있다는 사실과 해당 호스트 버전에서 실제로 적용되는지는 구분한다.

- `model`과 `effort`는 에이전트 노드에만 넣으며 각각 독립적으로 생략할 수 있다. 값이 없으면 기본값을 만들어 넣지 않는다.
- 프로젝트 공통 설정은 실제로 그 설정이 적용되는 Coordinator에만 반영한다. 같은 프로젝트의 모든 서브 에이전트로 복사하지 않는다. 이름만으로 Coordinator 노드를 새로 만들지 않는다.
- 전역 설정, 실행 중인 대화의 모델, 호스트의 기본값으로 빈 값을 채우지 않는다. `sonnet` 같은 별칭을 특정 모델 버전으로 확장하지 않는다. 표시하는 것은 프로젝트의 선언이며 실제 실행 모델을 확인한 결과가 아니다.
- `inherit`, `default`, `auto`처럼 명시된 값은 원문과 근거를 유지하고 중립색으로 표시한다. 알려지지 않은 effort 값도 원문을 유지하고 중립색으로 표시한다. 이 값이 호스트에서 지원된다고 단정하지 않는다.
- “어려운 작업이면 다른 모델/effort 사용”과 같은 조건부 override는 조건과 근거를 `notes`에 적는다. 에이전트의 기본 선언을 덮어쓰지 않으며, 기본 선언이 없으면 해당 필드는 생략한다. 선언 간 충돌이나 적용 범위가 불명확한 경우도 임의로 하나를 고르지 말고 `notes`에 남긴다.

Mermaid에서는 모델별 배경색과 effort별 테두리색을 사용하고 노드 라벨에 값도 쓴다. HTML에서는 같은 값의 배지, 색상 범례와 파일 근거를 제공한다. 모델이 같은 에이전트는 같은 모델색을 사용하며 effort는 별도로 구분한다. 색상만으로 값을 판별하게 만들지 않는다.

## 데이터 형식

파일은 UTF-8 JSON이다. 노드 ID는 그림 안에서 고유한 영문 소문자·숫자·밑줄 조합을 사용한다. 표시 이름은 한국어여도 된다. `source.line`은 요약한 사실을 실제로 확인한 1부터 시작하는 줄 번호이며, `source.path`는 프로젝트 루트 기준 상대경로다. 아래 예시는 형식 설명용이며 실제 프로젝트의 근거로 사용하지 않는다.

```json
{
  "title": "프로젝트 에이전트 지도",
  "scope": "현재 checkout 내부 설정",
  "summary": "프로젝트 문서에 명시된 위임과 필수 스킬 호출 관계입니다.",
  "nodes": [
    {
      "id": "qa",
      "label": "QA",
      "kind": "agent",
      "description": "검증 담당",
      "source": { "path": ".claude/agents/qa.md", "line": 1 },
      "model": {
        "value": "sonnet",
        "source": { "path": ".claude/agents/qa.md", "line": 4 }
      },
      "effort": {
        "value": "high",
        "source": { "path": ".claude/agents/qa.md", "line": 5 }
      }
    },
    {
      "id": "verify",
      "label": "verify",
      "kind": "skill",
      "description": "프로젝트 검증",
      "source": { "path": ".agents/skills/verify/SKILL.md", "line": 1 }
    }
  ],
  "edges": [
    {
      "from": "qa",
      "to": "verify",
      "kind": "required",
      "label": "검증 시 필수 호출",
      "source": { "path": ".claude/agents/qa.md", "line": 8 }
    }
  ],
  "optional_skills": [
    {
      "name": "benchmark",
      "path": ".agents/skills/benchmark/SKILL.md",
      "reason": "개발자가 필요할 때 선택할 수 있다고 명시됨. 근거: .claude/agents/developer.md:12"
    }
  ],
  "notes": ["문서 분석이며 실제 실행 여부는 확인하지 않았습니다."]
}
```

`nodes`, `edges`, `optional_skills`, `notes`는 비어 있어도 된다. 스킬이 존재하지만 호출 관계가 정의되지 않았으면 `optional_skills`에 “로컬 정의는 있으나 필수 호출 관계 없음”으로 기록한다. 읽을 수 없거나 형식을 지원하지 않아 분석하지 못한 경우를 “설정 없음”으로 바꾸지 않는다.

에이전트 노드의 선택 필드 `model`, `effort`는 각각 `{ "value": "비어 있지 않은 문자열", "source": { "path": "프로젝트 상대경로", "line": 1 } }` 형식이다. 각 필드의 근거는 노드 자체의 근거와 다를 수 있다. `instruction`, `skill` 노드에는 넣지 않는다. 이 필드가 없는 기존 `map.json`도 그대로 렌더링할 수 있다.

렌더링 전에 모든 간선의 양 끝 ID, 필수 호출 근거, 조건 라벨, 경로 범위를 확인한다. renderer는 데이터 형식을 검증하고 그림을 만들지만, 문장의 의미나 실제 프로젝트 활성화를 대신 판단하지 않는다.

## 형식 참고

- [Codex 프로젝트 에이전트](https://learn.chatgpt.com/docs/agent-configuration/subagents): 프로젝트 `.codex/agents/*.toml` 정의도 조사한다. 파일명만으로 역할을 추정하지 않고 `name`을 읽는다.
