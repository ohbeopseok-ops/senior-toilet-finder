# V0.4 — 경기도 공중화장실 주소 → 실제 좌표 자동 생성

## 목표

공식 공중화장실 데이터에 주소는 있지만 WGS84 위도/경도가 없는 경우,
행정안전부 주소정보 API를 이용해 실제 좌표를 자동 보강합니다.

## 파이프라인

```
경기/지자체 공중화장실 원본
        ↓
도로명주소 검색 API
        ↓
admCd + rnMgtSn + udrtYn + buldMnnm + buldSlno
        ↓
좌표제공 API
        ↓
UTM-K(GRS80) entX / entY
        ↓
EPSG:5179 → EPSG:4326
        ↓
lat / lng 저장
        ↓
Senior Safety Score
```

## GitHub Secrets

Settings → Secrets and variables → Actions → Repository secrets

- `JUSO_SEARCH_KEY`: 도로명주소 검색 API 승인키
- `JUSO_COORD_KEY`: 좌표제공 API 승인키

두 API는 승인키 유형이 서로 다를 수 있으므로 각각 발급받아 저장합니다.

## 현재 지역 범위

자동 배치는 우선 다음 지역만 처리합니다.

- 안양시

`GEOCODE_REGIONS` 값을 변경하면 경기도 전체로 확대할 수 있습니다.

## 안전 규칙

좌표가 공식 주소 API로 보강되어도 아래 값은 자동으로 사실로 간주하지 않습니다.

- 계단 없음
- 경사로 있음
- 현재 개방 중
- 비상벨 있음

즉 **좌표 검증과 배리어프리 검증은 분리**합니다.

V0.4에서도 Senior Safety Gate는 다음 세 조건을 모두 만족해야 통과합니다.

1. 500m 이내
2. 현재 개방이 검증됨
3. 계단 없음이 검증됨

## 호출 제한

행정안전부 주소정보 도움센터 답변 기준 좌표제공 API는 **5초당 10건 초과 호출이 제한**됩니다.
배치 스크립트는 안전 여유를 두고 약 0.6초 간격으로 호출합니다.
