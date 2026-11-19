# 공통 미디어

**우선 개발.** PRD `MED-01`, `HLT-04`, `D19`, 요구사항정의서 C76:H89 기준. 메타데이터는 MySQL 공통 `미디어` 테이블 한 개를 사용하고 실제 파일은 설정된 저장소에서 관리한다.

[공통 계약](README.md#공통-계약)을 함께 적용한다. 아래 경로·필드·오류 코드는 API 설계 초안이며 미정 정책은 마지막 절에서 추적한다.

## 데이터 모델

| 모델 | 필드 |
| --- | --- |
| MediaRef | `mediaId:string`, `fileName:string`, `contentType:string`, `fileSize:integer`, `fileUrl:string` |
| MediaDetail | MediaRef + `usage:string`, `status:string`, `createdAt:timestamp` |
| MediaPolicy | `usage:string`, `allowedContentTypes:string[]`, `maxFileSizeBytes:integer`, `maxAttachments:integer` |

`usage` 값은 `POST_ATTACHMENT`, `MEMBER_PROFILE`, `PET_PROFILE`, `HEALTH_ATTACHMENT`, `CONSULTATION_ATTACHMENT` 설계안이다. 설정되지 않은 사용처는 허용하지 않는다. 제한 수치는 D19 확정 후 서버가 제공한다. 필드의 선언만으로 제한값을 임의 생성하지 않는다. `fileSize` 단위는 byte다.

## 엔드포인트

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/media/policies` | 필수 | `usage` | `MediaPolicy` / 200 | 400 UNKNOWN_USAGE, 503 MEDIA_POLICY_UNAVAILABLE |
| `POST /api/media` | 필수 | multipart `file`, `usage` | `MediaDetail(status=READY)` / 201 | 400 INVALID_MEDIA_TYPE, 413 FILE_TOO_LARGE, 415 UNSUPPORTED_MEDIA_TYPE, 503 STORAGE_UNAVAILABLE |
| `GET /api/media/{mediaId}` | 사용처에 따름 | 경로 mediaId | `MediaDetail` / 200 | 404 NOT_FOUND |
| `GET /api/media/{mediaId}/file` | 사용처에 따름 | 경로 mediaId | 파일 바이너리 / 200 | 404 NOT_FOUND, 503 STORAGE_UNAVAILABLE |
| `DELETE /api/media/{mediaId}` | 필수 | 경로 mediaId | 본문 없음 / 204 | 404 NOT_FOUND, 409 MEDIA_IN_USE |

## 처리 규칙

- 업로드는 본인에게 발급된 파일만 생성한다. 확장자·신고 MIME·실제 내용·크기를 검사하고 실패 사유를 안내한다. 완료된 파일에만 201과 식별자를 반환한다. 업로드 진행률은 전송 상태로 표시하고 실패 시 새 업로드를 시도한다.
- 업로드 파일은 부모 저장 전 임시 상태다. 업로더만 조회·포기할 수 있으며 임의의 `mediaId`를 아는 것만으로 접근하지 못한다.
- 파일 첨부는 부모의 JSON `mediaIds` 또는 `profileMediaId`로 저장한다. 부모가 인증된 호출자와 파일의 완료·소유·usage·개수·연결 권한을 검사한다.
- 서버는 부모 저장 및 연결 상태 갱신 중 부분 실패를 감지·복구하여 이전 연결과 새 연결을 일관되게 유지한다. MySQL 미디어와 MongoDB 부모 저장을 단일 DB 트랜잭션으로 가정하지 않는다.
- 교체는 새 파일 업로드와 부모 저장이 모두 성공한 후 기존 연결을 해제한다. 첨부 제거도 부모 PATCH 성공 후 반영한다. 부모 저장 실패 시 이전 연결을 보존한다.
- DELETE는 본인이 업로드한 미연결 파일의 사용 포기 계약이다. 연결된 파일을 부모와 무관하게 삭제하지 못하게 409로 거절한다. 실제 보관·파기는 D19 정책과 정리 작업이 수행한다.
- 공개 게시글 미디어는 공개 권한으로, 프로필·건강·상담 파일 등은 현재 사용처의 권한으로 제공한다. 삭제·숨김 부모의 이전 URL 접근은 거절한다. 한 파일의 복수 연결 허용 여부는 D19에서 확정한다.
- `fileUrl`은 권한 검사 경로다. 비공개 파일은 인증된 fetch 등으로 조회하며 영구 공개 URL을 발급하지 않는다. 다운로드 파일명·Content-Type은 검증한 메타데이터로 설정한다.
- 저장소 파일이 사라진 경우를 정상 파일 응답으로 숨기지 않는다. 프런트는 404 등 조회 실패 시 이미지 대체 화면 또는 동영상·문서 안내를 표시한다.
- 미사용·연결 해제 파일 정리에는 작성 취소·저장 실패 파일을 포함하고 활성 연결을 재확인한다. 삭제 실패는 대상 파일과 오류를 기록해 재처리한다. 정리는 내부 작업이며 공개 관리 API를 만들지 않는다.

## 구현 전 확인

- D19 — 형식·용량·사용처별 개수, 임시·연결 해제·소프트 삭제 원본의 보관기간, 복수 사용처 연결, 정리·파기 방식.
- D18 — 업로더·상태·사용처 연결·정리 상태 저장 구조. 현재 SQL에 없는 필드는 기능 개발 시 추가한다.
