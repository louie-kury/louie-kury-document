# 참조 대상 확인이 필요한 외래키

원본 모델에는 아래 외래키의 참조 테이블과 컬럼을 식별할 수 있는 객체가 없어 ERD 관계에서 제외했다. 확인 후 해당 스키마 문서에 반영한다.

| 참조하는 테이블 | 컬럼 | 외래키 이름 |
| --- | --- | --- |
| `svc_care.chat_room` | `consultation_id` | `fk_chat_room_consult` |
| `svc_care.consultation` | `medical_subject_id` | `fk_consult_subject` |
| `svc_care.consultation_symptom` | `symptom_id` | `fk_consult_symptom_symptom` |
| `svc_care.video_participant` | `video_session_id` | `fk_video_participant_session` |
| `svc_care.visit_reservation` | `visit_slot_id` | `fk_reservation_slot` |
| `svc_clinic.vet_date_off` | `vet_id` | `fk_date_off_vet` |
| `svc_clinic.vet_duty_session` | `vet_id` | `fk_duty_vet` |
| `svc_clinic.vet_hospital_affiliation` | `vet_id` | `fk_affiliation_vet` |
| `svc_clinic.vet_weekday_off` | `vet_id` | `fk_vet_off_vet` |
| `svc_community.comment_like` | `comment_id` | `fk_comment_like_comment` |
| `svc_matching.match_offer` | `wave_id` | `fk_offer_wave` |
| `svc_pet.breed` | `species_id` | `fk_breed_species` |
| `svc_pet.caregiver_pet` | `pet_id` | `fk_caregiver_pet_pet` |
| `svc_pet.pet_vaccination` | `vaccine_id` | `fk_vaccination_vaccine` |
