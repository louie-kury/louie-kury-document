# ERD (Entity Relationship Diagram)

## 기준과 표기

이 문서는 사용자가 최종본으로 지정한 MySQL Workbench 모델 `vetconsult.mwb`의 구조를 기준으로 한다. 모델에 기록된 스키마·테이블·컬럼·인덱스·외래키를 옮겼으며, 실제 운영 DB에 적용되었는지는 확인하지 않았다. 저장소와 서비스 경계는 모델의 스키마 이름을 그대로 표시한다. 총 11개 스키마, 87개 테이블, 668개 컬럼, 302개 인덱스, 46개 외래키를 포함한다.

- 컬럼의 `NOT NULL`과 `NULL` 표기는 모델의 `isNotNull` 값에 따른다. 기본값 `—`는 모델에 기본값이 지정되지 않은 경우다.
- PK와 UNIQUE는 인덱스의 실제 컬럼 조합을 기준으로 표시한다. 일반 인덱스도 함께 기록한다.
- 관계는 모델에 명시된 외래키 중 참조 대상을 확인할 수 있는 것만 표시한다. 원본의 외래키 14개는 참조 대상을 확인할 수 없어 관계에서 제외했다.
- 외래키의 삭제·수정 규칙이 비어 있으면 `미지정`으로 표시한다. 원본 주석과 명칭은 의역하거나 수정하지 않았다.
- 원본 모델은 MySQL 설계 자료이며 실제 DB나 다른 저장소의 구현 상태를 나타내지 않는다.

## 스키마 목록

| 스키마 | 테이블 수 |
| --- | ---: |
| [svc_identity](erd/svc_identity.md) | 8 |
| [svc_clinic](erd/svc_clinic.md) | 13 |
| [svc_pet](erd/svc_pet.md) | 7 |
| [svc_care](erd/svc_care.md) | 12 |
| [svc_community](erd/svc_community.md) | 8 |
| [svc_moderation](erd/svc_moderation.md) | 4 |
| [svc_media](erd/svc_media.md) | 3 |
| [svc_notification](erd/svc_notification.md) | 2 |
| [svc_platform](erd/svc_platform.md) | 5 |
| [svc_matching](erd/svc_matching.md) | 5 |
| [vet_query](erd/vet_query.md) | 20 |

각 스키마의 관계도와 테이블 상세는 위 목록의 링크에서 확인한다.
