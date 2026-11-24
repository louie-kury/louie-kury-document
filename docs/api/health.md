# 건강 기록·병원진료 API

**후순위 설계 초안**이다. [PRD](../prd.md)의 `HLT-01`~`HLT-04`, `PET-03`과 요구사항정의서의 `(필수3)요구사항정의서` 29~33행·37~41행을 따른다. 건강 기록·진료 이력은 MongoDB에 저장한다. 요청 경로·모델 이름은 이번 API 설계안이며 필수값·단위·범위는 `D12` 확정 후 검증 규칙에 반영한다.

[공통 계약](README.md)을 적용한다. 아래 JSON은 성공 응답의 `data`다. `Page<T>`는 공통 목록 모델이며 모든 ID는 문자열이다.

## 데이터 모델

| 모델 | 필드 |
| --- | --- |
| HealthRecordInput | `type:string`, `observedAt:datetime`, `details:HealthDetails`, `mediaIds:string[]` |
| HealthRecordItem | `recordId:string`, `petId:string`, `type:string`, `observedAt:datetime`, `summary:string`, `media:MediaRef[]` |
| HealthRecordDetail | HealthRecordItem + `details:HealthDetails`, `createdAt:datetime`, `updatedAt:datetime` |
| HealthCalendarDay | `date:date`, `recordCount:integer` |
| VisitInput | `visitedAt:date`, `hospitalName:string`, `category:string`, `reason:string`, `diagnosis:string`, `treatment:string`, `medicationInstructions:string`, `cost:decimal`, `nextVisitDate:date?`, `memo:string` |
| VisitItem | `visitId:string`, `petId:string`, `visitedAt:date`, `hospitalName:string`, `category:string` |
| VisitDetail | VisitItem + `reason:string?`, `diagnosis:string?`, `treatment:string?`, `medicationInstructions:string?`, `cost:decimal?`, `nextVisitDate:date?`, `memo:string?`, `createdAt:datetime`, `updatedAt:datetime` |

입력 모델 표는 **입력 후보 필드 전체**를 나열한다. 공통 선택 표기와 별도로 HealthRecordInput·VisitInput의 필드별 필수성·NULL 허용은 `D12` 미정이다. PATCH는 변경 필드만 보내며 누락은 유지한다. 허용된 필드의 명시적 NULL 해제 규칙도 `D12`에서 정한다. 수정 요청의 `petId` 변경은 받지 않으며 대상은 경로로 결정한다.

건강 유형의 기술 코드 초안은 다음과 같다. 제품 요구의 확정 범위와 각 유형의 상세 입력을 구분한다.

| type 초안 | 제품 유형 | HealthDetails의 입력 후보 |
| --- | --- | --- |
| STOOL | 변 상태 | `shape:string?`, `color:string?`, `memo:string?` |
| WOUND | 상처 | `location:string?`, `memo:string?` |
| MEDICATION | 복용약 | `name:string?`, `takenAt:datetime?`, `amount:decimal?`, `unit:string?`, `memo:string?` |
| MEAL_WATER | 식사·음수 | `kind:string?`, `amount:decimal?`, `unit:string?`, `memo:string?` |
| VOMIT | 구토 | `color:string?`, `memo:string?` |
| ACTIVITY | 활동 변화 | `memo:string?` |
| WEIGHT | 체중 | `value:decimal?`, `unit:string?` |
| OTHER | 기타 | `memo:string?` |

상세 필드·코드·단위는 설계 후보이며 아직 입력 범위가 확정된 enum이 아니다. 복용 시각과 관찰 시각, 서버 작성 시각은 구분한다. 진료비 `cost`의 통화 단위·음수/0 허용도 `D12`에서 확정한다.

## 엔드포인트

모든 API는 Bearer 인증이 필요하다. `{petId}`는 로그인 사용자의 현재 관리 대상 반려동물이어야 한다.

### `GET /api/pets/{petId}/health-records`

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 건강 기록 목록 | `GET /api/pets/{petId}/health-records` | Query `date?:date`, `type?:string`, `page`, `size` | `Page<HealthRecordItem>`, 200 | 400 VALIDATION_ERROR, 404 NOT_FOUND | HLT-02 |

요청 예시:

```http
GET /api/pets/pet_01/health-records?page=0&size=20 HTTP/1.1
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

### `GET /api/pets/{petId}/health-records/calendar`

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 달력 표시 | `GET /api/pets/{petId}/health-records/calendar` | Query `month:YYYY-MM` | `{"month":"2026-11","days":[{"date":"2026-11-19","recordCount":2}]}`, 200 | 400 VALIDATION_ERROR, 404 NOT_FOUND | HLT-02 |

요청 예시:

```http
GET /api/pets/pet_01/health-records/calendar?month=2026-11 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "month": "2026-11",
    "days": [
      {
        "date": "2026-11-19",
        "recordCount": 2
      }
    ]
  }
}
```

### `GET /api/pets/{petId}/health-records/{recordId}`

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 건강 기록 상세 | `GET /api/pets/{petId}/health-records/{recordId}` | 없음 | `HealthRecordDetail`, 200 | 404 NOT_FOUND | HLT-01 |

요청 예시:

```http
GET /api/pets/pet_01/health-records/record_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "recordId": "record_01",
    "petId": "pet_01",
    "type": "OTHER",
    "observedAt": "2026-11-19T10:00:00+09:00",
    "summary": "메모",
    "media": [],
    "details": {
      "memo": "메모"
    },
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `POST /api/pets/{petId}/health-records`

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 건강 기록 추가 | `POST /api/pets/{petId}/health-records` | Body `HealthRecordInput` | `HealthRecordDetail`, 201 | 400 VALIDATION_ERROR, 404 NOT_FOUND, 409 MEDIA_NOT_READY | HLT-01·HLT-04 |

요청 예시:

```http
POST /api/pets/pet_01/health-records HTTP/1.1
Authorization: Bearer <액세스 토큰>
Idempotency-Key: <요청별 고유 키>
Content-Type: application/json

{
  "type": "OTHER",
  "observedAt": "2026-11-19T10:00:00+09:00",
  "details": {
    "memo": "메모"
  },
  "mediaIds": []
}
```

응답 예시 (`201`):

```json
{
  "data": {
    "recordId": "record_01",
    "petId": "pet_01",
    "type": "OTHER",
    "observedAt": "2026-11-19T10:00:00+09:00",
    "summary": "메모",
    "media": [],
    "details": {
      "memo": "메모"
    },
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `PATCH /api/pets/{petId}/health-records/{recordId}`

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 건강 기록 수정 | `PATCH /api/pets/{petId}/health-records/{recordId}` | Body 변경할 HealthRecordInput 필드 | `HealthRecordDetail`, 200 | 400 VALIDATION_ERROR, 404 NOT_FOUND, 409 MEDIA_NOT_READY | HLT-01·HLT-04 |

요청 예시:

```http
PATCH /api/pets/pet_01/health-records/record_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
Content-Type: application/json

{
  "details": {
    "memo": "메모"
  }
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "recordId": "record_01",
    "petId": "pet_01",
    "type": "OTHER",
    "observedAt": "2026-11-19T10:00:00+09:00",
    "summary": "메모",
    "media": [],
    "details": {
      "memo": "메모"
    },
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `DELETE /api/pets/{petId}/health-records/{recordId}`

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 건강 기록 삭제 | `DELETE /api/pets/{petId}/health-records/{recordId}` | 없음 | 본문 없음, 204 | 404 NOT_FOUND | HLT-01 |

요청 예시:

```http
DELETE /api/pets/pet_01/health-records/record_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답: `204`, 본문 없음.

### `GET /api/pets/{petId}/visits`

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 병원진료 목록 | `GET /api/pets/{petId}/visits` | Query `page`, `size` | `Page<VisitItem>`, 200 | 404 NOT_FOUND | PET-03 |

요청 예시:

```http
GET /api/pets/pet_01/visits?page=0&size=20 HTTP/1.1
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

### `GET /api/pets/{petId}/visits/{visitId}`

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 병원진료 상세 | `GET /api/pets/{petId}/visits/{visitId}` | 없음 | `VisitDetail`, 200 | 404 NOT_FOUND | PET-03 |

요청 예시:

```http
GET /api/pets/pet_01/visits/visit_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "visitId": "visit_01",
    "petId": "pet_01",
    "visitedAt": "2026-11-19",
    "hospitalName": "동물병원",
    "category": "진료",
    "reason": null,
    "diagnosis": null,
    "treatment": null,
    "medicationInstructions": null,
    "cost": null,
    "nextVisitDate": null,
    "memo": null,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `POST /api/pets/{petId}/visits`

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 병원진료 기록 추가 | `POST /api/pets/{petId}/visits` | Body `VisitInput` | `VisitDetail`, 201 | 400 VALIDATION_ERROR, 404 NOT_FOUND | PET-03 |

요청 예시:

```http
POST /api/pets/pet_01/visits HTTP/1.1
Authorization: Bearer <액세스 토큰>
Idempotency-Key: <요청별 고유 키>
Content-Type: application/json

{
  "visitedAt": "2026-11-19",
  "hospitalName": "동물병원",
  "category": "진료",
  "reason": "진료",
  "diagnosis": "진단",
  "treatment": "처치",
  "medicationInstructions": "복약 안내",
  "cost": 10000,
  "nextVisitDate": null,
  "memo": "메모"
}
```

응답 예시 (`201`):

```json
{
  "data": {
    "visitId": "visit_01",
    "petId": "pet_01",
    "visitedAt": "2026-11-19",
    "hospitalName": "동물병원",
    "category": "진료",
    "reason": null,
    "diagnosis": null,
    "treatment": null,
    "medicationInstructions": null,
    "cost": null,
    "nextVisitDate": null,
    "memo": null,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `PATCH /api/pets/{petId}/visits/{visitId}`

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 병원진료 수정 | `PATCH /api/pets/{petId}/visits/{visitId}` | Body 변경할 VisitInput 필드 | `VisitDetail`, 200 | 400 VALIDATION_ERROR, 404 NOT_FOUND | PET-03 |

요청 예시:

```http
PATCH /api/pets/pet_01/visits/visit_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
Content-Type: application/json

{
  "memo": "메모"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "visitId": "visit_01",
    "petId": "pet_01",
    "visitedAt": "2026-11-19",
    "hospitalName": "동물병원",
    "category": "진료",
    "reason": null,
    "diagnosis": null,
    "treatment": null,
    "medicationInstructions": null,
    "cost": null,
    "nextVisitDate": null,
    "memo": null,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `DELETE /api/pets/{petId}/visits/{visitId}`

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 병원진료 삭제 | `DELETE /api/pets/{petId}/visits/{visitId}` | 없음 | 본문 없음, 204 | 404 NOT_FOUND | PET-03 |

요청 예시:

```http
DELETE /api/pets/pet_01/visits/visit_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답: `204`, 본문 없음.


## 처리 규칙

- 반려동물과 각 기록의 소유권·연결 관계를 모두 검사한다. `{petId}`를 바꿔 다른 동물의 `{recordId}`·`{visitId}`를 조회하거나 수정할 수 없다. 존재하지 않음·타인 소유·삭제 상태는 404로 통일한다.
- 목록은 발생 시각 내림차순·동률 식별자 순으로 정렬하는 설계안이다. 서버는 서버 작성 시각을 별도로 기록한다. 달력은 삭제되지 않은 기록이 있는 날짜만 반환하며 빈 달은 `days:[]`다.
- 기록을 삭제하면 원본과 첨부를 보관하면서 달력·목록·상세 및 기존 공유 경로에서 제외한다. 같은 날짜에 다른 기록이 있으면 해당 날짜 표시를 유지한다.
- 미디어는 [공통 미디어](media.md)로 먼저 업로드한 식별자를 연결한다. 저장 전 존재·완료·권한을 검사하고 저장 실패 시 기존 첨부를 유지한다. 파일 직접 조회에도 원본 기록의 현재 권한·삭제 상태를 적용한다.
- 새 기록 추가 요청의 중복 처리 정책은 공통 멱등성 계약을 적용한다. 저장과 미디어 연결이 나뉘면 보상·재처리 방식을 정하여 한쪽만 성공한 상태를 복구한다.

## 구현 전 확인

- `D12` — 유형별 필수값·코드·단위·정밀도·날짜·변경 범위, 프로필 체중 연계, 같은 시각 다건 처리
- `D11`·`D19` — 반려동물 삭제에 따른 기록·파일 접근과 보관·파기, 파일 제한
- `D18` — MongoDB 문서·인덱스와 미디어 식별자 연결, 달력 날짜 경계와 조회 정렬

후순위 초안의 경로와 모델은 위 정책을 확정한 뒤 구현 계약으로 고정한다. 실제 API·MongoDB 실행 검증은 아직 수행하지 않았다.
