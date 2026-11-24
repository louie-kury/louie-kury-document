# Louie Kury

반려동물의 상태 기록을 바탕으로 수의사에게 전화 상담을 요청하는 포트폴리오 프로젝트입니다. [제품 요구사항과 정책](docs/prd.md)을 참고하세요.

작업은 [문서 라우팅](docs/ai/ROUTING.md#읽기-규칙)에서 시작합니다. 승인 절차는 [휴먼게이트](docs/ai/HUMAN_GATES.md), 역할 배정과 검증은 [워크플로](docs/ai/WORKFLOW.md)를 따릅니다.

프론트엔드와 백엔드 작업은 이 공통 문서 레포를 Codex 프로젝트로 열어 시작합니다. 실제 코드는 [옆에 둔 대상 레포](docs/ai/WORKFLOW.md#서비스-작업-경로)에서 작업합니다.

- [작업별 문서 찾기](docs/ai/ROUTING.md)
- [시작과 도구 사용](docs/ai/SETUP.md)
- [짧은 개발 흐름](docs/ai/WORKFLOW.md)
- [Git 컨벤션과 작성 템플릿](docs/convension/GIT_CONVENTIONS.md)
- [사람이 검토할 실행 계획서 틀](docs/ai/templates/plan.md)
- [기능 동작·선택 이유를 담는 명세 틀](docs/ai/templates/spec.md)

프로젝트 스킬은 `.agents/skills/`에 포함되어 있습니다. 개인별 별도 플러그인 설치는 필요하지 않습니다. 컨텍스트·세션 인계, Context7, Playwright는 유지합니다. 제품 서버와 DB는 아직 구성하지 않았습니다.
