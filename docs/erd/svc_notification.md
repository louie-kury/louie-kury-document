# svc_notification ERD

[전체 ERD 목록](../erd.md)


## 테이블 구조

컬럼 타입은 기본 타입으로 표시한다. 길이·NULL 허용·기본값과 복합 인덱스는 아래 상세 표를 따른다. 관계선은 참조 대상이 확인된 외래키이며, 필수 여부와 유일성은 모델의 컬럼과 인덱스를 기준으로 표시한다.

```mermaid
erDiagram
    notification {
        BIGINT id PK
        CHAR uuid
        CHAR recipient_uuid
        CHAR actor_uuid
        CHAR event_id
        VARCHAR type
        VARCHAR title
        VARCHAR content
        VARCHAR target_type
        CHAR target_uuid
        DATETIME read_at
        DATETIME created_at
    }
    outbox {
        BIGINT id PK
        CHAR event_id
        VARCHAR event_type
        CHAR aggregate_uuid
        JSON payload
        DATETIME occurred_at
        DATETIME published_at
    }
```

#### `svc_notification.notification`

알림 수신함. 생산자 테이블 FK 없음. event_id 로 멱등

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | NOT NULL | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | NOT NULL | — | — |
| `recipient_uuid` | `CHAR(36)` | NOT NULL | — | — |
| `actor_uuid` | `CHAR(36)` | NOT NULL | — | — |
| `event_id` | `CHAR(36)` | NOT NULL | — | — |
| `type` | `VARCHAR(30)` | NOT NULL | — | — |
| `title` | `VARCHAR(200)` | NOT NULL | — | — |
| `content` | `VARCHAR(500)` | NOT NULL | — | — |
| `target_type` | `VARCHAR(30)` | NOT NULL | — | — |
| `target_uuid` | `CHAR(36)` | NOT NULL | — | — |
| `read_at` | `DATETIME` | NULL | `NULL` | — |
| `created_at` | `DATETIME` | NOT NULL | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_notification_uuid` | UNIQUE | `uuid` |
| `uk_notification_event` | UNIQUE | `recipient_uuid`, `event_id` |
| `idx_notification_inbox` | INDEX | `recipient_uuid`, `read_at`, `created_at` |

**외래키**

모델에 명시된 외래키가 없습니다.

#### `svc_notification.outbox`

notification 트랜잭셔널 아웃박스

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | NOT NULL | — | AUTO_INCREMENT |
| `event_id` | `CHAR(36)` | NOT NULL | — | — |
| `event_type` | `VARCHAR(100)` | NOT NULL | — | — |
| `aggregate_uuid` | `CHAR(36)` | NOT NULL | — | — |
| `payload` | `JSON` | NOT NULL | — | — |
| `occurred_at` | `DATETIME(6)` | NOT NULL | — | — |
| `published_at` | `DATETIME(6)` | NULL | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_outbox_event` | UNIQUE | `event_id` |
| `idx_outbox_unpublished` | INDEX | `published_at`, `id` |

**외래키**

모델에 명시된 외래키가 없습니다.

## 모델과 후속 정책의 차이

위 구조는 원본 모델이다. 대상 없는 알림을 허용하기로 합의했으며 `target_type`과 `target_uuid`를 함께 NULL 허용하도록 후속 변경이 필요하다. 두 값은 함께 존재하거나 함께 없어야 한다. 외부 `notificationId`는 `notification.uuid`를 사용한다. 알림 outbox 재시도·수동 재처리 및 보관을 위한 구체 상태 저장 구조는 구현 설계에서 정한다.
