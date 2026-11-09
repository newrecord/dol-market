# 예시 프로젝트 — 역할 구성 검증용

이 프로젝트의 주 에이전트는 Coordinator다. 세부 역할은 `.claude/agents/`에 정의한다.
Coordinator는 변경 요구를 Planner에게 위임한다.
기획안이 확정되면 Coordinator는 Developer에게 구현을 위임한다.
화면 변경이 포함되면 Coordinator는 Designer에게 시각 검토를 위임한다.
구현이 끝나면 Coordinator는 QA에게 검증을 위임한다.
이 지침은 위의 모든 역할에 적용한다.
