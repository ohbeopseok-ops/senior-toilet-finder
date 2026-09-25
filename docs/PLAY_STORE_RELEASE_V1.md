# 안심화장실 Google Play Release V1

## 앱 식별자
- App name: 안심화장실 - 가까운 화장실 찾기
- Application ID: `kr.aijoylab.seniortoilet`
- Version: 1.0.0 (versionCode 1)
- Target SDK: 36
- Production URL: `https://toilet.aijoylab.kr/`
- Privacy Policy: `https://toilet.aijoylab.kr/privacy.html`

## Store short description
GPS로 가장 가까운 화장실을 찾고 큰 글씨와 음성으로 바로 안내해 드립니다.

## Core positioning
급할 때 지도에서 찾지 말고, 가장 가까운 화장실부터 바로 안내.

## Data safety draft
- 위치정보: 현재 위치 기반 거리 계산과 주변 화장실 검색에 사용
- 계정 생성: 없음
- 광고: 없음
- 자체 계정 DB에 사용자 위치 영구 저장: 없음
- Third-party processing: Kakao Local API 중계 검색
- Encryption in transit: HTTPS

Play Console 입력 시 실제 구현과 운영 정책을 다시 대조해 최종 제출한다.

## Release gates
1. Android build workflow PASS
2. Debug APK 실기기 실행
3. GPS 권한 허용/거부/재허용
4. Kakao Nearby + 공공데이터 TOP10
5. Play App Signing SHA-256 확보
6. `.well-known/assetlinks.json` 배포
7. TWA 주소창 없는 실행 확인
8. Signed production AAB
9. Internal testing
10. Production submission


## Upload key
- Alias: `upload`
- Upload certificate SHA-256: `48:2E:7F:21:8F:C8:A6:C7:88:99:7C:DF:81:1C:8F:70:53:60:55:77:4F:6F:92:CD:62:60:84:29:F2:84:BA:07`
- 비밀번호/keystore는 저장소에 커밋하지 않는다.
- Netlify `TWA_SHA256_FINGERPRINTS`에는 현재 이 지문이 등록되어 사이드로드 QA를 지원한다.
- Play App Signing certificate SHA-256이 발급되면 같은 환경변수에 쉼표로 추가한다.
