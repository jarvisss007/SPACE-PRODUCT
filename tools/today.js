<script>
(()=>{'use strict';
const TODAY=/*golapada-today*/null;
const $=id=>document.getElementById(id),pad=n=>String(n).padStart(2,'0');
@@MOON@@
// tonight's Moon: phase and nakshatra (Lahiri, as in the Kundli Lab and Tonight's Sky)
const NAK=['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati'];
const TI=['Pratipada','Dwitiya','Tritiya','Chaturthi','Panchami','Shashthi','Saptami','Ashtami','Navami','Dashami','Ekadashi','Dwadashi','Trayodashi','Chaturdashi'];
(()=>{const ev=new Date();ev.setHours(21,0,0,0);const jd=ev.getTime()/864e5+2440587.5,T=(jd-2451545)/36525;
  const L=nrm(280.46646+36000.76983*T),M=nrm(357.52911+35999.05029*T)*D2R,sun=nrm(L+(1.914602-0.004817*T)*Math.sin(M)+0.019993*Math.sin(2*M));
  const m=moonApparent(jd).lon,el=nrm(m-sun),lit=Math.round((1-Math.cos(el*D2R))/2*100),ay=23.853+(jd-2451545)/365.25*50.29/3600,sid=nrm(m-ay),k=Math.floor(sid/(360/27)),t=Math.floor(el/12);
  const ph=el<12?'New Moon':el<84?'Crescent, growing':el<96?'Half Moon, growing':el<168?'Gibbous, growing':el<192?'Full Moon':el<264?'Gibbous, shrinking':el<276?'Half Moon, shrinking':el<348?'Crescent, shrinking':'New Moon';
  const tn=t===14?'Purnima':t===29?'Amavasya':(t<15?'Shukla ':'Krishna ')+TI[t%15];
  $('tdMoon').innerHTML=`<b>${ph}, ${lit}% lit</b><span>At 9 pm tonight the Moon is in <strong>${NAK[k]}</strong>, ${tn}.</span>`})();
// on this day, from the history timelines
(()=>{const box=$('tdHist');if(!TODAY||!TODAY.onthis){box.closest('.td').hidden=true;return}
  const now=new Date(),key=d=>pad(d.getMonth()+1)+'-'+pad(d.getDate());let lead='On this day',list=TODAY.onthis[key(now)];
  if(!list){for(let i=1;i<=14&&!list;i++){const d=new Date(now.getTime()+i*864e5);list=TODAY.onthis[key(d)];if(list)lead='Coming up on '+d.toLocaleDateString(undefined,{day:'numeric',month:'long'})}}
  if(!list){box.closest('.td').hidden=true;return}
  box.innerHTML=`<b>${lead}</b>`+list.slice(0,3).map(e=>`<a href="${e[2]}"><span class="ty">${e[0]}</span> ${e[1]}</a>`).join('')})();
// this week's closest asteroid, from Asteroid Watch's daily NASA/JPL data
(()=>{const box=$('tdRock');const now=Date.now();const rows=((TODAY&&TODAY.neo)||[]).filter(r=>Date.parse(r[1])>now-864e5);if(!rows.length){box.closest('.td').hidden=true;return}
  const r=rows.slice().sort((a,b)=>a[2]-b[2])[0],ld=r[2],when=new Date(r[1]).toLocaleDateString(undefined,{weekday:'long',day:'numeric',month:'short'});
  const size=r[3]?(r[3]<1?'about '+Math.round(r[3]*1000)+' m':'about '+r[3].toFixed(1)+' km'):'';
  box.innerHTML=`<b>${r[0]}</b><span>Passes Earth on ${when} at ${ld<1?'<strong>closer than the Moon</strong> ('+ld.toFixed(2)+' Moon distances)':ld.toFixed(1)+' times the Moon’s distance'}${size?', '+size+' across':''}. It will miss.</span>`})();
// the next rocket launch, sharing Launch Watch's 30-minute cache (the free service allows few requests an hour)
(async()=>{const box=$('tdLaunch');let d=null;try{const c=JSON.parse(localStorage.getItem('gp-ll-upcoming')||'null');if(c&&Date.now()-c.t<30*60e3)d=c.d}catch(e){}
  if(!d){try{const r=await fetch('https://ll.thespacedevs.com/2.3.0/launches/upcoming/?limit=25&mode=normal&hide_recent_previous=true');if(!r.ok)throw 0;const j=await r.json();
    d=j.results.map(L=>({name:L.name,net:Date.parse(L.net),prec:(L.net_precision||{}).abbrev||'',status:(L.status||{}).abbrev||'',rocket:((L.rocket||{}).configuration||{}).full_name||'',prov:(L.launch_service_provider||{}).name||'',pad:(L.pad||{}).name||'',site:((L.pad||{}).location||{}).name||'',lat:+(L.pad||{}).latitude,lon:+(L.pad||{}).longitude,cc:(((L.pad||{}).country)||{}).alpha_3_code||'',orbit:(((L.mission||{}).orbit)||{}).name||'',desc:((L.mission||{}).description||'').slice(0,240)}));
    try{localStorage.setItem('gp-ll-upcoming',JSON.stringify({t:Date.now(),d}))}catch(e){}}catch(e){box.innerHTML='<b>Rocket launches</b><span>Could not reach the launch list just now; Launch Watch has the full list.</span>';return}}
  const L=d.find(x=>x.net>Date.now()-36e5)||d[0];if(!L){box.closest('.td').hidden=true;return}
  const india=d.find(x=>x.cc==='IND'&&x.net>Date.now());const nm=x=>x.name.split(' | ')[1]||x.name;
  const tick=()=>{const s=Math.max(0,(L.net-Date.now())/1000),dd=Math.floor(s/86400),h=Math.floor(s%86400/3600),mi=Math.floor(s%3600/60);
    box.innerHTML=`<b>${nm(L)}</b><span>${L.rocket}, from ${L.site.split(',')[0]}. ${s>0?`Lifts off in <strong>${dd?dd+'d ':''}${h}h ${pad(mi)}m</strong>`:'Launching about now'}${L.prec&&L.prec!=='SEC'&&L.prec!=='MIN'?' (time not fixed yet)':''}.</span>${india&&india!==L?`<span class="tin">Next from India: ${nm(india)}, ${new Date(india.net).toLocaleDateString(undefined,{day:'numeric',month:'short'})}</span>`:''}`};
  tick();setInterval(tick,30000)})();
// question of the day: the same question for everyone today, a new one tomorrow, from the labs' quizzes
(()=>{const box=$('tdQuiz');const now=new Date(),day=Math.floor((Date.UTC(now.getFullYear(),now.getMonth(),now.getDate()))/864e5),q=TODAY&&TODAY.qod&&TODAY.qod[day];if(!q){box.closest('.td').hidden=true;return}
  box.innerHTML=`<span class="tq">${q[0]}</span><details><summary>Show the answer</summary><span>${q[1]}</span></details><a class="more" href="${q[2]}">Work it out in the lab →</a>`+`<div class="qs" id="qScore"></div>`;
  const K='golapada-qod',wk=()=>{const d=new Date(),m=new Date(d.getFullYear(),d.getMonth(),d.getDate()-((d.getDay()+6)%7));return Math.floor(Date.UTC(m.getFullYear(),m.getMonth(),m.getDate())/864e5)};
  const get=()=>{try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return {}}},put=o=>{try{localStorage.setItem(K,JSON.stringify(o))}catch(e){}};
  const draw=()=>{const o=get(),w=wk(),mine=Object.entries(o).filter(([k])=>+k>=w&&+k<w+7),right=mine.filter(([,v])=>v===1).length,el=$('qScore');
    el.innerHTML=(o[day]===undefined?`<span>Did you get it right?</span><button type="button" data-v="1">Yes</button><button type="button" data-v="0">Not this time</button>`:`<span>${o[day]?'Nice one!':'Tomorrow brings a new one.'}</span>`)+(mine.length?`<span class="note">This week: <b>${right} of ${mine.length}</b> right · kept only in this browser</span>`:'');
    el.querySelectorAll('button').forEach(b=>b.onclick=()=>{const o=get();o[day]=+b.dataset.v;Object.keys(o).forEach(k=>{if(+k<day-60)delete o[k]});put(o);draw()})};
  box.querySelector('details').addEventListener('toggle',draw,{once:true})})();
// coming up in the sky: next full and new Moon, next meteor shower peak, next total solar eclipse
(()=>{const box=$('tdSky');const now=Date.now(),out=[];
  const sunL=jd=>{const T=(jd-2451545)/36525,L=nrm(280.46646+36000.76983*T),M=nrm(357.52911+35999.05029*T)*D2R;return nrm(L+(1.914602-0.004817*T)*Math.sin(M)+0.019993*Math.sin(2*M))};
  const el=t=>{const jd=t/864e5+2440587.5;return nrm(moonApparent(jd).lon-sunL(jd))};
  const find=target=>{let prev=((el(now)-target+540)%360)-180;for(let t=now+36e5;t<now+32*864e5;t+=36e5){const v=((el(t)-target+540)%360)-180;if(prev<0&&v>=0){let a=t-36e5,b=t;for(let i=0;i<20;i++){const m=(a+b)/2;if(((el(m)-target+540)%360)-180<0)a=m;else b=m}return b}prev=v}return null};
  const dt=t=>new Date(t).toLocaleDateString(undefined,{weekday:'short',day:'numeric',month:'short'});
  const fm=find(180),nm=find(0);
  [[fm,'Full Moon','Purnima'],[nm,'New Moon','Amavasya: the darkest nights for stars']].filter(x=>x[0]).sort((a,b)=>a[0]-b[0]).forEach(([t,n,x])=>out.push([t,`<b>${dt(t)}</b> ${n} <em>${x}</em>`,'tonight.html']));
  const yr=new Date().getFullYear();let sh=null;for(const [n,m,d,z] of ((TODAY&&TODAY.showers)||[])){for(const y of [yr,yr+1]){const t=new Date(y,m-1,d,23).getTime();if(t>now-864e5&&(!sh||t<sh[0])){sh=[t,n,z]}}}
  if(sh)out.push([sh[0],`<b>${dt(sh[0])}</b> ${sh[1]} meteor shower peaks <em>${sh[2]?'up to about '+sh[2]+' an hour from a dark site':'numbers vary year to year'}</em>`,'meteor-showers.html']);
  const ld=x=>{const [y,m,d]=x.split('-').map(Number);return new Date(y,m-1,d)};const ec=((TODAY&&TODAY.eclipses)||[]).find(e=>ld(e[0]).getTime()>now);
  if(ec)out.push([ld(ec[0]).getTime(),`<b>${ld(ec[0]).toLocaleDateString(undefined,{day:'numeric',month:'short',year:'numeric'})}</b> Next total solar eclipse <em>${ec[1].split(' · ').pop()}</em>`,'eclipse-lab.html']);
  if(!out.length){box.closest('.td').hidden=true;return}
  box.innerHTML=out.sort((a,b)=>a[0]-b[0]).map(o=>`<a href="${o[2]}">${o[1]}</a>`).join('')})();
// your visit streak, kept only in this browser
(()=>{const box=$('tdStreak');try{const k='golapada-days',d=new Date(),key=x=>x.getFullYear()+'-'+pad(x.getMonth()+1)+'-'+pad(x.getDate());let days=JSON.parse(localStorage.getItem(k)||'[]');
  if(!days.includes(key(d))){days.push(key(d));days=days.slice(-400);localStorage.setItem(k,JSON.stringify(days))}
  let n=0;for(let x=new Date(d);days.includes(key(x));x.setDate(x.getDate()-1))n++;
  box.textContent=n>1?`🔥 ${n} days in a row. Come back tomorrow to keep it going. (Remembered only in this browser.)`:'Come back tomorrow: this strip changes every day, and your visits in a row are counted here (only in this browser).';box.hidden=false}catch(e){}})();
// your birthday in space: the date is kept only in this browser (localStorage), never sent anywhere
(()=>{const box=$('tdBday');if(!box)return;const K='golapada-bday';
  const get=()=>{try{return localStorage.getItem(K)}catch(e){return null}},put=v=>{try{v?localStorage.setItem(K,v):localStorage.removeItem(K)}catch(e){}};
  const form=()=>{box.innerHTML=`<span>Enter your birthday to see the sky the day you were born, your age in Mars years, and what happened in space on your date. It stays on this phone only.</span>
    <label class="bd-l">Your birthday <input type="date" id="bdIn" min="1900-01-01" max="${new Date().toISOString().slice(0,10)}"></label><button type="button" id="bdGo" class="bd-b">Show my birthday in space</button>`;
    $('bdGo').onclick=()=>{const v=$('bdIn').value;if(/^\d{4}-\d{2}-\d{2}$/.test(v)){put(v);show(v)}}};
  const show=v=>{const [y,m,d]=v.split('-').map(Number),born=new Date(y,m-1,d,12),now=new Date(),today=new Date(now.getFullYear(),now.getMonth(),now.getDate());
    if(isNaN(born)||born>now){put(null);form();return}
    const days=Math.floor((today-new Date(y,m-1,d))/864e5),years=days/365.2422;
    let next=new Date(now.getFullYear(),m-1,d);if(next<today)next=new Date(now.getFullYear()+1,m-1,d);const until=Math.round((next-today)/864e5);
    // the Moon on the day you were born (noon); the nakshatra can change during the day
    const jd=born.getTime()/864e5+2440587.5,T=(jd-2451545)/36525,L=nrm(280.46646+36000.76983*T),M=nrm(357.52911+35999.05029*T)*D2R,sun=nrm(L+(1.914602-0.004817*T)*Math.sin(M)+0.019993*Math.sin(2*M));
    const mo=moonApparent(jd).lon,el=nrm(mo-sun),lit=Math.round((1-Math.cos(el*D2R))/2*100),ay=23.853+(jd-2451545)/365.25*50.29/3600,nk=NAK[Math.floor(nrm(mo-ay)/(360/27))];
    const RASHI=['Mesha','Vrishabha','Mithuna','Karka','Simha','Kanya','Tula','Vrishchika','Dhanu','Makara','Kumbha','Meena'],sunR=RASHI[Math.floor(nrm(sun-ay)/30)],moonR=RASHI[Math.floor(nrm(mo-ay)/30)];
    const ph=el<12||el>348?'a new Moon':el<168?'a growing Moon':el<192?'a full Moon':'a shrinking Moon';
    const mars=years*365.2422/686.98,km=years*940e6,fulls=Math.floor(days/29.5306);
    const fmt=x=>x.toLocaleString(undefined,{maximumFractionDigits:0});
    const hist=((TODAY&&TODAY.onthis)||{})[pad(m)+'-'+pad(d)]||[];
    const head=until===0?`<b>🎂 Happy birthday!</b><span>You have gone round the Sun <strong>${Math.round(years)}</strong> times.</span>`:`<b>${until===1?'Tomorrow':until+' days'} to your birthday</b>`;
    box.innerHTML=head+`<span>The day you were born the Moon was ${ph}, ${lit}% lit, in <strong>${nk}</strong> (rashi ${moonR}); the Sun was in ${sunR}. The Moon moves to a new nakshatra about once a day, so for your exact birth time open the <a href="kundli.html">Kundli Lab</a>.</span>
      <span>You are <strong>${mars.toFixed(1)}</strong> in Mars years, you have seen about <strong>${fmt(fulls)}</strong> full Moons, and riding on Earth you have travelled about <strong>${fmt(km/1e9)} billion km</strong> around the Sun.</span>
      ${hist.length?`<span>Also on ${d} ${born.toLocaleDateString(undefined,{month:'long'})}: ${hist.slice(0,2).map(e=>`<a href="${e[2]}">${e[0]}, ${e[1]}</a>`).join('; ')}</span>`:''}
      <button type="button" id="bdForget" class="bd-x">Forget my birthday</button>`;
    $('bdForget').onclick=()=>{put(null);form()}};
  const v=get();v?show(v):form()})();
// share today's sky: draws a picture of today's cards on the phone itself and hands it to WhatsApp or any app
(()=>{const btn=$('tdShare');if(!btn)return;
  const txt=id=>{const e=$(id);return e&&!e.closest('.td').hidden?e.innerText.replace(/\n+/g,'\n').trim():''};
  function wrap(g,t,x,y,w,lh,max){const words=t.split(/\s+/);let line='',n=0;for(const wd of words){const test=line?line+' '+wd:wd;if(g.measureText(test).width>w&&line){g.fillText(line,x,y);y+=lh;n++;line=wd;if(n>=max-1){line=line+' …';break}}else line=test}if(line){g.fillText(line,x,y);y+=lh}return y}
  function draw(){const W=1080,H=1350,c=document.createElement('canvas');c.width=W;c.height=H;const g=c.getContext('2d');
    const bg=g.createLinearGradient(0,0,0,H);bg.addColorStop(0,'#0b1430');bg.addColorStop(1,'#04060b');g.fillStyle=bg;g.fillRect(0,0,W,H);
    let s=7;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};for(let i=0;i<220;i++){g.globalAlpha=.2+R()*.7;g.fillStyle='#fff';g.beginPath();g.arc(R()*W,R()*H*0.55,R()*1.8+.3,0,7);g.fill()}g.globalAlpha=1;
    g.fillStyle='#e8c46a';g.font='600 34px "Saira Condensed","Arial Narrow",sans-serif';g.fillText('GOLAPADA · TODAY IN SPACE',70,110);
    g.fillStyle='#e7edf3';g.font='700 64px "Saira Condensed","Arial Narrow",sans-serif';g.fillText(new Date().toLocaleDateString(undefined,{weekday:'long',day:'numeric',month:'long'}).toUpperCase(),70,185);
    const blocks=[['TONIGHT’S MOON','#e8c46a',txt('tdMoon')],['NEXT LAUNCH','#ffa24a',txt('tdLaunch')],['FROM HISTORY','#b6a4ff',txt('tdHist')],['ASTEROID THIS WEEK','#e0774a',txt('tdRock')]].filter(b=>b[2]&&!/Loading/.test(b[2]));
    let y=260;for(const [k,col,t] of blocks){g.fillStyle='rgba(18,26,37,.85)';const top=y-10;g.fillRect(60,top,W-120,230);g.fillStyle=col;g.fillRect(60,top,8,230);
      g.font='700 28px "Saira Condensed","Arial Narrow",sans-serif';g.fillText(k,95,y+32);g.fillStyle='#e7edf3';g.font='400 34px "IBM Plex Sans",system-ui,sans-serif';
      wrap(g,t.replace(/\n/g,' · ').replace(/(All launches|What else is up tonight|Every close pass) →/g,''),95,y+82,W-200,44,3);y+=228}
    g.fillStyle='#8a97a8';g.font='400 30px "IBM Plex Sans",system-ui,sans-serif';g.fillText('Free space-science labs, worked out from real data',70,H-110);
    g.fillStyle='#74c7ff';g.font='600 34px "IBM Plex Sans",system-ui,sans-serif';g.fillText(location.host?location.host+location.pathname.replace(/index\.html$/,''):'jarvisss007.github.io/SPACE-PRODUCT',70,H-60);
    return c}
  btn.onclick=async()=>{btn.disabled=true;try{const c=draw();const blob=await new Promise(r=>c.toBlob(r,'image/png'));const file=new File([blob],'golapada-today.png',{type:'image/png'});
      const text='Today in space, from Golapada: '+(location.href.split('#')[0]);
      if(navigator.canShare&&navigator.canShare({files:[file]})){await navigator.share({files:[file],text})}
      else{const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='golapada-today.png';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000);$('tdShareNote').textContent='Saved as a picture. Send it from your photos or downloads.'}}
    catch(e){if(e&&e.name!=='AbortError')$('tdShareNote').textContent='Sharing did not work on this device.'}finally{btn.disabled=false}}})();
// this week's Mars Colony challenge (same rotation as the simulator)
(()=>{const el=$('tdChal');if(!el)return;const T=["Storm on arrival","Thin air","No ships coming","Half the parts","Ticket home","A rough landing"];
  const d=new Date(),t=Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()),dow=(new Date(t).getUTCDay()+6)%7,th=t+(3-dow)*864e5,y=new Date(th).getUTCFullYear(),w=1+Math.floor((th-Date.UTC(y,0,1))/(7*864e5)),key=y+"-W"+String(w).padStart(2,"0");
  let done=false;try{done=!!JSON.parse(localStorage.getItem("golapada-mc-done")||"{}")[key]}catch(e){}
  el.innerHTML=`🚀 This week's Mars challenge: <a href="mars-colony.html">${T[(y*53+w)%T.length]}</a>${done?' <span style="color:#5fd6a0">✓ done</span>':''}`})();
// the space station over you: the next pass you can see in the next 3 days (station in sunlight, your sky dark, 10°+ up)
(()=>{const box=$('tdIss');if(!box)return;if(!TODAY||!TODAY.iss){box.closest('.td').hidden=true;return}
  const IN='Asia/Kolkata',CITY=[['Delhi',28.61,77.21,IN],['Mumbai',19.08,72.88,IN],['Bengaluru',12.97,77.59,IN],['Chennai',13.08,80.27,IN],['Kolkata',22.57,88.36,IN],['Hyderabad',17.39,78.49,IN],['Ahmedabad',23.02,72.57,IN],['Pune',18.52,73.86,IN],['Jaipur',26.91,75.79,IN],['Lucknow',26.85,80.95,IN],['Guwahati',26.14,91.74,IN],['Thiruvananthapuram',8.52,76.94,IN],['Hubballi',15.36,75.12,IN],['Mysuru',12.30,76.64,IN]];
  const K='golapada-place';let place=null;try{place=JSON.parse(localStorage.getItem(K)||'null')}catch(e){}
  const D=Math.PI/180,dirs=['north','north-east','east','south-east','south','south-west','west','north-west'],dir=a=>dirs[Math.round(((a%360)+360)%360/45)%8];
  const sunEq=t=>{const n=t/864e5+2440587.5-2451545,L=(280.460+0.9856474*n)*D,g=(357.528+0.9856003*n)*D,lam=L+(1.915*Math.sin(g)+0.020*Math.sin(2*g))*D,eps=23.4393*D;return [Math.cos(lam),Math.cos(eps)*Math.sin(lam),Math.sin(eps)*Math.sin(lam)]};
  const sunAlt=(t,lat,lon)=>{const v=sunEq(t),ra=Math.atan2(v[1],v[0]),dec=Math.asin(v[2]),gm=((280.46061837+360.98564736629*(t/864e5+2440587.5-2451545))%360)*D,H=gm+lon*D-ra;return Math.asin(Math.sin(lat*D)*Math.sin(dec)+Math.cos(lat*D)*Math.cos(dec)*Math.cos(H))/D};
  let lib=null;const load=()=>lib||(lib=new Promise((ok,no)=>{if(window.satellite)return ok();const sc=document.createElement('script');sc.src='https://cdn.jsdelivr.net/npm/satellite.js@5.0.0/dist/satellite.min.js';sc.onload=ok;sc.onerror=no;document.head.appendChild(sc)}));
  const pick=()=>{box.innerHTML=`<span>Find out when you can see the space station from where you are: a bright, steady light crossing the sky in a few minutes.</span>
    <label class="bd-l">Your city <select id="issCity"><option value="">Choose…</option>${CITY.map((c,i)=>`<option value="${i}">${c[0]}</option>`).join('')}</select></label>
    <button type="button" id="issGeo" class="bd-b">Use my location</button><span class="note" id="issNote">Your place stays on this phone.</span>`;
    $('issCity').onchange=e=>{const c=CITY[+e.target.value];if(c)go({n:c[0],lat:c[1],lon:c[2],tz:c[3]})};
    $('issGeo').onclick=()=>{if(!navigator.geolocation){$('issNote').textContent='Location is not available here; pick a city.';return}
      navigator.geolocation.getCurrentPosition(p=>go({n:'your location',lat:+p.coords.latitude.toFixed(2),lon:+p.coords.longitude.toFixed(2),tz:''}),()=>{$('issNote').textContent='Location not shared; pick a city instead.'},{timeout:8000})}};
  async function go(pl){place=pl;try{localStorage.setItem(K,JSON.stringify(pl))}catch(e){}box.innerHTML='<span>Working out the passes…</span>';
    try{await load()}catch(e){box.innerHTML='<span>Could not load the orbit calculator just now.</span>';return}
    const rec=satellite.twoline2satrec(TODAY.iss[0],TODAY.iss[1]),o={latitude:pl.lat*D,longitude:pl.lon*D,height:0},now=Date.now();let up=null,found=null;
    for(let t=now;t<now+3*864e5&&!found;t+=20000){const dt=new Date(t),pv=satellite.propagate(rec,dt);if(!pv||!pv.position||typeof pv.position!=='object')continue;
      const la=satellite.ecfToLookAngles(o,satellite.eciToEcf(pv.position,satellite.gstime(dt))),el=la.elevation/D;
      if(el>10){const sv=sunEq(t),p=pv.position,dd=p.x*sv[0]+p.y*sv[1]+p.z*sv[2],lit=dd>0||Math.hypot(p.x-dd*sv[0],p.y-dd*sv[1],p.z-dd*sv[2])>6378,dark=sunAlt(t,pl.lat,pl.lon)<-6;
        if(!up)up={t0:t,az0:la.azimuth/D,max:el,vis:false};up.max=Math.max(up.max,el);if(lit&&dark){if(!up.vis){up.v0=t;up.vaz0=la.azimuth/D}up.vis=true;up.v1=t;up.vaz1=la.azimuth/D}}
      else if(up){if(up.vis)found=up;up=null}}
    const fmt=t=>new Intl.DateTimeFormat(undefined,{weekday:'short',hour:'numeric',minute:'2-digit',...(pl.tz?{timeZone:pl.tz}:{})}).format(t);
    const where=pl.n==='your location'?'your location':pl.n;
    box.innerHTML=found?`<b>${fmt(found.v0)}</b><span>From ${where}: look ${dir(found.vaz0)}. The space station climbs ${found.max>60?'almost overhead':found.max>30?'high':'low'} (up to ${Math.round(found.max)}°) and moves towards the ${dir(found.vaz1)}, visible for about ${Math.max(1,Math.round((found.v1-found.v0)/60000))} min.</span><span class="note">A steady white light, not blinking. It fades out when it enters Earth's shadow.</span>`
      :`<b>No visible pass in the next 3 days</b><span>From ${where}, the station only shows up when it is sunlit and your sky is dark, which happens in runs a few weeks apart. Check again in a few days.</span>`;
    box.insertAdjacentHTML('beforeend','<button type="button" id="issChange" class="bd-x">Change place</button>');$('issChange').onclick=pick}
  place?go(place):pick()})();
// planets tonight: which bright planets are up this evening and before dawn, from your saved city (or Delhi)
(()=>{const box=$('tdPlan');if(!box)return;const D=Math.PI/180,EPS=23.4393*D,norm=a=>((a%360)+360)%360;
@@PLANETS@@
  let pl=null;try{pl=JSON.parse(localStorage.getItem('golapada-place')||'null')}catch(e){}if(!pl)pl={n:'Delhi',lat:28.61,lon:77.21};
  const NM={mercury:'Mercury',venus:'Venus',mars:'Mars',jupiter:'Jupiter',saturn:'Saturn'},dirs=['north','north-east','east','south-east','south','south-west','west','north-west'],dirn=a=>dirs[Math.round(norm(a)/45)%8];
  const hgt=h=>h<20?'low in the':h<50?'halfway up in the':'high in the';
  const d=new Date(),eve=Date.UTC(d.getFullYear(),d.getMonth(),d.getDate(),20)-pl.lon/15*36e5,dawn=eve+9*36e5;
  const look=t=>{const jd=t/864e5+2440587.5;return Object.keys(NM).map(k=>{const o=planet(k,jd),h=altaz(o,jd,pl.lat,pl.lon);return {k,alt:h.alt,az:h.az,mag:o.mag}}).filter(p=>p.alt>10).sort((a,b)=>a.mag-b.mag)};
  const fmt=a=>a.map(p=>`<strong>${NM[p.k]}</strong> ${hgt(p.alt)} ${dirn(p.az)}`).join(', ');
  const ev=look(eve),dw=look(dawn).filter(p=>!ev.some(e=>e.k===p.k));
  box.innerHTML=(ev.length?`<b>${ev.map(p=>NM[p.k]).join(', ').replace(/, ([^,]*)$/,' and $1')} this evening</b><span>Around 8 pm from ${pl.n}: ${fmt(ev)}.</span>`:`<b>No bright planets this evening</b><span>From ${pl.n} none is well up around 8 pm.</span>`)
    +(dw.length?`<span>Before dawn (about 5 am): ${fmt(dw)}.</span>`:'')+`<span class="note">Planets shine steadily; stars twinkle. ${ev[0]&&ev[0].k==='venus'?'Venus is the brightest thing in the sky after the Moon.':''}</span>`;
  // tonight's sky challenge: the brightest planet up this evening, or the Moon; tick it off when you have seen it
  const target=ev[0]?`${NM[ev[0].k]}, ${hgt(ev[0].alt)} ${dirn(ev[0].az)} around 8 pm`:'the Moon tonight';const K='golapada-sky',key=new Date().toISOString().slice(0,10);
  const get=()=>{try{return JSON.parse(localStorage.getItem(K)||'[]')}catch(e){return []}};
  const ch=document.createElement('div');ch.className='skych';box.appendChild(ch);
  const draw=()=>{const done=get();let n=0;for(let d=new Date();done.includes(d.toISOString().slice(0,10));d.setDate(d.getDate()-1))n++;
    ch.innerHTML=`<b>Tonight's sky challenge</b><span>Go outside and find ${target}.</span>`+(done.includes(key)?`<span class="ok">✓ Seen tonight${n>1?` · ${n} nights in a row`:''}</span>`:`<button type="button">I saw it!</button>`)+(done.length?`<span class="note">${done.length} challenge${done.length>1?'s':''} done · kept only in this browser</span>`:'');
    const b=ch.querySelector('button');if(b)b.onclick=()=>{const d=get();if(!d.includes(key))d.push(key);try{localStorage.setItem(K,JSON.stringify(d.slice(-400)))}catch(e){}draw()}};draw()})();
// since your last visit: launches, close asteroid passes, full Moons and new labs since then (the time is kept only in this browser)
(()=>{const el=$('tdSince');if(!el||!TODAY)return;const K='golapada-last',now=Date.now();let last=null;try{last=+localStorage.getItem(K)||null}catch(e){}
  try{if(!last||now-last>36e5)localStorage.setItem(K,String(now))}catch(e){}
  if(!last||now-last<6*36e5)return;const from=Math.max(last,now-30*864e5),out=[];
  const L=(TODAY.recent||[]).filter(r=>{const t=Date.parse(r[0]);return t>from&&t<=now}),IN=L.filter(r=>r[1]==='IND');
  if(L.length)out.push(`<b>${L.length}</b> rocket${L.length>1?'s':''} launched${IN.length?` (${IN.length} from India: ${IN.map(r=>r[3]).join(', ')})`:''}`);
  const N=(TODAY.neo||[]).filter(r=>{const t=Date.parse(r[1]);return t>from&&t<=now}).sort((a,b)=>a[2]-b[2]);
  if(N.length)out.push(`<b>${N.length}</b> asteroid${N.length>1?'s':''} passed within 5 Moon distances, closest ${N[0][0]} at ${N[0][2].toFixed(1)} Moon distances`);
  const el2=t=>{const jd=t/864e5+2440587.5,T=(jd-2451545)/36525,Ls=nrm(280.46646+36000.76983*T),M=nrm(357.52911+35999.05029*T)*D2R;return nrm(moonApparent(jd).lon-nrm(Ls+(1.914602-0.004817*T)*Math.sin(M)+0.019993*Math.sin(2*M)))};
  let fm=0,pv=el2(from);for(let t=from+6*36e5;t<=now;t+=6*36e5){const v=el2(t);if(pv<180&&v>=180)fm++;pv=v}if(fm)out.push(`<b>${fm}</b> full Moon${fm>1?'s':''}`);
  const lastDay=new Date(last).toISOString().slice(0,10),NL=(TODAY.newlabs||[]).filter(r=>r[0]>lastDay);
  if(NL.length)out.push(`new lab${NL.length>1?'s':''}: ${NL.slice(0,4).map(r=>`<a href="${r[1]}">${r[2]}</a>`).join(', ')}`);
  if(!out.length)return;const ago=Math.round((now-last)/864e5);
  el.innerHTML=`<b>Welcome back!</b> Since you were last here ${ago<1?'earlier today':ago===1?'yesterday':ago+' days ago'}${now-last>30*864e5?' (we keep the last 30 days)':''}: `+out.join(' · ')+'.';el.hidden=false})();
})();
</script>
