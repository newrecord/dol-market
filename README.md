# 돌마켓 · dol-market

Claude Code와 Codex에서 필요한 플러그인만 골라 설치하는 개인 마켓플레이스다.
GitHub 저장소가 카탈로그와 플러그인을 함께 배포한다. npm/pnpm 레지스트리나 별도 서버는 필요 없다.
표시 이름은 **돌마켓**, 설치 식별자는 **dol-market**이다. 공개 저장소는 [newrecord/dol-market](https://github.com/newrecord/dol-market)이다. 공통 배포 구조를 제공하며, 현재 등록된 플러그인은 없다.

## 설치 단위와 구조

기본은 **플러그인 하나 = 독립 기능 하나 = 스킬 하나**다. 같이 설치해야 의미가 있는 스킬만 같은 플러그인에 묶는다.
플러그인 내부의 개별 스킬을 패키지처럼 선택 설치하는 방식은 아니다. 마켓플레이스 등록 자체로 모든 플러그인을 설치하지 않는다.

```text
plugins/<plugin>/
  plugin.json                    공통 메타데이터 원본, 버전의 기준
  .claude-plugin/plugin.json     Claude용 생성 파일
  skills/<skill>/SKILL.md        두 환경이 공유하는 스킬 본문
.claude-plugin/marketplace.json  Claude용 생성 카탈로그
.agents/plugins/marketplace.json Codex용 생성 카탈로그
scripts/catalog.mjs             카탈로그 생성 및 정합성 검사
```

본문을 복제하지 않는다. 도구와 모델에 의존하지 않는 스킬부터 추가하고, 호스트 전용 동작이 필요해질 때만 해당 플러그인 내부에 환경별 참고 문서를 둔다.
플러그인은 캐시에 복사되므로 저장소 밖의 파일이나 다른 플러그인의 상대 경로에 의존하지 않는다.
`AGENTS.md`는 개발 규칙이며 설치된 스킬의 실행 지침을 대신하지 않는다.

## 현재 플러그인

현재 카탈로그는 비어 있다. 설치 확인용 `dol-check`는 GitHub에서 Claude Code와 Codex CLI에 각각 설치하고, 새 세션에서 기대 응답을 확인한 뒤 제거했다.
두 설치 캐시의 스킬 본문과 원본이 일치함도 확인했다. Codex 데스크톱 앱 화면에서의 호출은 별도로 검증하지 않았다.

아래 `PLUGIN_NAME`과 `SKILL_NAME`은 앞으로 추가할 실제 이름으로 바꾼다. 플러그인이 추가되기 전에는 설치 명령을 실행할 수 없다.

## Claude Code에서 로컬 설치

저장소 루트에서 실행한다. 이 명령은 실제 사용자 설치 설정을 변경한다.

```sh
claude plugin marketplace add .
claude plugin install PLUGIN_NAME@dol-market
```

다른 터미널에서 `claude`를 시작하고 `/PLUGIN_NAME:SKILL_NAME`를 실행한다.
로컬 폴더를 가리키는 마켓플레이스이므로 폴더를 옮기면 다시 등록해야 한다.

## GitHub 배포 후 설치

GitHub 저장소를 마켓플레이스로 등록하고 필요한 플러그인을 설치한다.
Claude Code 안에서:

```text
/plugin marketplace add newrecord/dol-market
/plugin install PLUGIN_NAME@dol-market
```

새 세션에서 `/PLUGIN_NAME:SKILL_NAME`를 실행한다. 이미 같은 이름의 로컬 마켓플레이스를 등록했다면 먼저 기존 등록을 제거하고 GitHub 원본으로 다시 등록한다.

## Codex 설치

현재 로컬 CLI가 제공하는 명령은 다음과 같다. 저장소 루트에서 실행한다.

```sh
codex plugin marketplace add .
codex plugin add PLUGIN_NAME@dol-market
```

GitHub 배포 후에는 첫 명령의 `.`을 `newrecord/dol-market`로 바꾼다.
Codex 앱의 새 대화에서 설치한 플러그인의 스킬을 선택하고 로딩 확인을 요청한다.
CLI 버전에 `plugin add`가 없다면 앱 플러그인 화면에서 등록된 마켓플레이스의 플러그인을 설치한다.
CLI 설치와 앱의 실제 스킬 로딩은 각각 확인해야 한다.

## 새 플러그인 작성

1. `plugins/<이름>/plugin.json`에 이름, `0.1.0` 버전, 설명, 작성자, 라이선스를 작성한다. 공통 manifest에 `name`, `version`, `description`, `author.name`, `license`를 포함한다.
2. `skills/<스킬명>/SKILL.md`에 `name`, 한 줄 `description`, 실제 작업 지침을 작성한다. 이름과 폴더명은 동일한 소문자 kebab-case로 쓴다.
3. 플러그인 안에 필요한 참고 문서·스크립트만 추가한다. 검사 스크립트의 frontmatter 검사는 이 저장소의 단순 형식을 대상으로 하며 범용 YAML 검증기는 아니다.
4. 아래 검증을 수행하고 실제 호스트별 호출 결과를 확인한다.

```sh
node scripts/catalog.mjs
node scripts/catalog.mjs --check
claude plugin validate .
claude plugin validate ./plugins/PLUGIN_NAME
```

마지막 명령은 추가하거나 변경한 플러그인 경로로 바꾼다. Node.js는 관리자의 생성·검증에만 필요하며 사용자 설치에는 필요 없다.
생성 파일도 Git에 함께 올린다. CI는 생성 파일의 일치 여부를 검사한다. Claude 공식 검증과 실제 모델 호출은 별도의 로컬/출시 점검이다.

## 버전과 배포

플러그인별 SemVer로 관리한다. 지침 수정도 설치 캐시 갱신을 위해 버전을 올린다.
마켓플레이스에는 버전을 복제하지 않고 플러그인 manifest를 기준으로 한다.
새 스킬 작성 → 로컬 검증 → GitHub에 push → 새 터미널에서 원격 설치 → 실제 호출 순서로 진행한다.
초기 구성의 형식 검증과 두 CLI의 원격 설치·스킬 호출·제거를 확인했다. 새 스킬은 호스트별로 다시 검증한다.
PR을 만들 때는 이 저장소의 승인 규칙을 따른다.

업데이트는 게시된 Git commit과 플러그인 버전 증가로 배포한다. GitHub Release와 npm publish는 필수가 아니다.

```sh
claude plugin marketplace update dol-market
claude plugin update PLUGIN_NAME@dol-market
codex plugin marketplace upgrade dol-market
```

Codex에서는 새 버전 발견 후 앱의 업데이트 동작을 확인한다. catalog refresh 자체를 설치된 코드 갱신 성공으로 간주하지 않는다.
자동 업데이트는 호스트 설정을 따르며 활성화되어 있다고 가정하지 않는다.
문제 발생 시 플러그인을 비활성화/제거하고, 원인을 수정하거나 이전 내용을 더 높은 patch 버전으로 재배포한다. 이미 공개한 Git 이력을 재작성하지 않는다.

```sh
claude plugin uninstall PLUGIN_NAME@dol-market
claude plugin marketplace remove dol-market
codex plugin remove PLUGIN_NAME@dol-market
codex plugin marketplace remove dol-market
```

## 설계 범위와 라이선스

초기 라이선스는 재배포 가능한 MIT로 선택했다. 외부 스킬을 가져올 때는 원본 라이선스와 저작권 표시를 보존한다.
공개 저장소에는 개인 경로·토큰·설정·대화 기록을 포함하지 않는다.
초기 범위는 공통 스킬과 카탈로그이며 MCP 서버, hooks, 모델별 에이전트 오케스트레이션, 자동 배포는 포함하지 않는다.
공식 공개 디렉터리 심사 제출은 개인 GitHub 마켓플레이스 운영과 별개다.

## 근거

- [Claude Code 마켓플레이스](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code manifest](https://code.claude.com/docs/en/plugins-reference)
- [OpenAI 플러그인 패키징](https://developers.openai.com/plugins/build/plugins)
- [Codex 스킬](https://learn.chatgpt.com/docs/build-skills)
