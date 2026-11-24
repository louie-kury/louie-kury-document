# 커뮤니티·신고

**우선 개발.** PRD `COM-01·COM-02`, `NTF-01`, `MED-01`, `D08`, 요구사항정의서 C90:H103 기준. 게시글·댓글·반응·신고는 MySQL, 작성자 프로필은 MongoDB에서 조회한다.

[공통 계약](README.md#공통-계약)을 함께 적용한다. 아래 경로·필드·오류 코드는 API 설계 초안이며 미정 정책은 마지막 절에서 추적한다.

## 데이터 모델

| 모델 | 필드 |
| --- | --- |
| Author | `memberId:string`, `nickname:string`, `profileMedia:MediaRef 또는 null` |
| Board | `boardId:string`, `name:string` |
| Category | `categoryId:string`, `name:string` |
| PostWrite | `boardId:string`, `categoryId:string`, `title:string`, `content:string`, `mediaIds:string[]` |
| PostSummary | `postId:string`, `boardId:string`, `category:Category`, `title:string`, `author:Author`, `likeCount:integer`, `viewCount:integer`, `commentCount:integer`, `likedByMe:boolean 또는 null`, `createdAt:timestamp`, `updatedAt:timestamp 또는 null` |
| PostDetail | PostSummary + `content:string`, `media:MediaRef[]` |
| Comment | `commentId:string`, `postId:string`, `parentCommentId:string 또는 null`, `depth:integer`, `author:Author 또는 null`, `content:string 또는 null`, `deleted:boolean`, `likeCount:integer`, `replyCount:integer`, `likedByMe:boolean 또는 null`, `createdAt:timestamp`, `updatedAt:timestamp 또는 null` |
| Reaction | `liked:boolean`, `likeCount:integer` |
| ReportReason | `reasonCode:string`, `name:string` |
| ReportWrite | `targetType:string`, `targetId:string`, `reasonCodes:string[]`, `content:string`, `contextPostId?:string` (MEMBER 신고에서 필요) |
| ReportReceipt | `reportId:string`, `receivedAt:timestamp` |

게시글 생성에 boardId는 서버가 제공한 유일한 초기 게시판을 사용한다. 게시판은 이후 확장을 지원한다. 생성 필드 필수값·길이, 신고 사유·본문 필수 여부는 D08에서 확정한다. 비회원의 `likedByMe`는 null이며 회원의 실제 상태를 임의로 false 처리하지 않는다. 삭제 댓글은 본문 null과 deleted=true로 반환하고 화면에서 “삭제된 댓글입니다”로 표시한다.

## 엔드포인트

### `GET /api/boards`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/boards` | 공개 | 없음 | `Board[]` / 200 | 공통 오류 |

요청 예시:

```http
GET /api/boards HTTP/1.1
```

응답 예시 (`200`):

```json
{
  "data": [
    {
      "boardId": "board_01",
      "name": "자유게시판"
    }
  ]
}
```

### `GET /api/boards/{boardId}/categories`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/boards/{boardId}/categories` | 공개 | 경로 boardId | `Category[]` / 200 | 404 NOT_FOUND |

요청 예시:

```http
GET /api/boards/board_01/categories HTTP/1.1
```

응답 예시 (`200`):

```json
{
  "data": [
    {
      "categoryId": "category_01",
      "name": "일상"
    }
  ]
}
```

### `GET /api/posts`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/posts` | 공개 | `boardId,categoryId?,page,size` | `Page<PostSummary>` / 200 | 400 INVALID_FILTER, 404 NOT_FOUND |

요청 예시:

```http
GET /api/posts?boardId=board_01&page=0&size=20 HTTP/1.1
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

### `GET /api/posts/{postId}`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/posts/{postId}` | 공개 | 경로 postId | `PostDetail` / 200 | 404 NOT_FOUND |

요청 예시:

```http
GET /api/posts/post_01 HTTP/1.1
```

응답 예시 (`200`):

```json
{
  "data": {
    "postId": "post_01",
    "boardId": "board_01",
    "category": {
      "categoryId": "category_01",
      "name": "일상"
    },
    "title": "안녕하세요",
    "author": {
      "memberId": "member_01",
      "nickname": "루이집사",
      "profileMedia": null
    },
    "likeCount": 0,
    "viewCount": 1,
    "commentCount": 0,
    "likedByMe": null,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": null,
    "content": "반갑습니다.",
    "media": []
  }
}
```

### `POST /api/posts`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `POST /api/posts` | 필수 | JSON `PostWrite` | `PostDetail` / 201 | 400 VALIDATION_ERROR, 409 MEDIA_NOT_READY, 422 ATTACHMENT_LIMIT_EXCEEDED |

요청 예시:

```http
POST /api/posts HTTP/1.1
Authorization: Bearer <액세스 토큰>
Idempotency-Key: <요청별 고유 키>
Content-Type: application/json

{
  "boardId": "board_01",
  "categoryId": "category_01",
  "title": "안녕하세요",
  "content": "반갑습니다.",
  "mediaIds": []
}
```

응답 예시 (`201`):

```json
{
  "data": {
    "postId": "post_01",
    "boardId": "board_01",
    "category": {
      "categoryId": "category_01",
      "name": "일상"
    },
    "title": "안녕하세요",
    "author": {
      "memberId": "member_01",
      "nickname": "루이집사",
      "profileMedia": null
    },
    "likeCount": 0,
    "viewCount": 1,
    "commentCount": 0,
    "likedByMe": false,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": null,
    "content": "반갑습니다.",
    "media": []
  }
}
```

### `PATCH /api/posts/{postId}`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `PATCH /api/posts/{postId}` | 필수·작성자 | JSON `title?,content?,mediaIds?` | `PostDetail` / 200 | 400 EMPTY_UPDATE, 404 NOT_FOUND, 422 ATTACHMENT_LIMIT_EXCEEDED |

요청 예시:

```http
PATCH /api/posts/post_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
Content-Type: application/json

{
  "title": "수정한 제목"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "postId": "post_01",
    "boardId": "board_01",
    "category": {
      "categoryId": "category_01",
      "name": "일상"
    },
    "title": "안녕하세요",
    "author": {
      "memberId": "member_01",
      "nickname": "루이집사",
      "profileMedia": null
    },
    "likeCount": 0,
    "viewCount": 1,
    "commentCount": 0,
    "likedByMe": false,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": null,
    "content": "반갑습니다.",
    "media": []
  }
}
```

### `DELETE /api/posts/{postId}`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `DELETE /api/posts/{postId}` | 필수·작성자 | 경로 postId | 본문 없음 / 204 | 404 NOT_FOUND |

요청 예시:

```http
DELETE /api/posts/post_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답: `204`, 본문 없음.

### `PUT /api/posts/{postId}/like`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `PUT /api/posts/{postId}/like` | 필수 | 본문 없음 | `Reaction` / 200 | 404 NOT_FOUND |

요청 예시:

```http
PUT /api/posts/post_01/like HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "liked": true,
    "likeCount": 1
  }
}
```

### `DELETE /api/posts/{postId}/like`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `DELETE /api/posts/{postId}/like` | 필수 | 본문 없음 | `Reaction` / 200 | 404 NOT_FOUND |

요청 예시:

```http
DELETE /api/posts/post_01/like HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "liked": false,
    "likeCount": 0
  }
}
```

### `GET /api/posts/{postId}/comments`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/posts/{postId}/comments` | 공개 | `page,size` 최상위만 | `Page<Comment>` / 200 | 404 NOT_FOUND |

요청 예시:

```http
GET /api/posts/post_01/comments?page=0&size=20 HTTP/1.1
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

### `GET /api/comments/{commentId}/replies`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/comments/{commentId}/replies` | 필수 | `page,size` 직계 답글 | `Page<Comment>` / 200 | 404 NOT_FOUND |

요청 예시:

```http
GET /api/comments/comment_01/replies?page=0&size=20 HTTP/1.1
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

### `POST /api/posts/{postId}/comments`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `POST /api/posts/{postId}/comments` | 필수 | JSON `content:string,parentCommentId?:string` | `Comment` / 201 | 400 INVALID_PARENT, 409 COMMENT_DEPTH_EXCEEDED, 404 NOT_FOUND |

요청 예시:

```http
POST /api/posts/post_01/comments HTTP/1.1
Authorization: Bearer <액세스 토큰>
Idempotency-Key: <요청별 고유 키>
Content-Type: application/json

{
  "content": "안녕하세요"
}
```

응답 예시 (`201`):

```json
{
  "data": {
    "commentId": "comment_01",
    "postId": "post_01",
    "parentCommentId": null,
    "depth": 1,
    "author": {
      "memberId": "member_01",
      "nickname": "루이집사",
      "profileMedia": null
    },
    "content": "안녕하세요",
    "deleted": false,
    "likeCount": 0,
    "replyCount": 0,
    "likedByMe": false,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": null
  }
}
```

### `PATCH /api/comments/{commentId}`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `PATCH /api/comments/{commentId}` | 필수·작성자 | JSON `content:string` | `Comment` / 200 | 404 NOT_FOUND, 409 COMMENT_HAS_REPLIES |

요청 예시:

```http
PATCH /api/comments/comment_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
Content-Type: application/json

{
  "content": "수정한 댓글"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "commentId": "comment_01",
    "postId": "post_01",
    "parentCommentId": null,
    "depth": 1,
    "author": {
      "memberId": "member_01",
      "nickname": "루이집사",
      "profileMedia": null
    },
    "content": "안녕하세요",
    "deleted": false,
    "likeCount": 0,
    "replyCount": 0,
    "likedByMe": false,
    "createdAt": "2026-11-19T10:00:00+09:00",
    "updatedAt": null
  }
}
```

### `DELETE /api/comments/{commentId}`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `DELETE /api/comments/{commentId}` | 필수·작성자 | 경로 commentId | 본문 없음 / 204 | 404 NOT_FOUND |

요청 예시:

```http
DELETE /api/comments/comment_01 HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답: `204`, 본문 없음.

### `PUT /api/comments/{commentId}/like`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `PUT /api/comments/{commentId}/like` | 필수 | 본문 없음 | `Reaction` / 200 | 404 NOT_FOUND |

요청 예시:

```http
PUT /api/comments/comment_01/like HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "liked": true,
    "likeCount": 1
  }
}
```

### `DELETE /api/comments/{commentId}/like`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `DELETE /api/comments/{commentId}/like` | 필수 | 본문 없음 | `Reaction` / 200 | 404 NOT_FOUND |

요청 예시:

```http
DELETE /api/comments/comment_01/like HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "liked": false,
    "likeCount": 0
  }
}
```

### `GET /api/report-reasons`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/report-reasons` | 필수 | `targetType:POST 또는 COMMENT 또는 MEMBER` | `ReportReason[]` / 200 | 400 INVALID_TARGET_TYPE |

요청 예시:

```http
GET /api/report-reasons?targetType=POST HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": [
    {
      "reasonCode": "<조회한 신고 사유 코드>",
      "name": "스팸"
    }
  ]
}
```

### `POST /api/reports`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `POST /api/reports` | 필수 | JSON `ReportWrite` | `ReportReceipt` / 201 | 400 INVALID_REPORT_REASON, 404 NOT_FOUND |

요청 예시:

```http
POST /api/reports HTTP/1.1
Authorization: Bearer <액세스 토큰>
Idempotency-Key: <요청별 고유 키>
Content-Type: application/json

{
  "targetType": "POST",
  "targetId": "post_01",
  "reasonCodes": [
    "<조회한 신고 사유 코드>"
  ],
  "content": "신고 내용"
}
```

응답 예시 (`201`):

```json
{
  "data": {
    "reportId": "report_01",
    "receivedAt": "2026-11-19T10:00:00+09:00"
  }
}
```

### `GET /api/members/{memberId}/profile`

| 메서드·경로 | 인증 | 요청 | 성공 data / 상태 | 주요 오류 |
| --- | --- | --- | --- | --- |
| `GET /api/members/{memberId}/profile` | 필수 | 경로 memberId | `{memberId,nickname,profileMedia}` / 200 | 404 NOT_FOUND |

요청 예시:

```http
GET /api/members/member_02/profile HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "memberId": "member_02",
    "nickname": "루이집사",
    "profileMedia": null
  }
}
```


## 처리 규칙

- 공개 게시글의 목록·상세·미디어·최상위 댓글은 비회원 열람이 가능하다. 글쓰기·좋아요·답글 조회·신고는 인증이 필요하다. 프런트의 로그인 안내와 서버의 401 검사를 함께 적용한다.
- 공개 Author에는 닉네임·프로필만 담고 이메일·전화번호·로그인 ID를 노출하지 않는다. 사용자 프로필 단독 조회의 비회원 허용 여부는 D08에서 정하며 현재 경로는 로그인 설계안이다.
- parentCommentId가 없으면 depth=1이다. 부모와 같은 postId인지 확인하고 부모 depth+1이 4를 넘으면 거절한다. 대댓글 조회에서도 원본 게시글의 공개·삭제 상태를 확인한다.
- 하위 답글의 존재 검사와 댓글 수정은 경쟁 요청에서도 일관되게 처리한다. 하위 답글이 있으면 수정 불가다. 삭제 댓글 중 답글이 남은 노드는 자리 표시를 유지하고, 답글이 없는 노드는 목록에서 숨긴다. 깊이와 부모 관계를 임의로 재배치하지 않는다.
- 게시글·댓글의 삭제·숨김은 직접 URL 접근과 관련 첨부에 반영한다. 삭제·숨김 글에 신규 댓글과 반응을 추가할 수 없다. 작성자만 수정·삭제한다.
- 좋아요 PUT/DELETE는 목표 상태를 지정한다. 중복·동시 요청으로 동일 반응이나 수가 증가하지 않으며 응답 카운트는 반영 결과와 일치한다.
- 게시글 PATCH의 mediaIds는 최종 첨부 목록이다. 생략하면 유지, 빈 배열이면 전부 제거다. 저장 실패 시 기존 첨부를 보존한다.
- 댓글 생성 성공과 연결된 알림 이벤트를 유실 없이 전달하고 재시도 시 중복 알림을 만들지 않는다. 대댓글은 직접 답글 대상 댓글 작성자에게 알린다. 자기 댓글·자기 대댓글 세부는 [알림 명세](notifications.md)를 따른다.
- ReportWrite의 targetType은 POST, COMMENT, MEMBER 설계안이며 대댓글도 COMMENT다. MEMBER는 게시글 작성자 신고를 뜻하며 접근 가능한 게시글 ID를 `contextPostId`로 함께 제출하는 안을 적용한다. 서버는 그 게시글 작성자가 targetId와 일치하는지 검증한다. 신고자는 인증 주체에서 결정한다.
- 신고 생성에는 공통 Idempotency-Key 제안을 적용한다. 같은 제출 재시도는 같은 접수 결과를 반환한다. 신고자·운영 처리 내용을 공개 프로필·댓글·알림에 노출하지 않는다.

## 구현 전 확인

- D08 — 게시글/댓글 길이·필수값, 신고 입력·사유, 중복 신고 정책, 목록 정렬, 프로필 공개 범위와 팔로우 목록의 비회원 접근.
- D15 — 자기 대댓글 알림과 이벤트 중복 방지·재전달 기준.
- D18·D19 — 작성자 UUID 타입 정합성, 부모/깊이·삭제 표시, 미디어 연결과 제한 설정.
