# svc_platform ERD

[전체 ERD 목록](../erd.md)


## 테이블 구조

컬럼 타입은 기본 타입으로 표시한다. 길이·NULL 허용·기본값과 복합 인덱스는 아래 상세 표를 따른다. 관계선은 참조 대상이 확인된 외래키이며, 필수 여부와 유일성은 모델의 컬럼과 인덱스를 기준으로 표시한다.

```mermaid
erDiagram
    admin_audit {
        BIGINT id PK
        CHAR uuid
        CHAR admin_uuid
        VARCHAR action
        VARCHAR target_type
        CHAR target_uuid
        JSON detail
        DATETIME created_at
    }
    matching_policy {
        BIGINT id PK
        CHAR uuid
        VARCHAR name
        TINYINT active
        INT default_radius_m
        INT emergency_radius_m
        INT radius_step_m
        INT max_waves
        INT max_offers_per_wave
        INT offer_ttl_sec
        INT request_ttl_sec
        DATETIME updated_at
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
    platform_setting {
        VARCHAR setting_key PK
        JSON setting_value
        DATETIME updated_at
    }
    region {
        BIGINT id PK
        VARCHAR code
        VARCHAR name
        VARCHAR parent_code
        DECIMAL latitude
        DECIMAL longitude
    }
```

#### `svc_platform.admin_audit`

플랫폼 관리자 감사 로그

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | 불가 | — | — |
| `admin_uuid` | `CHAR(36)` | 불가 | — | — |
| `action` | `VARCHAR(80)` | 불가 | — | — |
| `target_type` | `VARCHAR(40)` | 불가 | — | — |
| `target_uuid` | `CHAR(36)` | 불가 | — | — |
| `detail` | `JSON` | 허용 | `NULL` | — |
| `created_at` | `DATETIME` | 불가 | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_audit_uuid` | UNIQUE | `uuid` |
| `idx_audit_created` | INDEX | `created_at` |
| `idx_audit_target` | INDEX | `target_type`, `target_uuid` |

**외래키**

모델에 명시된 외래키가 없습니다.

#### `svc_platform.matching_policy`

호출 반경, 제안 수, 수락 제한시간. 카카오택시의 배차 정책에 해당

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | 불가 | — | — |
| `name` | `VARCHAR(50)` | 불가 | — | — |
| `active` | `TINYINT(1)` | 불가 | — | — |
| `default_radius_m` | `INT` | 불가 | — | — |
| `emergency_radius_m` | `INT` | 불가 | — | — |
| `radius_step_m` | `INT` | 불가 | — | — |
| `max_waves` | `INT` | 불가 | — | — |
| `max_offers_per_wave` | `INT` | 불가 | — | — |
| `offer_ttl_sec` | `INT` | 불가 | — | — |
| `request_ttl_sec` | `INT` | 불가 | — | — |
| `updated_at` | `DATETIME` | 불가 | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_policy_uuid` | UNIQUE | `uuid` |
| `idx_policy_active` | INDEX | `active`, `updated_at` |

**외래키**

모델에 명시된 외래키가 없습니다.

#### `svc_platform.outbox`

platform 트랜잭셔널 아웃박스. 토픽 platform.policy.v1

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `event_id` | `CHAR(36)` | 불가 | — | — |
| `event_type` | `VARCHAR(100)` | 불가 | — | — |
| `aggregate_uuid` | `CHAR(36)` | 불가 | — | — |
| `payload` | `JSON` | 불가 | — | — |
| `occurred_at` | `DATETIME(6)` | 불가 | — | — |
| `published_at` | `DATETIME(6)` | 허용 | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_outbox_event` | UNIQUE | `event_id` |
| `idx_outbox_unpublished` | INDEX | `published_at`, `id` |

**외래키**

모델에 명시된 외래키가 없습니다.

#### `svc_platform.platform_setting`

플랫폼 운영 설정

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `setting_key` | `VARCHAR(80)` | 불가 | — | — |
| `setting_value` | `JSON` | 불가 | — | — |
| `updated_at` | `DATETIME` | 불가 | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `setting_key` |

**외래키**

모델에 명시된 외래키가 없습니다.

#### `svc_platform.region`

플랫폼 권역 코드

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `code` | `VARCHAR(20)` | 불가 | — | — |
| `name` | `VARCHAR(50)` | 불가 | — | — |
| `parent_code` | `VARCHAR(20)` | 허용 | `NULL` | — |
| `latitude` | `DECIMAL(9,6)` | 허용 | `NULL` | — |
| `longitude` | `DECIMAL(9,6)` | 허용 | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_region_code` | UNIQUE | `code` |
| `idx_region_parent` | INDEX | `parent_code`, `name` |

**외래키**

모델에 명시된 외래키가 없습니다.
