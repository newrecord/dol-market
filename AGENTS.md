# 돌마켓 개발 지침

- 사용자 설명·문서·스킬 지침은 한국어를 기본으로 작성한다.
- `plugins/<name>/plugin.json`과 해당 플러그인 안의 스킬이 원본이다. 생성된 카탈로그와 `.claude-plugin/plugin.json`을 직접 편집하지 않는다.
- 스킬 하나를 독립 설치하려면 별도 플러그인으로 만든다. 소비자에게 Node.js를 요구하지 않는다.
- 호스트 고유 도구가 필요하면 실행 환경에서 지원 여부를 확인한다. Claude 도구·모델 이름을 Codex에서도 쓸 수 있다고 가정하지 않는다.
- 변경 후 `node scripts/catalog.mjs`와 `node scripts/catalog.mjs --check`, `claude plugin validate .` 및 변경 플러그인의 검증을 실행한다.
- 설치된 스킬은 이 저장소 밖에서 실행되므로 이 AGENTS.md에 필요한 런타임 지침을 숨기지 않는다.
- 공개 저장소에 개인 경로·계정 정보·토큰·로그를 넣지 않는다.
- PR 생성은 최초 push 필요 여부, branch/base, 요약, 검증 결과를 제시한 뒤 명시 승인을 받는다. 미해결 최신 CI 실패가 있는 head는 병합하지 않는다.
