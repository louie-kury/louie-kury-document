# 공통 미디어

**우선 개발.** PRD `MED-01`, `HLT-04`, `D19`, 요구사항정의서 C76:H89 기준. 미디어 메타데이터와 첨부 연결의 확정 SQL은 [서비스별 미디어 ERD](../erd/svc_media.md)의 `svc_media`를 따른다. 실제 파일의 S3 저장은 기존 공통 설계다.

[공통 계약](README.md#공통-계약)을 함께 적용한다. 아래 경로·필드·오류 코드는 API 설계 초안이며 미정 정책은 마지막 절에서 추적한다.

## 데이터 모델

| 모델 | 필드 |
| --- | --- |
| MediaRef | `mediaId:string`, `fileName:string`, `contentType:string`, `fileSize:integer`, `fileUrl:string` |
| MediaDetail | MediaRef + `usage:string`, `status:string`, `createdAt:timestamp` |
| MediaPolicy | `usage:string`, `allowedContentTypes:string[]`, `maxFileSizeBytes:integer`, `maxAttachments:integer` |

`usage` 값은 `POST_ATTACHMENT`, `MEMBER_PROFILE`, `PET_PROFILE`, `HEALTH_ATTACHMENT`, `CONSULTATION_ATTACHMENT` 설계안이다. 설정되지 않은 사용처는 허용하지 않는다. 사용처별 제한은 서버가 제공하며 `fileSize` 단위는 byte다.

### 사용자 대화에서 선택한 제한

다음은 사용자 대화에서 선택해 [PRD MED-01](../prd.md#69-공통-미디어--med)에 반영한 정책이며 SQL의 제약이 아니다.

| 사용처 | 허용 형식 및 제한 |
| --- | --- |
| 회원·반려동물 프로필 | JPEG·PNG·WebP 이미지, 파일당 최대 10MB |
| 게시글 | JPEG·PNG·WebP 이미지 파일당 최대 10MB, MP4 파일당 최대 100MB, 이미지와 동영상을 합해 최대 5개 |
| 건강 기록·상담 첨부 | JPEG·PNG·WebP 이미지 파일당 최대 10MB, 각각 최대 3개 |

삭제 실패는 최초 시도 후 최대 3회 재시도하며 각 실패 후 1분·3분·7분을 기다린다. 최종 실패는 운영자가 확인한다. DB에는 삭제 대상·상태·시도 횟수·다음 시도 시각 등 작업 정보를 저장하고 오류 내용은 애플리케이션 로그에 남긴다. 로그 항목과 운영자 확인 절차는 미정이다.

`fileName`, `contentType`, `fileSize`, `createdAt`은 각각 `file_name`, `content_type`, `file_size`, `created_at`에 대응한다. 업로더는 `uploader_uuid`에 기록한다. `media.id`는 내부 BIGINT PK이고 API의 `mediaId`는 고유한 `media.uuid`를 사용한다. API의 `fileUrl`은 권한 검사 경로이며 `object_key`는 서버 내부에서 사용한다. 허용 형식은 SQL 컬럼 길이와 별개의 정책이다.

미디어 테이블은 파일 메타데이터를, `media_attachment`는 파일과 사용처의 연결을 기록한다. 한 파일의 동시 사용처는 한 곳이며 작성 화면 단위로 활동 신호를 관리한다. 제공 SQL의 복합 UNIQUE는 단일 활성 연결을 보장하지 않아 후속 합의로 `media_attachment.media_id`에 UNIQUE를 추가할 예정이다. SQL의 `target_uuid`가 NOT NULL이므로 연결 전 임시 첨부는 별도로 관리한다. 임시 첨부와 `usage`, 활동·정리 보호 정보의 구체 저장 구조와 신호 전송 계약은 미정이다.

## 엔드포인트

### `GET /api/media/policies`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/media/policies` | 필수 | `usage` | `MediaPolicy` / 200 | 400 UNKNOWN_USAGE, 503 MEDIA_POLICY_UNAVAILABLE |

요청 예시:

```http
GET /api/media/policies?usage=PET_PROFILE HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답: `200`의 `data`는 `MediaPolicy`다. 사용처별 허용 형식·용량·개수는 위 정책을 따른다.

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

응답: `200`과 파일 바이너리. Content-Type과 파일명은 검증된 파일 메타데이터에 따른다.

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

- 업로드는 본인에게 발급된 파일만 생성한다. 확장자·신고 MIME·실제 내용·크기를 검사하고 실패 사유를 안내한다. 완료된 파일에만 201과 식별자를 반환한다. 업로드 진행률은 전송 상태로 표시하고 실패 시 새 업로드를 시도한다.
- S3 저장 전에 MySQL에 업로드 작업과 객체 키를 기록하고 S3 저장 후 미디어와 별도 임시 첨부 기록을 저장해 성공한 작업 기록을 정리한다. 제공 SQL에는 해당 작업 기록과 임시 첨부 구조가 없으므로 구체 저장 구조는 미정이다. 객체 키는 파일마다 새로 발급하고 재사용하지 않는다. S3 성공 후 DB 저장 실패나 프로세스 중단 및 정리 후 지연된 S3 쓰기 완료를 복구해야 한다.
- 업로드 파일은 부모 저장 전 임시 상태다. 업로더만 조회·포기할 수 있으며 임의의 `mediaId`를 아는 것만으로 접근하지 못한다.
- 작성 화면이 열려 활동 신호가 도착하는 동안 연결 전 파일을 보호한다. 마지막 신호로부터 30분 동안 신호가 없으면 연결·저장 진행 여부를 다시 확인하고 정리한다. 30분 내 신호가 돌아오면 보호를 연장한다. 취소 또는 명확한 저장 실패 시 미연결 파일을 정리하고, 저장 실패 화면에서 첨부 목록을 제거해 재첨부를 안내한다.
- 파일 첨부는 부모의 JSON `mediaIds` 또는 `profileMediaId`로 저장한다. 부모가 인증된 호출자와 파일의 완료·소유·usage·개수·연결 권한을 검사한다.
- 서버는 부모 저장 및 연결 상태 갱신 중 부분 실패를 감지·복구하여 이전 연결과 새 연결을 일관되게 유지한다. MySQL 미디어와 MongoDB 부모 저장을 단일 DB 트랜잭션으로 가정하지 않는다.
- 타임아웃 등 부모 저장 결과가 불명확하면 파일과 기존 연결을 보호하고 부모의 실제 참조를 확인한 뒤 자동 복구한다. 부모 저장 중인 파일을 정리로부터 보호한다. 연결과 정리 선점을 원자적으로 처리하고 늦게 완료된 작업은 선점 상태를 확인해 경합으로 사용 중 파일이 삭제되지 않도록 한다.
- 교체는 새 파일 업로드와 부모 저장이 모두 성공한 후 기존 연결을 해제한다. 첨부 제거도 부모 PATCH 성공 후 반영한다. 부모 저장 실패 시 이전 연결을 보존한다.
- DELETE는 본인이 업로드한 미연결 파일의 사용 포기 계약이다. 연결된 파일을 부모와 무관하게 삭제하지 못하게 409로 거절한다. 실제 보관·파기는 D19 정책과 정리 작업이 수행한다.
- 공개 게시글 미디어는 공개 권한으로, 프로필·건강·상담 파일 등은 현재 사용처의 권한으로 제공한다. 삭제·숨김 부모의 이전 URL 접근은 거절한다.
- `fileUrl`은 권한 검사 경로다. 비공개 파일은 인증된 fetch 등으로 조회하며 영구 공개 URL을 발급하지 않는다. 다운로드 파일명·Content-Type은 검증한 메타데이터로 설정한다.
- 저장소 파일이 사라진 경우를 정상 파일 응답으로 숨기지 않는다. 프런트는 404 등 조회 실패 시 이미지 대체 화면 또는 동영상·문서 안내를 표시한다.
- 연결 해제 파일은 해제 후 24시간이 지나면 정리 대상으로 삼는다. 소프트 삭제된 부모의 첨부 원본은 부모와 함께 보관하고 접근을 차단한다. 정리 직전 활성 연결과 진행 중인 저장을 확인한다. S3 삭제 실패 시 작업 상태를 기록하고 자동 재시도하며 오류 내용은 애플리케이션 로그에 남긴다. 정리는 내부 작업이며 공개 관리 API를 만들지 않는다.

## 구현 전 확인

- D19 — 실제 파일 유형 검증의 세부 방식, 상세 오류 로그 항목과 반복 실패 운영자 확인 절차 등 선택되지 않은 세부 사항은 미정이다.
- D18 — 임시 첨부·업로드 작업·활동 기록의 구체 저장 구조, 신호·복구 계약과 경합 제어를 구체화한다. `media_id` UNIQUE 추가는 후속 합의이며 SQL의 현재 컬럼 길이·키·인덱스는 서비스별 미디어 ERD을 따른다.
