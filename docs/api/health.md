# API 계약 — 건강 기록

공통 응답 형식은 [API 명세 안내](README.md)를 참고한다.

---

### 건강 기록 목록 조회

| Method | URL | 인증 | 요청 | 성공 응답 | 오류 응답 | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| `GET` | `/api/pets/{petId}/health-records` | 보호자 본인 | `date(YYYY-MM-DD, 선택), type(선택), page, size` | `200 Page<HealthRecordSummary>` | 400 VALIDATION_ERROR, 404 NOT_FOUND | No. 18 · HLT-02 · D12 |

같은 날짜와 반려동물로 조회한 달력과 목록은 동일한 기록을 반영한다. 삭제된 기록은 목록과 페이지 집계에서 제외한다.

### 건강 기록 달력 조회

| Method | URL | 인증 | 요청 | 성공 응답 | 오류 응답 | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| `GET` | `/api/pets/{petId}/health-records/calendar` | 보호자 본인 | `month(YYYY-MM, 필수)` | `200 {"dates":["2026-11-10","2026-11-12"]}` | 400 VALIDATION_ERROR, 404 NOT_FOUND | No. 18 · HLT-02 · D12 |

삭제되지 않은 기록이 있는 날짜만 오름차순으로 반환한다. 빈 달은 dates가 빈 배열이다.

### 건강 기록 상세 조회

| Method | URL | 인증 | 요청 | 성공 응답 | 오류 응답 | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| `GET` | `/api/pets/{petId}/health-records/{recordId}` | 보호자 본인 | `petId, recordId` | `200 HealthRecord` | 404 NOT_FOUND | No. 19 · HLT-01·02 · D12 |

기록이 지정한 반려동물에 속해야 한다. 삭제된 기록의 ID로 조회하면 `404 NOT_FOUND`를 반환한다.

### 건강 기록 등록

| Method | URL | 인증 | 요청 | 성공 응답 | 오류 응답 | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| `POST` | `/api/pets/{petId}/health-records` | 보호자 본인 | `multipart/form-data. data: {"type":"WOUND","observedAt":"2026-11-12T09:00:00+09:00","details":[{"subType":null,"textValue":"왼쪽 앞발 상처","numericValue":null}]}, files(선택, 파일마다 같은 파트 이름 반복)` | `201 HealthRecord` | 400 VALIDATION_ERROR, 404 NOT_FOUND, 413 FILE_TOO_LARGE, 415 UNSUPPORTED_MEDIA_TYPE, 503 STORAGE_UNAVAILABLE | No. 20 · HLT-01·04 · D12 |

type, observedAt는 필수 초안이다. 유형별 입력값과 첨부 제한은 미정이다. 첨부는 생성한 건강 기록 ID로 기존 건강기록미디어에 연결한다.

### 건강 기록 수정

| Method | URL | 인증 | 요청 | 성공 응답 | 오류 응답 | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| `PATCH` | `/api/pets/{petId}/health-records/{recordId}` | 보호자 본인 | `multipart/form-data. data: 등록 JSON 필드 중 변경할 값과 retainedMediaIds(선택, 기존 첨부 ID 배열), files(선택, 파일마다 같은 파트 이름 반복)` | `200 HealthRecord` | 400 VALIDATION_ERROR, 404 NOT_FOUND, 413 FILE_TOO_LARGE, 415 UNSUPPORTED_MEDIA_TYPE, 503 STORAGE_UNAVAILABLE | No. 21 · HLT-01·04 · D12 |

수정 허용 범위와 수의사 공유 반영 방식(D05)은 미정이다.

`retainedMediaIds`를 생략하면 기존 첨부를 모두 유지한다. 배열을 보내면 현재 기록에 이미 연결된 ID만 지정할 수 있으며, 지정한 첨부만 유지한다. 빈 배열은 기존 첨부를 모두 해제한다. 새 `files`는 유지한 첨부에 추가한다.

### 건강 기록 삭제

| Method | URL | 인증 | 요청 | 성공 응답 | 오류 응답 | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| `DELETE` | `/api/pets/{petId}/health-records/{recordId}` | 보호자 본인 | `petId, recordId` | `204 본문 없음` | 404 NOT_FOUND | No. 22 · HLT-01·04 · D05·D12 |

`deleted_at`에 삭제 시각을 기록하고 본문·상세·첨부 원본은 보관한다. 삭제가 성공하면 보호자의 달력·목록·상세와 수의사의 상담 조회·공유 요약에서 기록과 첨부를 제외한다. 삭제된 기록이나 해당 첨부의 기존 ID·URL로 요청하면 `404 NOT_FOUND`를 반환한다. 기록과 파일의 보관 기간은 미정이다.

### 예방접종 이력 조회

| Method | URL | 인증 | 요청 | 성공 응답 | 오류 응답 | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| `GET` | `/api/pets/{petId}/vaccinations` | 보호자 본인 | `page, size` | `200 Page<Vaccination>` | 400 VALIDATION_ERROR, 404 NOT_FOUND | PRD HLT-03 · D12 |

기본 예방접종 여부는 반려동물 프로필의 별도 항목이다.

### 예방접종 이력 등록

| Method | URL | 인증 | 요청 | 성공 응답 | 오류 응답 | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| `POST` | `/api/pets/{petId}/vaccinations` | 보호자 본인 | `{"vaccineNameId":1,"vaccinatedAt":"2026-11-12T09:00:00+09:00"}` | `201 Vaccination` | 400 VALIDATION_ERROR, 404 NOT_FOUND | PRD HLT-03 · D12 |

`vaccineNameId`는 접종명 목록의 정수 ID다. 필수 항목, 접종명 선택지 공급, 수정·삭제 범위는 미정이다.

### 병원 진료 이력 조회

| Method | URL | 인증 | 요청 | 성공 응답 | 오류 응답 | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| `GET` | `/api/pets/{petId}/clinic-visits` | 보호자 본인 | `page, size` | `200 Page<ClinicVisit>` | 400 VALIDATION_ERROR, 404 NOT_FOUND | PRD HLT-03 · D12 |

방문 시각을 기준으로 조회한다.

### 병원 진료 이력 등록

| Method | URL | 인증 | 요청 | 성공 응답 | 오류 응답 | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| `POST` | `/api/pets/{petId}/clinic-visits` | 보호자 본인 | `{"visitedAt":"2026-11-12T09:00:00+09:00","type":"외래","content":"정기 검진"}` | `201 ClinicVisit` | 400 VALIDATION_ERROR, 404 NOT_FOUND | PRD HLT-03 · D12 |

필수 항목과 진료 유형·수정·삭제 범위는 미정이다.

## 응답 필드와 데이터 정책

| 응답 타입 | 필드 |
|---|---|
| HealthRecordSummary | `recordId: integer`, `type: string`, `observedAt: datetime`, `summary: string?` |
| HealthRecord | HealthRecordSummary + `petId: string`, `details: Detail[]`, `media: MediaRef[]`, `createdAt: datetime`, `updatedAt: datetime` |
| Detail | `subType: string?`, `textValue: string?`, `numericValue: number?` |
| Vaccination | `vaccinationId: string`, `vaccineNameId: integer`, `vaccineName: string`, `vaccinatedAt: datetime` |
| ClinicVisit | `visitId: string`, `visitedAt: datetime`, `type: string`, `content: string` |

유형 초안은 `STOOL`(변 상태), `WOUND`, `MEDICATION`, `FOOD`, `WATER`, `VOMIT`, `ACTIVITY_CHANGE`, `WEIGHT`, `OTHER`다. 복용약에는 복용 시각이 필요하다. 복용약·활동 변화·기타는 요구사항 시트에 있으며 PRD·ERD 기존 유형에 추가 합의가 필요하다. 복용 시각이 관찰 시각과 다른 경우의 입력 구조 및 상세 유형별 단위는 D12에서 정한다.
