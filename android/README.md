# 안심화장실 Android

Production PWA `https://toilet.aijoylab.kr/`를 Trusted Web Activity(TWA)로 패키징한다.

## Identity
- Application ID: `kr.aijoylab.seniortoilet`
- App name: `안심화장실`
- Version: `1.0.0` / versionCode `1`
- compileSdk: `36`
- targetSdk: `36`
- minSdk: `23`
- TWA helper: `com.google.androidbrowserhelper:androidbrowserhelper:2.7.3`

## Build
GitHub Actions의 `Android TWA Build` workflow가 다음을 생성한다.

- Debug APK
- Release AAB (현재 signing secret 연결 전 단계)

## Production TWA verification
Play Console에서 앱을 생성하고 Play App Signing certificate의 SHA-256을 확보한 뒤:

1. `android/assetlinks.template.json`의 지문을 교체
2. `/.well-known/assetlinks.json`으로 Production 도메인에 배포
3. `https://toilet.aijoylab.kr/.well-known/assetlinks.json` 200 확인
4. Play 설치본에서 주소창 없는 TWA 실행 확인

Upload key와 Play App Signing key는 서로 다를 수 있으므로 최종 assetlinks에는 Play App Signing certificate SHA-256을 사용한다.
