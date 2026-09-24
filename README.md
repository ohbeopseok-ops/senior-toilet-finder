# 안심화장실

급한 상황에서 **GPS 기준 가장 가까운 화장실부터** 큰 글씨와 음성으로 안내하는 시니어·보행약자 친화 PWA입니다.

## 현재 Production 기능

- GPS 기준 실제 거리 재계산
- Kakao Nearby + 안양시 공공데이터 Hybrid 검색
- 안양시 공공데이터 좌표 사용 가능 시설 225건
- TOP10 가까운 순 표시
- 운영시간·장애인시설·비상벨 정보
- 계단은 Hard Gate가 아니며, 필요 시 `계단 없는 곳 우선` 선택
- 큰 글씨 / 고대비 UI
- 한국어 음성 안내(TTS)
- iPhone/Android 홈 화면 설치형 PWA
- stale cache 방지용 network-first app shell

## 운영 주소

현재:

```
https://ohbeopseok-ops.github.io/senior-toilet-finder/
```

Android 출시용 권장 Production origin:

```
https://toilet.aijoylab.kr/
```

custom domain 연결 절차는 `docs/CUSTOM_DOMAIN_TOILET.md` 참고.

## QA

```
https://ohbeopseok-ops.github.io/senior-toilet-finder/?qa=1
```

현재 Production QA에서 GPS TOP10 거리순 PASS를 확인했습니다.

## Android 출시

Android는 기존 PWA를 Trusted Web Activity(TWA)로 패키징하는 방향입니다.

- 제안 package: `kr.aijoylab.seniortoilet`
- Target SDK: 36
- 배포 포맷: AAB
- Play App Signing 사용
- Digital Asset Links 필요

세부 계획은 `docs/ANDROID_RELEASE_V1.md` 참고.
