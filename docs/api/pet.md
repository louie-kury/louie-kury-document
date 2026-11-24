# 반려동물 관리

**우선 개발.** PRD `PET-01`, `MED-01`, `D11·D12·D18`, 요구사항정의서 `(필수3)` C18:H22 기준. 반려동물·소유 관계·종/품종은 MongoDB, 파일 메타데이터는 공통 미디어 저장소에서 관리한다.

[공통 계약](README.md#공통-계약)을 함께 적용한다. 아래 경로·필드·오류 코드는 API 설계 초안이며 미정 정책은 마지막 절에서 추적한다.

## 데이터 모델

| 모델 | 필드 |
| --- | --- |
| PetWrite | `name:string`, `speciesId:string`, `breedId:string 또는 null`, `profileMediaId:string 또는 null`, `birth:date 또는 null`, `sex:string`, `isNeutered:boolean 또는 null`, `weight:number 또는 null`, `basicVaccinationCompleted:boolean 또는 null` |
| PetSummary | `petId:string`, `name:string`, `species:{speciesId,name}`, `breed:{breedId,name} 또는 null`, `profileMedia:MediaRef 또는 null`, `age:Age 또는 null`, `sex:string` |
| PetDetail | PetSummary 필드 + `birth:date 또는 null`, `isNeutered:boolean 또는 null`, `weight:number 또는 null`, `basicVaccinationCompleted:boolean 또는 null`, `createdAt:timestamp`, `updatedAt:timestamp` |
| Age | `years:integer`, `months:integer`. 산정 기준은 D12 확정 후 적용 |
| Species | `speciesId:string`, `name:string`, `breeds:[{breedId:string,name:string}]` |

PetWrite는 입력 가능한 전체 필드를 나열한 것이다. 생성 시 필수 여부와 null 허용은 D12 확정 후 구현한다. `name` 등 문자열을 빈 값으로 받는 정책도 함께 정한다. `sex`의 외부 값은 `MALE`, `FEMALE` 설계안이며 원문 BOOLEAN의 실제 의미는 D18에서 확인한다. 체중 단위·정밀도·범위를 아직 고정하지 않는다.

## 엔드포인트

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/pets` | 필수 | `page,size` | `Page<PetSummary>` / 200 | 공통 오류 |
| `GET /api/pets/{petId}` | 필수 | 경로 petId | `PetDetail` / 200 | 404 NOT_FOUND |
| `POST /api/pets` | 필수 | JSON `PetWrite` | `PetDetail` / 201 | 400 VALIDATION_ERROR, 404 MEDIA_NOT_FOUND, 409 MEDIA_NOT_READY |
| `PATCH /api/pets/{petId}` | 필수 | JSON PetWrite의 변경 필드 | `PetDetail` / 200 | 400 EMPTY_UPDATE, 404 NOT_FOUND, 409 MEDIA_NOT_READY |
| `DELETE /api/pets/{petId}` | 필수 | 경로 petId | 본문 없음 / 204 | 404 NOT_FOUND, 409 PET_STATE_CONFLICT |
| `GET /api/pet-species` | 필수 | 없음 | `Species[]` / 200 | 503 REFERENCE_DATA_UNAVAILABLE |

## 처리 규칙

- 보호자는 인증된 계정에서 결정한다. 요청에 `caregiverId`를 받아 타인 동물로 저장하지 않는다. 목록은 본인 소유의 삭제되지 않은 동물만 반환한다.
- `speciesId`와 `breedId`가 일치하는지 확인한다. 종·품종 목록도 MongoDB 기준 데이터이며 접종명 MySQL과 구분한다.
- 프로필 파일은 [미디어 업로드](media.md) 후 받은 `mediaId`로 연결한다. 파일 존재·완료·소유·사용처 권한을 확인하고 부모 저장이 실패하면 기존 프로필을 유지한다.
- PATCH의 생략은 유지다. 허용된 필드의 null만 해제를 뜻한다. 응답에 요청으로 보내지 않은 타인 정보나 MongoDB 내부 문서를 그대로 노출하지 않는다.
- 삭제는 소프트 삭제다. 목록·상세·수정·기존 프로필 파일 직접 조회의 현재 접근 정책에 반영한다. 첨부 원본은 동물과 함께 보관하며 삭제된 동물의 기존 프로필 파일 접근을 차단한다.
- 생성 중복 방지는 공통 Idempotency-Key 제안을 따른다. 재시도로 동물이 여러 건 생기지 않게 한다.

## 구현 전 확인

- D12 — 생성 필수값, 생일을 모르는 경우, 나이 산식·기준일, 중성화·기본 접종 값, 체중 단위·범위, 프로필 선택 여부.
- D11 — 진행 중 상담이 있는 동물 삭제의 허용 조건과 연결 이력 보관.
- D18 — MongoDB 식별자·소유 관계·종/품종 문서 구조. 이 API의 필드가 DB 컬럼 설계를 확정하는 것은 아니다.

## 요청·응답 예시

아래 값은 형식 설명용이며 미정 정책, 제한값, 상태 전이나 실제 서버 동작을 확정하지 않는다. 인증·멱등성 등 공통 헤더는 [공통 계약](README.md#공통-계약)을 따른다. 각 예시는 별도의 상황이다.

### `GET /api/pets`

요청 예시:

```http
GET /api/pets?page=0&size=20 HTTP/1.1
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

### `GET /api/pets/{petId}`

요청 예시:

```http
GET /api/pets/pet_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "petId": "pet_01",
    "name": "루이",
    "species": {
      "speciesId": "species_01",
      "name": "개"
    },
    "breed": null,
    "profileMedia": null,
    "age": null,
    "sex": "MALE",
    "birth": null,
    "isNeutered": null,
    "weight": null,
    "basicVaccinationCompleted": null,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `POST /api/pets`

요청 예시:

```http
POST /api/pets HTTP/1.1
Authorization: Bearer <액세스 토큰>
Idempotency-Key: <요청별 고유 키>
Content-Type: application/json

{
  "name": "루이",
  "speciesId": "species_01",
  "breedId": null,
  "profileMediaId": null,
  "birth": null,
  "sex": "MALE",
  "isNeutered": null,
  "weight": null,
  "basicVaccinationCompleted": null
}
```

응답 예시 (`201`):

```json
{
  "data": {
    "petId": "pet_01",
    "name": "루이",
    "species": {
      "speciesId": "species_01",
      "name": "개"
    },
    "breed": null,
    "profileMedia": null,
    "age": null,
    "sex": "MALE",
    "birth": null,
    "isNeutered": null,
    "weight": null,
    "basicVaccinationCompleted": null,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `PATCH /api/pets/{petId}`

요청 예시:

```http
PATCH /api/pets/pet_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
Content-Type: application/json

{
  "name": "루이"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "petId": "pet_01",
    "name": "루이",
    "species": {
      "speciesId": "species_01",
      "name": "개"
    },
    "breed": null,
    "profileMedia": null,
    "age": null,
    "sex": "MALE",
    "birth": null,
    "isNeutered": null,
    "weight": null,
    "basicVaccinationCompleted": null,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `DELETE /api/pets/{petId}`

요청 예시:

```http
DELETE /api/pets/pet_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답: `204`, 본문 없음.

### `GET /api/pet-species`

요청 예시:

```http
GET /api/pet-species HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": [
    {
      "speciesId": "species_01",
      "name": "개",
      "breeds": []
    }
  ]
}
```
