# Louie Kury

반려동물의 상태 기록을 바탕으로 수의사에게 전화 상담을 요청하는 포트폴리오 프로젝트입니다. [제품 요구사항과 정책](docs/prd.md)을 참고하세요.

일반 기능 개발은 관련 PRD·ERD·API·정책·컨벤션을 모두 조사한 뒤 planner가 사람이 읽을 계획서를 작성합니다. 사람이 계획을 승인하면 이슈를 작성하고, 이슈 승인 후 브랜치를 만들어 구현·검증을 이어갑니다. 메인이 planner·implementer·tester·독립 reviewer를 배정하며 승인 범위의 역할 전환마다 다시 묻지 않습니다. 커밋·푸시·PR은 요청·계획 범위에서 수행하고 PR 게시 후 대기합니다. 설계·문서·리뷰만 요청한 범위는 유지하며 VibeWise는 학습 모드를 명시적으로 요청한 경우에만 적용합니다.

프론트엔드와 백엔드 작업은 이 공통 문서 레포를 Codex 프로젝트로 열어 시작합니다. 실제 코드는 [옆에 둔 대상 레포](docs/ai/WORKFLOW.md#서비스-작업-경로)에서 작업합니다.

- [작업별 문서 찾기](docs/ai/ROUTING.md)
- [시작과 도구 사용](docs/ai/SETUP.md)
- [짧은 개발 흐름](docs/ai/WORKFLOW.md)
- [Git 컨벤션과 작성 템플릿](docs/convension/GIT_CONVENTIONS.md)
- [사람이 검토할 실행 계획서 틀](docs/ai/templates/plan.md)
- [기능 동작·선택 이유를 담는 명세 틀](docs/ai/templates/spec.md)

프로젝트 스킬은 `.agents/skills/`에 포함되어 있습니다. 개인별 별도 플러그인 설치는 필요하지 않습니다. 컨텍스트·세션 인계, Context7, Playwright는 유지합니다. 제품 서버와 DB는 아직 구성하지 않았습니다.
