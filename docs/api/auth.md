# 계정·인증 API

우선 개발 대상은 일반·카카오·네이버 가입과 로그인, 아이디·비밀번호 찾기다. 마이페이지·탈퇴는 PRD의 후속 계정 기능으로 함께 기록한다. 근거는 [PRD ACC-01·ACC-03](../prd.md#61-보호자-계정--acc)과 요구사항정의서 `(필수3)요구사항정의서` 6~11행·34~36행이다. 공통 응답·오류 형식은 [API 안내](README.md)를 따른다.

이메일 인증과 일반 가입에는 현재 인증 서비스 구현을 함께 표시한다. 그 밖의 경로·필드·토큰 교환 흐름은 API 설계 초안이다. PRD에서 미정인 본인확인 세부 정책은 D11·D18에 따라 확정한 후 구현한다.

## 데이터 모델

`?`는 요청 필드 생략 가능을 뜻한다. 응답에서 NULL 가능한 필드는 `타입?`로 표시한다. 모든 식별자는 문자열이다.

| 모델 | 필드 |
| --- | --- |
| EmailVerificationRequest | `email:string`, `purpose:SIGNUP 또는 EMAIL_CHANGE` |
| VerificationChallenge | `verificationId:string`, `expiresAt:datetime` |
| VerificationConfirmRequest | `code:string` |
| EmailVerificationProof | `emailVerificationToken:string`, `expiresAt:datetime` |
| SignupRequest | `name:string`, `phoneNumber:string`, `gender:string`, `birthDate:date`, `address:string`, `nickname:string`, `loginId:string`, `password:string`, `email:string`, `emailVerificationToken:string` |
| SignupResult | `memberId:string` |
| LoginRequest | `loginId:string`, `password:string` |
| SessionResult | `accessToken:string`, `tokenType:Bearer`, `expiresAt:datetime`, `memberId:string` |
| OAuthLoginResult | `result:LOGIN`, `session:SessionResult` |
| OAuthSignupRequiredResult | `result:SIGNUP_REQUIRED`, `signupTicket:string`, `expiresAt:datetime`, `suggestedNickname:string?` |
| OAuthSignupRequest | `signupTicket:string`, `email:string`, `emailVerificationToken:string`, `name:string`, `phoneNumber:string`, `nickname?:string` |
| RecoveryRequest | `email:string` |
| LoginIdRecoveryRequest | `verificationId:string`, `code:string` |
| LoginIdResult | `loginId:string` |
| PasswordResetRequest | `name:string`, `loginId:string` |
| PasswordResetVerificationRequest | `verificationId:string`, `code:string` |
| PasswordResetProof | `passwordResetToken:string`, `expiresAt:datetime` |
| PasswordResetCompleteRequest | `passwordResetToken:string`, `newPassword:string` |
| MemberProfile | `memberId:string`, `nickname:string`, `email:string`, `phoneNumber:string`, `petCount:integer`, `profileMedia:MediaRef?` |
| MemberPatchRequest | `nickname?:string`, `email?:string`, `emailVerificationToken?:string`, `phoneNumber?:string`, `profileMediaId?:string 또는 null` |
| PasswordChangeRequest | `currentPassword:string`, `newPassword:string` |

- `date`는 `YYYY-MM-DD`, `datetime`은 오프셋을 포함한 ISO 8601이다. 일반 가입 구현은 성별 코드 `MALE`·`FEMALE`, 숫자로만 된 전화번호와 단일 주소 문자열을 받는다. 주소 검색·상세 주소 방식은 별도 설계 사항이다.
- 일반 가입 필수 입력은 이름·전화번호·성별·생년월일·주소·닉네임·아이디·비밀번호·이메일과 이메일 인증 증명이다. 현재 구현의 입력 제한은 아래 가입 API에 적는다. 비밀번호 기준은 PRD의 8~20자와 조합 요구와 다르므로 정책 차이를 확인해야 한다.
- 약관 내용은 MongoDB에, 계정의 약관 동의 여부는 MySQL에 저장하는 기존 설계다. 현재 가입 구현의 동의 값은 임시 처리이며 실제 동의 기록이 아니다. 가입 요청의 동의 필드와 약관별 필수 여부·버전은 상세 정책 확정 후 정한다.
- 소셜 이름·전화번호는 서버가 검증한 제공자 정보로 보완할 수 있으며, 누락된 값은 가입 완료 전에 직접 입력한다. `OAuthSignupRequest`의 필드는 제공값을 적용한 최종 제출값이다.
- 소셜 닉네임을 입력하지 않으면 검증된 제공자 닉네임을 사용하고, 제공값도 없으면 서버가 랜덤 생성한다. 생성값은 나중에 수정할 수 있다.
- 비밀번호·인증번호·검증 토큰은 요청 또는 해당 검증 응답에서만 전달한다. 계정·프로필 조회 응답에 비밀번호나 비밀번호 해시를 포함하지 않는다.

## 이메일 인증과 일반 가입

일반 회원가입 이메일 인증에는 앞뒤 공백을 제거한 ASCII 이메일만 허용하고, 비교할 때는 이메일 전체의 대소문자를 구분하지 않는다. 예를 들어 `User@example.com`과 `user@example.com`은 같다. 점이나 `+` 뒤 문자열을 임의로 제거하지 않는다. 실제 메일 발송에는 앞뒤 공백을 제거한 입력 주소의 대소문자를 유지한다. 다른 이메일 관련 흐름에 적용할 때도 이 비교 기준과 저장소 제약의 일관성을 확인한다. 개인정보 저장 방식에 관한 기존 PRD와 #3 결정의 차이는 별도 확인 사항이다.

### `POST /api/auth/email-verifications`

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/email-verifications` | SIGNUP 공개, EMAIL_CHANGE 본인 Bearer | EmailVerificationRequest | `202 VerificationChallenge` | 400 VALIDATION_ERROR, 409 EMAIL_ALREADY_EXISTS, 429 RATE_LIMITED, 503 VERIFICATION_DELIVERY_FAILED·VERIFICATION_UNAVAILABLE | ACC-01, D11 |

현재 인증 서비스는 `SIGNUP` 발송을 구현했다. `EMAIL_CHANGE`는 설계 초안이며 이번 구현 범위가 아니다. `202`는 Brevo의 발송 요청 수락을 뜻하며 실제 수신을 보장하지 않는다. 이전 구현에서 실제 발송·수신, 확인 및 발급된 증명을 이용한 가입을 확인했다. 최신 변경 후 실제 서버 연동은 재검증하지 않았다.

요청 예시:

```http
POST /api/auth/email-verifications HTTP/1.1
Content-Type: application/json

{
  "email": "caregiver@example.com",
  "purpose": "SIGNUP"
}
```

응답 예시 (`202`):

```json
{
  "data": {
    "verificationId": "verify_01",
    "expiresAt": "2026-11-19T10:05:00+09:00"
  }
}
```

### `POST /api/auth/email-verifications/{verificationId}/confirm`

인증 서비스에 `SIGNUP` 확인과 가입 증명 발급 및 가입 API의 일회성 증명 소비를 구현했다.

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/email-verifications/{verificationId}/confirm` | 공개, 발송한 SIGNUP 인증 요청 ID와 코드 | VerificationConfirmRequest | `200 EmailVerificationProof` | 400 VALIDATION_ERROR·INVALID_VERIFICATION_CODE, 404 NOT_FOUND, 409 VERIFICATION_EXPIRED, 429 RATE_LIMITED, 503 VERIFICATION_UNAVAILABLE | ACC-01, D11 |

`verificationId`는 발송 응답에서 받은 값을 사용하고 `code`는 메일에 기재된 숫자 6자리를 문자열로 전달한다. 앞의 0을 보존해야 한다. 성공 시 반환한 증명은 민감한 값이므로 로그나 공유 문서에 기록하지 않는다.

발급 후 24시간 동안 남는 상태 표식으로 만료된 요청은 `409 VERIFICATION_EXPIRED`로 구분한다. 없는 ID, 재발송으로 무효화된 ID, 이미 성공한 ID 또는 표식 보관기간이 지난 ID는 `404 NOT_FOUND`다. 번호별 5회째 실패는 해당 번호를 무효화하고 보통 `400 INVALID_VERIFICATION_CODE`를 반환하며, 이후 같은 ID는 `404 NOT_FOUND`다. 그 실패가 이메일별 최근 1시간 내 10번째 실패이기도 하면 `429 RATE_LIMITED`가 우선한다. 10번째 실패 시점부터 1시간 동안 해당 이메일의 활성 인증번호 확인을 제한한다. 잠금 상태에서 재발송은 가능하지만 새 번호 확인도 제한된다. 성공하더라도 최근 1시간 실패 기록은 조기 초기화하지 않는다.

요청 예시:

```http
POST /api/auth/email-verifications/verify_01/confirm HTTP/1.1
Content-Type: application/json

{
  "code": "123456"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "emailVerificationToken": "<이메일 인증 증명>",
    "expiresAt": "2026-11-19T10:05:00+09:00"
  }
}
```

### `POST /api/auth/signup`

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/signup` | 공개, SIGNUP 인증 증명 | SignupRequest | `201 SignupResult` | 400 VALIDATION_ERROR·INVALID_EMAIL_VERIFICATION, 409 EMAIL_ALREADY_EXISTS·LOGIN_ID_ALREADY_EXISTS·NICKNAME_ALREADY_EXISTS, 503 VERIFICATION_UNAVAILABLE·SIGNUP_PENDING | ACC-01, D11·D18 |

현재 구현은 멱등 키를 사용하지 않는다. 비밀번호를 제외한 필수 문자열은 공백만 입력할 수 없고 길이는 Unicode 코드 포인트 기준이다. 이름·아이디·증명은 최대 100자, 전화번호는 숫자만 최대 30자, 주소는 최대 255자, 닉네임은 최대 30자다. 생년월일은 `1000-01-01`부터 `9999-12-31`까지이며, 비밀번호는 조합 제한 없이 8~128 코드 포인트다. 이메일은 ASCII 형식이며 최대 254자다. 입력을 검증한 뒤 증명을 소비한다.

요청 예시:

```http
POST /api/auth/signup HTTP/1.1
Content-Type: application/json

{
  "name": "김보호",
  "phoneNumber": "01000000000",
  "gender": "FEMALE",
  "birthDate": "1995-01-01",
  "address": "서울특별시",
  "nickname": "루이집사",
  "loginId": "loui-care",
  "password": "Example!123",
  "email": "caregiver@example.com",
  "emailVerificationToken": "<이메일 인증 증명>"
}
```

응답 예시 (`201`):

```json
{
  "data": {
    "memberId": "member_01"
  }
}
```


### 아이디·닉네임 사용 가능 여부

| Method·경로 | 요청 | 성공 응답 | 주요 오류 |
| --- | --- | --- | --- |
| `GET /api/auth/login-ids/availability` | `loginId` 쿼리, 최대 100 코드 포인트 | `200`, `data.available:boolean` | 400 VALIDATION_ERROR |
| `GET /api/auth/nicknames/availability` | `nickname` 쿼리, 최대 30 코드 포인트 | `200`, `data.available:boolean` | 400 VALIDATION_ERROR |

두 값은 필수이며 공백만 입력할 수 없다. 조회 결과는 값을 예약하지 않으므로 실제 가입 시에도 중복을 검사한다.

### 가입 공통 처리

1. 일반·소셜 가입 모두 사용자가 직접 입력한 이메일로 인증번호를 발송하고 확인한다. 소셜 제공자의 이메일 인증 상태를 근거로 이 절차를 생략하지 않는다.
2. 인증 증명은 서버에서 이메일·목적·발급 절차·유효기간을 확인한다. 다른 이메일, EMAIL_CHANGE 증명 또는 만료된 증명으로 가입할 수 없다. EMAIL_CHANGE 인증 절차와 증명은 발급 요청자의 memberId에도 연결하고 이메일 변경 시 같은 본인인지 확인한다.
3. 한 이메일당 계정 하나를 허용하고 로그인 ID 중복도 거부한다. 동일 이메일의 일반·소셜 계정을 자동 병합하지 않는다.
4. 가입 성공 시 `Location: /api/members/me`를 반환한다. 가입 이후 로그인은 별도 로그인 API로 수행한다.
5. 현재 일반 가입 구현은 계정·로그인 정보·`user_profile`을 MySQL 트랜잭션에 저장한다. PRD의 일반 프로필 MongoDB 요구와 차이가 있으며 최종 저장소는 후속 검토한다.
6. 현재 일반 가입은 이메일·목적·유효기간을 확인한 증명을 Redis에서 원자적으로 한 번 소비한다. 이후 중복이나 DB 저장 실패가 발생해도 증명은 복원되지 않으므로 다시 인증해야 한다. 동일 요청의 성공 결과 복구나 멱등 키는 지원하지 않는다. 소셜 가입은 설계 초안이다.

### 일반 가입 이메일 인증 정책

- 서버는 암호학적으로 안전한 난수로 숫자 6자리 인증번호를 발급한다. 번호는 5분간 유효하며 성공 시 한 번만 사용할 수 있다.
- 재발송은 60초 후 가능하며, 새 번호를 발급하면 이전 번호를 무효화한다. 동일 이메일은 1시간당 5회, 동일 IP는 1시간당 100회로 발송을 제한한다. 현재 구현은 연결의 원격 IP를 사용하고 임의 전달 헤더를 신뢰하지 않는다. 프록시 배포에서는 신뢰할 수 있는 프록시 설정이 필요하다.
- 발송 요청은 Brevo 트랜잭션 메일 API를 사용한다. 발송 실패 또는 결과가 불명확하더라도 제한 횟수는 차감하고 이전 번호는 무효로 유지한다. API 요청 수락과 실제 이메일 수신은 구분한다.
- 한 번호의 입력이 5회 실패하면 해당 번호를 무효화한다. 재발송해도 이메일별 누적 실패 횟수는 초기화하지 않는다. 최근 1시간에 누적 10회 틀리면 10번째 실패부터 1시간 동안 해당 이메일의 활성 인증번호 확인을 제한한다. 재발송은 제한하지 않으며 성공해도 기존 실패 기록은 해당 기간 동안 유지한다.
- 인증 성공 시 해당 이메일과 SIGNUP 목적에 연결된 일회성 가입 증명을 발급한다. 증명은 10분간 유효하며 이메일을 변경하면 다시 인증한다. 화면에는 가장 최근에 발송한 번호를 입력하도록 안내한다.
- 인증 요청 ID, 이메일 확인값, 인증번호 확인값, 목적, 만료 시각, 실패 횟수와 발송 제한 정보, 가입 증명은 Redis에 저장하고 각 유효기간에 맞는 TTL을 적용한다. 이메일과 인증번호 확인값은 각각 별도 비밀키로 HMAC을 계산한다. 가입 증명도 원문 대신 HMAC 확인값으로 저장한다. 인증번호와 증명 원문은 로그에 남기지 않는다.
- 가입 요청에서 유효한 증명은 원자적으로 소비되며 다른 가입에 재사용할 수 없다. Redis 장애로 증명을 확인할 수 없으면 가입을 완료하지 않는다. 증명 소비 후 저장 실패는 재인증이 필요하다.

## 로그인·소셜 가입·세션

`provider`의 경로 값은 `kakao`, `naver`만 허용한다. 제공자의 인가 응답은 서버가 직접 검증하고 계정 식별값을 얻는다.

### `POST /api/auth/login`

| Method·경로 | 인증 | 요청 | 성공 응답의 data 또는 헤더 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/login` | 공개 | LoginRequest | `200 SessionResult`, refresh cookie 설정 | 400 VALIDATION_ERROR, 401 INVALID_CREDENTIALS, 403 ACCOUNT_UNAVAILABLE | ACC-01 |

요청 예시:

```http
POST /api/auth/login HTTP/1.1
Content-Type: application/json

{
  "loginId": "loui-care",
  "password": "Example!123"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "accessToken": "<액세스 토큰>",
    "tokenType": "Bearer",
    "expiresAt": "2026-11-19T10:05:00+09:00",
    "memberId": "member_01"
  }
}
```

### `GET /api/auth/oauth/{provider}/authorize`

| Method·경로 | 인증 | 요청 | 성공 응답의 data 또는 헤더 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `GET /api/auth/oauth/{provider}/authorize` | 공개 | 브라우저 이동, 임의 redirect URL 입력 없음 | `302 Location` 제공자 인가 화면, 본문 없음 | 400 UNSUPPORTED_PROVIDER, 503 OAUTH_UNAVAILABLE | ACC-01, D11 |

요청 예시:

```http
GET /api/auth/oauth/kakao/authorize HTTP/1.1
```

응답: `302`와 `Location` 헤더. 이동 URL은 제공자 또는 허용된 프런트 설정에 따른다. 본문은 없다.

### `GET /api/auth/oauth/{provider}/callback`

| Method·경로 | 인증 | 요청 | 성공 응답의 data 또는 헤더 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `GET /api/auth/oauth/{provider}/callback` | 서버가 시작한 OAuth 절차 | 제공자 `code`, `state`, 실패 시 제공자 오류 | `302 Location` 허용된 프런트 완료 화면, 본문 없음 | 제공자 거절·state 불일치·검증 실패는 프런트 실패 화면으로 이동 | ACC-01, D11 |

요청 예시:

```http
GET /api/auth/oauth/kakao/callback?code=<제공자_인가_코드>&state=<요청_state> HTTP/1.1
```

응답: `302`와 `Location` 헤더. 이동 URL은 제공자 또는 허용된 프런트 설정에 따른다. 본문은 없다.

### `POST /api/auth/oauth/exchanges`

| Method·경로 | 인증 | 요청 | 성공 응답의 data 또는 헤더 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/oauth/exchanges` | 일회성 교환 증명 | `{exchangeTicket:string}` | `200 OAuthLoginResult` 또는 `OAuthSignupRequiredResult`; LOGIN이면 refresh cookie 설정 | 400 INVALID_OAUTH_TICKET, 403 ACCOUNT_UNAVAILABLE, 409 OAUTH_TICKET_USED | ACC-01, D11 |

요청 예시:

```http
POST /api/auth/oauth/exchanges HTTP/1.1
Content-Type: application/json

{
  "exchangeTicket": "<교환 증명>"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "result": "SIGNUP_REQUIRED",
    "signupTicket": "<가입 증명>",
    "expiresAt": "2026-11-19T10:05:00+09:00",
    "suggestedNickname": null
  }
}
```

`LOGIN` 응답도 가능하다. `result`와 `session`은 위 데이터 모델을 따른다.

### `POST /api/auth/oauth/signup`

| Method·경로 | 인증 | 요청 | 성공 응답의 data 또는 헤더 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/oauth/signup` | signupTicket·SIGNUP 이메일 증명 | OAuthSignupRequest, `Idempotency-Key` | `201 SignupResult` | 400 INVALID_OAUTH_TICKET, 400 INVALID_EMAIL_VERIFICATION, 409 EMAIL_ALREADY_REGISTERED, 409 ACCOUNT_CONFLICT, 409 IDEMPOTENCY_CONFLICT, 503 SIGNUP_PENDING | ACC-01, D11·D18 |

요청 예시:

```http
POST /api/auth/oauth/signup HTTP/1.1
Idempotency-Key: <요청별 고유 키>
Content-Type: application/json

{
  "signupTicket": "<가입 증명>",
  "email": "caregiver@example.com",
  "emailVerificationToken": "<이메일 인증 증명>",
  "name": "김보호",
  "phoneNumber": "01000000000"
}
```

응답 예시 (`201`):

```json
{
  "data": {
    "memberId": "member_01"
  }
}
```

### `POST /api/auth/refresh`

| Method·경로 | 인증 | 요청 | 성공 응답의 data 또는 헤더 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/refresh` | refresh cookie | 본문 없음, 쿠키 요청 보호 정보 | `200 SessionResult`, refresh cookie 교체 | 401 INVALID_REFRESH_TOKEN, 403 ACCOUNT_UNAVAILABLE | ACC-01, D11 |

요청 예시:

```http
POST /api/auth/refresh HTTP/1.1
```

요청에 refresh 쿠키와 확정된 쿠키 보호 정보를 함께 전달한다.

응답 예시 (`200`):

```json
{
  "data": {
    "accessToken": "<액세스 토큰>",
    "tokenType": "Bearer",
    "expiresAt": "2026-11-19T10:05:00+09:00",
    "memberId": "member_01"
  }
}
```

### `POST /api/auth/logout`

| Method·경로 | 인증 | 요청 | 성공 응답의 data 또는 헤더 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/logout` | 현재 세션·refresh cookie | 본문 없음, 쿠키 요청 보호 정보 | `204`, cookie 만료 | 403 REQUEST_ORIGIN_REJECTED | ACC-01, D11 |

요청 예시:

```http
POST /api/auth/logout HTTP/1.1
```

요청에 refresh 쿠키와 확정된 쿠키 보호 정보를 함께 전달한다.

응답: `204`, 본문 없음.


### 로그인·소셜 가입 공통 처리

- 서버는 `state`를 시작 세션과 연결하여 검증한다. 실패 콜백을 정상 로그인으로 처리하지 않는다. 제공자 거절·state 오류·제공자 장애는 고정된 프런트 완료 경로에서 구분 가능한 오류 코드로 안내한다.
- 콜백은 허용 목록의 프런트 완료 URL로만 이동한다. URL에는 짧게 유지하는 일회성 `exchangeTicket` 또는 공개 가능한 오류 코드만 담고 액세스·리프레시 토큰을 담지 않는다. 교환 증명은 시작한 브라우저 절차와 연결하고 교환 시 한 번만 사용한다.
- `LOGIN`은 이미 연결된 제공자·식별값의 계정이다. `SIGNUP_REQUIRED`는 서버가 검증한 제공자 식별값에 연결된 가입 증명만 발급한다. 클라이언트가 제출한 `providerId`로 소셜 계정을 만들지 않는다.
- 가입하지 않은 소셜 계정은 직접 입력한 이메일의 인증을 완료한 뒤 가입한다. 이미 가입된 이메일이면 신규 가입을 제한하고 기존 계정 로그인으로 안내한다. 자동 계정 연결은 수행하지 않는다. 기존 계정과의 수동 연결 정책은 D11 미정이다.
- 소셜 계정의 비밀번호는 NULL이다. 소셜 가입 요청은 비밀번호를 받지 않는다. 기존 계정 비밀번호를 소셜 제공자에 전달하지 않는다.
- 가입과 세션 발급의 재시도는 계정·소셜 연결·프로필을 중복 생성하지 않는다. 가입된 계정이 이용 불가 상태면 세션을 발급하지 않는다.

### 세션 설계 제안

액세스 토큰은 Bearer로 전달하고 리프레시 토큰은 `HttpOnly`, `Secure` 쿠키로 보관하는 안이다. 배포 도메인에 맞는 `SameSite`·쿠키 범위·CORS·CSRF 보호 방식과 토큰 유효기간은 D11에서 확정한다. 쿠키 기반 갱신·로그아웃은 요청 Origin과 확정된 CSRF 증명을 검증한다.

갱신 성공 시 리프레시 토큰을 회전하고 이전 토큰 재사용을 탐지한다. 동시에 갱신하거나 네트워크 실패로 재시도할 때 정상 세션이 손실되지 않도록 회전·재시도 계약을 함께 확정한다. 로그아웃은 서버의 해당 갱신 세션을 폐기하고, 이미 종료된 세션으로 다시 요청해도 204를 반환한다. 액세스 토큰의 로그아웃 후 효력·전체 기기 로그아웃 여부도 D11에서 정한다.

## 아이디 찾기와 비밀번호 복구

아이디 찾기는 입력한 가입 이메일로 인증번호를 보내고 확인된 경우에만 아이디를 반환한다. 비밀번호 복구의 본인확인 수단은 D11 미정이다. 아래 비밀번호 복구는 가입 이메일 인증번호를 사용하는 설계 제안이며, 이름·아이디 일치만으로 변경 권한을 부여하지 않는다.

### `POST /api/auth/login-id/recovery-requests`

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/login-id/recovery-requests` | 공개 | RecoveryRequest | `202 VerificationChallenge` | 400 VALIDATION_ERROR, 429 RATE_LIMITED, 503 VERIFICATION_DELIVERY_FAILED | ACC-01, D11 |

요청 예시:

```http
POST /api/auth/login-id/recovery-requests HTTP/1.1
Content-Type: application/json

{
  "email": "caregiver@example.com"
}
```

응답 예시 (`202`):

```json
{
  "data": {
    "verificationId": "verify_01",
    "expiresAt": "2026-11-19T10:05:00+09:00"
  }
}
```

### `POST /api/auth/login-id/recoveries`

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/login-id/recoveries` | 아이디 찾기용 인증 절차 | LoginIdRecoveryRequest | `200 LoginIdResult` | 400 INVALID_VERIFICATION_CODE, 404 NOT_FOUND, 409 VERIFICATION_EXPIRED, 429 RATE_LIMITED | ACC-01, D11 |

요청 예시:

```http
POST /api/auth/login-id/recoveries HTTP/1.1
Content-Type: application/json

{
  "verificationId": "verify_01",
  "code": "123456"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "loginId": "loui-care"
  }
}
```

### `POST /api/auth/password/reset-requests`

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/password/reset-requests` | 공개 | PasswordResetRequest | `202 VerificationChallenge` | 400 VALIDATION_ERROR, 429 RATE_LIMITED, 503 VERIFICATION_DELIVERY_FAILED | ACC-01, D11 |

요청 예시:

```http
POST /api/auth/password/reset-requests HTTP/1.1
Content-Type: application/json

{
  "name": "김보호",
  "loginId": "loui-care"
}
```

응답 예시 (`202`):

```json
{
  "data": {
    "verificationId": "verify_01",
    "expiresAt": "2026-11-19T10:05:00+09:00"
  }
}
```

### `POST /api/auth/password/reset-verifications`

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/password/reset-verifications` | 비밀번호 복구용 인증 절차 | PasswordResetVerificationRequest | `200 PasswordResetProof` | 400 INVALID_VERIFICATION_CODE, 404 NOT_FOUND, 409 VERIFICATION_EXPIRED, 429 RATE_LIMITED | ACC-01, D11 |

요청 예시:

```http
POST /api/auth/password/reset-verifications HTTP/1.1
Content-Type: application/json

{
  "verificationId": "verify_01",
  "code": "123456"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "passwordResetToken": "<재설정 증명>",
    "expiresAt": "2026-11-19T10:05:00+09:00"
  }
}
```

### `POST /api/auth/password/resets`

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/password/resets` | 비밀번호 복구 증명 | PasswordResetCompleteRequest | `204`, 본문 없음 | 400 INVALID_PASSWORD_RESET, 400 VALIDATION_ERROR, 409 PASSWORD_UNAVAILABLE | ACC-01, D11 |

요청 예시:

```http
POST /api/auth/password/resets HTTP/1.1
Content-Type: application/json

{
  "passwordResetToken": "<재설정 증명>",
  "newPassword": "Example!456"
}
```

응답: `204`, 본문 없음.


### 계정 복구 공통 처리

- 복구 요청의 접수 응답은 계정 존재 여부를 구별하지 않는 형식으로 제안한다. 해당 계정이 확인되고 발송이 가능한 경우에만 실제 인증번호를 보내며, 유효한 증명을 확인하기 전에는 아이디·가입 이메일 등 계정 정보를 공개하지 않는다.
- 가입 이메일 인증, 이메일 변경, 아이디 찾기, 비밀번호 재설정의 증명은 서로 바꿔 사용할 수 없다. 각 절차의 확인 완료와 결과 사용을 서버에서 기록한다.
- `passwordResetToken`은 대상 계정·목적·유효기간에 연결하고 비밀번호 변경 성공 시 한 번만 사용한다. 재시도로 다른 비밀번호가 덮어써지지 않도록 소비와 계정 갱신을 일관되게 처리한다.
- 소셜 전용 계정에 일반 비밀번호를 생성하는 동작은 D11 확정 후 제공한다. 기존 세션 폐기 범위와 재설정 완료 안내도 함께 정한다.

## 내 회원정보와 탈퇴

### `GET /api/members/me`

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `GET /api/members/me` | 본인 Bearer | 없음 | `200 MemberProfile` | 401 UNAUTHORIZED, 403 ACCOUNT_UNAVAILABLE | ACC-01 |

요청 예시:

```http
GET /api/members/me HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답 예시 (`200`):

```json
{
  "data": {
    "memberId": "member_01",
    "nickname": "루이집사",
    "email": "caregiver@example.com",
    "phoneNumber": "01000000000",
    "petCount": 1,
    "profileMedia": null
  }
}
```

### `PATCH /api/members/me`

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `PATCH /api/members/me` | 본인 Bearer | MemberPatchRequest | `200 MemberProfile` | 400 VALIDATION_ERROR, 400 INVALID_EMAIL_VERIFICATION, 409 EMAIL_ALREADY_REGISTERED, 409 PROFILE_UPDATE_CONFLICT, 400 INVALID_MEDIA_REFERENCE | ACC-01, MED-01, D11·D18·D19 |

요청 예시:

```http
PATCH /api/members/me HTTP/1.1
Authorization: Bearer <액세스 토큰>
Content-Type: application/json

{
  "nickname": "루이집사"
}
```

응답 예시 (`200`):

```json
{
  "data": {
    "memberId": "member_01",
    "nickname": "루이집사",
    "email": "caregiver@example.com",
    "phoneNumber": "01000000000",
    "petCount": 1,
    "profileMedia": null
  }
}
```

### `PUT /api/members/me/password`

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `PUT /api/members/me/password` | 본인 Bearer | PasswordChangeRequest | `204`, 본문 없음 | 400 VALIDATION_ERROR, 401 INVALID_CREDENTIALS, 409 PASSWORD_UNAVAILABLE | ACC-01, D11 |

요청 예시:

```http
PUT /api/members/me/password HTTP/1.1
Authorization: Bearer <액세스 토큰>
Content-Type: application/json

{
  "currentPassword": "Example!123",
  "newPassword": "Example!456"
}
```

응답: `204`, 본문 없음.

### `DELETE /api/members/me`

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `DELETE /api/members/me` | 본인 Bearer·D11의 재확인 절차 | 본문 없음; 재확인 증명의 전달 방식은 D11 | `204`, 본문 없음 | 401 UNAUTHORIZED, 409 ACTIVE_CONSULTATION_CONFLICT | ACC-03, D11 |

요청 예시:

```http
DELETE /api/members/me HTTP/1.1
Authorization: Bearer <액세스 토큰>
```

응답: `204`, 본문 없음.


### 회원정보 변경·탈퇴 처리

- PATCH에서 생략한 값은 유지하며, 변경 필드가 없으면 400이다. 비밀번호는 별도 경로에서 변경한다. 이메일을 바꾸면 변경할 이메일과 목적 `EMAIL_CHANGE`에 묶인 인증 증명이 필수다. 다른 이메일·가입용 증명으로 변경할 수 없다. 이메일 변경 인증을 요구하는 방식은 D11의 계정 변경 세부 설계안으로 검토한다.
- 프로필 이미지는 [공통 미디어](media.md)의 `MEMBER_PROFILE` 사용처로 업로드한 뒤 `profileMediaId`로 연결한다. 서버는 현재 사용자의 파일인지, 업로드가 완료됐는지, 사용처·연결 권한이 맞는지 검사한다. 생략하면 기존 이미지를 유지하고 명시적 `null`은 이미지 연결을 제거한다. 응답의 `profileMedia`는 현재 연결된 `MediaRef` 또는 null이며 `MediaRef` 필드는 공통 미디어 문서를 따른다.
- 프로필 이미지 연결·교체·제거는 계정·MongoDB 프로필 저장과 연결 상태 갱신이 성공한 후 확정한다. 저장이 실패하면 이전 연결을 유지하고 부분 실패는 복구한다. 기존 파일의 보관·정리는 공통 미디어 정책을 따른다.
- 회원정보 변경은 계정(MySQL)과 프로필(MongoDB)의 식별자를 기준으로 일관되게 반영한다. 두 저장소 중 하나만 바뀐 상태를 최종 성공으로 응답하지 않으며 재조회·복구 기준을 둔다.
- 반려동물 수는 삭제되지 않은 본인 반려동물 기준으로 조회한다. 탈퇴의 소프트 삭제·진행 중 매칭/상담·기록 보관·세션 폐기 정책은 D11 확정 후 구현한다. `ACTIVE_CONSULTATION_CONFLICT`는 진행 중 상담을 가진 탈퇴 요청을 보류하는 설계안이며 최종 정책은 미정이다.

## 구현 전 확인

| PRD 항목 | 확인할 내용 |
| --- | --- |
| D11 | 소셜 가입·이메일 변경의 인증 세부 정책, 토큰·쿠키·CSRF·CORS, 비밀번호 복구 본인확인, 소셜 계정 연결, 정보 변경·탈퇴 재확인과 진행 중 상담 처리 |
| D18 | MySQL 계정과 MongoDB 프로필의 식별자·속성 배치·가입/변경 부분 실패 복구, 이메일·로그인 ID·소셜 식별값의 유일성 |

이 문서는 요청·응답 설계이며 실제 서버·DB·메일·OAuth 제공자 연동 검증은 수행하지 않았다.
