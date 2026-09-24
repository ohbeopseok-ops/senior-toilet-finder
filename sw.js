const CACHE="senior-toilet-v0.5.2";
const APP_SHELL=["./manifest.webmanifest","./icon.svg"];

self.addEventListener("install",event=>{
  event.waitUntil(
    caches.open(CACHE)
      .then(cache=>cache.addAll(APP_SHELL))
      .then(()=>self.skipWaiting())
  );
});

self.addEventListener("activate",event=>{
  event.waitUntil(
    caches.keys()
      .then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
      .then(()=>self.clients.claim())
  );
});

self.addEventListener("fetch",event=>{
  if(event.request.method!=="GET") return;

  const url=new URL(event.request.url);
  const isAppHtml=event.request.mode==="navigate" || url.pathname.endsWith("/index.html") || url.pathname.endsWith("/senior-toilet-finder/");
  const isRuntimeConfig=url.pathname.endsWith("/nearby-config.js");
  const isLiveData=url.pathname.endsWith("/data/toilets-live.json");

  // Never let stale app HTML/config hide the latest GPS logic.
  if(isAppHtml || isRuntimeConfig || isLiveData){
    event.respondWith(
      fetch(event.request,{cache:"no-store"})
        .then(response=>{
          const copy=response.clone();
          caches.open(CACHE).then(cache=>cache.put(event.request,copy)).catch(()=>{});
          return response;
        })
        .catch(()=>caches.match(event.request).then(cached=>cached || caches.match("./index.html")))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then(cached=>cached||fetch(event.request).then(response=>{
      const copy=response.clone();
      caches.open(CACHE).then(cache=>cache.put(event.request,copy)).catch(()=>{});
      return response;
    }))
  );
});
