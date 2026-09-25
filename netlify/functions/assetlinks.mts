export default async (_req: Request) => {
  const raw = Netlify.env.get("TWA_SHA256_FINGERPRINTS")?.trim()
    || Netlify.env.get("PLAY_APP_SIGNING_SHA256")?.trim()
    || "";

  const fingerprints = raw.split(",").map(x => x.trim()).filter(Boolean);

  if (!fingerprints.length) {
    return Response.json(
      { error: "twa_sha256_fingerprints_not_configured" },
      { status: 503, headers: { "Cache-Control": "no-store" } }
    );
  }

  const body = [{
    relation: ["delegate_permission/common.handle_all_urls"],
    target: {
      namespace: "android_app",
      package_name: "kr.aijoylab.seniortoilet",
      sha256_cert_fingerprints: fingerprints
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
