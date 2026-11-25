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

서비스 디렉터리는 `consultation-service`처럼 소문자와 하이픈으로 작성한다. Java 루트 패키지는 `com.louiekury.<서비스명>`이며, 여러 단어의 서비스명은 `medicalrecord`처럼 붙여 쓴다. 실행 클래스는 루트에 둔다.

루트 아래에 업무 모듈별 패키지를 두고 각 모듈 안에서 `domain`, `application`, `adapter`로 나눈다. 모듈은 업무 개념을 기준으로 나누며 여러 유스케이스에서 쓰는 도메인과 출력 포트는 모듈 안에서 공유한다. `application` 아래에는 유스케이스별 패키지를 두고 입력 포트, Command/Query와 구현 서비스를 함께 둔다. 아래는 상담 모듈의 상태 변경 예시다. 실제로 필요한 유스케이스와 어댑터만 만든다.

```text
com.louiekury.consultation
├── ConsultationApplication.java
├── booking
│   ├── domain
│   │   ├── Consultation.java
│   │   └── ConsultationStatus.java
│   ├── application
│   │   ├── updateconsultation
│   │   │   ├── UpdateConsultationUseCase.java
│   │   │   ├── UpdateConsultationCommand.java
│   │   │   └── UpdateConsultationService.java
│   │   ├── model
│   │   │   └── ConsultationResult.java
│   │   └── port
│   │       └── out
│   │           ├── GetConsultationPort.java
│   │           └── UpdateConsultationPort.java
│   └── adapter
│       ├── in
│       │   ├── web
│       │   │   ├── ConsultationController.java
│       │   │   ├── ConsultationWebAdapter.java
│       │   │   └── dto
│       │   │       ├── request
│       │   │       └── response
│       │   │           └── ConsultationResponseDto.java
│       │   └── messaging
│       └── out
│           ├── persistence
│           │   ├── ConsultationPersistenceAdapter.java
│           │   ├── ConsultationJpaRepository.java
│           │   ├── ConsultationJpaEntity.java
│           │   └── ConsultationPersistenceMapper.java
│           └── client
├── shared
│   └── exception
│       ├── BusinessException.java
│       └── ErrorCode.java
└── global
    ├── config
    ├── web
    │   ├── response
    │   │   └── ApiResponse.java
    │   └── exception
    │       ├── GlobalExceptionHandler.java
    │       └── ErrorCodeHttpMapper.java
    └── persistence
        └── BaseEntity.java
```

- `shared`에는 여러 기능이 실제로 공유하는 내부 타입을 둔다. Spring·JPA·Jackson·외부 SDK에 의존하지 않는다.
- `global`에는 서비스 공통의 외부 기술 설정과 어댑터 지원 코드를 둔다. 내부 계층에서 `global`을 참조하지 않는다.
- `application.createpet`, `application.getpet`처럼 유스케이스별 패키지에 입력 포트·Command/Query·서비스를 함께 둔다. 유스케이스마다 입력 포트와 서비스를 분리한다. 여러 유스케이스가 공유하는 결과 모델은 `application.model`, 출력 포트는 `application.port.out`에 둔다. 한 유스케이스에서만 쓰는 모델은 해당 유스케이스 패키지에 둔다. 불필요한 빈 계층이나 사용하지 않는 포트는 만들지 않는다.
- 특정 기능에서만 쓰는 설정과 변환기는 그 기능의 어댑터에 둔다.
- `CommonService`, `Manager`, `Helper`처럼 이름만으로 책임을 알기 어려운 공통 클래스를 만들지 않는다.

## 의존 방향과 계층별 책임

소스 코드의 의존 방향은 항상 바깥에서 안쪽으로 향한다. 화살표는 호출 순서가 아니라 타입 참조의 방향이다. 출력 어댑터는 애플리케이션이 소유한 출력 포트를 구현하고, 조립 시 구현체를 주입한다.

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
| 입력 어댑터 | HTTP·메시지·배치 입력 해석, 입력 모델 변환, 입력 포트 호출, 응답 변환 | 입력 포트와 입력·결과 모델, 해당 외부 기술 |
| 출력 어댑터 | 출력 포트 구현, JPA·Querydsl·외부 SDK 호출과 모델 변환 | 출력 포트, 도메인·애플리케이션 모델, 해당 외부 기술 |

- 도메인은 애플리케이션·어댑터·프레임워크를 참조하지 않는다. 애플리케이션은 웹·영속성·외부 SDK 구현과 설정을 참조하지 않는다. 서로 독립된 입력·출력 어댑터 사이에서는 직접 호출하지 않으며 외부 연동은 해당 출력 포트를 통한다. 동일한 웹 입력 어댑터 내부의 컨트롤러가 요청·응답 변환 담당 `WebAdapter`에 위임하는 것은 허용한다.
- 포트는 내부 계층이 소유하는 Java 인터페이스다. 필요한 업무 단위로 정의하고 사용하지 않는 범용 CRUD 메서드를 늘리거나 외부 SDK 전체 메서드를 복제하지 않는다. 입력 포트는 유스케이스의 호출 계약, 출력 포트는 유스케이스가 외부에 요구하는 기능과 반환·실패 계약을 정의한다.
- 입력 어댑터(컨트롤러와 웹 어댑터)는 유스케이스를 호출한다. 출력 어댑터는 출력 포트를 구현하며 서비스에서 구현 클래스를 직접 참조하지 않는다. 컴포넌트 스캔 또는 별도 설정이 구현체를 연결한다. 여러 구현체가 있을 때는 설정에서 주입 대상을 명시한다.
- 컨트롤러는 웹 어댑터를 생성자로 주입받고 각 메서드 본문에 `return` 한 문장으로 해당 메서드를 호출한다. 객체 생성·변환·조건문·지역 변수·업무 처리를 작성하지 않는다. 반환 본문이 없는 경우에도 웹 어댑터가 반환하는 `ResponseEntity<Void>`를 그대로 반환한다.
- 웹 어댑터는 요청 DTO를 Command/Query로 변환하고 입력 포트를 호출한 뒤 Result를 HTTP 응답으로 변환한다. 서비스는 웹 DTO와 HTTP 타입을 알지 못한다. 웹 어댑터는 업무 판단이나 저장을 직접 수행하지 않는다.
- 애플리케이션 서비스는 입력 포트를 구현하고 출력 포트를 주입받는다. `JpaRepository`, `EntityManager`, HTTP 클라이언트와 외부 SDK를 직접 사용하지 않는다.
- 포트의 인자와 반환값에 JPA 엔티티, Spring Data `Page`·`Pageable`, `ResponseEntity`, Jackson 타입, 외부 SDK 모델을 사용하지 않는다. 페이지 조건과 결과는 필요한 필드를 가진 애플리케이션 모델로 표현한다.
- 같은 서비스의 다른 모듈은 공개 입력 포트와 입력·결과 모델을 통해 호출한다. 다른 모듈의 서비스 구현체·도메인 내부 객체·영속성 어댑터를 직접 참조하지 않는다. 다른 모듈에 접근하는 흐름이 외부 연동과 같거나 결합을 분리해야 하면 출력 포트와 모듈 연동 어댑터를 사용한다. 모듈 간 순환 의존을 만들지 않는다. 같은 모듈의 다른 서비스 구현체를 직접 주입하지 않고 공통 업무가 필요하면 책임과 포트를 재설계한다.
- 별도 마이크로서비스는 출력 포트와 클라이언트·메시지 어댑터를 통해 연결한다. 다른 서비스의 DB나 내부 구현체에 직접 접근하지 않는다.
- 프로젝트에서는 실용적인 예외로 애플리케이션 서비스에 `@Service`와 `@Transactional` 사용을 허용한다. 이는 프레임워크 독립적인 코어를 지향하는 참고 저장소와 다른 선택이다. 포트·입력·결과 모델과 도메인은 프레임워크 독립적으로 유지한다. 구성·트랜잭션 지원 외의 Spring 기술 타입은 어댑터에서 다룬다.

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

구체적인 클래스와 호출 흐름은 [상품 등록과 조회 예제](#상품-등록과-조회-예제)를 참고한다.

- 요청·응답 DTO와 애플리케이션 입력·결과 모델은 일반 `class`와 `private final` 필드로 작성한다. DTO 클래스 자체에는 `final`을 붙이지 않는다.
- 객체 하나를 변환하면 `from`, 필드 값을 조합하면 `of` 정적 팩토리 메서드를 사용한다. DTO 매핑과 생성은 팩토리 내부에서 처리하며 빌더는 비공개로 둔다.
- `@Getter`, `@RequiredArgsConstructor(access = AccessLevel.PRIVATE)`, `@Builder(access = AccessLevel.PRIVATE)`를 사용한다.
- JSON 요청 DTO의 `of`에는 `@JsonCreator`, 인자에는 `@JsonProperty`를 붙인다. Bean Validation 제약은 웹 DTO 필드에 작성하며, 어노테이션과 필드를 한 묶음으로 배치한다.
- 필수 여부와 값의 범위는 API 명세에 맞춘다. 누락을 구분해야 하는 숫자·불리언 입력은 Wrapper 타입을 사용한다. PATCH의 생략과 명시적 `null`을 구분해야 할 때는 웹 어댑터에서 존재 여부도 읽고 명시적인 변경 모델로 전달한다.
- 컨트롤러는 요청 DTO, 인증된 사용자 식별자와 경로 값을 웹 어댑터에 그대로 전달한다. 웹 어댑터는 필요한 값을 추출하여 `Command.of(...)` 또는 Query를 만든다. 본문의 사용자 ID를 인증된 호출자 정보로 신뢰하지 않는다.
- 애플리케이션 모델의 팩토리는 웹 DTO를 인자로 받지 않는다.
- 애플리케이션 서비스는 결과 모델을 반환한다. 웹 어댑터는 `ResponseDto.from(result)`로 변환한 뒤 `ApiResponse.success(...)`와 HTTP 상태를 지정한다.
- JPA 엔티티와 도메인 모델은 영속성 어댑터에서 변환한다. 외부 API 모델은 클라이언트 어댑터에서 변환한다.

```text
요청 흐름: HTTP → 컨트롤러 → 웹 어댑터 → 입력 포트 → 서비스 → 출력 포트 → 영속성 어댑터 → DB
응답 흐름: DB → 영속성 어댑터 → 서비스 → 웹 어댑터 → 컨트롤러 → HTTP
모델 변환: 요청 DTO → Command/Query → 도메인 모델 ↔ 영속성 모델
           결과 모델 → 응답 DTO
```

이 흐름은 실행 순서다. 소스 의존 방향은 앞의 의존 방향 표를 따르며 서비스는 영속성 어댑터를 직접 참조하지 않는다.

웹 입력 검증에 더해 서비스에서도 업무 조건을 검증한다. 메시지·배치에서 같은 입력 포트를 호출해도 동일한 업무 규칙을 적용한다.

## Lombok과 객체 생성

| 대상 | 사용 기준 |
| --- | --- |
| 컨트롤러·서비스·어댑터 | `private final` 의존성과 `@RequiredArgsConstructor`로 생성자 주입 |
| DTO와 애플리케이션 모델 | `@Getter`, 비공개 필수 인자 생성자, 비공개 빌더와 정적 팩토리 |
| 도메인 모델 | 필요한 getter와 명시적 생성자·상태 변경 메서드 |
| JPA 엔티티 | `@Getter`, `@Entity`, `@Table`, `@NoArgsConstructor(access = AccessLevel.PROTECTED)` 순으로 선언 |
| 로그가 필요한 어댑터·서비스 | `@Slf4j` |

- 필드 주입용 `@Autowired`, DTO·도메인·JPA 엔티티의 `@Data`와 클래스 전체 `@Setter`는 금지한다.
- 필드는 기본 `private`으로 두고 외부에서 필요한 메서드만 공개한다.
- 도메인과 JPA 엔티티는 필요한 값을 받는 생성자로 초기화한다. DTO의 비공개 빌더 규칙을 엔티티에 적용하지 않는다.
- 도메인은 서비스가 판단한 상태 변경을 반영한다. API DTO나 영속성 모델을 참조하지 않도록 한다.

## 도메인 규칙

- 도메인 모델은 Spring, JPA, Jackson 및 외부 SDK에 의존하지 않는 Java 객체로 작성한다.
- 업무 필수값·불변 조건 검증, 상태 전이 허용 여부와 계산은 서비스에서 판단한다. 도메인은 서비스가 결정한 값을 보유하고 변경을 반영한다. 업무 검증을 서비스에 두는 선택은 헥사고날의 의존 방향과 양립하지만, 유효하지 않은 도메인 상태를 생성할 위험이 있다. HTTP·메시지·배치 등 모든 신규 업무 입력과 상태 변경은 동일한 입력 포트와 서비스 검증을 통과시킨다. 영속성 복원은 별도 경로로 구분하고 손상된 데이터는 정상 업무 결과로 취급하지 않는다.
- 여러 객체의 조회·저장과 외부 요청 순서도 서비스에서 조정한다. 이 점은 업무 불변식과 행동을 도메인에 두는 참고 저장소와 다른 프로젝트 선택이다.
- 현재 시각이 업무 판단에 필요하면 서비스에서 `Clock` 등으로 얻어 테스트에서 시간을 제어할 수 있게 한다.
- 날짜와 시각은 의미에 맞는 타입으로 표현한다. API 오프셋·시간대와 DB 시각 변환 기준은 계약과 스키마에 맞춰 어댑터에서 명시한다.
- 금액·코인 계산은 요구사항의 단위와 반올림 기준을 따른다. 정확한 소수 계산에는 `BigDecimal`, 정수 단위에는 범위를 검토한 정수 타입을 사용한다.

## 영속성과 JPA 엔티티

- `JpaRepository`, Querydsl, JPA 엔티티와 매핑 코드는 `adapter.out.persistence`에 둔다. Spring Data 인터페이스는 `JpaRepository<엔티티, ID>`를 상속하고 `@Repository`를 중복 선언하지 않는다.
- JPA 엔티티는 DB 매핑을 담당하고, 업무 규칙은 애플리케이션 서비스가 담당한다. 테이블·컬럼·식별자 생성 전략·필수값·제약은 ERD와 실제 마이그레이션에 맞춘다.
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

### 연관관계와 ID 참조 예시

같은 서비스의 상품 이미지 JPA 엔티티에서 상품을 탐색해야 하는 경우 다음 필드를 둔다. 아래 코드는 엔티티 필드의 발췌다.

```java
@ManyToOne(fetch = FetchType.LAZY, optional = false)
@JoinColumn(name = "product_id", nullable = false)
private ProductJpaEntity product;
```

다른 서비스의 상품을 참조하는 주문 항목 JPA 엔티티에는 외부 식별자를 저장한다.

```java
@Column(name = "product_id", nullable = false)
private Long productId;
```

### BaseEntity와 소프트 삭제

[BaseEntity](#베이스-엔티티--baseentityjava)와 [감사 설정](#감사-설정--jpaauditingconfigjava) 예제를 함께 적용한다.

- 공통 JPA 상위 클래스 `BaseEntity`는 `global.persistence`에 둔다. 도메인 모델은 이를 상속하지 않는다.
- `createdAt`, `updatedAt`, `deletedAt`을 공유하는 테이블만 해당 상위 클래스를 적용한다. 컬럼 구성이 다른 엔티티는 스키마에 맞는 필드를 직접 선언하거나 필요한 감사 필드만 공유한다.
- JPA Auditing을 사용하는 서비스는 설정에서 `@EnableJpaAuditing`을 활성화하고 생성·수정 시각 저장을 검증한다.
- 소프트 삭제 시각을 변경하는 저장 동작과 삭제된 데이터를 제외하는 조회 조건을 함께 구현한다. 단건·목록·존재 확인·집계와 관련 첨부 조회에 동일한 접근 정책을 적용한다.
- 소프트 삭제·보관·파기 정책의 기준은 PRD와 API 명세다. 보관 기간 등 미정 정책은 기능 구현 전에 확인한다.

## Querydsl 사용 기준

- 기본 CRUD와 단순 조회는 Spring Data JPA의 기본 메서드와 쿼리 메서드를 사용한다.
- 선택 조건 조합, 다중 조인·집계 등 복잡한 조회는 Querydsl로 작성한다. 구현 위치는 영속성 어댑터의 커스텀 조회 구현이다.
- 목록 조회에서 필요한 데이터를 묶어 읽는다. 연관관계 탐색과 ID별 개별 조회 모두 실제 SQL·외부 호출 횟수를 확인한다.
- 읽기 전용 목록은 출력 포트가 정의한 조회 결과 모델로 직접 매핑할 수 있다. 웹 응답 DTO를 영속성 조회의 반환 타입으로 사용하지 않는다.
- 성능 개선을 위해 조회 방식을 바꾸면 실제 SQL, 쿼리 횟수와 필요한 실행 계획을 비교한다.

## 트랜잭션과 외부 연동

- DB 쓰기 유스케이스의 공개 서비스 메서드에 `@Transactional`, DB 조회 전용 유스케이스에 `@Transactional(readOnly = true)`을 적용한다.
- 하나의 유스케이스에서 원자적으로 처리해야 하는 DB 변경은 같은 트랜잭션에 포함한다. 예외를 삼켜 부분 변경이 커밋되지 않도록 하고, 롤백이 필요한 예외의 동작을 검증한다.
- 같은 객체 내부 호출로 트랜잭션 프록시를 우회하지 않도록 진입 경로를 확인한다. 동시성 제어는 업무 조건에 따라 DB 제약·조건부 갱신·잠금 등을 선택하고 경쟁 상황을 검증한다.
- 외부 API, 메시지, 파일 저장은 각각 출력 포트와 어댑터로 연결한다. 타임아웃과 재시도는 연동 계약에 맞추고 중복 실행 가능한 작업인지 먼저 확인한다. 외부 호출 실패를 무시하고 유스케이스를 성공 처리하지 않는다.
- 로컬 DB 트랜잭션은 외부 시스템의 변경을 함께 롤백하지 않는다. DB 변경과 이벤트 발행의 일관성이 필요하면 아웃박스 등 전달 보장 방법을 정하고, 외부 변경 후 실패할 수 있는 작업은 보상·재시도 경로를 설계한다.
- 멱등성 키의 범위, 동일 키의 다른 입력 처리, 재시도 시 결과와 보관 기간은 API 계약을 따른다. 소비자는 중복 메시지와 순서 변경에 대한 처리 기준을 갖는다.

## API와 공통 응답

구현 코드는 [공통 API 응답 예제](#공통-api-응답--apiresponsejava)를 참고한다.

- HTTP 경로·메서드·상태·필드·페이지네이션은 [API 공통 계약](../api/README.md#공통-계약-초안)과 해당 도메인 명세를 따른다. 웹 어댑터는 `/api` 경로와 계약의 응답 형식을 구현한다.
- 컨트롤러에 `@RestController`, 공통 경로에 `@RequestMapping`, 엔드포인트에 HTTP 메서드별 매핑을 사용한다. JSON 본문 검증은 `@Valid @RequestBody`로 수행한다. 본문은 등록할 값이고 헤더는 인증 토큰 등 요청 메타데이터다. 인증 사용자 식별자는 인증된 보안 컨텍스트나 신뢰할 수 있는 게이트웨이 계약을 통해 전달하며, 클라이언트가 임의로 설정할 수 있는 사용자 ID 헤더를 인증 근거로 신뢰하지 않는다.
- `ApiResponse<T>`는 `global.web.response`에 둔다. `success(data)`는 성공 본문을, `error(code, message)`는 오류 본문을 만든다. HTTP 상태는 웹 어댑터의 `ResponseEntity`에서 지정한다.
- 성공은 `{"data":{"balanceCoins":7000}}`, 오류는 `{"code":"VALIDATION_ERROR","message":"요청 값이 올바르지 않습니다."}` 형식을 따른다. 공통 래퍼의 사용하지 않는 필드는 직렬화에서 제외한다.
- `204`, 본문 없는 `202`, 파일 응답과 `302` 리다이렉트는 API 명세의 본문 규칙을 따른다.
- 서비스나 포트는 `ApiResponse`, HTTP 상태 또는 웹 응답 DTO를 반환하지 않는다.

## 예외와 오류 처리

[업무 예외](#비즈니스-예외--businessexceptionjava), [오류 코드](#오류-코드--errorcodejava), [HTTP 매핑](#http-오류-매핑--errorcodehttpmapperjava), [전역 핸들러](#전역-예외-핸들러--globalexceptionhandlerjava)의 전체 코드는 공통 클래스 예제에 있다.

- 업무 규칙 위반은 기술 독립적인 `BusinessException`과 `ErrorCode`로 표현한다. 공통 타입은 `shared.exception`에 두고 코드와 공개 가능한 기본 메시지를 관리한다.
- `BusinessException`은 `RuntimeException`을 상속하고 오류 코드를 보관한다. 기본 메시지, 공개 가능한 사용자 메시지 또는 원인 예외를 지정할 수 있다.
- `ErrorCode`는 업무 실패의 식별자와 메시지만 가진다. HTTP 요청 형식·메서드 등 전송 계층 전용 실패는 웹 계층의 `WebErrorCode`에 둔다. `HttpStatus`와 업무 오류의 HTTP 매핑은 `global.web.exception.ErrorCodeHttpMapper` 등 웹 계층에서 관리한다.
- `GlobalExceptionHandler`는 `@RestControllerAdvice`로 업무 예외, 입력 오류, 예상하지 못한 오류를 공통 응답에 매핑한다. 업무 코드별 HTTP 상태는 해당 API 명세에 맞춰 명시적으로 매핑하고 누락을 테스트한다.
- Spring MVC 요청 오류는 상태와 필요한 헤더를 보존한다. 예상하지 못한 오류는 서버에 원인을 기록하고 클라이언트에는 기본 500 메시지를 반환한다.
- Spring Security 필터의 인증·인가 오류는 `AuthenticationEntryPoint`, `AccessDeniedHandler`에서 같은 오류 형식으로 반환한다.
- 출력 어댑터는 처리 가능한 외부 기술 오류를 포트 계약의 실패로 변환한다. 예상하지 못한 장애를 정상적인 조회 부재나 성공으로 바꾸지 않는다.
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
- 아키텍처 검증에서 도메인 → 애플리케이션/어댑터/프레임워크, 애플리케이션 → 어댑터/영속성 구현·웹 타입의 의존을 금지한다. 입력·출력 어댑터가 각 포트 경계를 따르는지와 모듈 간 순환 의존도 확인한다. ArchUnit 등 도구를 도입한 서비스는 이 규칙을 자동 검사하고, 미도입 서비스는 코드 리뷰로 확인한다. 서비스의 `@Service`·`@Transactional` 예외를 검사 설정에 반영한다.
- Mock·단위 테스트 통과를 실제 DB·외부 API 검증 완료로 표현하지 않는다. 실행한 환경과 미검증 범위를 보고한다.

### 테스트 이름 예시 · CreateProductServiceTest.java

메서드명과 DisplayName에 조건과 기대 결과를 드러낸다. 다음은 상품 생성 서비스의 가격 검증 예제다.

```java
package com.louiekury.product.catalog.application.createproduct;

import com.louiekury.product.shared.exception.BusinessException;
import com.louiekury.product.shared.exception.ErrorCode;
import java.math.BigDecimal;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class CreateProductServiceTest {

    @Test
    @DisplayName("가격이 0이면 상품 생성에 실패한다")
    void rejectsZeroPrice() {
        BusinessException exception = assertThrows(
            BusinessException.class,
            () -> new CreateProductService(product -> product)
                .createProduct(CreateProductCommand.of("사료", BigDecimal.ZERO))
        );
        assertEquals(ErrorCode.INVALID_PRODUCT, exception.getErrorCode());
    }
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

### 서식 허용 및 위반 예시

각 항목의 첫 번째 코드는 허용 예시, 두 번째 코드는 위반 예시다. 아래 코드는 서식 설명용 발췌다.

#### 들여쓰기와 공백

**허용**

```java
if (petId != null) {
    int limit = pageSize + 1;
    return getRecords(petId, limit);
}
```

**위반**

```java
if( petId!=null ) {
  int limit   = pageSize+1;
  return getRecords (petId,limit);
}
```

#### 여러 줄 인자

**허용**

```java
return consultationService.createConsultation(
    petId,
    veterinarianId,
    requestedAt,
    consultationReason
);
```

**위반**

```java
return consultationService.createConsultation(petId, veterinarianId,
                                  requestedAt, consultationReason);
```

#### 중괄호

**허용**

```java
if (record.isEmpty()) {
    return defaultRecord;
} else {
    return record.get();
}
```

**위반**

```java
if (record.isEmpty())
    return defaultRecord;
else
    return record.get();
```

#### import 순서

**허용**

```java
import java.time.Instant;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
```

**위반**

```java
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import java.time.Instant;
```

## 설정과 로깅

- 비밀번호·API 키·토큰은 코드나 공유 설정 파일에 저장하지 않는다. 환경 변수 등 서비스의 비밀값 주입 방식으로 전달한다.
- 외부 기술 설정은 `global.config` 또는 기능별 어댑터 설정에 둔다. 도메인이 환경 변수나 설정 파일을 직접 읽지 않도록 한다.
- 로그에는 실패 맥락과 추적 식별자를 남기고, 요청·응답 본문과 개인정보·인증 정보를 그대로 기록하지 않는다.
- 동일한 예외를 여러 계층에서 반복 기록하지 않도록 처리 책임이 있는 경계에서 기록한다.

## 상품 등록과 조회 예제

상품은 계층 간 연결을 설명하기 위한 예시다. 아래 클래스는 `com.louiekury.product` 서비스의 `catalog` 모듈에 둔다. 생성 유스케이스는 `application.createproduct`, 조회 유스케이스는 `application.getproduct`, 공유 출력 포트와 결과 모델은 각각 `application.port.out`, `application.model`에 둔다. 실제 서비스의 필드·권한·오류 코드는 해당 API·ERD에 맞춘다. 예제는 Java 17 이상 문법과 Jakarta 기반 Spring, JPA, Validation, Jackson, Lombok을 사용하며 실제 의존성 버전은 서비스 빌드 설정에서 정한다.

등록 요청은 컨트롤러가 웹 어댑터에 위임하고 웹 어댑터가 Command로 변환해 입력 포트를 호출한다. 서비스는 도메인을 생성하여 신규 저장 포트를 호출하고 Result를 반환한다. 조회는 삭제되지 않은 상품을 조회하는 출력 포트를 사용한다. 웹 어댑터는 Result를 HTTP 응답 DTO로 변환한다.

- [웹 컨트롤러](#웹-컨트롤러--productcontrollerjava)
- [생성 서비스](#애플리케이션-서비스--createproductservicejava) · [조회 서비스](#애플리케이션-서비스--getproductservicejava)
- [입력 포트](#입력-포트--createproductusecasejava)
- [출력 포트](#출력-포트--createproductportjava)
- [도메인 모델](#도메인-모델--productjava)
- [영속성 어댑터](#영속성-어댑터--productpersistenceadapterjava)
- [공통 클래스 예제](#공통-클래스-예제)

### 웹 컨트롤러 · ProductController.java

컨트롤러는 웹 어댑터만 주입받고 각 메서드에 return 문만 둔다.

```java
package com.louiekury.product.catalog.adapter.in.web;

import com.louiekury.product.catalog.adapter.in.web.dto.request.CreateProductRequestDto;
import com.louiekury.product.catalog.adapter.in.web.dto.response.ProductResponseDto;
import com.louiekury.product.global.web.response.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
public class ProductController {

    private final ProductWebAdapter productWebAdapter;

    @PostMapping
    public ResponseEntity<ApiResponse<ProductResponseDto>> createProduct(
        @Valid @RequestBody CreateProductRequestDto request
    ) {
        return productWebAdapter.createProduct(request);
    }

    @GetMapping("/{productId}")
    public ResponseEntity<ApiResponse<ProductResponseDto>> getProduct(
        @PathVariable("productId") Long productId
    ) {
        return productWebAdapter.getProduct(productId);
    }
}
```

### 웹 어댑터 · ProductWebAdapter.java

웹 경계에서 모델과 HTTP 응답을 변환한다. 업무 처리는 입력 포트에 위임한다.

```java
package com.louiekury.product.catalog.adapter.in.web;

import com.louiekury.product.catalog.adapter.in.web.dto.request.CreateProductRequestDto;
import com.louiekury.product.catalog.adapter.in.web.dto.response.ProductResponseDto;
import com.louiekury.product.catalog.application.createproduct.CreateProductCommand;
import com.louiekury.product.catalog.application.model.ProductResult;
import com.louiekury.product.catalog.application.createproduct.CreateProductUseCase;
import com.louiekury.product.catalog.application.getproduct.GetProductUseCase;
import com.louiekury.product.global.web.response.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class ProductWebAdapter {

    private final CreateProductUseCase createProductUseCase;
    private final GetProductUseCase getProductUseCase;

    public ResponseEntity<ApiResponse<ProductResponseDto>> createProduct(CreateProductRequestDto request) {
        CreateProductCommand command = CreateProductCommand.of(request.getName(), request.getPrice());
        ProductResult result = createProductUseCase.createProduct(command);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(ApiResponse.success(ProductResponseDto.from(result)));
    }

    public ResponseEntity<ApiResponse<ProductResponseDto>> getProduct(Long productId) {
        ProductResult result = getProductUseCase.getProduct(productId);
        return ResponseEntity.ok(ApiResponse.success(ProductResponseDto.from(result)));
    }
}
```

### 요청 DTO · CreateProductRequestDto.java

JSON 역직렬화용 팩토리와 필드 검증은 웹 DTO에 둔다.

```java
package com.louiekury.product.catalog.adapter.in.web.dto.request;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import java.math.BigDecimal;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
@Builder(access = AccessLevel.PRIVATE)
public class CreateProductRequestDto {

    @NotBlank
    private final String name;

    @NotNull
    @Positive
    private final BigDecimal price;

    @JsonCreator
    public static CreateProductRequestDto of(
        @JsonProperty("name") String name,
        @JsonProperty("price") BigDecimal price
    ) {
        return CreateProductRequestDto.builder()
            .name(name)
            .price(price)
            .build();
    }
}
```

### 응답 DTO · ProductResponseDto.java

응답 DTO는 애플리케이션 결과를 변환한다.

```java
package com.louiekury.product.catalog.adapter.in.web.dto.response;

import com.louiekury.product.catalog.application.model.ProductResult;
import java.math.BigDecimal;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
@Builder(access = AccessLevel.PRIVATE)
public class ProductResponseDto {

    private final Long id;
    private final String name;
    private final BigDecimal price;

    public static ProductResponseDto from(ProductResult result) {
        return ProductResponseDto.builder()
            .id(result.getId())
            .name(result.getName())
            .price(result.getPrice())
            .build();
    }
}
```

### 입력 모델 · CreateProductCommand.java

애플리케이션 입력은 HTTP와 독립적인 값만 담는다. 업무 값의 유효성은 아래 CreateProductService에서 검증한다.

```java
package com.louiekury.product.catalog.application.createproduct;

import java.math.BigDecimal;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
@Builder(access = AccessLevel.PRIVATE)
public class CreateProductCommand {

    private final String name;

    private final BigDecimal price;

    public static CreateProductCommand of(
        String name,
        BigDecimal price
    ) {
        return CreateProductCommand.builder()
            .name(name)
            .price(price)
            .build();
    }
}
```

### 결과 모델 · ProductResult.java

서비스는 도메인에서 필요한 값만 결과에 담는다.

```java
package com.louiekury.product.catalog.application.model;

import com.louiekury.product.catalog.domain.Product;
import java.math.BigDecimal;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
@Builder(access = AccessLevel.PRIVATE)
public class ProductResult {

    private final Long id;
    private final String name;
    private final BigDecimal price;

    public static ProductResult from(Product product) {
        return ProductResult.builder()
            .id(product.getId())
            .name(product.getName())
            .price(product.getPrice())
            .build();
    }
}
```

### 입력 포트 · CreateProductUseCase.java

유스케이스의 입력과 반환 계약을 선언한다.

```java
package com.louiekury.product.catalog.application.createproduct;

import com.louiekury.product.catalog.application.model.ProductResult;

public interface CreateProductUseCase {

    ProductResult createProduct(CreateProductCommand command);
}
```

### 입력 포트 · GetProductUseCase.java

유스케이스의 입력과 반환 계약을 선언한다.

```java
package com.louiekury.product.catalog.application.getproduct;

import com.louiekury.product.catalog.application.model.ProductResult;

public interface GetProductUseCase {

    ProductResult getProduct(Long productId);
}
```

### 출력 포트 · CreateProductPort.java

새 상품만 저장하는 계약이다. ID가 있는 상품의 수정은 별도 저장 계약으로 구현한다.

```java
package com.louiekury.product.catalog.application.port.out;

import com.louiekury.product.catalog.domain.Product;

public interface CreateProductPort {

    Product createProduct(Product product);
}
```

### 출력 포트 · GetProductPort.java

삭제되지 않은 상품만 반환하고 대상이 없으면 Optional.empty()를 반환한다.

```java
package com.louiekury.product.catalog.application.port.out;

import com.louiekury.product.catalog.domain.Product;
import java.util.Optional;

public interface GetProductPort {

    Optional<Product> getProduct(Long productId);
}
```

### 애플리케이션 서비스 · CreateProductService.java

유스케이스마다 서비스를 분리하고 각 서비스가 하나의 입력 포트를 구현한다.

```java
package com.louiekury.product.catalog.application.createproduct;

import com.louiekury.product.catalog.application.model.ProductResult;
import com.louiekury.product.catalog.application.port.out.CreateProductPort;
import com.louiekury.product.catalog.domain.Product;
import com.louiekury.product.shared.exception.BusinessException;
import com.louiekury.product.shared.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class CreateProductService implements CreateProductUseCase {

    private final CreateProductPort createProductPort;

    @Override
    @Transactional
    public ProductResult createProduct(CreateProductCommand command) {
        if (command.getName() == null || command.getName().isBlank()
            || command.getPrice() == null || command.getPrice().signum() <= 0) {
            throw new BusinessException(ErrorCode.INVALID_PRODUCT);
        }
        Product product = new Product(command.getName(), command.getPrice());
        Product savedProduct = createProductPort.createProduct(product);
        return ProductResult.from(savedProduct);
    }
}
```

### 애플리케이션 서비스 · GetProductService.java

```java
package com.louiekury.product.catalog.application.getproduct;

import com.louiekury.product.catalog.application.model.ProductResult;
import com.louiekury.product.catalog.application.port.out.GetProductPort;
import com.louiekury.product.catalog.domain.Product;
import com.louiekury.product.shared.exception.BusinessException;
import com.louiekury.product.shared.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class GetProductService implements GetProductUseCase {

    private final GetProductPort getProductPort;

    @Override
    @Transactional(readOnly = true)
    public ProductResult getProduct(Long productId) {
        Product product = getProductPort.getProduct(productId)
            .orElseThrow(() -> new BusinessException(ErrorCode.PRODUCT_NOT_FOUND));
        return ProductResult.from(product);
    }
}
```

### 도메인 모델 · Product.java

상품 상태를 보유한다. 업무 검증은 생성 서비스에서 수행한다. 영속성 복원용 팩토리는 저장된 식별자를 함께 받는다.

```java
package com.louiekury.product.catalog.domain;

import java.math.BigDecimal;
import java.util.Objects;

public class Product {

    private final Long id;
    private final String name;
    private final BigDecimal price;

    public Product(String name, BigDecimal price) {
        this(null, name, price);
    }

    private Product(Long id, String name, BigDecimal price) {
        this.id = id;
        this.name = name;
        this.price = price;
    }

    public static Product restore(Long id, String name, BigDecimal price) {
        return new Product(Objects.requireNonNull(id, "id"), name, price);
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public BigDecimal getPrice() {
        return price;
    }
}
```

### JPA 엔티티 · ProductJpaEntity.java

products 테이블의 매핑을 담당한다. 이 예제의 테이블에는 BaseEntity의 created_at, updated_at, deleted_at 컬럼도 둔다.

```java
package com.louiekury.product.catalog.adapter.out.persistence;

import com.louiekury.product.global.persistence.BaseEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Entity
@Table(name = "products")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ProductJpaEntity extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private BigDecimal price;

    public ProductJpaEntity(String name, BigDecimal price) {
        this.name = name;
        this.price = price;
    }
}
```

### Spring Data 레포지토리 · ProductJpaRepository.java

조회 메서드에 삭제 상태 조건을 포함한다.

```java
package com.louiekury.product.catalog.adapter.out.persistence;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProductJpaRepository extends JpaRepository<ProductJpaEntity, Long> {

    Optional<ProductJpaEntity> findByIdAndDeletedAtIsNull(Long productId);
}
```

### 영속성 매퍼 · ProductPersistenceMapper.java

신규 저장용 변환은 ID가 없는 모델만 허용한다. 복원 시 저장된 필수값과 범위가 손상되었으면 기술 장애로 처리한다. 이는 신규 요청의 업무 검증이 아니며 서비스의 검증을 대신하지 않는다. 기존 엔티티 수정은 필요한 필드만 반영하는 별도 변환으로 구현하고 감사·삭제·버전 정보를 보존한다.

```java
package com.louiekury.product.catalog.adapter.out.persistence;

import com.louiekury.product.catalog.domain.Product;

public final class ProductPersistenceMapper {

    private ProductPersistenceMapper() {
    }

    public static ProductJpaEntity toNewEntity(Product product) {
        if (product.getId() != null) {
            throw new IllegalArgumentException("신규 상품만 저장할 수 있습니다.");
        }
        return new ProductJpaEntity(product.getName(), product.getPrice());
    }

    public static Product toDomain(ProductJpaEntity entity) {
        if (entity.getId() == null || entity.getName() == null || entity.getName().isBlank()
            || entity.getPrice() == null || entity.getPrice().signum() <= 0) {
            throw new IllegalStateException("저장된 상품 데이터가 올바르지 않습니다.");
        }
        return Product.restore(entity.getId(), entity.getName(), entity.getPrice());
    }
}
```

### 영속성 어댑터 · ProductPersistenceAdapter.java

출력 포트를 구현하고 JPA 엔티티를 도메인으로 변환한다. 트랜잭션은 이 어댑터를 호출하는 유스케이스가 시작한다.

```java
package com.louiekury.product.catalog.adapter.out.persistence;

import com.louiekury.product.catalog.application.port.out.CreateProductPort;
import com.louiekury.product.catalog.application.port.out.GetProductPort;
import com.louiekury.product.catalog.domain.Product;
import java.util.Optional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class ProductPersistenceAdapter implements CreateProductPort, GetProductPort {

    private final ProductJpaRepository productJpaRepository;

    @Override
    public Product createProduct(Product product) {
        ProductJpaEntity entity = ProductPersistenceMapper.toNewEntity(product);
        ProductJpaEntity savedEntity = productJpaRepository.save(entity);
        return ProductPersistenceMapper.toDomain(savedEntity);
    }

    @Override
    public Optional<Product> getProduct(Long productId) {
        return productJpaRepository.findByIdAndDeletedAtIsNull(productId)
            .map(ProductPersistenceMapper::toDomain);
    }
}
```

## 공통 클래스 예제

아래 코드는 상품 예제와 같은 서비스 루트를 사용한다. 다른 서비스에 적용할 때 패키지와 업무 오류 코드를 해당 서비스에 맞춘다. API 응답과 HTTP 예외 처리는 웹 계층, 업무 예외는 shared, 감사 필드는 영속성 계층에 둔다.

### 공통 API 응답 · ApiResponse.java

success와 error 정적 팩토리를 사용하고 비공개 빌더로 생성한다.

```java
package com.louiekury.product.global.web.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.Objects;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
@Builder(access = AccessLevel.PRIVATE)
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {

    private final String code;
    private final String message;
    private final T data;

    public static <T> ApiResponse<T> success(T data) {
        return ApiResponse.<T>builder()
            .data(Objects.requireNonNull(data, "data"))
            .build();
    }

    public static ApiResponse<Void> error(String code, String message) {
        return ApiResponse.<Void>builder()
            .code(Objects.requireNonNull(code, "code"))
            .message(Objects.requireNonNull(message, "message"))
            .build();
    }
}
```

### 비즈니스 예외 · BusinessException.java

업무 코드, 공개 가능한 메시지와 원인 예외를 보관한다.

```java
package com.louiekury.product.shared.exception;

import lombok.Getter;

@Getter
public class BusinessException extends RuntimeException {

    private final ErrorCode errorCode;

    public BusinessException(ErrorCode errorCode) {
        this(errorCode, errorCode.getMessage());
    }

    public BusinessException(ErrorCode errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public BusinessException(ErrorCode errorCode, Throwable cause) {
        super(errorCode.getMessage(), cause);
        this.errorCode = errorCode;
    }
}
```

### 오류 코드 · ErrorCode.java

HTTP 상태를 필드에 포함하지 않는다. 아래 코드는 예제용이며 실제 업무 코드는 API 명세에 맞춘다.

```java
package com.louiekury.product.shared.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum ErrorCode {

    // 참고용 예시 코드입니다.
    PRODUCT_NOT_FOUND("상품을 찾을 수 없습니다."),
    INVALID_PRODUCT("상품 이름과 가격이 올바르지 않습니다.");

    private final String message;
}
```

### HTTP 오류 매핑 · ErrorCodeHttpMapper.java

업무 코드의 HTTP 표현을 웹 계층에서 정한다. 모든 상수를 명시적으로 매핑한다.

```java
package com.louiekury.product.global.web.exception;

import com.louiekury.product.shared.exception.ErrorCode;
import org.springframework.http.HttpStatus;

public final class ErrorCodeHttpMapper {

    private ErrorCodeHttpMapper() {
    }

    public static HttpStatus toStatus(ErrorCode code) {
        return switch (code) {
            case INVALID_PRODUCT -> HttpStatus.BAD_REQUEST;
            case PRODUCT_NOT_FOUND -> HttpStatus.NOT_FOUND;
        };
    }
}
```

### 웹 오류 코드 · WebErrorCode.java

HTTP 요청과 인증 처리에서만 사용하는 코드는 웹 경계에 둔다. 업무 코드에는 HTTP 상태를 추가하지 않는다.

```java
package com.louiekury.product.global.web.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;

@Getter
@RequiredArgsConstructor
public enum WebErrorCode {
    VALIDATION_ERROR(HttpStatus.BAD_REQUEST, "요청 값이 올바르지 않습니다."),
    UNAUTHORIZED(HttpStatus.UNAUTHORIZED, "인증이 필요합니다."),
    FORBIDDEN(HttpStatus.FORBIDDEN, "접근 권한이 없습니다."),
    NOT_FOUND(HttpStatus.NOT_FOUND, "대상을 찾을 수 없습니다."),
    METHOD_NOT_ALLOWED(HttpStatus.METHOD_NOT_ALLOWED, "지원하지 않는 요청 방식입니다."),
    INTERNAL_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "서버 내부 오류가 발생했습니다.");

    private final HttpStatus status;
    private final String message;
}
```

### 전역 예외 핸들러 · GlobalExceptionHandler.java

업무 예외와 Spring MVC 오류를 공통 오류 본문으로 변환한다. Spring Security 필터에서 발생한 실패는 별도 AuthenticationEntryPoint·AccessDeniedHandler에서도 같은 ApiResponse.error 형식을 사용한다.

```java
package com.louiekury.product.global.web.exception;

import com.louiekury.product.global.web.response.ApiResponse;
import com.louiekury.product.shared.exception.BusinessException;
import com.louiekury.product.shared.exception.ErrorCode;
import jakarta.validation.ConstraintViolationException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.web.ErrorResponse;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ApiResponse<Void>> handleBusinessException(BusinessException exception) {
        ErrorCode code = exception.getErrorCode();
        return ResponseEntity.status(ErrorCodeHttpMapper.toStatus(code))
            .body(ApiResponse.error(code.name(), exception.getMessage()));
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<ApiResponse<Void>> handleValidation() {
        return build(WebErrorCode.VALIDATION_ERROR);
    }

    @ExceptionHandler(AuthenticationException.class)
    public ResponseEntity<ApiResponse<Void>> handleAuthentication() {
        return build(WebErrorCode.UNAUTHORIZED);
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ApiResponse<Void>> handleAccessDenied() {
        return build(WebErrorCode.FORBIDDEN);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleException(Exception exception) {
        if (exception instanceof ErrorResponse error && error.getStatusCode().is4xxClientError()) {
            return handleRequestError(error);
        }
        log.error("요청 처리 중 예상하지 못한 예외가 발생했습니다.", exception);
        if (exception instanceof ErrorResponse error) {
            return ResponseEntity.status(error.getStatusCode())
                .headers(error.getHeaders())
                .body(errorBody(WebErrorCode.INTERNAL_SERVER_ERROR));
        }
        return build(WebErrorCode.INTERNAL_SERVER_ERROR);
    }

    private ResponseEntity<ApiResponse<Void>> handleRequestError(ErrorResponse error) {
        var status = error.getStatusCode();
        ApiResponse<Void> body = switch (status.value()) {
            case 400 -> errorBody(WebErrorCode.VALIDATION_ERROR);
            case 404 -> errorBody(WebErrorCode.NOT_FOUND);
            case 405 -> errorBody(WebErrorCode.METHOD_NOT_ALLOWED);
            default -> status instanceof HttpStatus standardStatus
                ? ApiResponse.error(standardStatus.name(), standardStatus.getReasonPhrase())
                : ApiResponse.error("HTTP_" + status.value(), "요청을 처리할 수 없습니다.");
        };
        return ResponseEntity.status(status).headers(error.getHeaders()).body(body);
    }

    private ResponseEntity<ApiResponse<Void>> build(WebErrorCode code) {
        return ResponseEntity.status(code.getStatus()).body(errorBody(code));
    }

    private ApiResponse<Void> errorBody(WebErrorCode code) {
        return ApiResponse.error(code.name(), code.getMessage());
    }
}
```

### 베이스 엔티티 · BaseEntity.java

삭제 유스케이스의 저장 어댑터는 관리 중인 JPA 엔티티에 updateDeletedAt를 호출할 수 있다. 실제 삭제 허용 조건은 서비스가 판단하고, 조회에는 삭제 제외 조건을 적용한다.

```java
package com.louiekury.product.global.persistence;

import jakarta.persistence.Column;
import jakarta.persistence.EntityListeners;
import jakarta.persistence.MappedSuperclass;
import java.time.LocalDateTime;
import java.util.Objects;
import lombok.Getter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

@Getter
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    public void updateDeletedAt(LocalDateTime deletedAt) {
        if (this.deletedAt == null) {
            this.deletedAt = Objects.requireNonNull(deletedAt, "deletedAt");
        }
    }
}
```

### 감사 설정 · JpaAuditingConfig.java

서비스에서 감사 기능을 활성화한다. 시각의 저장·변환 기준은 실제 DB와 API 계약에 맞춰 설정한다.

```java
package com.louiekury.product.global.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

@Configuration
@EnableJpaAuditing
public class JpaAuditingConfig {
}
```

## 참고 자료

- [Domain-Driven Hexagon](https://github.com/Sairyss/domain-driven-hexagon): 기능별 유스케이스, 도메인과 포트·어댑터 구조의 참고 구현. TypeScript/NestJS 예제를 Java/Spring에 맞춰 적용한다.
- [네이버 핵데이 Java 코딩 컨벤션](https://naver.github.io/hackday-conventions-java/): Java 서식과 도구 설정의 기본 기준.

- [FinPlay 코드 컨벤션](https://github.com/finplay-team/finplay-backend/blob/dev/docs/conventions/code.md)의 주제별 문서 구성을 참고했다.
- 포트와 어댑터의 역할과 내부·외부 경계는 [Alistair Cockburn의 헥사고날 아키텍처 원문](https://alistair.cockburn.us/hexagonal-architecture)을 참고했다.
