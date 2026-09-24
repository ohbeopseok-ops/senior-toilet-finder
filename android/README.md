# Android

안심화장실 Android 앱은 기존 PWA를 Trusted Web Activity(TWA)로 배포하는 방향으로 설계한다.

## Proposed identity

- Application ID: `kr.aijoylab.seniortoilet`
- App name: `안심화장실`
- Target SDK: 36
- Start URL: Android 배포 도메인 확정 후 고정

## Blocker before generating the production TWA project

Digital Asset Links must be served from the root of the exact web origin:

```
https://<host>/.well-known/assetlinks.json
```

현재 GitHub Pages project URL은 origin root를 이 repository가 직접 소유하지 않으므로, production Android project 생성 전에 전용 도메인 `toilet.aijoylab.kr` 사용을 권장한다.

See `docs/ANDROID_RELEASE_V1.md`.
