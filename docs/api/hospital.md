# 지도·병원 조회 API

**후순위 설계 초안**이다. [PRD](../prd.md)의 지도 화면·`D16`과 요구사항정의서 `(필수3)요구사항정의서` 4행의 지역·현재 위치·진료 분야 필터를 근거로 한다. 병원 공개 정보의 제공 주체와 상세 공개 필드는 `D16` 확정 후 적용한다.

[공통 계약](README.md)을 적용한다. 모든 ID는 문자열이며 아래 모델은 성공 본문의 `data`다.

## 데이터 모델

| 모델 | 필드 |
| --- | --- |
| HospitalItem | `hospitalId:string`, `name:string`, `address:string`, `latitude:number?`, `longitude:number?`, `distanceMeters:number?`, `specialties:string[]` |
| HospitalDetail | HospitalItem + `detailAddress:string?`, `phoneNumber:string?`, `openingHours:string?`, `supportedAnimals:string[]` |

좌표·진료 시간·동물·분야는 원본 MySQL SQL에 모두 표현되어 있지 않다. 위 필드는 응답 설계 후보이며 컬럼이나 수집 범위를 확정하는 선언이 아니다. 병원 좌표가 없거나 거리 기준이 미확정이면 `distanceMeters:null`로 표시하고 0m로 대체하지 않는다.

## 엔드포인트

공개 조회를 가정한 설계안이며 비회원 접근 허용은 `D16`에서 확정한다.

| 기능 | 요청 | 인증 초안 | 입력 | 성공 data·상태 | 주요 오류 | PRD |
| --- | --- | --- | --- | --- | --- | --- |
| 지도 병원 목록 | `GET /api/hospitals` | 공개 제안 | Query `region?:string`, `latitude?:number`, `longitude?:number`, `specialty?:string`, `page`, `size` | `Page<HospitalItem>`, 200 | 400 VALIDATION_ERROR, 503 UPSTREAM_UNAVAILABLE | 지도·D16 |
| 병원 상세 | `GET /api/hospitals/{hospitalId}` | 공개 제안 | Path `hospitalId:string` | `HospitalDetail`, 200 | 404 NOT_FOUND, 503 UPSTREAM_UNAVAILABLE | 지도·D16 |

## 처리 규칙

- 현재 위치 필터를 사용할 때 위도·경도는 함께 전달한다. 한쪽만 있거나 지리 범위를 벗어나면 400이다. 위치 권한 거부 시 주소·지역 필터로 대체할지 여부는 `D16`에서 확정한다.
- 지역·현재 위치·진료 분야의 동시 사용 조건, 거리 정렬·탐색 반경은 제품 정책을 확인한 뒤 고정한다. 거리순과 지역별 기본 정렬은 같은 정책으로 가정하지 않는다.
- 목록이 비면 200과 빈 `content`를 반환한다. 상세는 공개 가능한 병원만 반환하며 존재하지 않거나 비공개·삭제된 대상은 404로 처리한다.
- 원본 또는 외부 병원 데이터의 장애를 빈 목록으로 바꾸지 않는다. 재시도 가능한 503으로 응답하며 보호자 화면에서 로딩·조회 실패·빈 결과를 구분한다.

## 구현 전 확인

`D16`의 병원 데이터 공급원·공개 필드·필터 값·인증·정렬·페이지 정책을 확인한다. 위치 기반 상담 탐색은 [상담 API](consultation.md)의 별도 유스케이스이며 병원 선택으로 예약을 생성하지 않는다. 실제 지도·위치 서비스와 MySQL 조회 검증은 아직 수행하지 않았다.
