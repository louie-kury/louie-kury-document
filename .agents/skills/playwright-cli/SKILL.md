---
name: playwright-cli
description: Check browser behavior and run interactive UI QA with the repository-pinned Playwright CLI.
---

# Playwright 브라우저 검사

`scripts/ai/browser.sh`와 `tools/ai/package-lock.json`이 있는 공통 문서 폴더에서 실행한다. 서비스 화면을 검사할 때는 대상 서비스가 실행 중인 로컬·테스트 URL을 사용한다.

## 설치와 실행

새 클론에서 의존성이 없거나 lock 파일이 바뀌면 설치한다.

```sh
npm ci --prefix tools/ai
sh scripts/ai/browser.sh --version
```

모든 브라우저 명령은 `sh scripts/ai/browser.sh`로 실행한다. 래퍼가 lock 파일로 고정된 CLI와 프로젝트의 격리 브라우저 설정을 사용한다. 서비스 폴더에 있다면 공통 문서 폴더로 이동하거나 래퍼의 절대 경로를 사용한다.

## 화면 확인

```sh
sh scripts/ai/browser.sh -s=my-check open about:blank
sh scripts/ai/browser.sh -s=my-check snapshot
sh scripts/ai/browser.sh -s=my-check close
```

실제 화면을 확인할 때는 `about:blank`를 확인할 주소로 바꾼다. 스냅샷의 요소 참조로 `click`이나 `fill`을 실행하고, 화면이 바뀌면 새 스냅샷을 확인한다. 검사 후 같은 세션 이름으로 브라우저를 닫는다. 브라우저에 입력할 값은 합성 데이터를 사용한다.

## 필요한 명령 찾기

- 지원 명령은 `sh scripts/ai/browser.sh --help`에서 확인한다.
- 참조 문서의 예제에서 브라우저 명령 앞의 `playwright-cli`를 `sh scripts/ai/browser.sh`로 바꿔 실행한다.
- [세션과 브라우저 설정](references/session-management.md), [요소 확인](references/element-attributes.md)
- [요청 모킹](references/request-mocking.md), [인증 상태](references/storage-state.md), [코드 실행](references/running-code.md)
- [Playwright 테스트 실행](references/playwright-tests.md), [테스트 생성](references/test-generation.md)
- [트레이스](references/tracing.md), [영상 기록](references/video-recording.md), [PR 첨부](references/pr-attachments.md)
