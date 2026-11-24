# svc_pet ERD

[전체 ERD 목록](../erd.md)


## 테이블 구조

컬럼 타입은 기본 타입으로 표시한다. 길이·NULL 허용·기본값과 복합 인덱스는 아래 상세 표를 따른다. 관계선은 참조 대상이 확인된 외래키이며, 필수 여부와 유일성은 모델의 컬럼과 인덱스를 기준으로 표시한다.

```mermaid
erDiagram
    breed {
        BIGINT id PK
        CHAR uuid
        BIGINT species_id
        VARCHAR name
    }
    caregiver_pet {
        CHAR caregiver_uuid PK
        BIGINT pet_id PK
        DATETIME linked_at
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
    pet {
        BIGINT id PK
        CHAR uuid
        BIGINT breed_id FK
        VARCHAR name
        DATE birth_date
        DECIMAL weight_kg
        VARCHAR sex
        TINYINT is_neutered
        DATETIME neutered_at
        VARCHAR status
        DATETIME created_at
        DATETIME updated_at
        DATETIME deleted_at
    }
    pet_vaccination {
        BIGINT id PK
        CHAR uuid
        BIGINT pet_id FK
        BIGINT vaccine_id
        DATETIME evented_at
        DATETIME created_at
        DATETIME updated_at
    }
    species {
        BIGINT id PK
        CHAR uuid
        VARCHAR name
    }
    vaccine {
        BIGINT id PK
        CHAR uuid
        VARCHAR name
        DATETIME created_at
    }
    breed ||--o{ pet : "breed_id"
    pet ||--o{ pet_vaccination : "pet_id"
```

#### `svc_pet.breed`

품종

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | NOT NULL | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | NOT NULL | — | — |
| `species_id` | `BIGINT` | NOT NULL | — | — |
| `name` | `VARCHAR(50)` | NOT NULL | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_breed_uuid` | UNIQUE | `uuid` |
| `uk_breed_name` | UNIQUE | `species_id`, `name` |

**외래키**

확인된 외래키가 없습니다.

#### `svc_pet.caregiver_pet`

보호자-반려동물. caregiver_uuid 는 identity 값이며 FK 없음

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `caregiver_uuid` | `CHAR(36)` | NOT NULL | — | — |
| `pet_id` | `BIGINT` | NOT NULL | — | — |
| `linked_at` | `DATETIME` | NOT NULL | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `caregiver_uuid`, `pet_id` |
| `idx_caregiver_pet_pet` | INDEX | `pet_id` |

**외래키**

확인된 외래키가 없습니다.

#### `svc_pet.outbox`

pet 트랜잭셔널 아웃박스

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

#### `svc_pet.pet`

반려동물. 보호자 키는 중계 테이블에만 있다

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | NOT NULL | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | NOT NULL | — | — |
| `breed_id` | `BIGINT` | NOT NULL | — | — |
| `name` | `VARCHAR(50)` | NOT NULL | — | — |
| `birth_date` | `DATE` | NULL | `NULL` | — |
| `weight_kg` | `DECIMAL(5,2)` | NULL | `NULL` | — |
| `sex` | `VARCHAR(10)` | NOT NULL | — | — |
| `is_neutered` | `TINYINT(1)` | NULL | `NULL` | — |
| `neutered_at` | `DATETIME` | NULL | `NULL` | — |
| `status` | `VARCHAR(20)` | NOT NULL | — | — |
| `created_at` | `DATETIME` | NOT NULL | — | — |
| `updated_at` | `DATETIME` | NOT NULL | — | — |
| `deleted_at` | `DATETIME` | NULL | `NULL` | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_pet_uuid` | UNIQUE | `uuid` |
| `idx_pet_breed_status` | INDEX | `breed_id`, `status`, `name` |
| `idx_pet_name` | INDEX | `name` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_pet_breed` | `breed_id` | `svc_pet.breed` (`id`) | 미지정 / 미지정 | — |

#### `svc_pet.pet_vaccination`

접종 이력. 펫과 접종명의 기능 중계

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | NOT NULL | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | NOT NULL | — | — |
| `pet_id` | `BIGINT` | NOT NULL | — | — |
| `vaccine_id` | `BIGINT` | NOT NULL | — | — |
| `evented_at` | `DATETIME` | NOT NULL | — | — |
| `created_at` | `DATETIME` | NOT NULL | — | — |
| `updated_at` | `DATETIME` | NOT NULL | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_vaccination_uuid` | UNIQUE | `uuid` |
| `idx_vaccination_pet_at` | INDEX | `pet_id`, `evented_at` |
| `idx_vaccination_vaccine` | INDEX | `vaccine_id`, `evented_at` |

**외래키**

| 이름 | 컬럼 | 참조 대상 | 삭제 / 수정 규칙 | 비고 |
| --- | --- | --- | --- | --- |
| `fk_vaccination_pet` | `pet_id` | `svc_pet.pet` (`id`) | 미지정 / 미지정 | — |

#### `svc_pet.species`

종

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | NOT NULL | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | NOT NULL | — | — |
| `name` | `VARCHAR(50)` | NOT NULL | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_species_uuid` | UNIQUE | `uuid` |
| `uk_species_name` | UNIQUE | `name` |

**외래키**

모델에 명시된 외래키가 없습니다.

#### `svc_pet.vaccine`

접종 카탈로그

| 컬럼 | 타입 | NULL | 기본값 | 속성 / 주석 |
| --- | --- | --- | --- | --- |
| `id` | `BIGINT` | NOT NULL | — | AUTO_INCREMENT |
| `uuid` | `CHAR(36)` | NOT NULL | — | — |
| `name` | `VARCHAR(100)` | NOT NULL | — | — |
| `created_at` | `DATETIME` | NOT NULL | — | — |

**인덱스**

| 이름 | 종류 | 컬럼 |
| --- | --- | --- |
| `PRIMARY` | PRIMARY KEY | `id` |
| `uk_vaccine_uuid` | UNIQUE | `uuid` |
| `uk_vaccine_name` | UNIQUE | `name` |

**외래키**

모델에 명시된 외래키가 없습니다.
