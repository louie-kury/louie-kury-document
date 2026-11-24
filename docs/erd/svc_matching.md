# svc_matching ERD

[전체 ERD 목록](../erd.md)


## 테이블 구조

컬럼 타입은 기본 타입으로 표시한다. 길이·NULL 허용·기본값과 복합 인덱스는 아래 상세 표를 따른다. 관계선은 참조 대상이 확인된 외래키이며, 필수 여부와 유일성은 모델의 컬럼과 인덱스를 기준으로 표시한다.

```mermaid
erDiagram
    consultation_request {
        BIGINT id PK
        CHAR uuid
        CHAR caregiver_uuid
        CHAR pet_uuid
        CHAR medical_subject_uuid
        VARCHAR channel
        TINYINT is_emergency
        VARCHAR status
        DECIMAL origin_lat
        DECIMAL origin_lng
        VARCHAR geohash
        VARCHAR region
        VARCHAR si
        VARCHAR gu
        INT search_radius_m
        VARCHAR symptom_memo
        DATETIME requested_at
        DATETIME expire_at
        CHAR assigned_vet_uuid
        CHAR assigned_hospital_uuid
        DATETIME assigned_at
    }
    match_offer {
        BIGINT id PK
        CHAR uuid
        BIGINT request_id FK
        BIGINT wave_id
        CHAR vet_uuid
        CHAR hospital_uuid
        INT distance_m
        DECIMAL score
        VARCHAR status
        DATETIME offered_at
        DATETIME respond_by
        DATETIME responded_at
    }
    match_wave {
        BIGINT id PK
        CHAR uuid
        BIGINT request_id FK
        INT wave_no
        INT radius_m
        DATETIME started_at
        DATETIME finished_at
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
    request_symptom {
        BIGINT request_id PK,FK
        CHAR symptom_uuid PK
    }
    consultation_request ||--o{ match_offer : "request_id"
    consultation_request ||--o{ match_wave : "request_id"
    consultation_request ||--o{ request_symptom : "request_id"
```

#### `svc_matching.consultation_request`

보호자 호출. 택시 호출에 해당. 실시간 후보 검색은 Mongo 2dsphere

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | NOT NULL | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | NOT NULL | — | — |
| `caregiver_uuid` | `CHAR(36)` | NOT NULL | — | — |
| `pet_uuid` | `CHAR(36)` | NOT NULL | — | — |
| `medical_subject_uuid` | `CHAR(36)` | NOT NULL | — | — |
| `channel` | `VARCHAR(20)` | NOT NULL | — | — |
| `is_emergency` | `TINYINT(1)` | NOT NULL | — | — |
| `status` | `VARCHAR(20)` | NOT NULL | — | — |
| `origin_lat` | `DECIMAL(9,6)` | NOT NULL | — | — |
| `origin_lng` | `DECIMAL(9,6)` | NOT NULL | — | — |
| `geohash` | `VARCHAR(12)` | NOT NULL | — | — |
| `region` | `VARCHAR(50)` | NOT NULL | — | — |
| `si` | `VARCHAR(50)` | NOT NULL | — | — |
| `gu` | `VARCHAR(50)` | NOT NULL | — | — |
| `search_radius_m` | `INT` | NOT NULL | — | — |
| `symptom_memo` | `VARCHAR(200)` | NULL | `NULL` | — |
| `requested_at` | `DATETIME` | NOT NULL | — | — |
| `expire_at` | `DATETIME` | NOT NULL | — | — |
| `assigned_vet_uuid` | `CHAR(36)` | NULL | `NULL` | — |
| `assigned_hospital_uuid` | `CHAR(36)` | NULL | `NULL` | — |
| `assigned_at` | `DATETIME` | NULL | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_request_uuid` | UNIQUE | `uuid` |
| `idx_request_status_at` | INDEX | `status`, `requested_at` |
| `idx_request_region` | INDEX | `region`, `status`, `is_emergency`, `requested_at` |
| `idx_request_caregiver` | INDEX | `caregiver_uuid`, `requested_at` |
| `idx_request_geo` | INDEX | `origin_lat`, `origin_lng` |

**외래키**

모델에 명시된 외래키가 없습니다.

#### `svc_matching.match_offer`

수의사 앱에 뜨는 콜 카드. 한 명이 수락하면 나머지는 SUPERSEDED

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | NOT NULL | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | NOT NULL | — | — |
| `request_id` | `BIGINT` | NOT NULL | — | — |
| `wave_id` | `BIGINT` | NOT NULL | — | — |
| `vet_uuid` | `CHAR(36)` | NOT NULL | — | — |
| `hospital_uuid` | `CHAR(36)` | NOT NULL | — | — |
| `distance_m` | `INT` | NOT NULL | — | — |
| `score` | `DECIMAL(6,2)` | NOT NULL | — | — |
| `status` | `VARCHAR(20)` | NOT NULL | — | — |
| `offered_at` | `DATETIME` | NOT NULL | — | — |
| `respond_by` | `DATETIME` | NOT NULL | — | — |
| `responded_at` | `DATETIME` | NULL | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_offer_uuid` | UNIQUE | `uuid` |
| `uk_offer_vet` | UNIQUE | `request_id`, `vet_uuid` |
| `idx_offer_inbox` | INDEX | `vet_uuid`, `status`, `offered_at` |
| `idx_offer_request` | INDEX | `request_id`, `status` |
| `fk_offer_wave` | INDEX | `wave_id` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_offer_request` | `request_id` | `svc_matching.consultation_request` (`id`) | 미지정 / 미지정 | — |

#### `svc_matching.match_wave`

반경을 넓혀 가며 다시 부르는 차수

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | NOT NULL | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | NOT NULL | — | — |
| `request_id` | `BIGINT` | NOT NULL | — | — |
| `wave_no` | `INT` | NOT NULL | — | — |
| `radius_m` | `INT` | NOT NULL | — | — |
| `started_at` | `DATETIME` | NOT NULL | — | — |
| `finished_at` | `DATETIME` | NULL | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_wave_uuid` | UNIQUE | `uuid` |
| `uk_wave_no` | UNIQUE | `request_id`, `wave_no` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_wave_request` | `request_id` | `svc_matching.consultation_request` (`id`) | 미지정 / 미지정 | — |

#### `svc_matching.outbox`

matching 아웃박스. 토픽 matching.request.v1, matching.offer.v1

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

#### `svc_matching.request_symptom`

호출-증상. symptom_uuid 는 care 값

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `request_id` | `BIGINT` | NOT NULL | — | — |
| `symptom_uuid` | `CHAR(36)` | NOT NULL | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `request_id`, `symptom_uuid` |
| `idx_request_symptom` | INDEX | `symptom_uuid`, `request_id` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_request_symptom_request` | `request_id` | `svc_matching.consultation_request` (`id`) | 미지정 / 미지정 | — |
