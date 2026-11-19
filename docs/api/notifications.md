# API 계약 — 알림

[PRD](../prd.md)의 NTF-01·COM-03, D15, Q24·Q26과 요구사항정의서 67~75행을 반영한 설계 초안이다. [공통 계약](README.md)을 적용한다. 시트 71행의 상담 알림은 미정이므로 아래 생성 유형에 포함하지 않는다.

## 요청·응답 모델

- `Notification`은 `{notificationId:string,type:string,content:string,createdAt:string,read:boolean,readAt:string|null,target:NotificationTarget|null}`이다.
- `type`의 초안 값은 `COMMENT`, `REPLY`, `FOLLOW`다. `content`는 사용자에게 표시할 내용이며 길이·문구 형식은 상세 설계에서 정한다.
- `NotificationTarget`은 `{type:string,id:string}`으로, 이동할 대상의 종류와 문자열 ID를 담는다. 대상이 없거나 연결할 수 없으면 `null`이다. 대상 콘텐츠 조회 시에는 해당 콘텐츠의 현재 접근 권한을 별도로 검사한다.
- `createdAt`, `readAt`, `processedAt`, `occurredAt`은 오프셋이 포함된 ISO 8601 시각이다. 미읽음은 `read:false`, `readAt:null`이며 읽음은 `read:true`와 최초 읽음 시각을 반환한다.
- `UnreadCount`는 `{unreadCount:integer}`이며 수는 0 이상이다.
- `ReadAllResult`는 `{readCount:integer,unreadCount:integer,processedAt:string}`이다. `readCount`는 이번 처리에서 새로 읽음 처리한 건수, `processedAt`은 처리 완료 시각이다. `unreadCount`는 처리 후 조회 시점의 미읽음 수다.
- 목록은 `page`, `size` 쿼리와 `Page<Notification>` 응답을 사용한다. 응답 필드는 `{content:Notification[],page:integer,size:integer,totalElements:integer,totalPages:integer,hasNext:boolean}`이며 기본값·허용 범위는 미정이다.
- JSON 성공은 `{"data":...}`, 오류는 `{"code":"...","message":"..."}` 형식이다. 스트림의 이벤트 형식은 아래 별도 제안을 따른다.

## 엔드포인트

모든 API는 Bearer 액세스 토큰으로 로그인한 본인만 사용한다. 수신자를 지정하는 입력은 받지 않는다.

| 요청 | 인증 | 입력 | 성공 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `GET /api/notifications` | 로그인 | 쿼리 `page`, `size` | 200 `Page<Notification>` | 400 `VALIDATION_ERROR`, 401 `UNAUTHORIZED` | NTF-01, 시트 67행 |
| `GET /api/notifications/unread-count` | 로그인 | 없음 | 200 `UnreadCount` | 401 `UNAUTHORIZED` | NTF-01, 시트 68행 |
| `PATCH /api/notifications/{notificationId}/read` | 로그인 | 문자열 경로 ID, 본문 없음 | 200 `Notification` | 401 `UNAUTHORIZED`, 404 `NOT_FOUND` | NTF-01, 시트 75행 |
| `POST /api/notifications/read-all` | 로그인 | 본문 없음 | 200 `ReadAllResult` | 401 `UNAUTHORIZED` | NTF-01, 시트 75행 |
| `GET /api/notifications/stream` | 로그인 | SSE 재연결 시 `Last-Event-ID` 선택 | 200 `text/event-stream` 제안 | 연결 전 401 `UNAUTHORIZED`, 503 `NOTIFICATION_STREAM_UNAVAILABLE` | NTF-01, 시트 73행, D15 |

## 생성·조회·읽음 처리

- 알림은 서버가 댓글·대댓글·팔로우 도메인 이벤트로 생성한다. 클라이언트에서 수신자·내용을 지정하는 생성 API를 제공하지 않는다.
- 댓글 생성은 게시글 작성자에게 전달하고 본인 댓글이면 만들지 않는다. 대댓글은 직접 답글을 단 댓글 작성자에게만 전달한다. 팔로우는 상대에게 전달하고 언팔로우는 전달하지 않는다.
- 같은 이벤트를 재수신해도 같은 수신자에게 알림은 한 건이다. 중복 방지 키와 원인 이벤트의 관계를 보존하여 전달 실패 후 재처리할 수 있어야 한다. 세부 키·보관 기준은 D15에서 확정한다.
- 목록은 생성일시 최신순으로 반환한다. 같은 시각의 순서를 안정적으로 유지할 보조 정렬 기준은 상세 설계에서 정한다. 비어 있으면 200과 빈 `content`를 반환하며 화면은 “알림이 없습니다.”를 표시한다.
- 미읽음 수가 0이면 화면의 숫자를 숨긴다. 목록과 수는 본인 알림의 실제 읽음 상태를 기준으로 계산한다.
- 알림 선택 시 개별 읽음 API를 호출한다. 이미 읽은 알림은 기존 읽음 상태·최초 `readAt`을 그대로 반환한다. 타인 ID와 없는 ID는 모두 404 `NOT_FOUND`다.
- 모두 읽음은 처리 시작 시점에 확정한 본인의 미읽음 알림 집합을 읽음 처리하는 계약을 제안한다. 처리 중 새로 생성된 알림은 그 집합에 포함하지 않는다. 이미 읽은 항목을 다시 집계하지 않으며 추가 미읽음이 없으면 `readCount`는 0이다.
- 모두 읽음 응답의 미읽음 수는 새 알림 때문에 0보다 클 수 있다. 통신 실패 후 다시 호출하면 새 요청 시작 시점의 집합을 대상으로 하므로 먼저 목록·수를 재조회하여 화면 상태를 확인한다.
- 읽음 저장 실패 시 성공으로 표시하지 않는다. 재조회로 실제 반영 여부를 확인하고 안전하게 재시도한다.

## 실시간 수신 제안

D15의 채널이 미정이므로 SSE를 설계안으로 제시한다. Bearer 헤더를 전달할 수 있는 스트림 클라이언트를 사용하고 액세스 토큰을 URL 쿼리에 넣지 않는다.

각 이벤트 JSON은 `{id:string,type:string,occurredAt:string,data:{unreadCount:integer}}`로 제안한다. `id`는 불투명 이벤트 식별자이며 SSE `id`와 일치한다. 이벤트 유형 `UNREAD_COUNT_CHANGED`는 새 알림 생성·읽음 처리로 미읽음 수가 바뀔 때의 현재 수를 전달한다. 클라이언트는 숫자를 임의 증감하는 대신 전달받은 수로 갱신한다.

```text
id: opaque-event-id
event: UNREAD_COUNT_CHANGED
data: {"id":"opaque-event-id","type":"UNREAD_COUNT_CHANGED","occurredAt":"2026-11-19T10:00:00+09:00","data":{"unreadCount":3}}
```

- 본인 수신자 스트림만 구독할 수 있다. 연결 후 인증이 만료되거나 연결이 실패하면 재인증·재연결하고 목록과 미읽음 수를 재조회한다.
- 이벤트 재전달 시 같은 `id`는 중복 적용하지 않는다. 재연결 시 `Last-Event-ID`를 보낼 수 있으나 이벤트 재생 지원·보관 범위는 미정이다. 전달 누락 복구를 스트림에만 의존하지 않고 재연결 후 두 조회 API로 동기화한다.
- 새 알림과 읽음 이벤트가 경합해도 전송 순서가 뒤집혀 이전 수가 최신 수를 덮어쓰지 않도록 해야 한다. 구체적인 순서 보장·버전 기준은 D15에서 정한다.
- 스트림 전송이 이미 시작된 뒤의 실패는 새 JSON HTTP 오류로 바꾸지 않고 연결 종료로 알린다. 화면은 재연결 상태를 표시하고 일반 조회로 현재 상태를 확인한다.

## 미정 항목

- 자기 댓글에 단 대댓글의 알림 여부, 재팔로우 이벤트 식별, 중복 방지 키·보관, 알림 목록 페이지 기본값·범위는 확정이 필요하다.
- SSE 채택 여부, 인증 만료·재연결·이벤트 재생·보관·순서 보장과 연결 유지 방식은 D15에서 결정한다.
- 알림 선택 시 이동 대상과 조회 불가 대상의 안내 문구는 화면 상세 설계에서 정한다. 읽음 처리 자체가 원본 콘텐츠 접근 권한을 부여하지 않는다.
