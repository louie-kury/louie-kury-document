# API 계약 — 팔로우·팔로잉

[PRD](../prd.md)의 COM-03·NTF-01, D08·D15, Q26과 요구사항정의서 12~17행을 반영한 설계 초안이다. [공통 계약](README.md)을 적용한다. 엔드포인트·필드명은 구현 계약 제안이며 미정인 공개 범위를 확정하지 않는다.

## 요청·응답 모델

- 모든 `memberId`는 외부 표현이 문자열이다. 인증된 요청자의 식별자는 액세스 토큰에서 읽는다.
- `FollowStatus`는 `{memberId:string, following:boolean}`이다. `following`은 요청자가 해당 사용자를 현재 팔로우하는지 나타낸다.
- `FollowCounts`는 `{memberId:string, followerCount:integer, followingCount:integer}`이다. 수는 0 이상이다.
- `FollowMember`는 `{memberId:string, nickname:string, following:boolean}`이다. 목록에 표시할 프로필 정보는 닉네임만 제안하며 `following`은 요청자와 해당 목록 항목 사이의 상태다.
- 목록 요청은 `page`, `size` 쿼리를 사용한다. 응답 `Page<FollowMember>`는 `{content:FollowMember[],page:integer,size:integer,totalElements:integer,totalPages:integer,hasNext:boolean}`이다. 기본값·허용 범위·정렬은 D08 미정이다.
- 성공 모델은 `{"data":...}`, 오류는 `{"code":"...","message":"..."}`로 감싼다. 204는 본문이 없다.

## 엔드포인트

`PUT`·`DELETE`의 `{memberId}`는 팔로우 **대상**이다. 목록 `GET`의 `{memberId}`는 팔로워·팔로잉 목록의 **소유자**다. 상태·수 조회의 `{memberId}`는 조회할 사용자다.

목록·수 조회의 비회원 허용 여부는 D08 미정이다. 표의 로그인 표시는 검토할 잠정 인증안이며 비회원 공개 정책의 확정 근거로 사용하지 않는다. 변경과 본인 기준 상태 조회는 로그인한다.

| 요청 | 인증 | 입력 | 성공 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `PUT /api/members/{memberId}/following` | 로그인 | 경로 `memberId`, 본문 없음 | 200 `FollowStatus` (`following:true`) | 400 `SELF_FOLLOW_NOT_ALLOWED`, 401 `UNAUTHORIZED`, 404 `NOT_FOUND` | COM-03, 시트 12행 |
| `DELETE /api/members/{memberId}/following` | 로그인 | 경로 `memberId`, 본문 없음 | 204 | 400 `SELF_FOLLOW_NOT_ALLOWED`, 401 `UNAUTHORIZED`, 404 `NOT_FOUND` | COM-03, 시트 13행 |
| `GET /api/members/{memberId}/followers` | 로그인 잠정안 | 경로 `memberId`, 쿼리 `page`, `size` | 200 `Page<FollowMember>` | 400 `VALIDATION_ERROR`, 401 `UNAUTHORIZED`, 404 `NOT_FOUND` | COM-03, 시트 14행, D08 |
| `GET /api/members/{memberId}/following` | 로그인 잠정안 | 경로 `memberId`, 쿼리 `page`, `size` | 200 `Page<FollowMember>` | 400 `VALIDATION_ERROR`, 401 `UNAUTHORIZED`, 404 `NOT_FOUND` | COM-03, 시트 15행, D08 |
| `GET /api/members/{memberId}/follow-status` | 로그인 | 경로 `memberId` | 200 `FollowStatus` | 401 `UNAUTHORIZED`, 404 `NOT_FOUND` | COM-03, 시트 16행 |
| `GET /api/members/{memberId}/follow-counts` | 로그인 잠정안 | 경로 `memberId` | 200 `FollowCounts` | 401 `UNAUTHORIZED`, 404 `NOT_FOUND` | COM-03, 시트 17행, D08 |

## 처리 규칙

- 팔로우·언팔로우의 주체는 항상 요청자다. 본문·쿼리로 다른 주체를 지정하지 않는다. 다른 사용자의 관계를 취소할 수 없다.
- 자기 팔로우는 거부한다. 요청자·대상 조합은 한 관계만 유지하며 동시 PUT과 재시도로 목록·수가 늘어나지 않는다. 이미 존재하는 관계에 대한 PUT은 현재 상태 200을 반환하는 멱등 계약을 제안한다.
- 언팔로우는 언제든 가능하다. 이미 없는 본인 관계의 DELETE도 204로 응답하며 상대 사용자 자체가 없으면 404다. 삭제 대상은 해당 요청자의 관계에 한정한다.
- `followers`는 해당 사용자를 팔로우하는 사람, `following` 목록은 해당 사용자가 팔로우하는 사람이다. 다른 사용자의 목록·수를 조회할 수 있고, 요청자 기준 현재 팔로우 상태는 관계 데이터와 일치해야 한다. 빈 목록은 200과 빈 `content`, 수는 0으로 반환한다.
- 새 팔로우 관계가 성립하면 상대에게 알림 생성 이벤트를 전달한다. 이미 존재하는 관계의 PUT은 새 알림을 만들지 않고 같은 이벤트의 재전달도 수신자별 한 번만 처리한다. 언팔로우 알림은 만들지 않는다. [알림 계약](notifications.md)
- 관계 저장과 알림 전달 사이의 실패를 복구할 수 있어야 한다. 알림 전달 재시도를 위해 이미 성공한 관계를 중복 생성하지 않는다. 실패한 요청을 성공한 팔로우로 표시하지 않는다.
- 프로필의 팔로우 상태와 목록·수는 같은 관계 상태를 기준으로 조회한다. 조회 사이에 다른 변경이 발생할 수 있으므로 서로 다른 시점의 응답 수가 같다고 보장하지 않는다.

## 미정 항목

- D08에서 비회원 목록·수 조회 허용 여부, 목록 정렬과 페이지 기본값·범위를 결정한다. 비회원 공개를 허용하면 요청자 기준 `following` 필드의 처리도 정한다.
- D15에서 언팔로우 후 다시 팔로우할 때의 이벤트 식별과 중복 방지 보관 기준을 결정한다. 재팔로우 알림의 생성 여부를 기존 요청 재시도 규칙만으로 확정하지 않는다.
