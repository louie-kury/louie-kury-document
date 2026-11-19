# 계정·인증 API

우선 개발 대상은 일반·카카오·네이버 가입과 로그인, 아이디·비밀번호 찾기다. 마이페이지·탈퇴는 PRD의 후속 계정 기능으로 함께 기록한다. 근거는 [PRD ACC-01·ACC-03](../prd.md#61-보호자-계정--acc)과 요구사항정의서 `(필수3)요구사항정의서` 6~11행·34~36행이다. 공통 응답·오류 형식은 [API 안내](README.md)를 따른다.

아래 경로·필드·토큰 교환 흐름은 구현을 위한 API 설계 초안이다. PRD에서 미정인 본인확인 세부 정책은 D11·D18에 따라 확정한 후 구현한다.

## 데이터 모델

`?`는 요청 필드 생략 가능을 뜻한다. 응답에서 NULL 가능한 필드는 `타입?`로 표시한다. 모든 식별자는 문자열이다.

| 모델 | 필드 |
| --- | --- |
| EmailVerificationRequest | `email:string`, `purpose:SIGNUP 또는 EMAIL_CHANGE` |
| VerificationChallenge | `verificationId:string`, `expiresAt:datetime` |
| VerificationConfirmRequest | `code:string` |
| EmailVerificationProof | `emailVerificationToken:string`, `expiresAt:datetime` |
| RegistrationRequest | `name:string`, `phoneNumber:string`, `gender:string`, `birthDate:date`, `address:string`, `nickname:string`, `loginId:string`, `password:string`, `email:string`, `emailVerificationToken:string` |
| RegistrationResult | `memberId:string` |
| LoginRequest | `loginId:string`, `password:string` |
| SessionResult | `accessToken:string`, `tokenType:Bearer`, `expiresAt:datetime`, `memberId:string` |
| OAuthLoginResult | `result:LOGIN`, `session:SessionResult` |
| OAuthSignupRequiredResult | `result:SIGNUP_REQUIRED`, `signupTicket:string`, `expiresAt:datetime`, `suggestedNickname:string?` |
| OAuthRegistrationRequest | `signupTicket:string`, `email:string`, `emailVerificationToken:string`, `name:string`, `phoneNumber:string`, `nickname?:string` |
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

- `date`는 `YYYY-MM-DD`, `datetime`은 오프셋을 포함한 ISO 8601이다. `gender`의 허용값과 연락처·주소의 구체 형식은 D11에서 정한다.
- 일반 가입의 필수 입력은 PRD의 이름·전화번호·성별·생년월일·주소·닉네임·아이디·비밀번호·이메일이다. 닉네임은 최대 30자, 비밀번호는 영문·숫자·특수문자를 포함한 8~20자다.
- 소셜 이름·전화번호는 서버가 검증한 제공자 정보로 보완할 수 있으며, 누락된 값은 가입 완료 전에 직접 입력한다. `OAuthRegistrationRequest`의 필드는 제공값을 적용한 최종 제출값이다.
- 소셜 닉네임을 입력하지 않으면 검증된 제공자 닉네임을 사용하고, 제공값도 없으면 서버가 랜덤 생성한다. 생성값은 나중에 수정할 수 있다.
- 비밀번호·인증번호·검증 토큰은 요청 또는 해당 검증 응답에서만 전달한다. 계정·프로필 조회 응답에 비밀번호나 비밀번호 해시를 포함하지 않는다.

## 이메일 인증과 일반 가입

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/email-verifications` | SIGNUP 공개, EMAIL_CHANGE 본인 Bearer | EmailVerificationRequest | `202 VerificationChallenge` | 400 VALIDATION_ERROR, 409 EMAIL_ALREADY_REGISTERED, 429 RATE_LIMITED, 503 VERIFICATION_DELIVERY_FAILED | ACC-01, D11 |
| `POST /api/auth/email-verifications/{verificationId}/confirm` | 발급 목적·세션에 연결된 인증 절차 | VerificationConfirmRequest | `200 EmailVerificationProof` | 400 INVALID_VERIFICATION_CODE, 404 NOT_FOUND, 409 VERIFICATION_EXPIRED, 429 RATE_LIMITED | ACC-01, D11 |
| `POST /api/auth/registrations` | 공개, SIGNUP 인증 증명 | RegistrationRequest, `Idempotency-Key` | `201 RegistrationResult` | 400 VALIDATION_ERROR, 400 INVALID_EMAIL_VERIFICATION, 409 ACCOUNT_CONFLICT, 409 IDEMPOTENCY_CONFLICT, 503 REGISTRATION_PENDING | ACC-01, D11·D18 |

1. 일반·소셜 가입 모두 사용자가 직접 입력한 이메일로 인증번호를 발송하고 확인한다. 소셜 제공자의 이메일 인증 상태를 근거로 이 절차를 생략하지 않는다.
2. 인증 증명은 서버에서 이메일·목적·발급 절차·유효기간을 확인한다. 다른 이메일, EMAIL_CHANGE 증명 또는 만료된 증명으로 가입할 수 없다. EMAIL_CHANGE 인증 절차와 증명은 발급 요청자의 memberId에도 연결하고 이메일 변경 시 같은 본인인지 확인한다. 인증번호 시도·발송 제한과 만료·재발송 세부값은 D11에서 정한다.
3. 한 이메일당 계정 하나를 허용하고 로그인 ID 중복도 거부한다. 동일 이메일의 일반·소셜 계정을 자동 병합하지 않는다.
4. 가입 성공 시 `Location: /api/members/me`를 반환한다. 가입 이후 로그인은 별도 로그인 API로 수행한다.
5. 계정·인증 데이터는 MySQL, 일반 회원 프로필은 MongoDB에 저장한다. 두 저장소의 가입 작업을 하나의 복구 가능한 가입 절차로 관리하고, 프로필 저장까지 완료된 계정만 로그인 가능한 상태로 만든다.
6. 동일 키·동일 입력의 가입 재시도는 진행 중 절차를 복구하거나 기존 성공 결과를 반환한다. 같은 키에 다른 입력은 409다. 인증 증명은 해당 가입 절차에 한 번 연결하며 부분 실패 재시도 때문에 이메일 증명이 다른 계정에 재사용되지 않도록 한다. 키·증명 보관 기간은 D11·D18에서 정한다.

### 일반 가입 요청 예시

```json
{
  "name": "김보호",
  "phoneNumber": "01000000000",
  "gender": "<확정된 성별 코드>",
  "birthDate": "1995-01-01",
  "address": "서울특별시",
  "nickname": "루이집사",
  "loginId": "loui-care",
  "password": "Example!123",
  "email": "caregiver@example.com",
  "emailVerificationToken": "<이메일 인증 증명>"
}
```

## 로그인·소셜 가입·세션

`provider`의 경로 값은 `kakao`, `naver`만 허용한다. 제공자의 인가 응답은 서버가 직접 검증하고 계정 식별값을 얻는다.

| Method·경로 | 인증 | 요청 | 성공 응답의 data 또는 헤더 | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/login` | 공개 | LoginRequest | `200 SessionResult`, refresh cookie 설정 | 400 VALIDATION_ERROR, 401 INVALID_CREDENTIALS, 403 ACCOUNT_UNAVAILABLE | ACC-01 |
| `GET /api/auth/oauth/{provider}/authorize` | 공개 | 브라우저 이동, 임의 redirect URL 입력 없음 | `302 Location` 제공자 인가 화면, 본문 없음 | 400 UNSUPPORTED_PROVIDER, 503 OAUTH_UNAVAILABLE | ACC-01, D11 |
| `GET /api/auth/oauth/{provider}/callback` | 서버가 시작한 OAuth 절차 | 제공자 `code`, `state`, 실패 시 제공자 오류 | `302 Location` 허용된 프런트 완료 화면, 본문 없음 | 제공자 거절·state 불일치·검증 실패는 프런트 실패 화면으로 이동 | ACC-01, D11 |
| `POST /api/auth/oauth/exchanges` | 일회성 교환 증명 | `{exchangeTicket:string}` | `200 OAuthLoginResult` 또는 `OAuthSignupRequiredResult`; LOGIN이면 refresh cookie 설정 | 400 INVALID_OAUTH_TICKET, 403 ACCOUNT_UNAVAILABLE, 409 OAUTH_TICKET_USED | ACC-01, D11 |
| `POST /api/auth/oauth/registrations` | signupTicket·SIGNUP 이메일 증명 | OAuthRegistrationRequest, `Idempotency-Key` | `201 RegistrationResult` | 400 INVALID_OAUTH_TICKET, 400 INVALID_EMAIL_VERIFICATION, 409 EMAIL_ALREADY_REGISTERED, 409 ACCOUNT_CONFLICT, 409 IDEMPOTENCY_CONFLICT, 503 REGISTRATION_PENDING | ACC-01, D11·D18 |
| `POST /api/auth/refresh` | refresh cookie | 본문 없음, 쿠키 요청 보호 정보 | `200 SessionResult`, refresh cookie 교체 | 401 INVALID_REFRESH_TOKEN, 403 ACCOUNT_UNAVAILABLE | ACC-01, D11 |
| `POST /api/auth/logout` | 현재 세션·refresh cookie | 본문 없음, 쿠키 요청 보호 정보 | `204`, cookie 만료 | 403 REQUEST_ORIGIN_REJECTED | ACC-01, D11 |

- 서버는 `state`를 시작 세션과 연결하여 검증한다. 실패 콜백을 정상 로그인으로 처리하지 않는다. 제공자 거절·state 오류·제공자 장애는 고정된 프런트 완료 경로에서 구분 가능한 오류 코드로 안내한다.
- 콜백은 허용 목록의 프런트 완료 URL로만 이동한다. URL에는 짧게 유지하는 일회성 `exchangeTicket` 또는 공개 가능한 오류 코드만 담고 액세스·리프레시 토큰을 담지 않는다. 교환 증명은 시작한 브라우저 절차와 연결하고 교환 시 한 번만 사용한다.
- `LOGIN`은 이미 연결된 제공자·식별값의 계정이다. `SIGNUP_REQUIRED`는 서버가 검증한 제공자 식별값에 연결된 가입 증명만 발급한다. 클라이언트가 제출한 `providerId`로 소셜 계정을 만들지 않는다.
- 미등록 소셜 계정은 직접 입력한 이메일의 인증을 완료한 뒤 가입한다. 이미 가입된 이메일이면 신규 가입을 제한하고 기존 계정 로그인으로 안내한다. 자동 계정 연결은 수행하지 않는다. 기존 계정과의 수동 연결 정책은 D11 미정이다.
- 소셜 계정의 비밀번호는 NULL이다. 소셜 가입 요청은 비밀번호를 받지 않는다. 기존 계정 비밀번호를 소셜 제공자에 전달하지 않는다.
- 가입과 세션 발급의 재시도는 계정·소셜 연결·프로필을 중복 생성하지 않는다. 등록된 계정이 이용 불가 상태면 세션을 발급하지 않는다.

### 소셜 교환 응답 예시

```json
{
  "data": {
    "result": "SIGNUP_REQUIRED",
    "signupTicket": "<서버가 검증한 소셜 가입 증명>",
    "expiresAt": "2026-11-19T15:00:00+09:00",
    "suggestedNickname": null
  }
}
```

### 세션 설계 제안

액세스 토큰은 Bearer로 전달하고 리프레시 토큰은 `HttpOnly`, `Secure` 쿠키로 보관하는 안이다. 배포 도메인에 맞는 `SameSite`·쿠키 범위·CORS·CSRF 보호 방식과 토큰 유효기간은 D11에서 확정한다. 쿠키 기반 갱신·로그아웃은 요청 Origin과 확정된 CSRF 증명을 검증한다.

갱신 성공 시 리프레시 토큰을 회전하고 이전 토큰 재사용을 탐지한다. 동시에 갱신하거나 네트워크 실패로 재시도할 때 정상 세션이 손실되지 않도록 회전·재시도 계약을 함께 확정한다. 로그아웃은 서버의 해당 갱신 세션을 폐기하고, 이미 종료된 세션으로 다시 요청해도 204를 반환한다. 액세스 토큰의 로그아웃 후 효력·전체 기기 로그아웃 여부도 D11에서 정한다.

## 아이디 찾기와 비밀번호 복구

아이디 찾기는 입력한 가입 이메일로 인증번호를 보내고 확인된 경우에만 아이디를 반환한다. 비밀번호 복구의 본인확인 수단은 D11 미정이다. 아래 비밀번호 복구는 등록 이메일 인증번호를 사용하는 설계 제안이며, 이름·아이디 일치만으로 변경 권한을 부여하지 않는다.

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `POST /api/auth/login-id/recovery-requests` | 공개 | RecoveryRequest | `202 VerificationChallenge` | 400 VALIDATION_ERROR, 429 RATE_LIMITED, 503 VERIFICATION_DELIVERY_FAILED | ACC-01, D11 |
| `POST /api/auth/login-id/recoveries` | 아이디 찾기용 인증 절차 | LoginIdRecoveryRequest | `200 LoginIdResult` | 400 INVALID_VERIFICATION_CODE, 404 NOT_FOUND, 409 VERIFICATION_EXPIRED, 429 RATE_LIMITED | ACC-01, D11 |
| `POST /api/auth/password/reset-requests` | 공개 | PasswordResetRequest | `202 VerificationChallenge` | 400 VALIDATION_ERROR, 429 RATE_LIMITED, 503 VERIFICATION_DELIVERY_FAILED | ACC-01, D11 |
| `POST /api/auth/password/reset-verifications` | 비밀번호 복구용 인증 절차 | PasswordResetVerificationRequest | `200 PasswordResetProof` | 400 INVALID_VERIFICATION_CODE, 404 NOT_FOUND, 409 VERIFICATION_EXPIRED, 429 RATE_LIMITED | ACC-01, D11 |
| `POST /api/auth/password/resets` | 비밀번호 복구 증명 | PasswordResetCompleteRequest | `204`, 본문 없음 | 400 INVALID_PASSWORD_RESET, 400 VALIDATION_ERROR, 409 PASSWORD_UNAVAILABLE | ACC-01, D11 |

- 복구 요청의 접수 응답은 계정 존재 여부를 구별하지 않는 형식으로 제안한다. 해당 계정이 확인되고 발송이 가능한 경우에만 실제 인증번호를 보내며, 유효한 증명을 확인하기 전에는 아이디·등록 이메일 등 계정 정보를 공개하지 않는다.
- 가입 이메일 인증, 이메일 변경, 아이디 찾기, 비밀번호 재설정의 증명은 서로 바꿔 사용할 수 없다. 각 절차의 확인 완료와 결과 사용을 서버에서 기록한다.
- `passwordResetToken`은 대상 계정·목적·유효기간에 연결하고 비밀번호 변경 성공 시 한 번만 사용한다. 재시도로 다른 비밀번호가 덮어써지지 않도록 소비와 계정 갱신을 일관되게 처리한다.
- 소셜 전용 계정에 일반 비밀번호를 생성하는 동작은 D11 확정 후 제공한다. 기존 세션 폐기 범위와 재설정 완료 안내도 함께 정한다.

## 내 회원정보와 탈퇴

| Method·경로 | 인증 | 요청 | 성공 응답의 data | 주요 오류 | 근거 |
| --- | --- | --- | --- | --- | --- |
| `GET /api/members/me` | 본인 Bearer | 없음 | `200 MemberProfile` | 401 UNAUTHORIZED, 403 ACCOUNT_UNAVAILABLE | ACC-01 |
| `PATCH /api/members/me` | 본인 Bearer | MemberPatchRequest | `200 MemberProfile` | 400 VALIDATION_ERROR, 400 INVALID_EMAIL_VERIFICATION, 409 EMAIL_ALREADY_REGISTERED, 409 PROFILE_UPDATE_CONFLICT, 400 INVALID_MEDIA_REFERENCE | ACC-01, MED-01, D11·D18·D19 |
| `PUT /api/members/me/password` | 본인 Bearer | PasswordChangeRequest | `204`, 본문 없음 | 400 VALIDATION_ERROR, 401 INVALID_CREDENTIALS, 409 PASSWORD_UNAVAILABLE | ACC-01, D11 |
| `DELETE /api/members/me` | 본인 Bearer·D11의 재확인 절차 | 본문 없음; 재확인 증명의 전달 방식은 D11 | `204`, 본문 없음 | 401 UNAUTHORIZED, 409 ACTIVE_CONSULTATION_CONFLICT | ACC-03, D11 |

- PATCH에서 생략한 값은 유지하며, 변경 필드가 없으면 400이다. 비밀번호는 별도 경로에서 변경한다. 이메일을 바꾸면 변경할 이메일과 목적 `EMAIL_CHANGE`에 묶인 인증 증명이 필수다. 다른 이메일·가입용 증명으로 변경할 수 없다. 이메일 변경 인증을 요구하는 방식은 D11의 계정 변경 세부 설계안으로 검토한다.
- 프로필 이미지는 [공통 미디어](media.md)의 `MEMBER_PROFILE` 사용처로 업로드한 뒤 `profileMediaId`로 연결한다. 서버는 현재 사용자의 파일인지, 업로드가 완료됐는지, 사용처·연결 권한이 맞는지 검사한다. 생략하면 기존 이미지를 유지하고 명시적 `null`은 이미지 연결을 제거한다. 응답의 `profileMedia`는 현재 연결된 `MediaRef` 또는 null이며 `MediaRef` 필드는 공통 미디어 문서를 따른다.
- 프로필 이미지 연결·교체·제거는 계정·MongoDB 프로필 저장과 연결 상태 갱신이 성공한 후 확정한다. 저장이 실패하면 이전 연결을 유지하고 부분 실패는 복구한다. 기존 파일의 보관·정리는 공통 미디어 정책을 따른다.
- 회원정보 변경은 계정(MySQL)과 프로필(MongoDB)의 식별자를 기준으로 일관되게 반영한다. 두 저장소 중 하나만 바뀐 상태를 최종 성공으로 응답하지 않으며 재조회·복구 기준을 둔다.
- 반려동물 수는 삭제되지 않은 본인 반려동물 기준으로 조회한다. 탈퇴의 소프트 삭제·진행 중 매칭/상담·기록 보관·세션 폐기 정책은 D11 확정 후 구현한다. `ACTIVE_CONSULTATION_CONFLICT`는 진행 중 상담을 가진 탈퇴 요청을 보류하는 설계안이며 최종 정책은 미정이다.

## 구현 전 확인

| PRD 항목 | 확인할 내용 |
| --- | --- |
| D11 | 이메일 인증 유효기간·재발송·실패 제한, 토큰·쿠키·CSRF·CORS, 비밀번호 복구 본인확인, 소셜 계정 연결, 정보 변경·탈퇴 재확인과 진행 중 상담 처리 |
| D18 | MySQL 계정과 MongoDB 프로필의 식별자·속성 배치·가입/변경 부분 실패 복구, 이메일·로그인 ID·소셜 식별값의 유일성 |

이 문서는 요청·응답 설계이며 실제 서버·DB·메일·OAuth 제공자 연동 검증은 수행하지 않았다.
