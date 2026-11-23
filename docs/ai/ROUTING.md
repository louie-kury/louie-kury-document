# 필요한 자료만 읽기

## 읽기 규칙

작업에 맞는 행에서 연결한 필수 절을 읽는다. 표에 없는 자료는 제목과 검색 결과로 관련성을 확인한 뒤 필요한 절만 추가로 읽는다. 같은 세션에서 이미 확인했고 변경되지 않은 절은 재사용한다. 계획서에는 확인한 경로·절과 적용 사실, 해당하지 않는 자료의 이유, 미확인·충돌 사항을 남긴다. 문서에 있는 답은 다시 묻지 않는다.

## 작업별 문서

| 할 일 | 참고할 곳 |
| --- | --- |
| 기능 요청 시작·계획 검토 | [시작 순서](HUMAN_GATES.md#일반-기능-개발)를 따른다. 위 읽기 규칙으로 조사하고 [계획서](templates/plan.md)를 작성한다. |
| 프로젝트 이해 | [PRD](../prd.md), 현재 Git 상태 |
| 프론트엔드·백엔드 작업 폴더 선택 | [서비스 작업 경로](WORKFLOW.md#서비스-작업-경로)에서 기존 클론 또는 새 서비스의 위치를 확인한다. |
| 제품 기능 설계·구현·검증 | 기능 ID가 없으면 [PRD 기능 목록](../prd.md#6-기능-요구사항과-수용-기준)에서 찾는다. ID를 알면 [6.10 기능 연결표](../prd.md#610-기능공통-정책질문qa-연결표)에서 해당 행을 먼저 찾아 기능 본문과 관련 정책·D 항목·Q 시나리오를 읽는다. 계획 전에 [ERD](../erd.md)의 관련 엔티티·관계·필수값·제약과 [API 명세](../api/README.md)의 공통 계약·해당 도메인, 관련 정책·컨벤션을 함께 확인한다. 작업에 해당하지 않는 자료는 이유를 기록한다. 확인한 파일·절과 데이터 제약을 계획서에 남기고 문서에 있는 내용을 다시 묻지 않는다. |
| 프론트엔드 화면 구현·QA | [PRD 화면 목록](../prd.md#9-기능-기반-화면-목록)과 해당 기능의 수용 기준을 확인한다. |
| 프론트엔드 코드 작성·리뷰 | [프론트엔드 코드 컨벤션](../convension/FRONTEND_CODE_CONVENTIONS.md)에서 작업에 해당하는 절을 읽는다. |
| 백엔드 코드 작성·리뷰 | [백엔드 코드 컨벤션](../convension/BACKEND_CODE_CONVENTIONS.md)에서 작업에 해당하는 절만 읽는다. [패키지 구조](../convension/BACKEND_CODE_CONVENTIONS.md#패키지-구조), [의존 방향과 계층별 책임](../convension/BACKEND_CODE_CONVENTIONS.md#의존-방향과-계층별-책임), [네이밍](../convension/BACKEND_CODE_CONVENTIONS.md#네이밍), [영속성과 JPA 엔티티](../convension/BACKEND_CODE_CONVENTIONS.md#영속성과-jpa-엔티티), [DTO와 경계 변환](../convension/BACKEND_CODE_CONVENTIONS.md#dto와-경계-변환), [트랜잭션과 외부 연동](../convension/BACKEND_CODE_CONVENTIONS.md#트랜잭션과-외부-연동), [API와 공통 응답](../convension/BACKEND_CODE_CONVENTIONS.md#api와-공통-응답), [예외와 오류 처리](../convension/BACKEND_CODE_CONVENTIONS.md#예외와-오류-처리), [테스트 작성 규칙](../convension/BACKEND_CODE_CONVENTIONS.md#테스트-작성-규칙)을 참고한다. |
| 백엔드 데이터 조회·저장, 소유권·접근 권한, 상태 전이, 금전 처리 | 스키마 변경 여부와 관계없이 [ERD](../erd.md)에서 작업에 관련된 엔티티·참조 관계·필수값·제약을 확인한다. 예를 들어 상담 완료(`CON-04`)는 상담·코인 홀드·정산을 확인한다. |
| 실행 계획·선택 이유 기록 | [계획서 틀](templates/plan.md), [명세 틀](templates/spec.md), 해당 기능 문서. 유효한 설계가 있어도 이번 실행 계획을 작성한다. |
| 사용자가 명시적으로 요청한 학습 모드 | [바이브 와이즈](../../.agents/skills/vibe-wise/SKILL.md). 일반 planner 작업에 자동 적용하지 않는다. |
| 주요 설계 결정 기록 | [ADR 작성 위치와 기준](WORKFLOW.md#설계-결정-기록) |
| 역할 배정·테스트/리뷰/QA·문서 동기화 | [단계 선택과 순서](WORKFLOW.md#단계-선택과-순서)와 [위임할 자료](WORKFLOW.md#짧게-위임하기)에서 해당 단계만 확인한다. |
| 기능 계획부터 이슈·개발·리뷰까지 진행 | [휴먼게이트](HUMAN_GATES.md)에서 승인 순서와 대기 시점을 확인한다. |
| GitHub PR 리뷰 작성·재리뷰 | [PR 리뷰 템플릿](templates/pr-review_template.md)을 사용한다. |
| 이슈·브랜치·커밋·PR 작성·검토, 머지 후 이슈 상태 확인 | [Git 컨벤션](../convension/GIT_CONVENTIONS.md)의 해당 절을 읽는다. |
| 반복 읽기·위임·리뷰·검증 비용 줄이기 | [컨텍스트·검증 비용 관리](WORKFLOW.md#컨텍스트검증-비용-관리)를 따른다. |
| 서비스 빌드·테스트·실행 | 대상 레포의 문서·빌드 설정에서 명령을 확인하고 해당 레포에서 실행한다. |
| 공통 하네스 설치·검사 | [SETUP](SETUP.md#commands) |
| 검증·코드 리뷰·보안 검토 | 필요한 경우에만 `project-verify` / `project-review` / `project-security-review` |
| 라이브러리 사용법 | 실제 설치 버전 확인 후 필요할 때 Context7 |
| 브라우저 확인 | 필요할 때 `playwright-cli`, [SETUP](SETUP.md#playwright) |
| 지난 결정·실수 | [기억 인덱스](memory/INDEX.md)에서 관련 항목만 |
| 작업 마무리·다음 세션 | `$project-handoff`, 명시적으로 전달받은 인계 파일 |

과거 검증 자료 `validation/`는 당시 기록이다. 제품 실행·검사 명령은 대상 저장소에서 확인한다.
