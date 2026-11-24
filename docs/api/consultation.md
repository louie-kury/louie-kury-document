# 실시간 상담·일지·후기 API

**후순위 설계 초안**이다. [PRD](../prd.md)의 `CON-01`~`CON-05`, `VET-01`, `LOG-01`, `REV-01`과 요구사항정의서 `(필수3)요구사항정의서` 42~48행을 근거로 한다. 보호자는 위치 기반 매칭으로 채팅·화상 상담을 신청하고 진행·종료·이력을 확인한다.

[공통 계약](README.md)을 적용한다. 아래 모델은 성공 응답 `data`이며 모든 ID는 문자열이다. HTTP 경로·상태 코드·내부 상태의 영문 표기는 이번 설계안이다. 가용 정보·수락·상담 연결·일지의 외부 제공 계약은 `D04`~`D07`·`D17`에서 확인한다.

## 데이터 모델

| 모델 | 필드 |
| --- | --- |
| ConsultationInput | `petId:string`, `channel:CHAT 또는 VIDEO`, `symptom:string`, `mediaIds:string[]`, `location:{latitude:number,longitude:number}` |
| VeterinarianInfo | `veterinarianId:string`, `name:string`, `hospital:{hospitalId:string,name:string}`, `profileMedia:MediaRef?`, `introduction:string?`, `averageRating:number?`, `reviewCount:integer?` |
| ConsultationItem | `consultationId:string`, `pet:{petId:string,name:string}`, `veterinarian:VeterinarianInfo?`, `channel:string`, `status:string`, `requestedAt:datetime` |
| ConsultationDetail | ConsultationItem + `symptom:string`, `media:MediaRef[]`, `matchedAt:datetime?`, `startedAt:datetime?`, `endedAt:datetime?`, `durationSeconds:integer?`, `journalAvailability:string` |
| MatchingStatus | `consultationId:string`, `status:string`, `requestedAt:datetime`, `expiresAt:datetime?`, `elapsedSeconds:integer`, `veterinarian:VeterinarianInfo?` |
| Connection | `connectionId:string`, `channel:string`, `status:string`, `expiresAt:datetime?`, `access:{url:string?,token:string?}` |
| EndAcceptance | `actionId:string`, `consultationId:string`, `status:ACCEPTED`, `requestedAt:datetime` |
| JournalResult | `availability:AVAILABLE 또는 NOT_WRITTEN`, `journal:{content:string,media:MediaRef[],updatedAt:datetime}?` |
| ReviewInput | `rating:number`, `content?:string` |
| Review | `reviewId:string`, `consultationId:string`, `rating:number`, `content:string?`, `createdAt:datetime` |
| ConsultationEvent | `eventId:string`, `type:string`, `consultationId:string`, `occurredAt:datetime`, `data:object` |

- 신청의 `petId`·`channel`·`location`은 매칭을 위한 설계 입력이다. 증상·첨부의 필수 여부와 길이·개수, 위치 권한 거부 시 대체 입력은 `D05`·`D17`·`D19` 확정 후 고정한다.
- 외부 응답과 DB enum을 그대로 노출하지 않는다. 화면 상태의 코드 초안은 `MATCHING`, `MATCHED`, `CONNECTING`, `IN_PROGRESS`, `ENDED`, `COMPLETED`, `CANCELLED`, `EXPIRED`, `CONNECTION_FAILED`다. `ENDED`와 `COMPLETED`의 구분·전이 조건은 `D04`에서 정한다.
- 매칭 전 수의사·병원 정보는 `null`이다. 아직 시작·종료하지 않은 시각과 상담 시간도 `null`이며 0초로 대체하지 않는다.
- 프로필 사진·소개·평점·후기 수는 제공 범위에 따라 조회할 선택 정보다. `D16` 확정 전 해당 필드의 제공을 보장하지 않는다. 평가가 없는 경우의 평균은 `null`로 표현하는 초안이다.
- Connection의 외부 접속 정보는 채팅·화상 업체 계약에 따라 구체화한다. 임의 URL·토큰을 본문으로 받아 연결 대상으로 신뢰하지 않는다.

## 엔드포인트

모든 API는 Bearer 인증이 필요하며 로그인 사용자의 상담에 한정한다.

| 기능 | 요청 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- |
| 실시간 상담 신청 | `POST /api/consultations` | Body `ConsultationInput`, Header `Idempotency-Key` | `ConsultationDetail`, 201 | 400 VALIDATION_ERROR, 404 NOT_FOUND, 409 MEDIA_NOT_READY·IDEMPOTENCY_CONFLICT, 503 UPSTREAM_UNAVAILABLE | CON-01·CON-05 |
| 내 상담 목록 | `GET /api/consultations` | Query `petId?:string`, `status?:string`, `page`, `size` | `Page<ConsultationItem>`, 200 | 400 VALIDATION_ERROR, 404 NOT_FOUND | CON-04 |
| 상담 상세 | `GET /api/consultations/{consultationId}` | 없음 | `ConsultationDetail`, 200 | 404 NOT_FOUND | CON-04 |
| 매칭 진행·결과 | `GET /api/consultations/{consultationId}/matching` | 없음 | `MatchingStatus`, 200 | 404 NOT_FOUND | CON-02·CON-05 |
| 매칭·상담 상태 구독 | `GET /api/consultations/{consultationId}/stream` | Header `Last-Event-ID?:string` | `ConsultationEvent` 스트림, 200 | 404 NOT_FOUND, 503 UPSTREAM_UNAVAILABLE | CON-02·CON-05 |
| 상담 취소 | `POST /api/consultations/{consultationId}/cancellation` | Body `{reason?:string}` | `ConsultationDetail`, 200 | 404 NOT_FOUND, 409 STATE_CONFLICT | CON-02·CON-04 |
| 상담 연결 | `POST /api/consultations/{consultationId}/connections` | Header `Idempotency-Key`, 본문 없음 | `Connection`, 201 | 404 NOT_FOUND, 409 STATE_CONFLICT·IDEMPOTENCY_CONFLICT, 503 UPSTREAM_UNAVAILABLE | CON-03 |
| 상담 종료 요청 | `POST /api/consultations/{consultationId}/termination` | Header `Idempotency-Key`, 본문 없음 | `EndAcceptance`, 202 | 404 NOT_FOUND, 409 STATE_CONFLICT·IDEMPOTENCY_CONFLICT, 503 UPSTREAM_UNAVAILABLE | CON-03·CON-04 |
| 제공된 상담 일지 | `GET /api/consultations/{consultationId}/journal` | 없음 | `JournalResult`, 200 | 404 NOT_FOUND, 503 UPSTREAM_UNAVAILABLE | LOG-01 |
| 매칭 상대 정보 | `GET /api/consultations/{consultationId}/veterinarian` | 없음 | `VeterinarianInfo`, 200 | 404 NOT_FOUND, 409 STATE_CONFLICT, 503 UPSTREAM_UNAVAILABLE | VET-01 |
| 완료 상담 평가 | `POST /api/consultations/{consultationId}/reviews` | Body `ReviewInput`, Header `Idempotency-Key` | `Review`, 201 | 400 VALIDATION_ERROR, 404 NOT_FOUND, 409 STATE_CONFLICT·IDEMPOTENCY_CONFLICT | REV-01 |
| 내 상담 평가 조회 | `GET /api/consultations/{consultationId}/reviews` | Query `page`, `size` | `Page<Review>`, 200 | 404 NOT_FOUND | REV-01 |

상태 구독은 SSE 방식의 설계 제안이며 `D17`의 전달 방식 확정 후 적용한다. 스트림은 JSON 래퍼를 사용하지 않으며 `id`에 `eventId`, `event`에 `type`, `data`에 ConsultationEvent JSON을 보낸다. 연결 이후 오류·종료·재연결 계약은 전달 채널과 함께 확정한다. Bearer 헤더를 지원하는 클라이언트 수신 방식을 정하고 접근 토큰을 URL 쿼리로 전달하지 않는다.

## 신청·매칭 처리

1. 신청한 동물의 소유권·삭제 상태, 채널과 위치, 제출한 미디어의 완료·접근 권한을 검사한다. 작성자와 상담 주체는 인증 정보에서 얻는다.
2. 요청을 매칭 대기로 저장하고 가까운 병원부터 탐색한다. 원본 SQL의 수의사 필수 컬럼과 매칭 전 상대 미정 상태는 `D18`에서 저장 구조를 맞춘다.
3. 수락 결과와 취소·만료 이벤트가 경합해도 한 최종 상태만 반영한다. 취소·만료된 요청은 뒤늦은 수락으로 연결하지 않는다. 한 요청은 한 수의사에게만 확정한다.
4. 매칭 성공·미매칭·취소를 상태 조회와 실시간 전달에 동일하게 반영한다. 이벤트는 중복·순서 변경 가능성을 고려해 버전 또는 순번을 포함할지 `D17`에서 정한다. 클라이언트는 재연결 후 상태 API로 최신 결과를 재조회한다.

`Idempotency-Key`는 같은 주체·동작·같은 입력의 재시도에 기존 결과를 반환한다. 같은 키로 다른 입력을 제출하면 409다. 멱등성 키 저장과 신청 상태가 분리되어 중복 신청되는 경우를 방지하고, 키 보관 기간은 구현 전에 정한다.

기존 반경·전체 60초 합의의 최신 적용 여부는 `D17` 미정이다. 응답 `expiresAt`은 서버가 확정한 기한이 있을 때만 제공한다. 클라이언트가 임의로 반경·만료를 확정하지 않도록 한다.

## 연결·취소·종료

- 취소는 매칭 대기 중 보호자에게 허용한다. 같은 취소 재시도는 기존 취소 결과를 반환한다. 매칭 후 허용 시점은 `D04`·`D17`을 확정한 뒤 적용하며 허용되지 않는 현재 상태에는 409를 반환한다.
- 연결 요청은 매칭된 본인 상담에 한정한다. 같은 키의 재시도로 새 세션을 여러 개 만들지 않는다. 외부 생성 성공 후 내부 저장 실패가 생기면 기존 세션을 재사용하거나 정리·재처리할 수 있게 식별자를 기록한다.
- 종료 요청 접수 202는 연결 종료의 성공 확정을 뜻하지 않는다. 실제 종료 이벤트·업무 완료 상태는 상세 조회·스트림으로 확인한다. 종료 이벤트가 중복되어도 종료 시각·완료 상태를 중복 반영하거나 되돌리지 않는다.
- 외부 연결이 성립하지 않았으면 정상 완료로 표시하지 않는다. 연결 실패를 기록하고 재연결 안내를 제공한다. 연결 정보·토큰·파일은 상담 당사자만 받을 수 있다.
- 매칭만으로 반려동물의 기존 건강 기록 열람 권한을 부여하지 않는다. 제출한 증상·이미지와 기존 건강 기록은 별도 접근 대상으로 취급한다.

## 일지·평가

- 상담 내역과 종료 결과는 일지가 없어도 조회한다. 외부 제공자가 미작성을 정상 응답으로 확인한 경우 `{"availability":"NOT_WRITTEN","journal":null}`을 반환한다.
- 제공된 일지가 있으면 `availability:AVAILABLE`과 본문·첨부를 반환한다. 원본 제공자의 장애·타임아웃은 503이며 미작성으로 바꾸지 않는다. 일지·첨부 직접 URL에도 해당 상담 보호자의 접근 권한을 검사한다.
- 평가는 본인 완료 상담에만 작성하며 `rating`은 필수, `content`는 선택이다. 별점 범위·상담당 평가 수·수정/삭제·집계 범위는 `D16`에서 정한다. 현재 목록 응답은 허용 평가 수를 하나로 확정하지 않도록 Page 모델을 사용하는 설계안이다.
- 동일 평가 요청의 재시도는 같은 평가를 반환하고 평균·개수 집계를 중복 증가시키지 않는다. 평가 작성 후 표시하는 집계의 반영 시점·실패 복구는 상세 설계에서 정한다.

## 구현 전 확인

| PRD 항목 | 확인 내용 |
| --- | --- |
| D04·D07 | 연결 종료·업무 완료·일지 제공 관계, 취소·중단·재시도와 완료 오처리 |
| D05·D19 | 증상·이미지의 후보/확정 상대 전달과 취소·종료 후 파일 접근 |
| D06 | 채팅·화상 업체, 연결/종료 이벤트, 세션 만료·재연결·이력 보관 |
| D16 | 상대 프로필·평가 범위·횟수·집계 |
| D17 | 가용 상태·수락 제공 주체·인증, 위치·거리·탐색 순서·반경·기한·전달 채널 |
| D18 | MySQL 상담과 MongoDB 반려동물의 식별자 연결·상태 저장·멱등성 제약 |

수락·종료·일지 제공 이벤트의 내부 연동 API는 제공 주체와 인증 계약을 정한 뒤 명세화한다. 현재 문서는 보호자 API 초안이며 실제 상담 제공 업체·서버·DB 연동 검증은 수행하지 않았다.

## 요청·응답 예시

아래 값은 형식 설명용이며 미정 정책, 제한값, 상태 전이나 실제 서버 동작을 확정하지 않는다. 인증·멱등성 등 공통 헤더는 [공통 계약](README.md#공통-계약)을 따른다. 각 예시는 별도의 상황이다.

### `POST /api/consultations`

요청 예시:

```http
POST /api/consultations HTTP/1.1
Authorization: Bearer <액세스 토큰>
Idempotency-Key: <요청별 고유 키>
Content-Type: application/json

{
  "petId": "pet_01",
  "channel": "CHAT",
  "symptom": "상담 요청",
  "mediaIds": [],
  "location": {
    "latitude": 37.5,
    "longitude": 127.0
  }
}
```

응답 예시 (`201`):

```json
{
  "data": {
    "consultationId": "consult_01",
    "pet": {
      "petId": "pet_01",
      "name": "루이"
    },
    "veterinarian": null,
    "channel": "CHAT",
    "status": "MATCHING",
    "requestedAt": "2026-11-19T10:00:00+09:00",
    "symptom": "상담 요청",
    "media": [],
    "matchedAt": null,
    "startedAt": null,
    "endedAt": null,
    "durationSeconds": null,
    "journalAvailability": "NOT_WRITTEN"
  }
}
```

### `GET /api/consultations`

요청 예시:

```http
GET /api/consultations?page=0&size=20 HTTP/1.1
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

### `GET /api/consultations/{consultationId}`

요청 예시:

```http
GET /api/consultations/consult_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "consultationId": "consult_01",
    "pet": {
      "petId": "pet_01",
      "name": "루이"
    },
    "veterinarian": null,
    "channel": "CHAT",
    "status": "MATCHING",
    "requestedAt": "2026-11-19T10:00:00+09:00",
    "symptom": "상담 요청",
    "media": [],
    "matchedAt": null,
    "startedAt": null,
    "endedAt": null,
    "durationSeconds": null,
    "journalAvailability": "NOT_WRITTEN"
  }
}
```

### `GET /api/consultations/{consultationId}/matching`

요청 예시:

```http
GET /api/consultations/consult_01/matching HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "consultationId": "consult_01",
    "status": "MATCHING",
    "requestedAt": "2026-11-19T10:00:00+09:00",
    "expiresAt": null,
    "elapsedSeconds": 0,
    "veterinarian": null
  }
}
```

### `GET /api/consultations/{consultationId}/stream`

요청 예시:

```http
GET /api/consultations/consult_01/stream HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200 text/event-stream`, 이벤트 유형은 미정):

```text
id: event_01
event: <이벤트_유형>
data: {"eventId":"event_01","type":"<이벤트_유형>","consultationId":"consult_01","occurredAt":"2026-11-19T10:00:00+09:00","data":{}}
```

### `POST /api/consultations/{consultationId}/cancellation`

요청 예시:

```http
POST /api/consultations/consult_01/cancellation HTTP/1.1
Authorization: Bearer <액세스 토큰>
Content-Type: application/json

{
  "reason": "일정 변경"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "consultationId": "consult_01",
    "pet": {
      "petId": "pet_01",
      "name": "루이"
    },
    "veterinarian": null,
    "channel": "CHAT",
    "status": "CANCELLED",
    "requestedAt": "2026-11-19T10:00:00+09:00",
    "symptom": "상담 요청",
    "media": [],
    "matchedAt": null,
    "startedAt": null,
    "endedAt": null,
    "durationSeconds": null,
    "journalAvailability": "NOT_WRITTEN"
  }
}
```

### `POST /api/consultations/{consultationId}/connections`

요청 예시:

```http
POST /api/consultations/consult_01/connections HTTP/1.1
Authorization: Bearer <액세스 토큰>
Idempotency-Key: <요청별 고유 키>
```

응답 예시 (`201`):

```json
{
  "data": {
    "connectionId": "connection_01",
    "channel": "CHAT",
    "status": "CONNECTING",
    "expiresAt": null,
    "access": {
      "url": null,
      "token": null
    }
  }
}
```

### `POST /api/consultations/{consultationId}/termination`

요청 예시:

```http
POST /api/consultations/consult_01/termination HTTP/1.1
Authorization: Bearer <액세스 토큰>
Idempotency-Key: <요청별 고유 키>
```

응답 예시 (`202`):

```json
{
  "data": {
    "actionId": "action_01",
    "consultationId": "consult_01",
    "status": "ACCEPTED",
    "requestedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `GET /api/consultations/{consultationId}/journal`

요청 예시:

```http
GET /api/consultations/consult_01/journal HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "availability": "NOT_WRITTEN",
    "journal": null
  }
}
```

### `GET /api/consultations/{consultationId}/veterinarian`

요청 예시:

```http
GET /api/consultations/consult_01/veterinarian HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "veterinarianId": "vet_01",
    "name": "수의사",
    "hospital": {
      "hospitalId": "hospital_01",
      "name": "동물병원"
    },
    "profileMedia": null,
    "introduction": null,
    "averageRating": null,
    "reviewCount": null
  }
}
```

### `POST /api/consultations/{consultationId}/reviews`

요청 예시:

```http
POST /api/consultations/consult_01/reviews HTTP/1.1
Authorization: Bearer <액세스 토큰>
Idempotency-Key: <요청별 고유 키>
Content-Type: application/json

{
  "rating": 5,
  "content": "감사합니다."
}
```

응답 예시 (`201`):

```json
{
  "data": {
    "reviewId": "review_01",
    "consultationId": "consult_01",
    "rating": 5,
    "content": "감사합니다.",
    "createdAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `GET /api/consultations/{consultationId}/reviews`

요청 예시:

```http
GET /api/consultations/consult_01/reviews?page=0&size=20 HTTP/1.1
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
