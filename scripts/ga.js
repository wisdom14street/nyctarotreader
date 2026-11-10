/* GA4 records visitor intent here, never a confirmed appointment or payment.
   Contact, booking and referral clicks have separate custom events.
   add_to_cart and begin_checkout are sent from cart.js. Only the system that
   confirms an order or booking can report completion. Analytics must not block navigation. */
(function(){
  function ga(n,p){try{if(typeof window.gtag==='function')window.gtag('event',n,p||{})}catch(_){}}
  window.niGA=ga;
  try{
    if(/^\/products\//.test(location.pathname)){
      var b=document.getElementById('buy'),it=null;
      if(b&&b.dataset&&b.dataset.v){var d=b.dataset;it={item_id:String(d.v),item_name:d.t+(d.vt&&d.vt!=='Default Title'?' - '+d.vt:''),price:+d.p||0,quantity:1};if(d.c)it.item_category=d.c}
      else{[].forEach.call(document.querySelectorAll('script[type="application/ld+json"]'),function(s){if(it)return;try{var j=JSON.parse(s.textContent);(Array.isArray(j)?j:[j]).forEach(function(o){if(!it&&o&&o['@type']==='Product'){var of=Array.isArray(o.offers)?o.offers[0]:(o.offers||{});it={item_id:String(o.sku||location.pathname.split('/')[2]),item_name:o.name,price:+of.price||0,quantity:1}}})}catch(_){}})}
      if(it)ga('view_item',{currency:'USD',value:it.price,items:[it]});
    }
  }catch(_){}
  function kind(a){
    var h=a.getAttribute('href')||'';
    if(/^tel:/i.test(h))return['contact_click','phone'];
    if(/^mailto:/i.test(h))return['contact_click','email'];
    var u;try{u=new URL(h,location.href)}catch(_){return''}
    if(u.origin===location.origin){if(a.dataset.placement&&(u.pathname==='/book-today/'||u.pathname==='/phone-tarot-readings/'))return['reader_directory_click','readers'];return'';}
    if(u.protocol!=='https:')return'';
    if(u.hostname==='book.squareup.com'&&u.pathname.startsWith('/appointments/'))return['booking_click','booking'];
    if((u.hostname==='www.google.com'&&u.pathname.startsWith('/maps/'))||u.hostname==='maps.google.com')return['directions_click','directions'];
    if((u.hostname==='namastebookshop.com'||u.hostname==='www.namastebookshop.com')&&!u.pathname.startsWith('/cart'))return['namaste_referral_click',a.dataset.linkType||'shop'];
    return'';
  }
  function track(e){try{
    if(e.type==='auxclick'&&e.button!==1)return;
    var a=e.target&&e.target.closest&&e.target.closest('a[href]');if(!a)return;var k=kind(a);if(!k)return;
    var u=new URL(a.getAttribute('href'),location.href);
    var p={link_type:k[1],link_url:(u.protocol==='https:'?u.origin+u.pathname:u.protocol+u.pathname).slice(0,200),link_text:(a.textContent||'').trim().replace(/\s+/g,' ').slice(0,100),transport_type:'beacon'};
    if(a.dataset.readerId)p.reader_id=a.dataset.readerId;
    if(a.dataset.placement)p.placement=a.dataset.placement;
    ga(k[0],p);
  }catch(_){}}
  document.addEventListener('click',track,true);
  document.addEventListener('auxclick',track,true);
  /* Namaste readings attribution (NAM-SISTERS-20261110-002). At interaction time (press, right-click,
     middle-click, keyboard, click) adds any MISSING utm_source=<this verified site>, utm_medium=referral,
     utm_campaign=namaste_readings to Namaste's own Square booking links (https://book.squareup.com,
     /appointments/<site>/location/LR25QQSXE9C2Q/...). Existing query, hash and utm_* are kept; origin and
     path bytes are untouched; nothing else is modified. No cookies, storage, endpoints or new accounts.
     No new event here: this site's existing booking_click already measures this click; only link tagging is added. */
  (function(){
    if(window.__nsReadingAttrV1)return;window.__nsReadingAttrV1=1;
    var SITES={'namastetarot.com':1,'namastepsychics.com':1,'nyctarotreader.com':1,'nycpsychicreaders.com':1,'psychiccenterofnewyork.com':1,'namastetarotcenter.com':1},
        LOC='LR25QQSXE9C2Q',EMIT=false,
        ADD=[['utm_source',''],['utm_medium','referral'],['utm_campaign','namaste_readings']];
    function site(){var h=String(location.hostname||'').toLowerCase();if(h.indexOf('www.')===0)h=h.slice(4);return Object.prototype.hasOwnProperty.call(SITES,h)?h:''}
    function sq(h){
      var u;try{u=new URL(h,location.href)}catch(_){return null}
      if(u.protocol!=='https:'||u.hostname!=='book.squareup.com'||u.username||u.password||u.port)return null;
      var m=u.pathname.match(/^\/appointments\/([a-z0-9]{6,20})\/location\/([A-Z0-9]{6,20})(?:\/|$)/);
      return m&&m[2]===LOC?{u:u,id:m[1]}:null;
    }
    function tag(a){try{
      var s=site(),h=a.getAttribute('href');if(!s||!h)return;var q=sq(h);if(!q)return;
      var add=[];for(var i=0;i<ADD.length;i++)if(!q.u.searchParams.has(ADD[i][0]))add.push(ADD[i][0]+'='+encodeURIComponent(ADD[i][1]||s));
      if(!add.length)return;
      var k=h.indexOf('#'),base=k<0?h:h.slice(0,k),hash=k<0?'':h.slice(k);
      var sep=base.indexOf('?')<0?'?':(/[?&]$/.test(base)?'':'&');
      a.setAttribute('href',base+sep+add.join('&')+hash);
    }catch(_){}}
    function onAct(e){var t=e.target,a=t&&t.closest&&t.closest('a[href]');if(a)tag(a)}
    ['pointerdown','mousedown','touchstart','contextmenu','auxclick','keydown','focusin','click'].forEach(function(n){
      document.addEventListener(n,onAct,{capture:true,passive:true})});
    if(EMIT)document.addEventListener('click',function(e){try{
      var t=e.target,a=t&&t.closest&&t.closest('a[href]');if(!a)return;var s=site();if(!s)return;var q=sq(a.getAttribute('href'));if(!q)return;
      var p=String(location.pathname||'/');if(!/^\/[A-Za-z0-9\/_.-]{0,100}$/.test(p))p='/other';
      ga('reading_book_click',{link_type:'booking',measurement_stage:'click',sister_site:s,destination_host:'book.squareup.com',square_booking_site:q.id,page_path:p,transport_type:'beacon'});
    }catch(_){}},{capture:true,passive:true});
  })();
})();
