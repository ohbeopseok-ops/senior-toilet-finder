# V0.3 Data Sources — Gyeonggi / Goyang / Suwon

## 확인된 공식 소스

### 경기데이터드림
- 데이터셋: **공중화장실 현황(제공표준)**
- 데이터 기준일자: **2026-01-30**
- 공식 데이터셋 페이지: https://data.gg.go.kr/portal/data/service/selectServicePage.do?infId=GW6U772M6045H11Q799612585601&infSeq=3
- Open API 기본 호스트: https://openapi.gg.go.kr
- 인증: 경기데이터드림 API Key
- 시군 필터: 서비스별로 `SIGUN_CD` / 시군 관련 요청변수를 사용할 수 있음

## 현재 연결 상태

V0.3 애플리케이션은 아래 순서로 동작합니다.

1. `data/toilets-live.json` — 공식/지역 API 동기화 결과 우선
2. 유효한 위·경도 데이터가 없으면 `data/toilets-fallback.json`
3. fallback 데이터는 UI에서 **검증 캐시**로 명시하고 Senior Safety Gate를 통과시키지 않음

현재 전국 공중화장실 표준 원천은 좌표 제공 제약이 있어, 가까운 시설 검색에는 좌표가 포함된 **지자체/지역 데이터 API**를 별도 연결해야 합니다.

## 실제 API 연결에 필요한 저장소 변수

GitHub 저장소의 Settings → Secrets and variables → Actions에서 아래 값을 설정합니다.

- `PUBLIC_TOILET_SOURCE_URL`: 좌표 포함 공식 CSV/JSON URL
- 또는 향후 경기데이터드림 전용 어댑터 사용 시:
  - `GG_TOILET_API_NAME`
  - `GG_DATA_KEY`

API Key는 HTML/JavaScript에 직접 포함하지 않습니다.

## 우선 적용 지역

1. 안양시
2. 경기도 전체

지역별 데이터에서 다음 항목을 실제로 제공하는 경우에만 Safety Gate에 반영합니다.

- 위도/경도
- 현재 개방 상태 또는 운영시간
- 계단 없음/무장애 진입 정보

주소와 좌표만 있는 데이터는 **근거리 후보**로는 사용할 수 있지만, '안심 1순위'로 자동 승격하지 않습니다.
