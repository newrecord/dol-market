# agent-map 검증

## 생성기 검사

저장소 루트에서 `python3 -m unittest discover -s tests -v`를 실행한다.
검사 대상은 프로젝트 밖 경로·symlink, 잘못된 줄 번호, 필수 연결 없는 스킬, 선택 스킬 분리, 스킬 간 필수 호출, 빈 프로젝트, Markdown과 HTML의 동일 Mermaid 및 HTML 삽입 방지다.

모델·effort 확장의 회귀 기준은 다음과 같다. 0.2.0에서 총 13개 생성기 검사가 통과했다.

- 에이전트의 모델·effort는 각각 값과 파일 근거를 보존하며, 하나만 있거나 둘 다 없는 기존 데이터도 처리한다.
- 메타데이터를 가진 비에이전트 노드, 비어 있는 값, 유효하지 않은 근거 경로·줄 번호는 거절한다.
- Mermaid의 모델 배경색과 effort 테두리색, 텍스트 라벨이 함께 유지된다. HTML에는 배지·범례·근거가 표시되며 외부 입력이 HTML로 실행되지 않는다.
- `inherit`·`default`·`auto`와 알려지지 않은 effort 값은 원문을 유지하며 중립색을 사용한다.

## 의미 분석 평가

`fixtures/team`과 `fixtures/codex`는 실제 프로젝트와 분리된 검증 자료다. 평가할 호스트에 `agent-map` 스킬과 대상 fixture만 주고, 출력 폴더를 별도로 지정한다. 아래 기대값은 평가 프롬프트에 넣지 않고 결과 판정에만 사용한다.

| 대상 | 확인할 결과 |
| --- | --- |
| team | 지침 1개, 역할 5개, 필수 스킬 1개; 위임 4개, 필수 호출 2개, 지침 적용 5개 |
| team | Designer 위임과 Developer의 verify 호출 조건 유지; brainstorm은 선택 목록에만 표시 |
| team | 참조되지 않는 폐기 문서의 SuperBoss를 현재 역할로 표시하지 않음 |
| codex | quality_reviewer → verify 필수 호출; 파일명 auditor를 역할 이름으로 쓰지 않음 |
| codex | 정의되지 않은 메인 에이전트나 위임을 만들지 않음 |
| team | Developer: opus/medium, QA: sonnet/high, Planner: inherit/effort 생략, Designer: 모델·effort 생략 |
| codex | quality_reviewer: gpt-example/high; gpt-example은 실제 호출하지 않는 가상 모델 값 |

모델·effort를 포함한 의미 분석에서는 직접 선언과 Coordinator에 실제 적용되는 프로젝트 설정만 반영하는지 확인한다. 전역 설정이나 호스트 기본값을 추정해 채우지 않고, 별칭을 특정 모델 버전으로 바꾸지 않아야 한다. 조건부 override는 기본 선언과 구분해 조건·근거를 `notes`에 남긴다. 이 기준은 아래 초기 평가 기록에 포함된 성공 결과를 뜻하지 않는다.

초기 로컬 평가에서 독립 Codex 에이전트가 두 fixture를, Claude Code의 새 `--plugin-dir` 세션이 team fixture를 분석했다. 생성된 데이터와 파일에서 위 결과를 확인했다. Claude 평가의 일부 읽기 명령은 권한 제한으로 거절됐지만 다른 읽기 도구로 분석·생성을 완료했으며, 결과를 별도로 검사했다.

team 예시와 현재 돌마켓 구성은 Codex 인앱 브라우저에서 Mermaid 렌더링을 확인했다. 예시 뷰어의 확대·맞춤·원문 보기도 확인했다. 독립 평가와 Claude 결과는 의미가 일치했으나 문장 표현은 다르며, 모델 출력의 완전한 재현성을 보장하지 않는다.

이 기록은 로컬 검증이다. GitHub Mermaid의 원격 렌더링, 신규 플러그인의 원격 설치, 모든 프로젝트 설정 형식의 지원까지 확인한 것은 아니다. 원격 CI는 변경을 push한 뒤 별도로 확인한다.

0.2.0에서는 Claude Code의 새 `--plugin-dir` 세션이 수정된 team fixture를 읽어 반환한 JSON을 별도로 검증했다. 모델·effort 값과 각각의 줄 번호가 일치했고, 미지정 값은 만들지 않았다. 이 평가는 파일 생성과 브라우저 실행을 제외한 의미 분석 검증이다.

## 모델·effort 화면 검증

0.2.0의 가상 team 예시를 Codex 인앱 브라우저에서 렌더링해 opus·sonnet의 서로 다른 배경색, inherit의 중립색, medium·high의 테두리와 범례를 확인했다. 별도의 로컬 프로젝트에서도 같은 모델에 서로 다른 effort를 표시하고, 각 값의 개별 파일·줄 번호 및 확대·맞춤 동작을 확인했다. 개인 프로젝트의 데이터와 결과물은 공개 저장소에 포함하지 않는다.

## 짧은 호출 이름

이름 변경 전 `dol-agent-map` 플러그인을 Claude Code의 새 `--plugin-dir` 세션에서 `/agent-map`으로 호출했다. 프로젝트 조사·파일 생성 없이 로드된 스킬의 제목, 출력 경로와 파일명을 요청했으며 본문과 일치하는 응답을 확인했다. 도구는 비활성화했으므로 별도 파일 검색으로 이름을 추측한 결과가 아니다. 이 검증은 이름 충돌 없는 환경의 명령 인식을 확인하며, 현재 플러그인 이름에서 명령이 겹치면 `/visual-review:agent-map`을 사용한다.
