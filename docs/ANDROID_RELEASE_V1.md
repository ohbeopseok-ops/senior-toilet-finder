# 안심화장실 Android Release V1

## 목표

현재 Production QA를 통과한 PWA를 Google Play에 배포 가능한 Android 앱으로 전환한다.

- 앱명: 안심화장실 - 가까운 화장실 찾기
- 패키지명(제안): `kr.aijoylab.seniortoilet`
- 웹앱 기준 URL: 현재 `https://ohbeopseok-ops.github.io/senior-toilet-finder/`
- Android 방식: Trusted Web Activity (TWA)
- Target SDK: 36 (Android 16)
- 배포 포맷: Android App Bundle (.aab)
- Play App Signing 사용 권장

## P0: 배포 도메인 확정

TWA는 Android 앱과 웹사이트의 소유권을 Digital Asset Links로 검증해야 한다.

검증 파일은 반드시 해당 origin의 루트에 있어야 한다.

```
https://<host>/.well-known/assetlinks.json
```

현재 앱은 GitHub Pages project site인:

```
https://ohbeopseok-ops.github.io/senior-toilet-finder/
```

에서 서비스된다. TWA 검증 파일은 프로젝트 경로가 아니라 다음 origin root에서 제공되어야 한다.

```
https://ohbeopseok-ops.github.io/.well-known/assetlinks.json
```

따라서 Android 출시 전 아래 둘 중 하나를 선택한다.

### 권장안
전용 커스텀 도메인 사용:

```
https://toilet.aijoylab.kr/
```

장점:
- 앱 브랜드 URL 확보
- Digital Asset Links를 같은 origin에서 직접 관리
- GitHub Pages 프로젝트 경로 의존 제거
- 향후 웹/Android/iOS 공통 URL 사용 가능

### 대안
`ohbeopseok-ops.github.io` 루트 사이트를 별도 관리하고 그 루트에 `.well-known/assetlinks.json`을 배포한다.

## P1: Android TWA

웹앱 기능을 네이티브로 다시 작성하지 않고 TWA로 감싼다.

유지되는 기존 기능:
- GPS
- Kakao Nearby
- 공공데이터 Hybrid 검색
- 거리순 TOP10
- 큰 글씨
- 음성 안내
- 계단 없는 곳 우선 옵션

Android 앱에서 추가 검증:
- 위치 권한 흐름
- Android Back 동작
- 전화 링크
- 외부 지도/링크
- 오프라인/네트워크 오류
- 앱 복귀 시 GPS 재계산
- Chrome/TWA fallback

## P2: Digital Asset Links

Play App Signing 인증서 SHA-256 지문이 확정된 뒤 `assetlinks.json`을 생성한다.

패키지:
```
kr.aijoylab.seniortoilet
```

주의:
- upload key와 Play app signing key 지문은 다를 수 있다.
- Play 설치본 검증에는 Play app signing certificate의 SHA-256을 사용한다.

## P3: Play Store Listing

앱명:
```
안심화장실 - 가까운 화장실 찾기
```

간단한 설명:
```
GPS로 가장 가까운 화장실을 찾고 큰 글씨와 음성으로 바로 안내해 드립니다.
```

핵심 포지션:
```
급할 때 지도에서 찾지 말고, 가장 가까운 화장실부터 바로 안내
```

## P4: Release Gate

출시 전 필수:
- targetSdk 36
- AAB release build 성공
- 앱 서명 확인
- Digital Asset Links 200 OK
- TWA 주소창 없는 실행 확인
- Android 실기기 GPS TOP10 거리순 PASS
- 위치 권한 거부/재허용 테스트
- 개인정보처리방침 URL 준비
- Play Data safety 작성
- 앱 아이콘 / Feature Graphic / 스크린샷 준비
- Internal testing -> Closed/Open testing 여부 결정 -> Production

## 다음 실행 순서

1. `toilet.aijoylab.kr` 사용 여부 확정
2. 도메인 연결 및 Production smoke
3. Android TWA project 생성
4. debug APK 실기기 테스트
5. Play Console 앱 생성 및 Play App Signing 활성화
6. signing certificate SHA-256 확보
7. assetlinks 배포
8. signed AAB 생성
9. Internal testing
10. Store listing + Data safety + Production submission
