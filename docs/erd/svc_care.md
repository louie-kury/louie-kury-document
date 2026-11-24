# svc_care ERD

[전체 ERD 목록](../erd.md)


관계도는 외래키가 가리키는 방향을 화살표로 표시한다.

```mermaid
flowchart LR
    T0["svc_care.chat_room"]
    T1["svc_care.consultation"]
    T2["svc_care.consultation_participant"]
    T3["svc_care.consultation_symptom"]
    T4["svc_care.medical_subject"]
    T5["svc_care.outbox"]
    T6["svc_care.symptom"]
    T7["svc_care.video_participant"]
    T8["svc_care.video_session"]
    T9["svc_care.visit_reservation"]
    T10["svc_care.visit_reservation_symptom"]
    T11["svc_care.visit_slot"]
    T12["미확정.{35310A4A-B889-48A3-8DC5-D5BF6CB330E6}"]
    T0 -.->|"consultation_id"| T12
    T13["미확정.{8E2495E4-1751-4823-BDA8-27A70DB4B993}"]
    T1 -.->|"medical_subject_id"| T13
    T2 -->|"consultation_id"| T1
    T3 -->|"consultation_id"| T1
    T14["미확정.{08C99905-0671-4C44-9C98-803418E85AF6}"]
    T3 -.->|"symptom_id"| T14
    T15["미확정.{A115C9DB-94AB-48A6-B3A6-8090000689FD}"]
    T7 -.->|"video_session_id"| T15
    T8 -->|"consultation_id"| T1
    T16["미확정.{C676C957-9A2E-4C0B-BD2F-14A58279655D}"]
    T9 -.->|"visit_slot_id"| T16
    T9 -->|"medical_subject_id"| T4
    T10 -->|"visit_reservation_id"| T9
    T10 -->|"symptom_id"| T6
```

#### `svc_care.chat_room`

채팅 방 메타. 메시지 본문은 MongoDB chat_messages

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | 불가 | — | — |
| `consultation_id` | `BIGINT` | 불가 | — | — |
| `status` | `VARCHAR(20)` | 불가 | — | — |
| `created_at` | `DATETIME` | 불가 | — | — |
| `closed_at` | `DATETIME` | 허용 | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_chat_room_uuid` | UNIQUE | `uuid` |
| `uk_chat_room_consult` | UNIQUE | `consultation_id` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_chat_room_consult` | `consultation_id` | `미확정 {35310A4A-B889-48A3-8DC5-D5BF6CB330E6}` (`미확정 {524D29A9-4CB3-4F97-9A49-E2314011D69C}`) | 미지정 / 미지정 | — |

#### `svc_care.consultation`

실시간상담. 보호자/펫/수의사 uuid 는 값

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | 불가 | — | — |
| `request_uuid` | `CHAR(36)` | 허용 | `NULL` | matching 호출 uuid |
| `caregiver_uuid` | `CHAR(36)` | 불가 | — | — |
| `pet_uuid` | `CHAR(36)` | 불가 | — | — |
| `vet_uuid` | `CHAR(36)` | 허용 | `NULL` | — |
| `hospital_uuid` | `CHAR(36)` | 허용 | `NULL` | 배정 병원 uuid |
| `medical_subject_id` | `BIGINT` | 불가 | — | — |
| `status` | `VARCHAR(20)` | 불가 | — | — |
| `consult_type` | `VARCHAR(20)` | 불가 | — | — |
| `is_emergency` | `TINYINT(1)` | 불가 | — | — |
| `content` | `TEXT` | 허용 | `NULL` | — |
| `clinical_note` | `TEXT` | 허용 | `NULL` | — |
| `summary` | `TEXT` | 허용 | `NULL` | — |
| `recommendation` | `VARCHAR(255)` | 허용 | `NULL` | — |
| `created_at` | `DATETIME` | 불가 | — | — |
| `accepted_at` | `DATETIME` | 허용 | `NULL` | — |
| `completed_at` | `DATETIME` | 허용 | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_consultation_uuid` | UNIQUE | `uuid` |
| `idx_consult_status_created` | INDEX | `status`, `created_at` |
| `idx_consult_vet_status` | INDEX | `vet_uuid`, `status`, `created_at` |
| `idx_consult_caregiver_created` | INDEX | `caregiver_uuid`, `created_at` |
| `idx_consult_pet_created` | INDEX | `pet_uuid`, `created_at` |
| `idx_consult_emergency_status` | INDEX | `is_emergency`, `status`, `created_at` |
| `fk_consult_subject` | INDEX | `medical_subject_id` |
| `idx_consult_request` | INDEX | `request_uuid` |
| `idx_consult_hospital` | INDEX | `hospital_uuid`, `status` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_consult_subject` | `medical_subject_id` | `미확정 {8E2495E4-1751-4823-BDA8-27A70DB4B993}` (`미확정 {85FE6F3C-6376-4541-A09B-134FC223F632}`) | 미지정 / 미지정 | — |

#### `svc_care.consultation_participant`

상담 참여자 중계

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `consultation_id` | `BIGINT` | 불가 | — | — |
| `participant_uuid` | `CHAR(36)` | 불가 | — | — |
| `participant_role` | `VARCHAR(20)` | 불가 | — | — |
| `joined_at` | `DATETIME` | 불가 | — | — |
| `left_at` | `DATETIME` | 허용 | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `consultation_id`, `participant_uuid` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_participant_consult` | `consultation_id` | `svc_care.consultation` (`id`) | 미지정 / 미지정 | — |

#### `svc_care.consultation_symptom`

상담-증상 N:M

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | 불가 | — | — |
| `consultation_id` | `BIGINT` | 불가 | — | — |
| `symptom_id` | `BIGINT` | 불가 | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_consult_symptom_uuid` | UNIQUE | `uuid` |
| `uk_consult_symptom_pair` | UNIQUE | `consultation_id`, `symptom_id` |
| `idx_consult_symptom_symptom` | INDEX | `symptom_id`, `consultation_id` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_consult_symptom_consult` | `consultation_id` | `svc_care.consultation` (`id`) | 미지정 / 미지정 | — |
| `fk_consult_symptom_symptom` | `symptom_id` | `미확정 {08C99905-0671-4C44-9C98-803418E85AF6}` (`미확정 {F4F931DA-9AD8-474E-9A5B-CC97BEA7C9C4}`) | 미지정 / 미지정 | — |

#### `svc_care.medical_subject`

진료과목

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | 불가 | — | — |
| `name` | `VARCHAR(100)` | 불가 | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_subject_uuid` | UNIQUE | `uuid` |
| `uk_subject_name` | UNIQUE | `name` |

**외래키**

모델에 명시된 외래키가 없습니다.

#### `svc_care.outbox`

care 트랜잭셔널 아웃박스

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

#### `svc_care.symptom`

증상 카탈로그

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | 불가 | — | — |
| `name` | `VARCHAR(100)` | 불가 | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_symptom_uuid` | UNIQUE | `uuid` |
| `uk_symptom_name` | UNIQUE | `name` |

**외래키**

모델에 명시된 외래키가 없습니다.

#### `svc_care.video_participant`

화상 참여자

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `video_session_id` | `BIGINT` | 불가 | — | — |
| `participant_uuid` | `CHAR(36)` | 불가 | — | — |
| `participant_role` | `VARCHAR(20)` | 불가 | — | — |
| `joined_at` | `DATETIME` | 허용 | `NULL` | — |
| `left_at` | `DATETIME` | 허용 | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_video_participant` | UNIQUE | `video_session_id`, `participant_uuid` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_video_participant_session` | `video_session_id` | `미확정 {A115C9DB-94AB-48A6-B3A6-8090000689FD}` (`미확정 {1D6F0B57-73A1-41B9-A18D-1CA6FEEAF253}`) | 미지정 / 미지정 | — |

#### `svc_care.video_session`

화상 방 메타. 입장 품질 로그는 MongoDB video_events

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | 불가 | — | — |
| `consultation_id` | `BIGINT` | 불가 | — | — |
| `provider` | `VARCHAR(20)` | 불가 | — | — |
| `room_key` | `VARCHAR(80)` | 불가 | — | — |
| `status` | `VARCHAR(20)` | 불가 | — | — |
| `started_at` | `DATETIME` | 허용 | `NULL` | — |
| `ended_at` | `DATETIME` | 허용 | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_video_uuid` | UNIQUE | `uuid` |
| `uk_video_room` | UNIQUE | `room_key` |
| `idx_video_consult` | INDEX | `consultation_id`, `status` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_video_consult` | `consultation_id` | `svc_care.consultation` (`id`) | 미지정 / 미지정 | — |

#### `svc_care.visit_reservation`

내원예약. 희망 일시는 예약 값이고 슬롯은 재고 점유

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | 불가 | — | — |
| `hospital_uuid` | `CHAR(36)` | 불가 | — | — |
| `caregiver_uuid` | `CHAR(36)` | 불가 | — | — |
| `pet_uuid` | `CHAR(36)` | 불가 | — | — |
| `medical_subject_id` | `BIGINT` | 불가 | — | — |
| `visit_slot_id` | `BIGINT` | 불가 | — | — |
| `status` | `VARCHAR(20)` | 불가 | — | — |
| `hoped_visit_date` | `DATE` | 불가 | — | — |
| `hoped_start_time` | `TIME` | 불가 | — | — |
| `symptom_memo` | `VARCHAR(200)` | 허용 | `NULL` | — |
| `created_at` | `DATETIME` | 불가 | — | — |
| `accepted_at` | `DATETIME` | 허용 | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_reservation_uuid` | UNIQUE | `uuid` |
| `uk_reservation_slot` | UNIQUE | `visit_slot_id` |
| `idx_reservation_status_date` | INDEX | `status`, `hoped_visit_date`, `hospital_uuid` |
| `idx_reservation_hospital_date` | INDEX | `hospital_uuid`, `hoped_visit_date`, `status` |
| `idx_reservation_caregiver_date` | INDEX | `caregiver_uuid`, `hoped_visit_date` |
| `idx_reservation_pet_date` | INDEX | `pet_uuid`, `hoped_visit_date` |
| `fk_reservation_subject` | INDEX | `medical_subject_id` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_reservation_slot` | `visit_slot_id` | `미확정 {C676C957-9A2E-4C0B-BD2F-14A58279655D}` (`미확정 {64A39D46-270A-4489-AFA2-71F3435EF4EF}`) | 미지정 / 미지정 | — |
| `fk_reservation_subject` | `medical_subject_id` | `svc_care.medical_subject` (`id`) | 미지정 / 미지정 | — |

#### `svc_care.visit_reservation_symptom`

예약-증상 N:M

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | 불가 | — | — |
| `visit_reservation_id` | `BIGINT` | 불가 | — | — |
| `symptom_id` | `BIGINT` | 불가 | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_reservation_symptom_uuid` | UNIQUE | `uuid` |
| `uk_reservation_symptom_pair` | UNIQUE | `visit_reservation_id`, `symptom_id` |
| `idx_reservation_symptom_symptom` | INDEX | `symptom_id`, `visit_reservation_id` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_reservation_symptom_reservation` | `visit_reservation_id` | `svc_care.visit_reservation` (`id`) | 미지정 / 미지정 | — |
| `fk_reservation_symptom_symptom` | `symptom_id` | `svc_care.symptom` (`id`) | 미지정 / 미지정 | — |

#### `svc_care.visit_slot`

내원 슬롯 재고. 병원/수의사 uuid 는 clinic 값이며 FK 없음

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | 불가 | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | 불가 | — | — |
| `hospital_uuid` | `CHAR(36)` | 불가 | — | — |
| `vet_uuid` | `CHAR(36)` | 허용 | `NULL` | — |
| `vet_key` | `CHAR(36)` | 허용 | `NULL` | GENERATED ifnull(`vet_uuid`,_utf8mb4'') STORED |
| `slot_date` | `DATE` | 불가 | — | — |
| `start_time` | `TIME` | 불가 | — | — |
| `end_time` | `TIME` | 불가 | — | — |
| `status` | `VARCHAR(20)` | 불가 | — | — |
| `created_at` | `DATETIME` | 불가 | — | — |
| `updated_at` | `DATETIME` | 불가 | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_slot_uuid` | UNIQUE | `uuid` |
| `uk_slot_inventory` | UNIQUE | `hospital_uuid`, `slot_date`, `start_time`, `vet_key` |
| `idx_slot_hospital_date_status` | INDEX | `hospital_uuid`, `slot_date`, `status` |
| `idx_slot_vet_date` | INDEX | `vet_uuid`, `slot_date`, `status` |

**외래키**

모델에 명시된 외래키가 없습니다.
