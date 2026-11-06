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
    if(u.origin===location.origin){if(a.dataset.placement&&u.pathname==='/book-today/')return['reader_directory_click','readers'];return'';}
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
})();
