# 예방접종 관리

**우선 개발.** PRD `PET-02`, `D12·D18`, 요구사항정의서 C23:E28 기준. 접종 이력은 MongoDB, 접종명 기준 데이터는 MySQL에서 관리한다.

[공통 계약](README.md#공통-계약)을 함께 적용한다. 아래 경로·필드·오류 코드는 API 설계 초안이며 미정 정책은 마지막 절에서 추적한다.

## 데이터 모델

| 모델 | 필드 |
| --- | --- |
| VaccineName | `vaccineNameId:string`, `name:string` |
| VaccinationWrite | `vaccineNameId:string`, `vaccinatedOn:date`, `nextVaccinationOn:date 또는 null`, `doseNumber:integer 또는 null`, `hospitalName:string 또는 null`, `memo:string 또는 null` |
| VaccinationSummary | `vaccinationId:string`, `vaccineName:VaccineName`, `vaccinatedOn:date`, `nextVaccinationOn:date 또는 null` |
| VaccinationDetail | VaccinationSummary + `petId:string`, `doseNumber:integer 또는 null`, `hospitalName:string 또는 null`, `memo:string 또는 null`, `createdAt:timestamp`, `updatedAt:timestamp` |

접종명 선택형 입력을 우선 설계안으로 제시한다. `vaccineNameId` 대신 자유 입력을 허용할지는 D12에서 결정한다. 필수값·null 허용·접종 차수와 날짜 제한도 D12 확정 대상이다. MySQL의 `접종명.vaccine`은 응답 `name`으로 변환한다.

## 엔드포인트

### `GET /api/vaccine-names`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/vaccine-names` | 필수 | `query?` 검색 문자열 | `VaccineName[]` / 200 | 503 REFERENCE_DATA_UNAVAILABLE |

요청 예시:

```http
GET /api/vaccine-names?query=예방 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": [
    {
      "vaccineNameId": "vaccine_01",
      "name": "예방접종"
    }
  ]
}
```

### `GET /api/pets/{petId}/vaccinations`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/pets/{petId}/vaccinations` | 필수 | 경로 petId, `page,size` | `Page<VaccinationSummary>` / 200 | 404 NOT_FOUND |

요청 예시:

```http
GET /api/pets/pet_01/vaccinations?page=0&size=20 HTTP/1.1
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

### `GET /api/pets/{petId}/vaccinations/{vaccinationId}`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/pets/{petId}/vaccinations/{vaccinationId}` | 필수 | 경로 식별자 | `VaccinationDetail` / 200 | 404 NOT_FOUND |

요청 예시:

```http
GET /api/pets/pet_01/vaccinations/vaccination_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "vaccinationId": "vaccination_01",
    "vaccineName": {
      "vaccineNameId": "vaccine_01",
      "name": "예방접종"
    },
    "vaccinatedOn": "2026-11-19",
    "nextVaccinationOn": null,
    "petId": "pet_01",
    "doseNumber": null,
    "hospitalName": null,
    "memo": null,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `POST /api/pets/{petId}/vaccinations`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `POST /api/pets/{petId}/vaccinations` | 필수 | JSON `VaccinationWrite` | `VaccinationDetail` / 201 | 400 VALIDATION_ERROR, 404 VACCINE_NAME_NOT_FOUND |

요청 예시:

```http
POST /api/pets/pet_01/vaccinations HTTP/1.1
Authorization: Bearer <액세스 토큰>
Idempotency-Key: <요청별 고유 키>
Content-Type: application/json

{
  "vaccineNameId": "vaccine_01",
  "vaccinatedOn": "2026-11-19",
  "nextVaccinationOn": null,
  "doseNumber": null,
  "hospitalName": null,
  "memo": null
}
```

응답 예시 (`201`):

```json
{
  "data": {
    "vaccinationId": "vaccination_01",
    "vaccineName": {
      "vaccineNameId": "vaccine_01",
      "name": "예방접종"
    },
    "vaccinatedOn": "2026-11-19",
    "nextVaccinationOn": null,
    "petId": "pet_01",
    "doseNumber": null,
    "hospitalName": null,
    "memo": null,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `PATCH /api/pets/{petId}/vaccinations/{vaccinationId}`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `PATCH /api/pets/{petId}/vaccinations/{vaccinationId}` | 필수 | JSON VaccinationWrite의 변경 필드 | `VaccinationDetail` / 200 | 400 EMPTY_UPDATE, 404 NOT_FOUND |

요청 예시:

```http
PATCH /api/pets/pet_01/vaccinations/vaccination_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
Content-Type: application/json

{
  "memo": "접종 메모"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "vaccinationId": "vaccination_01",
    "vaccineName": {
      "vaccineNameId": "vaccine_01",
      "name": "예방접종"
    },
    "vaccinatedOn": "2026-11-19",
    "nextVaccinationOn": null,
    "petId": "pet_01",
    "doseNumber": null,
    "hospitalName": null,
    "memo": null,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `DELETE /api/pets/{petId}/vaccinations/{vaccinationId}`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `DELETE /api/pets/{petId}/vaccinations/{vaccinationId}` | 필수 | 경로 식별자 | 본문 없음 / 204 | 404 NOT_FOUND |

요청 예시:

```http
DELETE /api/pets/pet_01/vaccinations/vaccination_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답: `204`, 본문 없음.


## 처리 규칙

- 반려동물 선택 목록은 `GET /api/pets`를 사용한다. 모든 접종 경로는 먼저 동물의 현재 소유권과 삭제 상태를 확인한다.
- 이력의 실제 `petId`가 경로와 다르면 404다. 다른 동물의 이력 ID를 경로에 끼워 넣어 변경할 수 없다.
- MongoDB 이력 저장 시 MySQL 접종명이 존재하는지 애플리케이션에서 확인한다. 저장소 간 FK로 표현하지 않는다. 기준 데이터 조회 장애는 잘못된 접종명 404와 구분하여 503으로 반환한다.
- 생성·수정 값이 목록·상세에 일치해야 한다. 삭제는 소프트 삭제이며 삭제된 이력의 직접 조회·수정을 차단한다.
- 다음 예정일의 저장은 리마인드 알림 생성 계약을 추가하지 않는다. 현재 알림 범위는 [알림 명세](notifications.md)를 따른다.

## 구현 전 확인

- D12 — 접종명 선택/직접 입력, 항목별 필수값, 차수 범위, 날짜 관계, 다음 예정일 미정 처리.
- D18 — MongoDB 이력과 MySQL 접종명 연결, 접종명 변경 시 이력의 표시명 보존 방식.
