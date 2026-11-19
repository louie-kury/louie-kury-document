# 루이쿠리 프론트엔드 코드 컨벤션

> 상태: 팀 검토용 v1.0 · 적용 대상: `frontend` 레포지토리 · 원본 권장 위치: `document/docs/convention/FRONTEND_CODE_CONVENTION.md`

## 1. 목적과 적용 원칙

- Next.js App Router 기반 Feature-Based Architecture + TypeScript 프론트엔드의 일관성, 보안, 유지보수성을 확보한다.
- 자동으로 검사할 수 있는 규칙은 Prettier, ESLint, TypeScript 및 CI에서 강제한다.
- 이 문서는 프론트엔드 개발자와 AI 에이전트 모두의 기준이다. `frontend/AGENTS.md`에서는 이 문서를 참조한다.
- 기존 코드와 본 문서가 충돌하면 임의로 대량 수정하지 않고 팀에서 변경 범위를 합의한다.
- 미확정 설계는 임의로 확정하지 않는다.

## 2. 기술 스택 및 역할

| 영역                 | 기술                      | 사용 원칙                                                                            |
| -------------------- | ------------------------- | ------------------------------------------------------------------------------------ |
| 프레임워크           | Next.js App Router, React | Server Component 우선                                                                |
| 언어                 | TypeScript                | `strict` 활성화                                                                      |
| 스타일               | Tailwind CSS              | 디자인 토큰 및 일관된 클래스 사용                                                    |
| UI                   | shadcn/ui                 | 생성된 UI 소스는 프로젝트에서 관리                                                   |
| 아이콘               | lucide-react              | 필요한 아이콘만 named import                                                         |
| 클라이언트 전역 상태 | Zustand                   | UI 상태 등 클라이언트 상태 전용                                                      |
| 서버 데이터          | TanStack Query            | 클라이언트 캐시/동기화가 필요한 서버 데이터                                          |
| 폼                   | React Hook Form + Zod     | 입력 및 유효성 검증                                                                  |
| 인증                 | Better Auth               | Next.js 서버 내부 통합; Spring 백엔드 인증에 JWT 사용; 발급·전달·검증 상세 설계 대기 |
| HTTP                 | 기본 `fetch`              | 서버/클라이언트 API 계층에서 공통 처리                                               |
| 패키지               | npm                       | lockfile 커밋, `npm ci`로 CI 설치                                                    |
| 포맷/검사            | Prettier, ESLint          | 저장 및 PR 단계 검사                                                                 |
| 테스트               | 추후 확정                 | 도입 전에도 타입·린트·빌드 검증                                                      |

라이브러리 버전과 실제 설치 여부는 `package.json` 및 lockfile을 기준으로 한다. 도입 전인 패키지를 이미 설치된 것으로 가정하지 않는다.

## 3. 파일 및 네이밍

| 대상                | 규칙                                   | 예시                                         |
| ------------------- | -------------------------------------- | -------------------------------------------- |
| React 컴포넌트 파일 | PascalCase                             | `UserProfile.tsx`                            |
| React 컴포넌트/타입 | PascalCase                             | `UserProfile`, `UserProfileProps`            |
| 일반 파일·폴더      | kebab-case                             | `date-utils.ts`, `user-profile/`             |
| 변수·함수           | camelCase                              | `isLoading`, `getUserProfile`                |
| 커스텀 Hook         | `use` + PascalCase                     | `useUserProfile`                             |
| 불변 설정 상수      | UPPER_SNAKE_CASE                       | `MAX_UPLOAD_SIZE`                            |
| Boolean             | `is`/`has`/`can` 등                    | `isAuthenticated`                            |
| Next.js 예약 파일   | 프레임워크 규칙                        | `page.tsx`, `layout.tsx`, `route.ts`         |
| 테스트 파일         | 대상 파일명 + `.test.ts` / `.test.tsx` | `date-utils.test.ts`, `UserProfile.test.tsx` |
| 타입 전용 파일      | kebab-case + `.types.ts` (권장)        | `user-profile.types.ts`                      |

- React 컴포넌트 및 일반 모듈은 **named export**를 기본으로 한다. Next.js 예약 파일처럼 default export가 요구되는 곳은 예외로 한다.
- `const` 우선, 재할당 시 `let`, `var` 금지.
- 식별자는 영어로 명확하게 작성하고 의미 없는 축약어를 피한다.
- 테스트 도구는 미정이지만 테스트 파일 접미사는 `.test.ts(x)`로 통일한다. Next.js 예약 파일명 규칙을 우선한다.
- 타입은 우선 해당 feature 가까이에 두고, 여러 feature가 공유하는 타입만 공통 `types/`에 둔다.

```tsx
// 권장: 일반 컴포넌트
export type UserProfileProps = { displayName: string };

export function UserProfile({ displayName }: UserProfileProps) {
  return <div>{displayName}</div>;
}
```

## 4. 프로젝트 구조

```text
frontend/
├── AGENTS.md
├── src/
│   ├── app/                    # 라우팅, 레이아웃, Route Handler
│   │   └── api/                # 필요한 BFF 엔드포인트
│   ├── components/
│   │   └── ui/                 # shadcn/ui 등 공통 기초 UI
│   ├── features/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── posts/
│   │   └── follows/
│   ├── hooks/                  # 도메인에 종속되지 않는 공통 Hook
│   ├── lib/                    # 공통 유틸/클라이언트/설정
│   │   ├── auth/               # Better Auth 관련 모듈(확정 후)
│   │   └── api/                # 서버/클라이언트 API 공통 처리
│   ├── stores/                 # 여러 기능에서 쓰는 Zustand 스토어
│   ├── types/                  # 범용 공통 타입
│   └── utils/                  # 순수 함수
├── eslint.config.mjs
├── package.json
└── tsconfig.json
```

- 이 구조는 **Next.js App Router + Feature-Based Architecture**를 결합한 하이브리드 구성이다.
- `app/`은 라우팅과 화면 조합에 집중한다. 도메인 기능은 `features/<domain>/`에 배치한다.
- 도메인 전용 컴포넌트·훅·타입·API 함수는 해당 feature 내부에 둔다. 공통 사용이 확인될 때만 상위 공통 폴더로 이동한다.
- 폴더는 필요할 때 생성한다. 위 트리는 권장 예시이며 빈 디렉터리를 강제하지 않는다.
- `@/*` alias는 `src/*`를 가리키도록 `tsconfig.json`과 일치시킨다.

## 5. TypeScript 규칙

- `strict: true`를 유지한다. 암묵적인 `any`와 불필요한 타입 단언을 피한다.
- Props는 `type`을 기본으로 사용한다. 선언 병합 등 명확한 이유가 있으면 `interface`를 사용할 수 있다.
- 타입 추론이 명확한 지역 변수에는 불필요한 타입을 중복 선언하지 않는다.
- 외부 API 응답은 TypeScript 타입만으로 안전성이 보장되지 않으므로 필요한 경계에서 Zod 등으로 런타임 검증한다.
- `any`는 원칙적으로 금지한다. 불가피할 때는 범위를 최소화하고 근거를 주석 또는 PR에 남긴다. 불명확한 데이터는 `unknown`부터 시작한다.

```ts
// 비권장
function getLabel(value: any) {
  return value.name;
}

// 권장
function getLabel(value: unknown): string {
  if (
    typeof value === "object" &&
    value !== null &&
    "name" in value &&
    typeof value.name === "string"
  ) {
    return value.name;
  }
  return "알 수 없음";
}
```

## 6. React 및 Next.js

- Server Component를 기본으로 한다. 브라우저 이벤트, 상태, 브라우저 API가 필요한 작은 경계에만 `'use client'`를 선언한다.
- 초기 SSR은 Server Component의 서버 측 API 모듈에서 조회하고, 클라이언트 재조회·캐싱이 필요한 경우 TanStack Query를 사용한다. 공개 데이터도 기본적으로 서버 경유를 우선하되 승인된 Gateway 직접 호출 예외를 적용할 수 있다. 인증 필요 데이터는 기본적으로 BFF를 경유한다.
- 컴포넌트는 책임과 재사용성 기준으로 분리한다. 임의의 줄 수 기준은 두지 않는다.
- Props는 읽기 전용으로 취급하고, 불필요한 prop drilling은 피하되 과도한 전역 상태도 피한다.
- Hook 호출 규칙을 준수한다. 파생 가능한 값을 `useEffect`로 중복 저장하지 않는다.
- `loading.tsx`, `error.tsx`, `not-found.tsx` 등을 필요한 라우트에 사용한다.
- 서버 전용 코드에는 클라이언트에서 import할 수 없도록 모듈 경계를 유지한다.

```tsx
// app/posts/page.tsx: Server Component (예시)
import { getPublicPosts } from "@/features/posts/api/get-public-posts";

export default async function PostsPage() {
  const posts = await getPublicPosts();
  return (
    <div>
      {posts.map((post) => (
        <p key={post.id}>{post.title}</p>
      ))}
    </div>
  );
}
```

## 7. 상태 관리

- **로컬 UI 상태:** `useState` 등 React 기본 기능 우선.
- **여러 클라이언트 컴포넌트가 공유하는 UI 상태:** Zustand. 예: 모달, 필터 UI, 임시 선택 상태.
- **서버 원본 데이터의 조회/캐싱/재검증:** TanStack Query. 예: 클라이언트 무한 스크롤, 낙관적 업데이트, 주기적 갱신.
- **초기 서버 렌더링 데이터:** Server Component의 서버 측 조회를 우선 고려. 인증이 필요한 요청은 Next.js BFF 경유 정책을 따른다.
- 같은 서버 데이터를 Zustand와 TanStack Query에 중복 저장하지 않는다. TanStack Query 사용 시 Provider와 hydration 경계를 명확히 한다.

## 8. API 통신: BFF 우선 정책

### 8.1 기본 요청 경로

```text
Browser → Next.js (Server Component / Route Handler / Server Action)
        → Spring Cloud Gateway → Spring Microservices
```

- 인증이 필요한 Spring API 호출은 **Next.js 서버(BFF) 경유를 기본**으로 한다. 공개 데이터의 초기 SSR 역시 서버 조회를 우선하고, 클라이언트 캐싱·재검증은 TanStack Query를 사용하되 호출 대상은 기본적으로 BFF다.
- 브라우저의 동적 요청은 필요에 따라 Next.js Route Handler 등을 호출한다.
- 서버 렌더링 요청은 불필요한 자체 HTTP 우회 호출 없이 서버 API 모듈에서 Gateway로 호출할 수 있다.
- Server Action은 모든 API를 대체하는 범용 프록시로 사용하지 않고, 해당 액션의 특성과 보안 정책을 검토한다.
- Next.js 서버에서 Gateway를 호출할 때 서버 전용 URL과 자격 증명을 사용한다.
- Spring 서비스 간 호출과 Eureka 디스커버리는 백엔드 책임이다. **브라우저에서 개별 마이크로서비스 주소로 직접 호출하는 것은 금지**한다. 아래 예외는 오직 승인된 **API Gateway 공개 엔드포인트** 등에 대한 직접 호출을 뜻한다.

### 8.2 직접 호출 예외

- 공개 API, WebSocket/SSE 등 실시간 연결, 대용량 전송 등은 팀 합의 후 **브라우저 → API Gateway 직접 호출**을 예외적으로 허용할 수 있다. 개별 마이크로서비스 직접 호출은 예외에 포함되지 않는다.
- 직접 Gateway 호출 시 CORS, 인증 전달, CSRF, XSS, 요청 제한 정책을 먼저 확정한다.
- S3 파일 업로드는 서버가 발급한 **Presigned URL**로 브라우저에서 S3에 직접 업로드하는 방식을 우선 검토한다. 파일 유형·크기·키 범위·만료·권한을 서버에서 제한한다.
- 예외를 적용하더라도 Spring 각 서비스의 인가 검사를 생략하지 않는다.

### 8.3 공통 API 처리

- `fetch`를 기본 HTTP 클라이언트로 사용한다.
- 요청·응답 타입, 에러 변환, 타임아웃, 캐시 정책을 공통 API 모듈에서 일관되게 관리한다.
- **공통 응답 타입은 백엔드 실제 API 계약에 맞춰 정의한다.** 백엔드가 모든 응답을 동일한 JSON envelope으로 감싼다고 가정하지 않는다.
- HTTP 상태와 비즈니스 오류를 구분하고, 사용자 메시지와 내부 로그 메시지를 분리한다. 백엔드 계약 확정 전에는 임의의 공통 에러 객체 필드(`code`, `message` 등)를 필수로 고정하지 않는다.
- `fetch`는 HTTP 4xx/5xx에 자동으로 throw하지 않으므로 `response.ok`를 확인한다.
- 민감한 인증 헤더, 개인정보, 토큰을 오류 로그에 기록하지 않는다.

```ts
// 공통 fetch 처리의 단순 예시. 실제 구현 시 응답 계약에 맞게 확장.
export async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}
```

> 위의 제네릭 타입은 서버 응답을 검증하지 않는다. 신뢰 경계에서는 런타임 스키마 검증을 추가한다.

## 9. Better Auth 및 보안

- Better Auth는 Next.js 내 인증 모듈로 통합한다. 인증 설정과 서버 전용 비밀값을 클라이언트 코드에서 import하지 않는다.
- **확정:** Spring 백엔드 인증에는 JWT를 사용한다. **미확정:** Better Auth 세션과 백엔드용 JWT의 연계, 발급 주체, 서명·검증, 전달, 만료·갱신·로그아웃 정책. Better Auth 세션 쿠키를 JWT로 간주하지 않는다.
- 브라우저 저장소(`localStorage`, `sessionStorage`)에 민감한 토큰을 임의로 저장하지 않는다.
- 세션 쿠키의 `HttpOnly`, `Secure`, `SameSite`, CSRF 방어 정책을 배포 환경에 맞게 검토한다.
- BFF에서 세션을 확인하더라도 Gateway 및 각 마이크로서비스는 정해진 인증/인가 정책을 수행한다.
- 로그인 여부만으로 리소스 소유권, 팔로우 권한, 관리자 권한을 판정하지 않는다.
- `NEXT_PUBLIC_` 접두사 변수는 브라우저에 노출될 수 있으므로 비밀값을 넣지 않는다.
- `.env` 비밀값을 커밋하지 않고 `.env.example`에는 키 이름과 비민감 예시만 둔다.
- 서버 전용 필수 환경변수(예: `BETTER_AUTH_SECRET`, 내부 Gateway URL)는 서버 전용 검증 모듈에서 Zod 등으로 검증하고, 누락·형식 오류를 가능한 한 앱 시작 시점에 조기 발견한다. 빌드 시점에 반드시 존재해야 하는 변수와 런타임 전용 변수는 배포 방식에 맞게 구분한다.

## 10. 스타일링 및 UI

- Tailwind CSS를 기본으로 하며 공통 색상·간격·타이포그래피는 디자인 토큰을 사용한다.
- `shadcn/ui`의 기초 UI는 `components/ui/`에 두고, 도메인 조합 컴포넌트는 `features/`에 둔다.
- shadcn/ui 생성 코드는 프로젝트 소스이므로 수정할 수 있지만, 무분별한 수정 대신 wrapper/variant를 우선 검토한다.
- 동적 클래스 조합은 프로젝트에서 채택한 `cn` 유틸리티 등으로 일관되게 처리한다.
- 버튼, 입력, 모달에 접근 가능한 이름, 키보드 조작, 포커스 표시를 제공한다.
- 색상만으로 오류나 상태를 구분하지 않는다.
- 레이아웃과 콘텐츠 구조에는 `<main>`, `<nav>`, `<header>`, `<section>`, `<article>` 등 역할에 맞는 시맨틱 HTML 태그를 우선 사용한다. 의미상 적절한 시맨틱 태그가 없는 경우에는 `<div>`를 사용한다.
- 내부 페이지 이동은 `next/link`의 `Link`를 우선 사용한다. 외부 링크 및 특수 스킴(`mailto:`, `tel:` 등)은 상황에 맞게 `<a>`를 사용하며, 이벤트 처리 후 프로그래밍 방식의 이동이 필요한 경우에는 `router.push()` 또는 `router.replace()`를 사용한다. 서버에서의 리다이렉트는 Next.js의 `redirect()` 등 서버 전용 API를 사용한다.
- 페이지 이동에는 링크(Link, <a>)를 사용하고, 폼 제출이나 모달 열기 등 사용자 동작을 실행할 때는 <button>을 사용한다.

### 10.1 lucide-react

- 아이콘은 `lucide-react`를 기본으로 사용한다. 라이브러리에서 제공하는 아이콘 이름(PascalCase)을 유지한다.
- 필요한 아이콘만 named import하고 임의의 이모지로 UI 아이콘을 대체하지 않는다.
- 장식용 아이콘은 `aria-hidden="true"`를 적용한다.
- 아이콘만 있는 버튼에는 `aria-label` 등 접근 가능한 이름을 제공한다.
- 아이콘 크기·stroke 두께는 디자인 시스템 규칙을 따른다.

```tsx
import { Search, Settings } from "lucide-react";

export function Toolbar() {
  return (
    <div>
      <Search aria-hidden="true" className="size-4" />
      <button type="button" aria-label="설정 열기">
        <Settings aria-hidden="true" className="size-4" />
      </button>
    </div>
  );
}
```

## 11. 폼과 검증

- React Hook Form으로 폼 상태를 관리하고 Zod로 입력 스키마를 정의한다. `@hookform/resolvers/zod`의 `zodResolver`로 폼과 스키마를 연결한다.
- 폼 스키마와 관련 타입은 해당 `features/<domain>/` 내부에 모으고, `z.infer`(또는 Zod 버전에 맞는 `z.input`/`z.output`)를 활용해 중복 타입 선언을 줄인다. 클라이언트 검증 스키마와 서버 API 응답 스키마는 용도가 다르면 구분하되, 동일 계약을 중복 정의하지 않는다.
- 클라이언트 검증은 UX를 위한 것이며 서버에서도 필수적으로 검증한다.
- 에러 메시지는 필드와 연결하고 접근성을 고려한다.
- 인증·개인정보·업로드 관련 검증은 서버에서 다시 수행한다.

## 12. 코드 스타일과 주석

- Prettier: 작은따옴표, 세미콜론 사용, 들여쓰기 2칸, `printWidth: 100`, 후행 쉼표 `all`, LF.
- JSX 속성은 큰따옴표를 사용한다.
- import는 경로 alias를 우선하고, 순환 의존성과 사용하지 않는 import를 피한다.
- 주석과 개발 문서는 한국어, 변수·함수·타입명은 영어로 작성한다.
- 주석은 **무엇**보다 **왜**를 설명한다. 주석 처리된 죽은 코드를 남기지 않는다.
- 예외적인 린트 규칙 비활성화에는 이유를 명시한다.

권장 `.prettierrc.json`:

```json
{
  "singleQuote": true,
  "jsxSingleQuote": false,
  "semi": true,
  "tabWidth": 2,
  "printWidth": 100,
  "trailingComma": "all",
  "endOfLine": "lf"
}
```

## 13. 검증 및 CI

- 로컬과 PR CI에서 동일한 명령으로 검사한다.
- Next.js 권장 ESLint 설정과 TypeScript 권장 규칙을 적용한다. 실제 규칙과 버전은 `eslint.config.mjs` 기준이다.
- 테스트 프레임워크는 추후 선정한다. 도입 전에도 lint/typecheck/build 검증을 수행한다.
- CI에서는 `npm ci`로 의존성을 재현한다.
- CI 및 배포 파이프라인에서 필수 환경변수의 존재·형식을 검증한다. 실제 비밀값은 CI 비밀 저장소에서 주입하며 로그에 출력하지 않는다. 빌드 전용 변수와 런타임 변수를 구분해 검증한다.
- `package.json`에 다음 스크립트를 실제 설정에 맞게 준비한다.

```json
{
  "scripts": {
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "format:check": "prettier --check .",
    "build": "next build"
  }
}
```

권장 검증 순서: `npm run format:check` → `npm run lint` → `npm run typecheck` → `npm run build`. 테스트 도입 후 테스트 명령을 추가한다.

- 코드 리뷰 전에 검사 실패를 해결한다. 실패한 검사를 통과한 것으로 보고하지 않는다.
- Git 브랜치·커밋·PR 규칙은 `document` 레포지토리의 별도 Git 컨벤션을 참조한다.

## 14. 결정 대기 항목

다음은 팀 합의 후 문서 개정이 필요하다.

1. Better Auth 세션과 Spring JWT의 연계, 발급자·검증자·전달 방식, 갱신/만료/로그아웃 정책. (프론트·백엔드·보안)
2. Spring API 응답 스키마, 오류 코드, 인증 실패 응답 계약. (백엔드·프론트)
3. 브라우저 → Gateway 직접 호출이 허용되는 구체적 엔드포인트. (프론트·백엔드·인프라)
4. S3 업로드 허용 확장자/MIME 타입, 크기 제한, Presigned URL 정책. (백엔드·인프라·프론트)
5. 테스트 프레임워크 및 커버리지 기준. (프론트·QA)
6. 디자인 토큰, 공통 UI variant, 아이콘 기본 크기. (디자인·프론트)
7. CI 플랫폼 및 브랜치 보호 규칙. (인프라·프론트)

## 15. 문서 관리

- 공식 문서는 `document/docs/convention/FRONTEND_CODE_CONVENTION.md`에서 관리한다.
- `frontend/AGENTS.md`는 공식 문서의 경로와 핵심 규칙을 명시한다. Codex 작업 공간에서 `frontend`와 `document`를 함께 열고 실제 읽기 권한을 확인한다.
- Codex가 별도 `document` 레포지토리를 읽을 수 없는 환경에서는 `frontend/docs/`에 **자동 동기화한 읽기 전용 사본**을 두거나, `AGENTS.md`에 핵심 규칙을 요약한다. 사본을 운영한다면 공식 문서만 수정하고 동기화 절차를 CI 또는 스크립트로 관리한다.
- 접근 가능 여부를 확인하지 않은 채 AI가 외부 문서를 읽었다고 가정하지 않는다.
- 코드 컨벤션 변경 시 Prettier/ESLint/CI 설정의 변경 필요 여부를 함께 검토한다.
- 대규모 포맷 수정은 기능 변경 PR과 분리한다.
