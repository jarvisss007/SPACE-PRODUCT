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
(()=>{const box=$('tdQuiz');const Q=(TODAY&&TODAY.quiz)||[];if(!Q.length){box.closest('.td').hidden=true;return}
  const now=new Date(),day=Math.floor((Date.UTC(now.getFullYear(),now.getMonth(),now.getDate()))/864e5),q=Q[(day*7919)%Q.length];
  box.innerHTML=`<span class="tq">${q[0]}</span><details><summary>Show the answer</summary><span>${q[1]}</span></details><a class="more" href="${q[2]}">Work it out in the lab →</a>`})();
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
})();
</script>
