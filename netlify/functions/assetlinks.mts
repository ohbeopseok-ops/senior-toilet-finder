export default async (_req: Request) => {
  const fingerprint = Netlify.env.get("PLAY_APP_SIGNING_SHA256")?.trim();

  if (!fingerprint) {
    return Response.json(
      { error: "play_app_signing_sha256_not_configured" },
      { status: 503, headers: { "Cache-Control": "no-store" } }
    );
  }

  const body = [{
    relation: ["delegate_permission/common.handle_all_urls"],
    target: {
      namespace: "android_app",
      package_name: "kr.aijoylab.seniortoilet",
      sha256_cert_fingerprints: [fingerprint]
    }
  }];

  return new Response(JSON.stringify(body, null, 2), {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-cache, no-store, must-revalidate"
    }
  });
};

export const config = {
  path: "/.well-known/assetlinks.json"
};
