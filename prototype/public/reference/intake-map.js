(function(){
  'use strict';
  const L=window.STS_LOCATION;
  let boundaryPromise;
  async function loadBoundaries(){
    if(!boundaryPromise)boundaryPromise=(async()=>{
      const response=await fetch('/reference/data/district-boundaries.v1.geojson',{signal:AbortSignal.timeout(12000)});
      if(!response.ok)throw Error('Boundary asset unavailable');
      const bytes=await response.arrayBuffer();
      const digest=await crypto.subtle.digest('SHA-256',bytes);
      const sha=[...new Uint8Array(digest)].map(b=>b.toString(16).padStart(2,'0')).join('');
      if(sha!==L.boundarySource.sha256)throw Error('Boundary checksum mismatch');
      const collection=JSON.parse(new TextDecoder().decode(bytes));
      if(collection.boundary_version!==L.boundarySource.version)throw Error('Boundary version mismatch');
      const index=L.makeIndex(collection,window.STS_INTAKE.districts.map(d=>d.id));
      return {index,collection};
    })().catch(error=>{boundaryPromise=null;throw error;});
    return boundaryPromise;
  }
  function runtime(){
    if(window.STS_LOAD_MAPLIBRE)return window.STS_LOAD_MAPLIBRE();
    return new Promise((resolve,reject)=>{
      const ready=()=>{clearTimeout(timer);document.removeEventListener('sts-map-runtime-ready',ready);resolve(window.STS_LOAD_MAPLIBRE());};
      const timer=setTimeout(()=>{document.removeEventListener('sts-map-runtime-ready',ready);reject(Error('Map runtime unavailable'));},8000);
      document.addEventListener('sts-map-runtime-ready',ready,{once:true});
    });
  }
  window.STS_INTAKE_MAP={loadBoundaries,create({getDraft,onPin,onBoundaries,onStatus,t}){
    let map=null,marker=null,host=null,lib=null,boundaries=null,pending=false,generation=0,timer=null,ready=false,camera=null,markerKey;
    function destroy(){
      generation++;pending=false;ready=false;clearTimeout(timer);
      if(map){camera={center:map.getCenter(),zoom:map.getZoom()};marker?.remove();map.remove();}
      map=null;marker=null;lib=null;host?.remove();host=null;
    }
    function updateMarker(){
      const pin=getDraft().mapPin;
      if(!map||!lib||!pin)return;
      const point=[pin.longitude,pin.latitude];if(!L.validPoint(point))return;
      if(!marker){
        const el=document.createElement('button');el.type='button';el.className='intake-pin';el.textContent='●';
        el.setAttribute('aria-label',t('pinLabel'));el.title=t('pinLabel');
        marker=new lib.Marker({element:el,draggable:true}).setLngLat(point).addTo(map);
        marker.on('dragstart',()=>{const p=marker.getLngLat();onPin([p.lng,p.lat]);});
        marker.on('dragend',()=>{const p=marker.getLngLat();onPin([p.lng,p.lat]);});
        markerKey=e=>{
          const offsets={ArrowLeft:[-10,0],ArrowRight:[10,0],ArrowUp:[0,-10],ArrowDown:[0,10]};
          if(!offsets[e.key])return;e.preventDefault();e.stopPropagation();
          const screen=map.project(marker.getLngLat()),offset=offsets[e.key],p=map.unproject([screen.x+offset[0],screen.y+offset[1]]);
          onPin([p.lng,p.lat]);updateMarker();
        };
        el.addEventListener('keydown',markerKey);
      }else marker.setLngLat(point);
      marker.getElement().setAttribute('aria-label',t('pinLabel'));
      marker.getElement().title=t('pinLabel');
      marker.getElement().classList.toggle('confirmed',L.normalizeLocation(getDraft(),boundaries?.index,window.STS_INTAKE.districts,window.STS_INTAKE.directorySource).location?.level==='point');
    }
    async function mount(){
      const placeholder=document.getElementById('intake-map-host');
      if(!placeholder||getDraft().locationMethod!=='map_pin'){destroy();return;}
      if(host){placeholder.replaceWith(host);if(map){map.resize();updateMarker();syncLabels();}return;}
      host=placeholder;host.setAttribute('aria-label',t('mapLabel'));
      if(pending)return;
      pending=true;const token=generation;onStatus('map_loading');
      try{
        const loaded=await Promise.all([runtime(),loadBoundaries()]);
        if(token!==generation||!host?.isConnected)return;
        lib=loaded[0];boundaries=loaded[1];onBoundaries(boundaries.index);
        const config=window.STS_MAP_CONFIG||{};
        host.textContent='';
        map=new lib.Map({container:host,style:config.styleUrl||'https://tiles.openfreemap.org/styles/liberty',
          locale:{'Map.Title':t('mapLabel'),'NavigationControl.ZoomIn':t('zoomIn'),'NavigationControl.ZoomOut':t('zoomOut'),'CooperativeGesturesHandler.MobileHelpText':t('touchMap'),'CooperativeGesturesHandler.MacHelpText':t('scrollMap'),'CooperativeGesturesHandler.WindowsHelpText':t('scrollMap')},
          center:[(boundaries.index.bbox[0]+boundaries.index.bbox[2])/2,(boundaries.index.bbox[1]+boundaries.index.bbox[3])/2],
          zoom:5.8,attributionControl:false,renderWorldCopies:false,cooperativeGestures:true,hash:false});
        map.addControl(new lib.NavigationControl({showCompass:false}),'top-right');
        map.addControl(new lib.AttributionControl({compact:false,customAttribution:'<a href="https://www.geoboundaries.org/">geoBoundaries</a> · BBS / OCHA ROAP · <a href="https://creativecommons.org/licenses/by/3.0/igo/">CC BY 3.0 IGO</a>'}),'bottom-right');
        if(camera)map.jumpTo(camera);
        else map.fitBounds([[boundaries.index.bbox[0],boundaries.index.bbox[1]],[boundaries.index.bbox[2],boundaries.index.bbox[3]]],{padding:20,duration:0});
        map.on('load',()=>{
          if(token!==generation)return;clearTimeout(timer);ready=true;
          map.addSource('intake-districts',{type:'geojson',data:boundaries.collection});
          map.addLayer({id:'intake-district-lines',type:'line',source:'intake-districts',paint:{'line-color':'#28634b','line-width':1.2,'line-opacity':0.75}});
          onStatus('map_ready');updateMarker();syncLabels();
        });
        map.on('error',()=>{if(token===generation)onStatus('map_tiles_failed');});
        map.on('webglcontextlost',()=>{ready=false;onStatus('map_failed');});
        map.on('click',e=>{if(ready&&!e.originalEvent?.target?.closest('.intake-pin')){onPin([e.lngLat.lng,e.lngLat.lat]);updateMarker();}});
        timer=setTimeout(()=>{if(token===generation&&!ready)onStatus('map_failed');},12000);
        const pin=getDraft().mapPin;
        if(pin&&L.validPoint([pin.longitude,pin.latitude])){map.jumpTo({center:[pin.longitude,pin.latitude],zoom:Math.max(map.getZoom(),9)});updateMarker();}
      }catch{if(token===generation){onStatus('map_failed');if(map){map.remove();map=null;}pending=false;}}
    }
    function syncLabels(){
      for(const [selector,key]of [['.maplibregl-ctrl-zoom-in','zoomIn'],['.maplibregl-ctrl-zoom-out','zoomOut'],['.maplibregl-canvas','mapLabel']]){
        const el=host?.querySelector?.(selector);if(el){el.setAttribute('aria-label',t(key));el.title=t(key);}
      }
      for(const [selector,key]of [['.maplibregl-desktop-message','scrollMap'],['.maplibregl-mobile-message','touchMap']]){
        const el=host?.querySelector?.(selector);if(el)el.textContent=t(key);
      }
    }
    document.addEventListener('sts-map-runtime-dispose',destroy);
    return {beforeRender(){if(host?.isConnected)host.remove();},afterRender:mount,destroy,updateMarker,
      placeCenter(){if(map&&ready){const p=map.getCenter();onPin([p.lng,p.lat]);updateMarker();}},
      isReady:()=>ready,retry(){destroy();void mount();}};
  }};
})();
