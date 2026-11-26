# 공통 미디어

**우선 개발.** PRD `MED-01`, `HLT-04`, `D19`, 요구사항정의서 C76:H89 기준. 미디어 메타데이터와 첨부 연결의 확정 SQL은 [서비스별 미디어 ERD](../erd/svc_media.md)의 `svc_media`를 따른다. 이 문서는 합의된 목표 설계이며 새 서비스에 구현된 동작을 뜻하지 않는다.

[공통 계약](README.md#공통-계약)을 함께 적용한다. 아래 경로·필드·오류 코드는 API 설계 초안이며 미정 정책은 마지막 절에서 추적한다.

## 데이터 모델

| 모델 | 필드 |
| --- | --- |
| MediaRef | `mediaId:string`, `fileName:string`, `contentType:string`, `fileSize:integer`, `fileUrl:string` |
| MediaDetail | MediaRef + `usage:string`, `status:string`, `createdAt:timestamp` |

`usage` 값은 `POST_ATTACHMENT`, `MEMBER_PROFILE`, `PET_PROFILE`, `HEALTH_ATTACHMENT`, `CONSULTATION_ATTACHMENT` 설계안이다. 설정되지 않은 사용처는 허용하지 않는다. 화면은 사용처별 제한을 미리 안내하고, 서버는 업로드와 연결 시 해당 제한을 검증한다. 정책 조회 API는 제공하지 않는다. 정책이 바뀌면 화면 안내도 함께 갱신한다. `fileSize` 단위는 byte다.

### 사용자 대화에서 선택한 제한

다음은 사용자 대화에서 선택해 [PRD MED-01](../prd.md#69-공통-미디어--med)에 반영한 정책이며 SQL의 제약이 아니다.

| 사용처 | 허용 형식 및 제한 |
| --- | --- |
| 회원·반려동물 프로필 | JPEG·PNG·WebP 이미지, 파일당 최대 10MB |
| 게시글 | JPEG·PNG·WebP 이미지 파일당 최대 10MB, MP4 파일당 최대 100MB, 이미지와 동영상을 합해 최대 5개 |
| 건강 기록·상담 첨부 | JPEG·PNG·WebP 이미지 파일당 최대 10MB, 각각 최대 3개 |

1MB는 1,000,000바이트다. 이미지 최대 크기는 10,000,000바이트, MP4 최대 크기는 100,000,000바이트다.

삭제 실패는 최초 시도 후 최대 3회 재시도하며 각 실패 후 10초·30초·60초를 기다린다. 최종 실패는 운영자가 확인한다. DB에는 삭제 대상·상태·시도 횟수·다음 시도 시각 등 작업 정보를 저장하고 오류 내용은 애플리케이션 로그에 남긴다. 로그 항목과 운영자 확인 절차는 미정이다.

`fileName`, `contentType`, `fileSize`, `createdAt`은 각각 `file_name`, `content_type`, `file_size`, `created_at`에 대응한다. 업로더는 `uploader_uuid`에 기록한다. `media.id`는 내부 BIGINT PK이고 API의 `mediaId`는 고유한 `media.uuid`를 사용한다. API의 `fileUrl`은 권한 검사 경로이며 `object_key`는 서버 내부에서 사용한다. 허용 형식은 SQL 컬럼 길이와 별개의 정책이다.

미디어 테이블은 파일 메타데이터를, `media_attachment`는 파일과 사용처의 연결을 기록한다. 파일 하나와 현재 연결을 `Media` 어그리게이트로 관리하고 기본 상태는 업로드 완료·미연결, 연결됨, 정리 대기다. 한 파일의 동시 사용처는 한 곳이며 본인 업로드 파일만 연결한다. 제공 SQL의 복합 UNIQUE는 단일 연결을 보장하지 않아 `media_attachment.media_id`에 UNIQUE를 추가할 예정이다. 게시글 첨부 순서를 관계에 기록하며 컬럼·제약은 구현 설계에서 정한다. 연결 전 파일, 사용처별 저장 작업과 정리 보호 정보의 구체 구조는 미정이다.

## 엔드포인트

### `POST /api/media`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `POST /api/media` | 필수 | multipart `file`, `usage` | `MediaDetail(status=READY)` / 201 | 400 INVALID_MEDIA_TYPE, 413 FILE_TOO_LARGE, 415 UNSUPPORTED_MEDIA_TYPE, 503 STORAGE_UNAVAILABLE |

요청 예시:

```http
POST /api/media HTTP/1.1
Authorization: Bearer <액세스 토큰>
Content-Type: multipart/form-data; boundary=<boundary>

--<boundary>
Content-Disposition: form-data; name="usage"

PET_PROFILE
--<boundary>
Content-Disposition: form-data; name="file"; filename="photo.jpg"
Content-Type: image/jpeg

<파일 바이너리>
--<boundary>--
```

응답 예시 (`201`):

```json
{
  "data": {
    "mediaId": "550e8400-e29b-41d4-a716-446655440000",
    "fileName": "photo.jpg",
    "contentType": "image/jpeg",
    "fileSize": 1024,
    "fileUrl": "/api/media/550e8400-e29b-41d4-a716-446655440000/file",
    "usage": "PET_PROFILE",
    "status": "READY",
    "createdAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `GET /api/media/{mediaId}`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/media/{mediaId}` | 사용처에 따름 | 경로 mediaId | `MediaDetail` / 200 | 404 NOT_FOUND |

요청 예시:

```http
GET /api/media/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "mediaId": "550e8400-e29b-41d4-a716-446655440000",
    "fileName": "photo.jpg",
    "contentType": "image/jpeg",
    "fileSize": 1024,
    "fileUrl": "/api/media/550e8400-e29b-41d4-a716-446655440000/file",
    "usage": "PET_PROFILE",
    "status": "READY",
    "createdAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `GET /api/media/{mediaId}/file`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/media/{mediaId}/file` | 사용처에 따름 | 경로 mediaId | 파일 바이너리 / 200 | 404 NOT_FOUND, 503 STORAGE_UNAVAILABLE |

요청 예시:

```http
GET /api/media/550e8400-e29b-41d4-a716-446655440000/file HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답: `200`과 파일 바이너리. `Content-Type`과 파일명은 검증된 파일 메타데이터에 따르며 이미지와 동영상은 `Content-Disposition: inline`을 사용한다.

### `DELETE /api/media/{mediaId}`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `DELETE /api/media/{mediaId}` | 필수 | 경로 mediaId | 본문 없음 / 204 | 404 NOT_FOUND, 409 MEDIA_IN_USE |

요청 예시:

```http
DELETE /api/media/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답: `204`, 본문 없음.


## 처리 규칙

- 로그인 사용자의 업로드에서 크기와 JPEG·PNG·WebP·MP4 식별 정보를 기본 검사하고 실패 사유를 안내한다. MP4에 ffprobe를 사용하지 않으며 이 검사만으로 파일 전체의 정상 여부나 재생 가능성을 보장하지 않는다. 완료된 파일에만 식별자를 반환한다.
- 미디어 서비스가 파일을 받아 AWS S3에 저장한다. S3와 DB 저장은 하나의 트랜잭션이 아니며 결과 불명확·부분 실패에 대비한다. 객체 키는 파일마다 새로 발급하고 재사용하지 않는다. 구체 저장 기록과 복구 계약은 미정이다.
- 업로드 파일은 부모 저장 전 임시 상태다. 업로더만 조회·포기할 수 있으며 임의의 `mediaId`를 아는 것만으로 접근하지 못한다.
- 게시글 작성 중 파일은 브라우저에서 미리보기하고 저장 버튼을 누른 뒤 업로드한다. 파일 업로드 후 비공개 임시 게시글을 저장하고 모든 연결이 완료되면 공개한다. 연결 실패 시 작성 내용과 파일을 보관하고 재시도를 안내한다. 마지막 작성·재시도부터 24시간이 지나면 도메인이 정리를 요청하며 미디어 서비스는 진행·연결 상태를 확인한다.
- 사용처 도메인이 인증된 호출자의 사용처 권한을 확인하고 미디어 서비스는 업로더·완료·usage·단일 연결을 확인한다. 게시글 생성의 파일 전송과 연결 API 세부 계약은 미정이며 기존 `mediaIds` JSON 예시는 변경 전 초안이다.
- 부모 저장 및 연결 중 부분 실패에서 이전 연결과 새 연결을 보호하고 사용자 재시도로 실제 상태를 확인한다. MySQL 미디어와 MongoDB 부모 저장을 단일 DB 트랜잭션으로 가정하지 않는다.
- 타임아웃 등 저장 결과가 불명확하면 파일과 기존 연결을 보호하고 사용자가 같은 작업 ID로 재시도할 때 실제 결과를 확인한다. 각 도메인이 사용자 key와 작업 ID로 전체 저장 상태를 관리하고 중복 생성을 방지한다. 작업 ID 하나에 여러 파일이 속할 때 파일별 재시도 식별 방식은 미정이다. 연결과 정리의 경합으로 사용 중인 파일이 삭제되지 않아야 한다.
- 만료 정리와 결과 불명확 파일 보호가 겹치면 24시간 경과만으로 안전한 삭제를 단정하지 않는다. 실제 상태를 확인할 수 없는 파일의 장기 보관 및 운영 조치 계약은 미정이다.
- 교체는 새 파일 업로드와 부모 저장이 모두 성공한 후 기존 연결을 해제한다. 첨부 제거도 부모 PATCH 성공 후 반영한다. 부모 저장 실패 시 이전 연결을 보존한다.
- DELETE는 본인이 업로드한 미연결 파일의 사용 포기 계약이다. 연결된 파일을 부모와 무관하게 삭제하지 못하게 409로 거절한다. 실제 보관·파기는 D19 정책과 정리 작업이 수행한다.
- 공개 게시글 미디어는 공개 권한으로, 프로필·건강·상담 파일 등은 현재 사용처의 권한으로 제공한다. 삭제·숨김 부모의 이전 URL 접근은 거절한다.
- 게이트웨이는 인증된 사용자 key를 신뢰할 수 있게 전달한다. 미디어 서비스는 파일 요청마다 해당 도메인에 내부 HTTP로 사용처 ID와 사용자 key 또는 비회원 정보를 전달해 현재 상태·권한을 확인하고 허용 시 S3 파일을 전달한다. 비회원은 공개 게시글을 볼 수 있다. 권한 확인 장애와 권한 거절·파일 부재를 구분하며 확인 장애 시 제공하지 않는다. 이미 전달된 파일은 회수할 수 없다.
- 공개 게시글 파일은 `Cache-Control: no-cache`, 비공개 파일은 `Cache-Control: private, no-cache`를 반환한다. 캐시 재검증과 304 응답 전에도 사용처의 현재 권한·삭제·숨김 상태를 확인한다. 검증자와 서비스 간 권한 확인 방식은 구현 전에 정한다.
- MP4 구간 요청은 초기 범위에서 지원하지 않는다. `Range`를 무시하고 `200`과 전체 파일을 반환한다. 실제 브라우저에서 큰 MP4의 재생과 구간 이동을 검증한다.
- `fileUrl`은 권한 검사 경로다. 비공개 파일은 인증된 fetch 등으로 조회하며 영구 공개 URL을 발급하지 않는다. 다운로드 파일명·Content-Type은 검증한 메타데이터로 설정한다.
- 저장소 파일이 사라진 경우를 정상 파일 응답으로 숨기지 않는다. 프런트는 404 등 조회 실패 시 이미지 대체 화면 또는 동영상·문서 안내를 표시한다.
- 연결 해제 파일은 해제 후 24시간이 지나면 정리 대상으로 삼는다. 소프트 삭제된 부모의 첨부 원본은 부모와 함께 보관하고 접근을 차단한다. 정리 직전 활성 연결과 진행 중인 저장을 확인한다. S3 원본은 실제 삭제하고 미디어 DB 기록은 삭제 시각을 남겨 일반 조회·새 연결에서 제외한다. 삭제 실패는 기록 후 재시도한다. 정리는 내부 작업이며 공개 관리 API를 만들지 않는다.

## 구현 전 확인

- D19 — 실제 파일 유형 검증의 세부 방식, 상세 오류 로그 항목과 반복 실패 운영자 확인 절차 등 선택되지 않은 세부 사항은 미정이다.
- D18 — 임시 첨부·작업 상태·파일별 재시도 식별, 도메인 간 API·신뢰 경계와 정리 경합 제어를 구체화한다. `media_id` UNIQUE 추가는 후속 합의이며 SQL의 현재 컬럼 길이·키·인덱스는 서비스별 미디어 ERD를 따른다.
