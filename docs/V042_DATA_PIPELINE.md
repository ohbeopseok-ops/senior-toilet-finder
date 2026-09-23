# V0.4.2 — DATA.GO.KR → JUSO → 실시간 개방상태

## 최종 자동 배치

1. **DATA.GO.KR 공중화장실 API**
   - 시설명
   - 도로명/지번 주소
   - 개방시간
   - 관리기관/전화번호
   - 장애인화장실·비상벨 등 응답에 실제 존재하는 필드

2. **응답 스키마 자동 검증**
   - `data/schema-report.json`
   - 실제 첫 응답에서 record array 위치와 필드명을 저장
   - 서비스키는 절대로 파일/로그에 저장하지 않음

3. **개방시간 계산**
   - `24시간`, `09:00~18:00` 형태를 보수적으로 파싱
   - `open` / `closing-soon` / `closed` / `unknown`
   - 마감 30분 이하는 `closing-soon`
   - 파싱 실패 시 임의로 열림 처리하지 않음

4. **JUSO 지오코딩**
   - DATA.GO.KR에 좌표가 없으면 주소를 좌표로 보강
   - 좌표 검증과 계단/무장애 검증은 별개

5. **Senior Safety Gate**
   - 500m 이내
   - 현재 개방 확인
   - 계단 없음 확인
   - 세 조건 모두 만족해야 자동 1순위

## GitHub 설정

### Repository secret
- `DATA_GO_KR_SERVICE_KEY`

### Repository variable
- `DATA_GO_KR_ENDPOINT`

서비스키는 Secret에, API operation URL은 Variable에 넣습니다.

## 중요한 원칙

API 응답에 없는 필드는 추정하지 않습니다.
특히 `stairsVerified`는 공중화장실 API에 계단/무장애 진입 정보가 실제로 확인되기 전까지 `false`를 유지합니다.
