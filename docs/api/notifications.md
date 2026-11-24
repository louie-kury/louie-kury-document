# API 계약 — 알림

[PRD](../prd.md)의 NTF-01·COM-03, D15, Q24·Q26과 요구사항정의서 67~75행을 반영한 설계 초안이다. [공통 계약](README.md)을 적용한다. 시트 71행의 상담 알림은 미정이므로 아래 생성 유형에 포함하지 않는다.

사용자가 제공한 SQL의 `svc_notification.notification`, `svc_notification.outbox`, `vet_query.q_notification` 컬럼과 제약은 [알림 ERD](../erd/svc_notification.md)와 [조회 모델 ERD](../erd/vet_query.md)에 기록한다. `notification`은 수신자·이벤트 조합을 UNIQUE로 보장하며 현재 SQL에서 `read_at`만 NULL이다. 조회 모델의 `is_unread`는 `read_at`에서 생성된다. 후속 합의에 따라 외부 `notificationId`는 `notification.uuid`를 사용한다. 원본과 조회 모델의 동기화 방식은 미정이다.

## 요청·응답 모델

- `Notification`은 `{notificationId:string,type:string,content:string,createdAt:string,read:boolean,readAt:string|null,target:NotificationTarget|null}`이다.
- `type`의 초안 값은 `COMMENT`, `REPLY`, `FOLLOW`, `REPORT_REVIEW_COMPLETED`다. `REPORT_REVIEW_COMPLETED`는 신고 검토 완료 알림의 코드 제안이다. `content`는 사용자에게 표시할 내용이며 길이·문구 형식은 상세 설계에서 정한다.
- `NotificationTarget`은 `{type:string,id:string}`으로, 이동할 대상의 종류와 문자열 ID를 담는다. 대상이 없거나 연결할 수 없으면 `null`을 반환한다. 현재 SQL의 `target_type`, `target_uuid`는 NOT NULL이며, 후속 합의에 따라 대상이 없는 경우 두 컬럼을 함께 NULL 허용으로 변경할 예정이다. 대상 콘텐츠 조회 시에는 해당 콘텐츠의 현재 접근 권한을 별도로 검사한다.
- `createdAt`, `readAt`, `processedAt`, `occurredAt`은 오프셋이 포함된 ISO 8601 시각이다. 미읽음은 `read:false`, `readAt:null`이며 읽음은 `read:true`와 최초 읽음 시각을 반환한다.
- `UnreadCount`는 `{unreadCount:integer}`이며 수는 0 이상이다.
- `ReadAllResult`는 `{readCount:integer,unreadCount:integer,processedAt:string}`이다. `readCount`는 이번 처리에서 새로 읽음 처리한 건수, `processedAt`은 처리 완료 시각이다. `unreadCount`는 처리 후 조회 시점의 미읽음 수다.
- 목록은 `page`, `size` 쿼리와 `Page<Notification>` 응답을 사용한다. 응답 필드는 `{content:Notification[],page:integer,size:integer,totalElements:integer,totalPages:integer,hasNext:boolean}`이다. 페이지 크기는 기본 10개, 최대 50개다.
- JSON 성공은 `{"data":...}`, 오류는 `{"code":"...","message":"..."}` 형식이다. 스트림의 이벤트 형식은 아래 별도 제안을 따른다.

## 엔드포인트

모든 API는 Bearer 액세스 토큰으로 로그인한 본인만 사용한다. 수신자를 지정하는 입력은 받지 않는다.

### `GET /api/notifications`

| 요청 | 인증 | 입력 | 성공 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `GET /api/notifications` | 로그인 | 쿼리 `page`, `size` | 200 `Page<Notification>` | 400 `VALIDATION_ERROR`, 401 `UNAUTHORIZED` | NTF-01, 시트 67행 |

요청 예시:

```http
GET /api/notifications?page=0&size=20 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "content": [],
    "page": 0,
    "size": 20,
    "totalElements": 0,
    "totalPages": 0,
    "hasNext": false
  }
}
```

### `GET /api/notifications/unread-count`

| 요청 | 인증 | 입력 | 성공 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `GET /api/notifications/unread-count` | 로그인 | 없음 | 200 `UnreadCount` | 401 `UNAUTHORIZED` | NTF-01, 시트 68행 |

요청 예시:

```http
GET /api/notifications/unread-count HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "unreadCount": 1
  }
}
```

### `PATCH /api/notifications/{notificationId}/read`

| 요청 | 인증 | 입력 | 성공 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `PATCH /api/notifications/{notificationId}/read` | 로그인 | 문자열 경로 ID, 본문 없음 | 200 `Notification` | 401 `UNAUTHORIZED`, 404 `NOT_FOUND` | NTF-01, 시트 75행 |

요청 예시:

```http
PATCH /api/notifications/550e8400-e29b-41d4-a716-446655440001/read HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "notificationId": "550e8400-e29b-41d4-a716-446655440001",
    "type": "FOLLOW",
    "content": "새 팔로워가 있습니다.",
    "createdAt": "2026-11-19T10:00:00+09:00",
    "read": true,
    "readAt": "2026-11-19T10:00:00+09:00",
    "target": null
  }
}
```

### `POST /api/notifications/read-all`

| 요청 | 인증 | 입력 | 성공 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/notifications/read-all` | 로그인 | 본문 없음 | 200 `ReadAllResult` | 401 `UNAUTHORIZED` | NTF-01, 시트 75행 |

요청 예시:

```http
POST /api/notifications/read-all HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "readCount": 1,
    "unreadCount": 0,
    "processedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `GET /api/notifications/stream`

| 요청 | 인증 | 입력 | 성공 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `GET /api/notifications/stream` | 로그인 | 없음 | 200 `text/event-stream` | 연결 전 401 `UNAUTHORIZED`, 503 `NOTIFICATION_STREAM_UNAVAILABLE` | NTF-01, 시트 73행, D15 |

요청 예시:

```http
GET /api/notifications/stream HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200 text/event-stream`):

```text
id: event_01
event: UNREAD_COUNT_CHANGED
data: {"id":"event_01","type":"UNREAD_COUNT_CHANGED","occurredAt":"2026-11-19T10:00:00+09:00","data":{}}
```


## 생성·조회·읽음 처리

- 알림은 서버가 댓글·대댓글·팔로우 및 신고 검토 완료 도메인 이벤트로 생성한다. 클라이언트에서 수신자·내용을 지정하는 생성 API를 제공하지 않는다.
- 댓글 생성은 게시글 작성자에게 전달하고 본인 댓글이면 만들지 않는다. 대댓글은 직접 답글을 단 댓글 작성자에게만 전달하며 본인 대댓글은 제외한다. 팔로우와 재팔로우는 상대에게 새 알림을 전달하고 언팔로우는 전달하지 않는다.
- 신고 검토가 완료되면 신고자에게 완료 사실만 알린다. 조치 여부와 운영 메모 등 상세 처리 내용은 알림에 포함하지 않는다. 신고 결과 저장과 알림 전달 구조는 [커뮤니티·신고 명세](community.md)를 따른다.
- 같은 이벤트를 재수신해도 같은 수신자에게 알림은 한 건이다. SQL은 `(recipient_uuid, event_id)`의 유일성을 선언한다. 재팔로우는 새 이벤트로 식별한다. 이벤트 ID 발급 방식은 구체화한다.
- 목록은 생성일시 최신순으로 반환한다. 같은 시각의 순서를 안정적으로 유지할 보조 정렬 기준은 상세 설계에서 정한다. 비어 있으면 200과 빈 `content`를 반환하며 화면은 “알림이 없습니다.”를 표시한다.
- 미읽음 수가 0이면 화면의 숫자를 숨긴다. 목록과 수는 본인 알림의 실제 읽음 상태를 기준으로 계산한다.
- 알림 선택 시 개별 읽음 API를 호출한다. 이미 읽은 알림은 기존 읽음 상태·최초 `readAt`을 그대로 반환한다. 타인 ID와 없는 ID는 모두 404 `NOT_FOUND`다.
- 모두 읽음은 처리 시작 시점에 확정한 본인의 미읽음 알림 집합을 읽음 처리하는 계약을 제안한다. 처리 중 새로 생성된 알림은 그 집합에 포함하지 않는다. 이미 읽은 항목을 다시 집계하지 않으며 추가 미읽음이 없으면 `readCount`는 0이다.
- 모두 읽음 응답의 미읽음 수는 새 알림 때문에 0보다 클 수 있다. 통신 실패 후 다시 호출하면 새 요청 시작 시점의 집합을 대상으로 하므로 먼저 목록·수를 재조회하여 화면 상태를 확인한다.
- 읽음 저장 실패 시 성공으로 표시하지 않는다. 재조회로 실제 반영 여부를 확인하고 안전하게 재시도한다.
- 삭제된 대상의 알림은 유지하며 원본 접근은 현재 권한·삭제 상태를 확인한다. 읽은 알림은 읽은 날로부터 90일 후 삭제하고 미읽음 알림은 보관한다.
- 알림 outbox 전송 실패는 최초 시도 후 최대 3회 재시도하며 각 실패 후 1분·3분·7분을 기다린다. 최종 실패는 수동 재처리한다. 성공한 outbox 기록은 7일 보관한다. 이 운영 정책은 대화에서 합의했으며 SQL 자체의 제약은 아니다.

## 실시간 수신

후속 합의에 따라 SSE를 사용한다. Bearer 헤더를 전달할 수 있는 스트림 클라이언트를 사용하고 액세스 토큰을 URL 쿼리에 넣지 않는다.

이벤트 유형 `UNREAD_COUNT_CHANGED`는 미읽음 수가 바뀌었음을 알린다. 클라이언트는 신호를 받으면 미읽음 수를 재조회한다. 조회는 순차 처리하거나 최신 요청의 응답만 반영해 이전 응답이 최신 수를 덮어쓰지 않게 한다. 이벤트 JSON의 세부 필드는 미정이다.

```text
event: UNREAD_COUNT_CHANGED
data: {}
```

- 본인 수신자 스트림만 구독할 수 있다. 연결 후 인증이 만료되거나 연결이 실패하면 재인증·재연결하고 목록과 미읽음 수를 재조회한다.
- 화면 전달용 SSE 이벤트는 재전송을 위해 별도 보관하거나 재생하지 않는다. 연결 중단 동안 발생한 알림은 재연결 후 목록과 미읽음 수를 재조회해 확인한다. 서버 내부 이벤트의 전달·재처리는 outbox 정책을 따른다.
- 스트림 전송이 이미 시작된 뒤의 실패는 새 JSON HTTP 오류로 바꾸지 않고 연결 종료로 알린다. 화면은 재연결 상태를 표시하고 일반 조회로 현재 상태를 확인한다.

## 미정 항목

- 이벤트 ID 발급 방식, 원본과 조회 모델의 동기화 방식은 구체화한다.
- SSE 인증 만료 처리, 연결 유지 및 이벤트 필드의 구체 계약은 D15에서 결정한다.
- 알림 선택 시 이동 대상과 조회 불가 대상의 안내 문구는 화면 상세 설계에서 정한다. 읽음 처리 자체가 원본 콘텐츠 접근 권한을 부여하지 않는다.
