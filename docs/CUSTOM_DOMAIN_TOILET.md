# toilet.aijoylab.kr Custom Domain Migration

## Target

Android TWA 및 향후 iOS/웹 공통 Production origin:

```
https://toilet.aijoylab.kr/
```

현재 운영 주소는 유지한다.

```
https://ohbeopseok-ops.github.io/senior-toilet-finder/
```

DNS와 GitHub Pages custom domain 검증이 끝나기 전에는 기존 주소를 제거하거나 리다이렉트하지 않는다.

## DNS

Cloudflare DNS에 다음 레코드를 생성한다.

```
Type: CNAME
Name: toilet
Target: ohbeopseok-ops.github.io
Proxy status: DNS only (초기 검증 권장)
TTL: Auto
```

GitHub Pages 인증서 발급과 custom domain 검증이 끝난 후 필요하면 Cloudflare proxy 사용 여부를 별도 검토한다.

## GitHub Pages

Repository:

```
ohbeopseok-ops/senior-toilet-finder
```

Settings → Pages → Custom domain:

```
toilet.aijoylab.kr
```

저장 후 DNS check가 성공하고 HTTPS 인증서가 발급될 때까지 기다린다.

## Production Smoke

다음을 확인한다.

1. `https://toilet.aijoylab.kr/` 200 OK
2. 하단 버전이 최신 버전
3. GPS 권한 요청 정상
4. Kakao Nearby 호출 정상
5. 공공데이터 225건 로드
6. TOP10 거리순 PASS
7. Service Worker 등록 정상
8. 새로고침/앱 복귀 후 stale cache 없음

## TWA prerequisite

Digital Asset Links는 아래 위치에서 제공되어야 한다.

```
https://toilet.aijoylab.kr/.well-known/assetlinks.json
```

Android package proposal:

```
kr.aijoylab.seniortoilet
```

Play App Signing SHA-256 지문 확보 후 실제 `assetlinks.json`을 배포한다.

## Rollback

custom domain에서 문제가 생기면 기존 GitHub Pages URL은 계속 유지한다.

```
https://ohbeopseok-ops.github.io/senior-toilet-finder/
```
