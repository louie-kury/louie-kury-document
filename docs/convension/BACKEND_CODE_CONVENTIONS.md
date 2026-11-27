# 루이쿠리 백엔드 코드 컨벤션

백엔드는 [domain-driven-hexagon](https://github.com/Sairyss/domain-driven-hexagon)의 모듈·유스케이스 중심 구조와 헥사고날 아키텍처(Ports and Adapters)를 Java와 Spring에 맞게 적용한다. 유스케이스와 도메인 모델을 중심에 두고, HTTP·DB·외부 서비스는 포트와 어댑터를 통해 연결한다.

코드 작성과 리뷰는 이 문서를 따른다. 브랜치·커밋·PR 형식은 [Git 컨벤션](GIT_CONVENTIONS.md), 작업 진행은 [워크플로](../ai/WORKFLOW.md), API 계약은 [API 명세](../api/README.md), 데이터 구조는 [ERD](../erd.md)를 참고한다.

## 적용 범위

- 백엔드 소스와 테스트 코드에 적용한다. 자동 생성 코드와 외부 코드는 원본 또는 생성 설정에서 관리한다.
- 새 코드와 이번 작업에서 수정하는 부분에 적용한다. 기존 계층 구조의 전환은 해당 기능의 호출 경로와 데이터 저장 동작을 함께 검증할 수 있는 범위로 진행한다.
- 아래 규칙을 기본 기준으로 지킨다. 외부 계약·프레임워크 제약·기존 호환성 때문에 예외가 필요하면 규칙, 사유와 적용 범위를 PR에 기록한다.

## SOLID 원칙

백엔드 코드를 설계하고 작성할 때 다음 SOLID 원칙을 지킨다. 기존 계층별 책임과 의존 방향을 함께 따른다.

- **단일 책임 원칙(SRP)**: 클래스와 모듈은 하나의 명확한 책임을 갖고, 서로 다른 변경 이유가 섞이지 않도록 분리한다.
- **개방-폐쇄 원칙(OCP)**: 변경이 예상되는 동작은 필요한 계약을 통해 확장하고, 기존 호출자의 코드를 반복해서 수정하지 않도록 설계한다.
- **리스코프 치환 원칙(LSP)**: 포트나 상위 타입의 구현체는 호출자가 기대하는 입력·반환·실패 계약을 지켜 서로 대체할 수 있어야 한다.
- **인터페이스 분리 원칙(ISP)**: 호출자에게 필요한 기능만 포트에 정의하고, 사용하지 않는 메서드에 의존하게 하지 않는다.
- **의존 역전 원칙(DIP)**: 애플리케이션은 외부 기술의 구현체가 아닌 내부에서 소유한 포트에 의존하고, 어댑터가 그 포트를 구현한다.

원칙을 적용하기 위해 사용하지 않는 인터페이스나 확장 지점을 미리 만들지 않는다.

## 패키지 구조

### 참고 저장소 구조

참고 저장소의 `main` 커밋 `1ea4ccb`에 기록된 전체 트리다.

```text
spharos8th-mas-userservice/
├── .DS_Store
├── .gitattributes
├── .gitignore
├── README.md
├── build.gradle
├── gradle
│   └── wrapper
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── gradlew
├── gradlew.bat
├── lombok.config
├── settings.gradle
└── src
    ├── main
    │   ├── java
    │   │   └── com
    │   │       └── spharos
    │   │           └── userservice
    │   │               ├── UserserviceApplication.java
    │   │               ├── adaptor
    │   │               │   ├── in
    │   │               │   │   └── web
    │   │               │   │       ├── AuthController.java
    │   │               │   │       ├── config
    │   │               │   │       │   ├── OpenApiConfig.java
    │   │               │   │       │   └── SecurityConfig.java
    │   │               │   │       ├── exception
    │   │               │   │       │   ├── ErrorResponseVo.java
    │   │               │   │       │   └── GlobalExceptionHandler.java
    │   │               │   │       ├── mapper
    │   │               │   │       │   └── AuthVoMapper.java
    │   │               │   │       ├── security
    │   │               │   │       │   ├── JwtAuthenticationFilter.java
    │   │               │   │       │   └── LoginUser.java
    │   │               │   │       └── vo
    │   │               │   │           ├── AuthLoginRequestVo.java
    │   │               │   │           ├── AuthLoginResponseVo.java
    │   │               │   │           ├── AuthMeResponseVo.java
    │   │               │   │           ├── AuthSignUpRequestVo.java
    │   │               │   │           └── AuthSignUpResponseVo.java
    │   │               │   └── out
    │   │               │       ├── mysql
    │   │               │       │   ├── AuthRepositoryAdapter.java
    │   │               │       │   ├── entity
    │   │               │       │   │   └── AuthEntity.java
    │   │               │       │   ├── mapper
    │   │               │       │   │   └── AuthEntityMapper.java
    │   │               │       │   └── repository
    │   │               │       │       └── AuthRepository.java
    │   │               │       └── security
    │   │               │           ├── BcryptPasswordEncoderAdapter.java
    │   │               │           └── JwtTokenProviderAdapter.java
    │   │               ├── application
    │   │               │   ├── exception
    │   │               │   │   └── InvalidAccessTokenException.java
    │   │               │   ├── port
    │   │               │   │   ├── in
    │   │               │   │   │   ├── AuthUseCase.java
    │   │               │   │   │   └── dto
    │   │               │   │   │       ├── AuthLoginRequestDto.java
    │   │               │   │   │       ├── AuthLoginResultDto.java
    │   │               │   │   │       ├── AuthSignUpRequestDto.java
    │   │               │   │   │       └── AuthSignUpResultDto.java
    │   │               │   │   └── out
    │   │               │   │       ├── AccessTokenClaims.java
    │   │               │   │       ├── AuthRepositoryPort.java
    │   │               │   │       ├── PasswordEncoderPort.java
    │   │               │   │       └── TokenProviderPort.java
    │   │               │   └── service
    │   │               │       └── AuthService.java
    │   │               ├── config
    │   │               │   └── JwtProperties.java
    │   │               └── domain
    │   │                   ├── exception
    │   │                   │   ├── DuplicateAuthIdentityException.java
    │   │                   │   ├── DuplicateEmailException.java
    │   │                   │   ├── DuplicateLoginIdException.java
    │   │                   │   ├── InvalidAuthDomainException.java
    │   │                   │   └── InvalidCredentialsException.java
    │   │                   └── model
    │   │                       └── AuthDomain.java
    │   └── resources
    │       ├── application-dev.yaml
    │       ├── application-local.yaml
    │       ├── application-prod.yaml
    │       ├── application.yaml
    │       └── db
    │           └── migration
    │               └── V1__create_auth_table.sql
    └── test
        ├── java
        │   └── com
        │       └── spharos
        │           └── userservice
        │               ├── ArchitectureTest.java
        │               ├── UserserviceApplicationTests.java
        │               ├── adaptor
        │               │   ├── in
        │               │   │   └── web
        │               │   │       ├── AuthControllerTest.java
        │               │   │       └── exception
        │               │   │           └── GlobalExceptionHandlerTest.java
        │               │   └── out
        │               │       ├── mysql
        │               │       │   └── AuthRepositoryAdapterTest.java
        │               │       └── security
        │               │           └── JwtTokenProviderAdapterTest.java
        │               ├── application
        │               │   └── service
        │               │       └── AuthServiceTest.java
        │               └── domain
        │                   └── model
        │                       └── AuthDomainTest.java
        └── resources
            └── application.yaml
```

회원가입·로그인은 `AuthController` → `AuthUseCase` → `AuthService` 순서로 실행된다. 회원가입은 도메인 생성, 중복 확인, 비밀번호 해싱, 저장 순으로 진행한다. 로그인은 계정 조회, 비밀번호 검증, 토큰 발급 순으로 진행한다.

내 정보 조회는 필터가 검증 포트로 토큰을 해석해 인증 주체를 만들고, 컨트롤러가 해당 주체의 식별자를 반환한다. 이 경로에는 사용자 DB 조회가 없다.

| 비교 항목 | 참고 구현 | 루이쿠리 기준 |
| --- | --- | --- |
| 패키지와 입력 포트 | 서비스 루트에 `domain`, `application`, `adaptor`를 두고, 하나의 `AuthUseCase`가 회원가입과 로그인을 제공 | 업무 모듈 안에 `domain`, `application`, `adapter`를 두고, 유스케이스별 입력 포트·입력 모델·서비스를 배치 |
| 웹 경계 | 컨트롤러가 `AuthVoMapper`로 HTTP VO와 애플리케이션 입력·결과 모델을 변환하고 입력 포트를 호출 | 컨트롤러가 웹 어댑터에 위임 |
| 업무 판단과 트랜잭션 | 도메인 팩토리가 생성 조건을 검사하고, 서비스가 중복 확인과 트랜잭션을 담당 | 기존 규칙대로 서비스가 업무 조건과 트랜잭션을 판단하고 도메인이 상태를 반영 |
| 출력 경계 | `AuthRepositoryPort`, `PasswordEncoderPort`, `TokenProviderPort`를 두고, MySQL 어댑터에서 JPA 모델을 변환하며 보안 어댑터에서 BCrypt·JWT를 사용 | 영속성·보안 기술을 출력 포트와 해당 어댑터에 배치 |

### 루이쿠리 패키지 배치

서비스 디렉터리는 `consultation-service`처럼 소문자와 하이픈으로 작성한다. Java 루트 패키지는 `com.louiekury.<서비스명>`이며, 여러 단어의 서비스명은 `medicalrecord`처럼 붙여 쓴다. 실행 클래스는 루트에 둔다.

루트 아래에 업무 개념별 모듈을 두고 각 모듈 안에서 `domain`, `application`, `adapter`로 나눈다.

- `shared`에는 여러 기능이 실제로 공유하는 내부 타입을 둔다. Spring·JPA·Jackson·외부 SDK에 의존하지 않는다.
- `global`에는 서비스 공통의 외부 기술 설정과 어댑터 지원 코드를 둔다. 내부 계층에서 `global`을 참조하지 않는다.
- `application.createpet`, `application.getpet`처럼 유스케이스별 패키지에 각 입력 포트·Command/Query·서비스와 해당 유스케이스 전용 결과 모델을 둔다. 같은 모듈에서 공유하는 도메인 타입은 `domain`, 결과 모델은 `application.model`, 출력 포트는 `application.port.out`에 둔다. 실제 사용하는 계층과 포트만 만든다.
- 인증 기능의 비밀번호 해싱·토큰 구현은 필요할 때 `adapter.out.security`에 두고, HTTP 인증 필터와 인증 주체 변환은 `adapter.in.web.security` 또는 서비스 공통 웹 경계에 둔다.
- `CommonService`, `Manager`, `Helper`처럼 이름만으로 책임을 알기 어려운 공통 클래스를 만들지 않는다.

#### 반려동물 등록 적용 예시

반려동물 서비스의 `com.louiekury.pet.pet` 모듈을 기준으로 새 기능의 파일 위치와 호출 경로를 확인한다.

| 순서 | 모듈 기준 패키지 | 파일과 역할 |
| --- | --- | --- |
| 1. HTTP 진입 | `adapter.in.web`, `adapter.in.web.dto.request` | `PetController`가 `CreatePetRequestDto`와 인증된 호출자 정보 등을 받아 `PetWebAdapter`에 위임한다. |
| 2. 입력 변환과 유스케이스 호출 | `adapter.in.web`, `application.createpet` | `PetWebAdapter`가 `CreatePetCommand`를 만들고 `CreatePetUseCase`를 호출한다. |
| 3. 업무 처리 | `application.createpet`, `application.port.out` | `CreatePetService`가 입력 포트를 구현한다. 서비스가 업무 검증을 수행하고 저장을 `CreatePetPort`에 요청한다. |
| 4. 저장 | `adapter.out.persistence` | `PetPersistenceAdapter`가 출력 포트를 구현하고 영속성 모델로 변환해 MongoDB에 저장한다. |
| 5. HTTP 응답 | `application.createpet`, `adapter.in.web.dto.response` | 서비스가 `PetResult`를 반환하면 웹 어댑터가 `PetDetailResponseDto`와 HTTP 응답을 만든다. |

## 의존 방향과 계층별 책임

소스 코드의 의존은 바깥에서 안쪽으로 향한다. 아래 화살표는 타입을 참조하는 방향을 나타낸다.

```text
입력 어댑터 → 입력 포트 ← 애플리케이션 서비스 → 출력 포트 ← 출력 어댑터
                             서비스·출력 포트·출력 어댑터 → 도메인
```

| 구성 요소 | 담당하는 일 | 의존할 수 있는 대상 |
| --- | --- | --- |
| 도메인 | 상태 보유와 서비스가 결정한 변경 반영 | JDK, 도메인 타입, 기술 독립적인 shared 타입 |
| 입력 포트 | 외부에서 실행할 유스케이스의 계약 | 애플리케이션 입력·결과 모델 |
| 애플리케이션 서비스 | 업무 검증·판단·계산·상태 변경 규칙, 유스케이스 순서, 권한 확인, 트랜잭션 경계, 포트 호출 | 도메인, 포트, 애플리케이션 모델, shared |
| 출력 포트 | 저장·조회·외부 요청 등 유스케이스가 필요로 하는 기능의 계약 | 도메인, 기술 독립적인 애플리케이션 모델 |
| 입력 어댑터 | HTTP·메시지·배치 입력 해석, 입력 모델 변환, 입력 포트 호출, 응답 변환 | 입력 포트와 입력·결과 모델, 해당 외부 기술, 전송 계층 인증 필터의 검증 포트 |
| 출력 어댑터 | 출력 포트 구현, JPA·Querydsl·외부 SDK 호출과 모델 변환 | 출력 포트, 도메인·애플리케이션 모델, 해당 외부 기술 |

- 도메인은 애플리케이션·어댑터·기술 설정·프레임워크를 참조하지 않는다. 애플리케이션은 어댑터, 기술 설정, 웹·영속성·외부 SDK 구현을 참조하지 않는다. 입력·출력 어댑터 사이의 직접 의존과 입력 어댑터의 애플리케이션 서비스 구현체 참조를 금지한다.
- 포트는 애플리케이션이 소유하는 Java 인터페이스다. 사용하는 업무 단위로 필요한 연산과 입력·반환·실패 계약을 정의한다. 범용 CRUD나 외부 SDK 메서드는 포트에 필요한 범위만 노출한다.
- 애플리케이션 서비스는 입력 포트를 구현하고 출력 포트를 주입받는다. 출력 포트 구현체는 컴포넌트 스캔 또는 별도 설정으로 연결하며, 후보가 여러 개일 때는 설정에서 주입 대상을 명시한다.
- 컨트롤러는 웹 어댑터를 생성자로 주입받고 각 메서드 본문에 `return` 한 문장으로 해당 메서드를 호출한다. 객체 생성·변환·조건문·지역 변수·업무 처리를 작성하지 않는다. 반환 본문이 없는 경우에도 웹 어댑터가 반환하는 `ResponseEntity<Void>`를 그대로 반환한다.
- 웹 어댑터의 요청·응답 변환과 입력 포트 호출은 [DTO와 경계 변환](#dto와-경계-변환)을 따른다.
- 서비스와 포트의 인자·반환값은 기술 독립적인 모델을 사용한다. JPA 엔티티, Spring Data `Page`·`Pageable`, HTTP 상태·`ResponseEntity`·`ApiResponse`·웹 DTO, Jackson 타입, 외부 SDK 모델을 경계 안으로 전달하지 않는다. 페이지 조건과 결과는 필요한 필드를 가진 애플리케이션 모델로 표현한다.
- 같은 서비스의 다른 모듈은 공개 입력 포트와 입력·결과 모델을 통해 호출한다. 다른 모듈의 서비스 구현체·도메인 내부 객체·영속성 어댑터를 직접 참조하지 않는다. 다른 모듈에 접근하는 흐름이 외부 연동과 같거나 결합을 분리해야 하면 출력 포트와 모듈 연동 어댑터를 사용한다. 모듈 간 순환 의존을 만들지 않는다. 같은 모듈의 다른 서비스 구현체를 직접 주입하지 않고 공통 업무가 필요하면 책임과 포트를 재설계한다.
- 별도 마이크로서비스는 출력 포트와 클라이언트·메시지 어댑터를 통해 연결한다. 다른 서비스의 DB나 내부 구현체에 직접 접근하지 않는다.
- 애플리케이션 서비스에는 `@Service`와 `@Transactional`을 허용한다. 그 외 Spring 기술 타입은 어댑터에서 다룬다.

## 네이밍

| 대상 | 기준과 예시 |
| --- | --- |
| 타입과 파일 | `PascalCase`, 공개 타입과 파일 이름 일치 |
| 메서드·필드·변수 | `lowerCamelCase`, `updateConsultation`, `veterinarianId` |
| 상수·오류 코드 | `UPPER_SNAKE_CASE`, `MAX_RETRY_COUNT`, `CONSULTATION_NOT_FOUND` |
| 도메인 모델 | 도메인 용어, `Consultation` |
| JPA 엔티티 | 도메인명 + `JpaEntity`, `ConsultationJpaEntity` |
| 입력 포트 | 행위 + 대상 + `UseCase`, `UpdateConsultationUseCase` |
| 출력 포트 | CRUD 행위 + 대상 + `Port`, `GetConsultationPort` |
| 유스케이스 구현 | 행위 + 대상 + `Service`, `UpdateConsultationService` |
| 어댑터 | 대상 + 기술/역할 + `Adapter`, `ConsultationPersistenceAdapter` |
| Spring Data 레포지토리 | 대상 + `JpaRepository`, `ConsultationJpaRepository` |
| 요청 DTO | 동작 + 대상 + `RequestDto`, `CreateConsultationRequestDto` |
| 응답 DTO | 대상 + `ResponseDto`, `ConsultationResponseDto` |
| 목록 항목 DTO | 대상 + `ListItemResponseDto`, `ConsultationListItemResponseDto` |
| 애플리케이션 모델 | 변경 입력 `Command`, 조회 입력 `Query`, 처리 결과 `Result` |

- 같은 개념에는 같은 용어를 쓴다. 수의사는 `veterinarian`처럼 뜻이 드러나게 쓴다.
- 약어도 한 단어로 취급한다. `ProductApiClient`, `productId`, `imageUrl`로 쓴다.
- 직접 작성하는 업무 유스케이스와 컨트롤러·웹 어댑터·서비스·포트의 클래스 및 메서드 이름은 `create`, `get`, `update`, `delete`와 대상을 조합한다. 예: `CreatePetService.createPet`, `GetPetPort.getPet`. 등록은 `registration`이나 `register`가 아닌 `create`를 쓴다. 상태 전이는 `update`와 대상·상태를 조합한다. 예: 상담 취소는 `updateConsultationStatus`로 표현하고 상태 값으로 취소를 전달한다. 목록과 조건은 `getPets`, `getPetsByOwnerId`처럼 대상 뒤에 명시한다. `get`의 부재 처리는 반환 계약에 `Optional` 또는 예외로 명시한다.
- 위 네 동사는 직접 작성하는 업무 행위에 적용한다. 생성 팩토리 `of`/`from`, getter, 변환 메서드, Spring Data가 요구하는 `save`/`findBy...`, 프레임워크 오버라이드 등 기술 API는 해당 API 규칙을 따른다.
- 참·거짓 필드는 `active`처럼 상태로 이름 짓고 기본형 `boolean` getter는 `isActive()`로 쓴다.
- 숫자의 단위가 타입에 드러나지 않으면 `timeoutMillis`처럼 이름에 적는다.
- Java `record` 타입은 사용하지 않는다.

## DTO와 경계 변환

경계 변환 사례는 [예시 코드](#예시-코드)를 참고한다.

- DTO와 애플리케이션 입력·결과 모델은 일반 `class`로 작성한다. 요청 DTO는 `private` 필드를 사용하고, 응답 DTO와 애플리케이션 입력·결과 모델은 `private final` 필드를 사용한다. DTO 클래스 자체에는 `final`을 붙이지 않는다.
- 응답 DTO와 애플리케이션 모델은 객체 하나를 변환할 때 `from`, 필드 값을 조합할 때 `of` 정적 팩토리를 사용한다. 매핑과 생성은 팩토리 안에서 처리한다.
- 요청 DTO는 기본 생성자와 필드별 setter로 본문 값을 받는다. 예제와 DTO에서 Jackson 직렬화 어노테이션 사용을 피한다. Bean Validation 제약은 웹 DTO 필드에 작성하고, 어노테이션과 필드를 한 묶음으로 배치한다. 각 제약에 `message`를 명시해 어떤 필드가 어떤 조건을 충족해야 하는지 알린다. 길이·범위·형식을 제한할 때는 `min`, `max`, `regexp` 등 해당 제약의 속성에 API 명세의 기준을 적는다.
- 필수 여부와 값의 범위는 API 명세에 맞춘다. 누락을 구분해야 하는 숫자·불리언 입력은 Wrapper 타입을 사용한다. PATCH에서 생략과 명시적 `null`을 구분해야 하는 필드는 요청 DTO의 setter에서 값과 호출 여부를 함께 기록한다. 웹 어댑터는 이 둘을 변경 모델로 입력 포트에 전달한다. 예를 들어 `profileMediaId`를 생략하면 기존 연결을 유지하고, 명시적으로 `null`을 보내면 API 명세에 따라 연결을 해제한다. 웹 경계 테스트에서 생략·`null`·값 입력을 각각 확인한다.
- 컨트롤러는 요청 DTO, 인증된 사용자 식별자와 경로 값을 웹 어댑터에 전달한다. 웹 어댑터는 필요한 값을 추출해 `Command.of(...)` 또는 Query를 만들고 입력 포트를 호출한다.
- 애플리케이션 모델의 팩토리는 웹 DTO를 인자로 받지 않는다.
- 웹 어댑터는 서비스의 Result를 `ResponseDto.from(result)`로 변환한 뒤 공통 응답 본문과 HTTP 상태를 지정한다.
- JPA 엔티티와 도메인 모델은 영속성 어댑터에서 변환한다. 외부 API 모델은 클라이언트 어댑터에서 변환한다.

```text
요청 흐름: HTTP → 컨트롤러 → 웹 어댑터 → 입력 포트 → 서비스 → 출력 포트 → 영속성 어댑터 → DB
응답 흐름: DB → 영속성 어댑터 → 서비스 → 웹 어댑터 → 컨트롤러 → HTTP
모델 변환: 요청 DTO → Command/Query → 도메인 모델 ↔ 영속성 모델
           결과 모델 → 응답 DTO
```

이 흐름은 실행 순서다. 타입 참조는 [의존 방향과 계층별 책임](#의존-방향과-계층별-책임)을 따른다.

## Lombok과 객체 생성

| 대상 | 사용 기준 |
| --- | --- |
| 컨트롤러·서비스·어댑터 | `private final` 의존성과 `@RequiredArgsConstructor`로 생성자 주입 |
| 요청 DTO | `@Getter`, `@NoArgsConstructor`, 본문 바인딩에 필요한 필드별 setter |
| 응답 DTO와 애플리케이션 모델 | `@Getter`, `@RequiredArgsConstructor(access = AccessLevel.PRIVATE)`, `@Builder(access = AccessLevel.PRIVATE)` |
| 도메인 모델 | 필요한 getter와 명시적 생성자·상태 변경 메서드 |
| JPA 엔티티 | `@Getter`, `@Entity`, `@Table`, `@NoArgsConstructor(access = AccessLevel.PROTECTED)` 순으로 선언 |
| 로그가 필요한 어댑터·서비스 | `@Slf4j` |

- 필드 주입용 `@Autowired`, DTO·도메인·JPA 엔티티의 `@Data`와 클래스 전체 `@Setter`는 금지한다.
- 필드는 기본 `private`으로 두고 외부에서 필요한 메서드만 공개한다.
- 도메인과 JPA 엔티티는 필요한 값을 받는 생성자로 초기화한다. DTO의 비공개 빌더 규칙을 엔티티에 적용하지 않는다.

## 도메인 규칙

- 업무 필수값·불변 조건 검증, 상태 전이 허용 여부와 계산은 서비스에서 판단한다. 도메인은 서비스가 결정한 값을 보유하고 변경을 반영한다. 업무 검증을 서비스에 두는 선택은 헥사고날의 의존 방향과 양립하지만, 유효하지 않은 도메인 상태를 생성할 위험이 있다. HTTP·메시지·배치 등 모든 신규 업무 입력과 상태 변경은 동일한 입력 포트와 서비스 검증을 통과시킨다. 영속성 복원은 별도 경로로 구분하고 손상된 데이터는 정상 업무 결과로 취급하지 않는다.
- 여러 객체의 조회·저장과 외부 요청 순서도 서비스에서 조정한다.
- 현재 시각이 업무 판단에 필요하면 서비스에서 `Clock` 등으로 얻어 테스트에서 시간을 제어할 수 있게 한다.
- 날짜와 시각은 의미에 맞는 타입으로 표현한다. API 오프셋·시간대와 DB 시각 변환 기준은 계약과 스키마에 맞춰 어댑터에서 명시한다.
- 금액·코인 계산은 요구사항의 단위와 반올림 기준을 따른다. 정확한 소수 계산에는 `BigDecimal`, 정수 단위에는 범위를 검토한 정수 타입을 사용한다.

## 영속성과 JPA 엔티티

- `JpaRepository`, Querydsl, JPA 엔티티와 매핑 코드는 `adapter.out.persistence`에 둔다. Spring Data 인터페이스는 `JpaRepository<엔티티, ID>`를 상속하고 `@Repository`를 중복 선언하지 않는다.
- JPA 엔티티의 테이블·컬럼·식별자 생성 전략·필수값·제약은 ERD와 실제 마이그레이션에 맞춘다.
- 저장 시 도메인 모델을 JPA 엔티티에 반영하고, 생성된 ID 등 이후 흐름에 필요한 저장 결과를 포트 반환값에 담는다.
- 도메인 객체의 변경을 영속화할 때는 저장 포트를 명시적으로 호출한다. 도메인 객체는 JPA 변경 감지 대상이 아니다.
- 기존 데이터를 수정할 때는 식별자, 기존 감사 시각, 삭제 상태와 연관관계를 보존한다. 전달되지 않은 필드를 새 엔티티의 기본값으로 덮어쓰지 않는다.
- 낙관적 잠금을 사용하면 읽은 버전을 저장 시점까지 전달·검증한다. 최신 엔티티를 다시 읽어 이전 버전을 잃는 매핑으로 충돌 검사를 우회하지 않는다.
- 어댑터는 포트가 요구하는 데이터를 트랜잭션 안에서 읽어 변환한다. 지연 로딩 프록시나 영속 컬렉션을 내부 계층에 반환하지 않는다.

| 참조 대상 | 매핑 기준 |
| --- | --- |
| 같은 서비스에서 객체 탐색이 필요한 데이터 | JPA 엔티티 사이에 연관관계를 매핑하고 지연 로딩을 명시한다. |
| 같은 서비스에서 식별자만 필요한 데이터 | ID 필드를 사용하고 참조 무결성은 필요한 DB 제약으로 보장한다. |
| 다른 서비스가 소유한 데이터 | 외부 ID를 저장하고 API·이벤트 출력 포트를 통해 필요한 값을 받는다. |

도메인 모델의 관계는 업무에 필요한 객체·값·식별자로 표현한다. JPA 연관관계 어노테이션은 영속성 어댑터 안에 둔다.

### BaseEntity와 소프트 삭제

- 공통 JPA 상위 클래스 `BaseEntity`는 `global.persistence`에 둔다. 도메인 모델은 이를 상속하지 않는다.
- `createdAt`, `updatedAt`, `deletedAt`을 공유하는 테이블만 해당 상위 클래스를 적용한다. 컬럼 구성이 다른 엔티티는 스키마에 맞는 필드를 직접 선언하거나 필요한 감사 필드만 공유한다.
- JPA Auditing을 사용하는 서비스는 설정에서 `@EnableJpaAuditing`을 활성화하고 생성·수정 시각 저장을 검증한다.
- 소프트 삭제 시각을 변경하는 저장 동작과 삭제된 데이터를 제외하는 조회 조건을 함께 구현한다. 단건·목록·존재 확인·집계와 관련 첨부 조회에 동일한 접근 정책을 적용한다.
- 소프트 삭제·보관·파기 정책의 기준은 PRD와 API 명세다. 보관 기간 등 미정 정책은 기능 구현 전에 확인한다.

## Querydsl 사용 기준

- 기본 CRUD와 단순 조회는 Spring Data JPA의 기본 메서드와 쿼리 메서드를 사용한다.
- 선택 조건 조합, 다중 조인·집계 등 복잡한 조회는 Querydsl로 작성한다. 구현 위치는 영속성 어댑터의 커스텀 조회 구현이다.
- 목록 조회에서 필요한 데이터를 묶어 읽는다. 연관관계 탐색과 ID별 개별 조회 모두 실제 SQL·외부 호출 횟수를 확인한다.
- 읽기 전용 목록은 출력 포트가 정의한 조회 결과 모델로 직접 매핑할 수 있다.
- 성능 개선을 위해 조회 방식을 바꾸면 실제 SQL, 쿼리 횟수와 필요한 실행 계획을 비교한다.

## 트랜잭션과 외부 연동

- DB 쓰기 유스케이스의 공개 서비스 메서드에 `@Transactional`, DB 조회 전용 유스케이스에 `@Transactional(readOnly = true)`을 적용한다.
- 하나의 유스케이스에서 원자적으로 처리해야 하는 DB 변경은 같은 트랜잭션에 포함한다. 예외를 삼켜 부분 변경이 커밋되지 않도록 하고, 롤백이 필요한 예외의 동작을 검증한다.
- 같은 객체 내부 호출로 트랜잭션 프록시를 우회하지 않도록 진입 경로를 확인한다. 동시성 제어는 업무 조건에 따라 DB 제약·조건부 갱신·잠금 등을 선택하고 경쟁 상황을 검증한다.
- 비밀번호 해싱·검증, 토큰 발급·검증처럼 유스케이스가 요구하는 기술 기능도 출력 포트로 정의한다. 포트는 필요한 연산과 실패 계약만 노출하며, BCrypt/JWT 구현과 기술 예외는 출력 어댑터에서 처리한다. 입력 필터가 전송 계층 인증만 수행할 때는 내부가 소유한 검증 포트에 의존할 수 있다. 사용자 상태·권한 등 업무 판단이 필요하면 해당 입력 포트를 호출한다.
- 외부 API, 메시지, 파일 저장은 각각 출력 포트와 어댑터로 연결한다. 타임아웃과 재시도는 연동 계약에 맞추고 중복 실행 가능한 작업인지 먼저 확인한다. 외부 호출 실패를 무시하고 유스케이스를 성공 처리하지 않는다.
- 로컬 DB 트랜잭션은 외부 시스템의 변경을 함께 롤백하지 않는다. DB 변경과 이벤트 발행의 일관성이 필요하면 아웃박스 등 전달 보장 방법을 정하고, 외부 변경 후 실패할 수 있는 작업은 보상·재시도 경로를 설계한다.
- 멱등성 키의 범위, 동일 키의 다른 입력 처리, 재시도 시 결과와 보관 기간은 API 계약을 따른다. 소비자는 중복 메시지와 순서 변경에 대한 처리 기준을 갖는다.

## API와 공통 응답

- HTTP 경로·메서드·상태·필드·페이지네이션은 [API 공통 계약](../api/README.md#공통-계약-초안)과 해당 도메인 명세를 따른다. 웹 어댑터는 `/api` 경로와 계약의 응답 형식을 구현한다.
- 컨트롤러에 `@RestController`, 공통 경로에 `@RequestMapping`, 엔드포인트에 HTTP 메서드별 매핑을 사용한다. JSON 본문 검증은 `@Valid @RequestBody`로 수행한다. 본문은 등록할 값이고 헤더는 인증 토큰 등 요청 메타데이터다. 인증 사용자 식별자는 인증된 보안 컨텍스트나 신뢰할 수 있는 게이트웨이 계약으로 전달한다. 클라이언트가 입력한 본문이나 임의 헤더의 사용자 ID는 인증 근거로 사용하지 않는다.
- `ApiResponse<T>`는 `global.web.response`에 둔다. `success(data)`는 성공 본문을, `error(code, message)`는 오류 본문을 만든다. HTTP 상태는 웹 어댑터의 `ResponseEntity`에서 지정한다.
- 기존 API를 수정할 때는 서비스별로 공개된 요청·응답 계약을 우선한다. 현재 인증 서비스의 오류 필드 `title`, `status`, `detail`, `code`는 기존 계약을 유지하고, 공통 형식 전환이 합의된 작업에서 변경한다.
- 공통 형식을 적용하는 API의 성공은 `{"data":{"balanceCoins":7000}}`, 오류는 `{"code":"VALIDATION_ERROR","message":"요청 값이 올바르지 않습니다."}` 형식을 따른다. 사용하지 않는 `null` 필드는 서비스의 응답 직렬화 설정에서 제외한다.
- `204`, 본문 없는 `202`, 파일 응답과 `302` 리다이렉트는 API 명세의 본문 규칙을 따른다.

## 예외와 오류 처리

- 업무 규칙 위반은 기술 독립적인 `BusinessException`과 `ErrorCode`로 표현한다. 공통 타입은 `shared.exception`에 두고 코드와 공개 가능한 기본 메시지를 관리한다.
- `BusinessException`은 `RuntimeException`을 상속하고 오류 코드를 보관한다. 기본 메시지, 공개 가능한 사용자 메시지 또는 원인 예외를 지정할 수 있다.
- `ErrorCode`는 업무 실패의 식별자와 메시지만 가진다. HTTP 요청 형식·메서드 등 전송 계층 전용 실패는 웹 계층의 `WebErrorCode`에 둔다. `HttpStatus`와 업무 오류의 HTTP 매핑은 `global.web.exception.ErrorCodeHttpMapper` 등 웹 계층에서 관리한다.
- `GlobalExceptionHandler`는 `@RestControllerAdvice`로 업무 예외, 입력 오류, 예상하지 못한 오류를 공통 응답에 매핑한다. 업무 코드별 HTTP 상태는 해당 API 명세에 맞춰 명시적으로 매핑하고 누락을 테스트한다.
- Spring MVC 요청 오류는 상태와 필요한 헤더를 보존한다. 예상하지 못한 오류는 서버에 원인을 기록하고 클라이언트에는 기본 500 메시지를 반환한다.
- Spring Security 필터의 인증·인가 오류는 `AuthenticationEntryPoint`, `AccessDeniedHandler`에서 같은 오류 형식으로 반환한다.
- 출력 어댑터는 처리 가능한 외부 기술 오류를 포트 계약의 실패로 변환한다. 고유성에 사전 조회를 사용하더라도 동시 요청에 대한 최종 보장은 DB의 고유 제약으로 한다. 위반된 제약을 확인해 해당 업무 예외로 변환하고, 다른 무결성 위반은 원인을 보존한다. 변환이 필요한 쓰기는 제약 오류가 어디에서 발생하는지 확인한다. 저장 시점에 어댑터에서 처리해야 하는 경우에만 필요한 flush를 적용한다. 예상하지 못한 장애를 정상적인 조회 부재나 성공으로 바꾸지 않는다.
- 원인 예외의 메시지, SQL, 외부 응답 본문과 비밀값을 클라이언트 오류 메시지에 그대로 노출하지 않는다.

## 테스트 작성 규칙

| 대상 | 확인할 내용 |
| --- | --- |
| 도메인 단위 테스트 | 서비스가 전달한 상태의 보유와 변경 반영을 검증한다. |
| 유스케이스 단위 테스트 | 입력 포트를 호출하고 출력 포트의 Fake·Mock으로 업무 검증·계산·상태 변경과 성공·실패 및 권한 조건을 검증한다. |
| 웹 어댑터 테스트 | 입력 검증, 인증 정보 변환, HTTP 상태·헤더·JSON 필드값과 예외 매핑을 확인한다. |
| 영속성 통합 테스트 | 실제 대상 DB에서 매핑, 조회 조건, 제약, 저장·롤백·동시성 동작을 확인한다. |
| 외부 연동 테스트 | 외부 계약, 타임아웃, 오류 변환·재시도·중복 처리를 해당 연동 환경에서 확인한다. |

- 테스트는 대상과 대응하는 패키지에 두고 일반 테스트는 `XxxTest`, 통합 테스트는 `XxxIntegrationTest`로 이름 짓는다.
- 메서드 이름은 검증 동작이 드러나는 영어로 작성하고, `@DisplayName`에는 조건과 기대 결과를 한글로 적는다.
- 실제 값을 가진 DTO·결과 모델로 검증하고 구현의 호출 순서를 그대로 복제하는 테스트를 피한다.
- 정상·빈 입력·경계·실패 사례를 필요한 만큼 구분한다. 버그 수정은 가능한 경우 수정 전 재현과 회귀 검증을 남긴다.
- 아키텍처 검증은 서비스의 업무 모듈을 포함해 [의존 방향과 계층별 책임](#의존-방향과-계층별-책임)을 확인한다. ArchUnit을 도입한 서비스는 패키지·타입 규칙과 모듈 순환 검사를 자동화하고 서비스 어노테이션의 허용 범위를 검사 설정에 반영한다. 그 외에는 코드 리뷰로 확인한다.
- Mock·단위 테스트 통과를 실제 DB·외부 API 검증 완료로 표현하지 않는다. 실행한 환경과 미검증 범위를 보고한다.

### 아키텍처 테스트 · ArchitectureTest.java

원본 `ArchitectureTest`에서 애플리케이션이 어댑터에 의존하지 않는지 확인하는 부분이다. 루이쿠리에 적용할 때는 서비스 루트 패키지를 검사 대상으로 삼고, 어댑터 패턴을 원본의 `..adaptor..`에서 루이쿠리의 `..adapter..`로 바꾼다.

```java
    @Test
    void applicationShouldNotDependOnAdapters() {
        ArchRule rule = noClasses()
                .that().resideInAPackage("..application..")
                .should().dependOnClassesThat().resideInAnyPackage("..adaptor..");

        rule.check(importedClasses);
    }
```

## 코드 서식과 주석

- Java 서식의 기본은 [네이버 핵데이 Java 코딩 컨벤션](https://naver.github.io/hackday-conventions-java/) v1.2다. 팀원이 IntelliJ에서는 [공식 IntelliJ 포매터](https://github.com/naver/hackday-conventions-java/blob/master/rule-config/naver-intellij-formatter.xml)를 가져오고, Eclipse에서는 [공식 Eclipse 포매터](https://github.com/naver/hackday-conventions-java/blob/master/rule-config/naver-eclipse-formatter.xml)를 가져와 적용한다. [공식 Checkstyle 규칙](https://github.com/naver/hackday-conventions-java/blob/master/rule-config/naver-checkstyle-rules.xml)은 8.24 이상과 호환되며 일부 규칙은 자동 검사하지 못한다. 각 서비스에 도구가 실제로 설정된 경우 해당 명령을 실행하고, 미설정이면 별도 작업으로 도입한다. 포매터 적용만으로 전체 규칙 준수를 보장하지 않는다. 아래에 명시한 팀 규칙과 차이가 있으면 팀 규칙을 우선하고 도구 설정도 그에 맞춘다.
- 공식 포매터와 Checkstyle의 기본 탭 들여쓰기는 이 팀의 스페이스 4칸 규칙과 다르다. 공식 포매터를 가져온 뒤 IntelliJ의 Java Code Style > Tabs and Indents에서 `Use tab character`를 해제하고 들여쓰기 크기를 4로 설정한다. Eclipse에서는 Java > Code Style > Formatter의 프로필을 편집해 Indentation의 탭 정책을 spaces only, 크기를 4로 설정한다. 서비스에 Checkstyle을 도입할 때도 탭·들여쓰기 검사를 팀 설정으로 조정해 포매터와 같은 기준으로 검사한다. 상세 가져오기 절차는 [네이버 공식 도구 설정 안내](https://github.com/naver/hackday-conventions-java/blob/master/src/tool-configs.adoc)를 따른다.
- UTF-8(BOM 없음), LF, 스페이스 4칸을 사용한다. 줄 끝 공백을 제거하고 파일 끝은 개행 하나로 마친다.
- 한 줄은 들여쓰기를 포함해 120자 이내로 쓴다. URL·외부 계약값처럼 분리할 수 없는 값은 예외로 둔다.
- 연산자 양옆과 쉼표 뒤에는 공백 한 칸을 둔다. 제어문 키워드와 여는 소괄호 사이는 띄우고 메서드 이름과 소괄호는 붙인다.
- 여러 줄 인자는 여는 소괄호 다음 줄부터 한 줄에 하나씩 쓰고 4칸 추가 들여쓰기한다. 닫는 소괄호는 시작 줄과 같은 깊이에 둔다. 연쇄 호출은 이어지는 줄 앞에 마침표를 둔다.
- 조건문·반복문은 한 줄이어도 중괄호를 쓴다. 여는 중괄호는 같은 줄에 두고 `else`, `catch`, `finally`는 앞의 닫는 중괄호와 같은 줄에 둔다.
- 메서드 사이에는 빈 줄 하나를 둔다. 연속 빈 줄과 블록의 처음·마지막 빈 줄을 피한다.
- 패키지 선언, import, 타입 선언 순서로 두고 사이에 빈 줄을 둔다. 일반 import 다음 정적 import를 별도 그룹으로 두고 그룹 안은 전체 이름으로 정렬한다. 와일드카드·미사용 import는 금지한다.
- 클래스 선언 순서는 상수, 필드, 생성자, 메서드, 중첩 타입이다. private 보조 메서드는 호출하는 메서드 가까이에 둘 수 있다.
- 이름과 구조로 드러나는 동작을 주석으로 반복하지 않는다. 코드만으로 알기 어려운 제약·결정 이유가 있으면 짧게 설명하고, 설계 결정은 관련 ADR에 기록한다.
- 포매터·정적 분석·테스트 명령은 서비스 저장소의 실제 빌드 설정을 확인해 실행한다.

## 설정과 로깅

- 비밀번호·API 키·토큰은 코드나 공유 설정 파일에 저장하지 않는다. 환경 변수 등 서비스의 비밀값 주입 방식으로 전달한다.
- 외부 기술 설정은 `global.config` 또는 기능별 어댑터 설정에 둔다. 도메인이 환경 변수나 설정 파일을 직접 읽지 않도록 한다.
- 로그에는 실패 맥락과 추적 식별자를 남기고, 요청·응답 본문과 개인정보·인증 정보를 그대로 기록하지 않는다.
- 동일한 예외를 여러 계층에서 반복 기록하지 않도록 처리 책임이 있는 경계에서 기록한다.

## 예시 코드

참고 저장소의 커밋 `1ea4ccb`에서 회원가입·로그인에 연결되는 핵심 파일을 가져왔다. 각 파일명을 펼치면 패키지 선언부터 전체 코드를 볼 수 있다. 루이쿠리에서 기능을 작성할 때는 위 패키지 배치와 응답 형식 규칙을 따른다.

### 컨트롤러와 웹 매퍼

<details>
<summary>AuthController.java</summary>

```java
package com.spharos.userservice.adaptor.in.web;

import com.spharos.userservice.adaptor.in.web.security.LoginUser;
import com.spharos.userservice.adaptor.in.web.mapper.AuthVoMapper;
import com.spharos.userservice.adaptor.in.web.vo.AuthLoginRequestVo;
import com.spharos.userservice.adaptor.in.web.vo.AuthLoginResponseVo;
import com.spharos.userservice.adaptor.in.web.vo.AuthMeResponseVo;
import com.spharos.userservice.adaptor.in.web.vo.AuthSignUpRequestVo;
import com.spharos.userservice.adaptor.in.web.vo.AuthSignUpResponseVo;
import com.spharos.userservice.application.port.in.AuthUseCase;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@Tag(name = "Auth", description = "회원 인증 API")
@RequiredArgsConstructor
@RequestMapping("/api/v1")
@RestController
public class AuthController {

    private final AuthUseCase authUseCase;
    private final AuthVoMapper authVoMapper;

    @Operation(
            summary = "회원가입",
            description = "신규 회원을 등록합니다."
    )
    @ApiResponse(responseCode = "201", description = "회원가입 성공")
    @ApiResponse(responseCode = "400", description = "요청 값 검증 실패")
    @ApiResponse(responseCode = "409", description = "loginId 또는 email 중복")
    @PostMapping("/auth/sign-up")
    @ResponseStatus(HttpStatus.CREATED)
    public AuthSignUpResponseVo signUp(@Valid @RequestBody AuthSignUpRequestVo authSignUpRequestVo) {
        return authVoMapper.toSignUpResponseVo(
                authUseCase.signUp(authVoMapper.toSignUpRequestDto(authSignUpRequestVo))
        );
    }

    @Operation(
            summary = "로그인",
            description = "loginId와 password로 인증하고 JWT 액세스 토큰을 발급합니다."
    )
    @ApiResponse(responseCode = "200", description = "로그인 성공")
    @ApiResponse(responseCode = "400", description = "요청 값 검증 실패")
    @ApiResponse(responseCode = "401", description = "loginId 또는 password 불일치")
    @PostMapping("/auth/login")
    public AuthLoginResponseVo login(@Valid @RequestBody AuthLoginRequestVo authLoginRequestVo) {
        return authVoMapper.toLoginResponseVo(
                authUseCase.login(authVoMapper.toLoginRequestDto(authLoginRequestVo))
        );
    }

    @Operation(
            summary = "내 정보",
            description = "액세스 토큰에 담긴 회원 식별자를 반환합니다."
    )
    @SecurityRequirement(name = "bearerAuth")
    @ApiResponse(responseCode = "200", description = "인증된 회원")
    @ApiResponse(responseCode = "401", description = "토큰 없음, 위조, 만료")
    @GetMapping("/auth/me")
    public AuthMeResponseVo me(@AuthenticationPrincipal LoginUser loginUser) {
        return new AuthMeResponseVo(loginUser.getAuthUuid(), loginUser.getLoginId());
    }
}
```

</details>

<details>
<summary>AuthVoMapper.java</summary>

```java
package com.spharos.userservice.adaptor.in.web.mapper;

import com.spharos.userservice.adaptor.in.web.vo.AuthLoginRequestVo;
import com.spharos.userservice.adaptor.in.web.vo.AuthLoginResponseVo;
import com.spharos.userservice.adaptor.in.web.vo.AuthSignUpRequestVo;
import com.spharos.userservice.adaptor.in.web.vo.AuthSignUpResponseVo;
import com.spharos.userservice.application.port.in.dto.AuthLoginRequestDto;
import com.spharos.userservice.application.port.in.dto.AuthLoginResultDto;
import com.spharos.userservice.application.port.in.dto.AuthSignUpRequestDto;
import com.spharos.userservice.application.port.in.dto.AuthSignUpResultDto;
import org.springframework.stereotype.Component;

@Component
public class AuthVoMapper {

    public AuthSignUpRequestDto toSignUpRequestDto(AuthSignUpRequestVo vo) {
        return AuthSignUpRequestDto.builder()
                .loginId(vo.getLoginId())
                .password(vo.getPassword())
                .email(vo.getEmail())
                .name(vo.getName())
                .build();
    }

    public AuthSignUpResponseVo toSignUpResponseVo(AuthSignUpResultDto resultDto) {
        return new AuthSignUpResponseVo(resultDto.getAuthUuid(), resultDto.getLoginId());
    }

    public AuthLoginRequestDto toLoginRequestDto(AuthLoginRequestVo vo) {
        return AuthLoginRequestDto.builder()
                .loginId(vo.getLoginId())
                .password(vo.getPassword())
                .build();
    }

    public AuthLoginResponseVo toLoginResponseVo(AuthLoginResultDto resultDto) {
        return new AuthLoginResponseVo(
                resultDto.getAuthUuid(),
                resultDto.getLoginId(),
                resultDto.getAccessToken()
        );
    }
}
```

</details>

### 웹 요청·응답 VO

<details>
<summary>AuthSignUpRequestVo.java</summary>

```java
package com.spharos.userservice.adaptor.in.web.vo;

import com.spharos.userservice.domain.model.AuthDomain;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@Schema(description = "회원가입 요청")
public class AuthSignUpRequestVo {

    @NotBlank(message = "loginId는 필수입니다.")
    @Size(min = 4, message = "loginId는 4자 이상이어야 합니다.")
    @Schema(description = "로그인 ID", example = "testuser")
    private String loginId;

    @NotBlank(message = "password는 필수입니다.")
    @Size(min = 8, message = "password는 8자 이상이어야 합니다.")
    @Schema(description = "비밀번호", example = "password123")
    private String password;

    @NotBlank(message = "email은 필수입니다.")
    @Pattern(regexp = AuthDomain.EMAIL_REGEX, message = "email 형식이 올바르지 않습니다.")
    @Schema(description = "이메일", example = "test@example.com")
    private String email;

    @NotBlank(message = "name은 필수입니다.")
    @Schema(description = "이름", example = "홍길동")
    private String name;

    public void setLoginId(String loginId) {
        this.loginId = trimToNull(loginId);
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public void setEmail(String email) {
        this.email = trimToNull(email);
    }

    public void setName(String name) {
        this.name = trimToNull(name);
    }

    private static String trimToNull(String value) {
        if (value == null) {
            return null;
        }
        return value.trim();
    }
}
```

</details>

<details>
<summary>AuthSignUpResponseVo.java</summary>

```java
package com.spharos.userservice.adaptor.in.web.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
@Schema(description = "회원가입 응답")
public class AuthSignUpResponseVo {

    @Schema(description = "회원 UUID", example = "550e8400-e29b-41d4-a716-446655440000")
    private final String authUuid;

    @Schema(description = "로그인 ID", example = "testuser")
    private final String loginId;
}
```

</details>

<details>
<summary>AuthLoginRequestVo.java</summary>

```java
package com.spharos.userservice.adaptor.in.web.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@Schema(description = "로그인 요청")
public class AuthLoginRequestVo {

    @NotBlank(message = "loginId는 필수입니다.")
    @Schema(description = "로그인 ID", example = "testuser")
    private String loginId;

    @NotBlank(message = "password는 필수입니다.")
    @Schema(description = "비밀번호", example = "password123")
    private String password;

    public void setLoginId(String loginId) {
        this.loginId = loginId == null ? null : loginId.trim();
    }

    public void setPassword(String password) {
        this.password = password;
    }
}
```

</details>

<details>
<summary>AuthLoginResponseVo.java</summary>

```java
package com.spharos.userservice.adaptor.in.web.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
@Schema(description = "로그인 응답")
public class AuthLoginResponseVo {

    @Schema(description = "회원 UUID")
    private final String authUuid;

    @Schema(description = "로그인 ID")
    private final String loginId;

    @Schema(description = "액세스 토큰")
    private final String accessToken;
}
```

</details>

<details>
<summary>AuthMeResponseVo.java</summary>

```java
package com.spharos.userservice.adaptor.in.web.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
@Schema(description = "인증된 회원")
public class AuthMeResponseVo {

    @Schema(description = "회원 UUID", example = "550e8400-e29b-41d4-a716-446655440000")
    private final String authUuid;

    @Schema(description = "로그인 ID", example = "testuser")
    private final String loginId;
}
```

</details>

### 입력 포트와 애플리케이션 DTO

<details>
<summary>AuthUseCase.java</summary>

```java
package com.spharos.userservice.application.port.in;

import com.spharos.userservice.application.port.in.dto.AuthLoginRequestDto;
import com.spharos.userservice.application.port.in.dto.AuthLoginResultDto;
import com.spharos.userservice.application.port.in.dto.AuthSignUpRequestDto;
import com.spharos.userservice.application.port.in.dto.AuthSignUpResultDto;

public interface AuthUseCase {

    AuthSignUpResultDto signUp(AuthSignUpRequestDto authSignUpRequestDto);

    AuthLoginResultDto login(AuthLoginRequestDto authLoginRequestDto);
}
```

</details>

<details>
<summary>AuthSignUpRequestDto.java</summary>

```java
package com.spharos.userservice.application.port.in.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AuthSignUpRequestDto {

    private String loginId;
    private String password;
    private String email;
    private String name;

}
```

</details>

<details>
<summary>AuthSignUpResultDto.java</summary>

```java
package com.spharos.userservice.application.port.in.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class AuthSignUpResultDto {

    private final String authUuid;
    private final String loginId;
}
```

</details>

<details>
<summary>AuthLoginRequestDto.java</summary>

```java
package com.spharos.userservice.application.port.in.dto;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class AuthLoginRequestDto {

    private final String loginId;
    private final String password;
}
```

</details>

<details>
<summary>AuthLoginResultDto.java</summary>

```java
package com.spharos.userservice.application.port.in.dto;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class AuthLoginResultDto {

    private final String authUuid;
    private final String loginId;
    private final String accessToken;
}
```

</details>

### 애플리케이션 서비스

<details>
<summary>AuthService.java</summary>

```java
package com.spharos.userservice.application.service;

import com.spharos.userservice.application.port.in.AuthUseCase;
import com.spharos.userservice.application.port.in.dto.AuthLoginRequestDto;
import com.spharos.userservice.application.port.in.dto.AuthLoginResultDto;
import com.spharos.userservice.application.port.in.dto.AuthSignUpRequestDto;
import com.spharos.userservice.application.port.in.dto.AuthSignUpResultDto;
import com.spharos.userservice.application.port.out.AuthRepositoryPort;
import com.spharos.userservice.application.port.out.PasswordEncoderPort;
import com.spharos.userservice.application.port.out.TokenProviderPort;
import com.spharos.userservice.domain.exception.DuplicateEmailException;
import com.spharos.userservice.domain.exception.DuplicateLoginIdException;
import com.spharos.userservice.domain.exception.InvalidCredentialsException;
import com.spharos.userservice.domain.model.AuthDomain;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService implements AuthUseCase {

    private final AuthRepositoryPort authRepositoryPort;
    private final PasswordEncoderPort passwordEncoderPort;
    private final TokenProviderPort tokenProviderPort;

    public AuthService(
            AuthRepositoryPort authRepositoryPort,
            PasswordEncoderPort passwordEncoderPort,
            TokenProviderPort tokenProviderPort
    ) {
        this.authRepositoryPort = authRepositoryPort;
        this.passwordEncoderPort = passwordEncoderPort;
        this.tokenProviderPort = tokenProviderPort;
    }

    @Override
    @Transactional
    public AuthSignUpResultDto signUp(AuthSignUpRequestDto authSignUpRequestDto) {
        AuthDomain authDomain = AuthDomain.createSignUp(
                authSignUpRequestDto.getLoginId(),
                authSignUpRequestDto.getPassword(),
                authSignUpRequestDto.getEmail(),
                authSignUpRequestDto.getName()
        );

        if (authRepositoryPort.existsByLoginId(authDomain.getLoginId())) {
            throw new DuplicateLoginIdException(authDomain.getLoginId());
        }
        if (authRepositoryPort.existsByEmail(authDomain.getEmail())) {
            throw new DuplicateEmailException(authDomain.getEmail());
        }

        AuthDomain encodedAuthDomain = authDomain.withEncodedPassword(
                passwordEncoderPort.encode(authDomain.getPassword())
        );

        authRepositoryPort.save(encodedAuthDomain);

        return new AuthSignUpResultDto(encodedAuthDomain.getAuthUuid(), encodedAuthDomain.getLoginId());
    }

    @Override
    @Transactional(readOnly = true)
    public AuthLoginResultDto login(AuthLoginRequestDto authLoginRequestDto) {
        AuthDomain authDomain = authRepositoryPort.findByLoginId(authLoginRequestDto.getLoginId())
                .orElseThrow(InvalidCredentialsException::new);

        if (!passwordEncoderPort.matches(authLoginRequestDto.getPassword(), authDomain.getPassword())) {
            throw new InvalidCredentialsException();
        }

        String accessToken = tokenProviderPort.createAccessToken(authDomain);

        return new AuthLoginResultDto(authDomain.getAuthUuid(), authDomain.getLoginId(), accessToken);
    }
}
```

</details>

### 출력 포트

<details>
<summary>AuthRepositoryPort.java</summary>

```java
package com.spharos.userservice.application.port.out;

import com.spharos.userservice.domain.model.AuthDomain;

import java.util.Optional;

public interface AuthRepositoryPort {

    void save(AuthDomain authDomain);

    boolean existsByLoginId(String loginId);

    boolean existsByEmail(String email);

    Optional<AuthDomain> findByLoginId(String loginId);
}
```

</details>

<details>
<summary>PasswordEncoderPort.java</summary>

```java
package com.spharos.userservice.application.port.out;

public interface PasswordEncoderPort {

    String encode(String rawPassword);

    boolean matches(String rawPassword, String encodedPassword);
}
```

</details>

<details>
<summary>TokenProviderPort.java</summary>

```java
package com.spharos.userservice.application.port.out;

import com.spharos.userservice.domain.model.AuthDomain;

public interface TokenProviderPort {

    String createAccessToken(AuthDomain authDomain);

    AccessTokenClaims parseAccessToken(String accessToken);
}
```

</details>

<details>
<summary>AccessTokenClaims.java</summary>

```java
package com.spharos.userservice.application.port.out;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class AccessTokenClaims {

    private final String authUuid;
    private final String loginId;
}
```

</details>

### 영속성 어댑터와 레포지토리

<details>
<summary>AuthRepositoryAdapter.java</summary>

```java
package com.spharos.userservice.adaptor.out.mysql;

import com.spharos.userservice.adaptor.out.mysql.mapper.AuthEntityMapper;
import com.spharos.userservice.adaptor.out.mysql.repository.AuthRepository;
import com.spharos.userservice.application.port.out.AuthRepositoryPort;
import com.spharos.userservice.domain.exception.DuplicateAuthIdentityException;
import com.spharos.userservice.domain.model.AuthDomain;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class AuthRepositoryAdapter implements AuthRepositoryPort {

    private final AuthRepository authRepository;
    private final AuthEntityMapper authEntityMapper;

    @Override
    public void save(AuthDomain authDomain) {
        try {
            authRepository.saveAndFlush(authEntityMapper.toEntity(authDomain));
        } catch (DataIntegrityViolationException exception) {
            throw new DuplicateAuthIdentityException();
        }
    }

    @Override
    public boolean existsByLoginId(String loginId) {
        return authRepository.existsByLoginId(loginId);
    }

    @Override
    public boolean existsByEmail(String email) {
        return authRepository.existsByEmail(email);
    }

    @Override
    public java.util.Optional<AuthDomain> findByLoginId(String loginId) {
        return authRepository.findByLoginId(loginId)
                .map(authEntityMapper::toDomain);
    }
}
```

</details>

<details>
<summary>AuthRepository.java</summary>

```java
package com.spharos.userservice.adaptor.out.mysql.repository;

import com.spharos.userservice.adaptor.out.mysql.entity.AuthEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface AuthRepository extends JpaRepository<AuthEntity, Long> {

    boolean existsByLoginId(String loginId);
    boolean existsByEmail(String email);
    Optional<AuthEntity> findByLoginId(String loginId);
    Optional<AuthEntity> findByAuthUuid(String authUuid);

}
```

</details>

<details>
<summary>AuthEntityMapper.java</summary>

```java
package com.spharos.userservice.adaptor.out.mysql.mapper;

import com.spharos.userservice.adaptor.out.mysql.entity.AuthEntity;
import com.spharos.userservice.domain.model.AuthDomain;
import org.springframework.stereotype.Component;

@Component
public class AuthEntityMapper {

    public AuthEntity toEntity(AuthDomain authDomain) {
        return AuthEntity.builder()
                .authUuid(authDomain.getAuthUuid())
                .loginId(authDomain.getLoginId())
                .password(authDomain.getPassword())
                .email(authDomain.getEmail())
                .name(authDomain.getName())
                .build();
    }

    public AuthDomain toDomain(AuthEntity authEntity) {
        return AuthDomain.fromPersistence(
                authEntity.getAuthUuid(),
                authEntity.getLoginId(),
                authEntity.getPassword(),
                authEntity.getEmail(),
                authEntity.getName()
        );
    }
}
```

</details>

<details>
<summary>AuthEntity.java</summary>

```java
package com.spharos.userservice.adaptor.out.mysql.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "auth")
public class AuthEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String authUuid;

    @Column(nullable = false, unique = true)
    private String loginId;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String name;
}
```

</details>

## 참고 자료

- [Domain-Driven Hexagon](https://github.com/Sairyss/domain-driven-hexagon): 기능별 유스케이스, 도메인과 포트·어댑터 구조의 참고 구현. TypeScript/NestJS 예제를 Java/Spring에 맞춰 적용한다.
- [FinPlay 코드 컨벤션](https://github.com/finplay-team/finplay-backend/blob/dev/docs/conventions/code.md)의 주제별 문서 구성을 참고했다.
- 포트와 어댑터의 역할과 내부·외부 경계는 [Alistair Cockburn의 헥사고날 아키텍처 원문](https://alistair.cockburn.us/hexagonal-architecture)을 참고했다.
