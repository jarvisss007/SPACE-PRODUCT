<script>
// "Today" line at the top of a lab: one or two things that change every day, from data the site already has.
// build_site.py writes DAY (this lab's own data) and, for Moon labs, the Moon code shared with the Kundli Lab.
(()=>{'use strict';
const DAY=/*golapada-day*/null;if(!DAY)return;
const box=document.getElementById('gday');if(!box)return;
const pad=n=>String(n).padStart(2,'0'),now=Date.now(),items=[];
const dshort=t=>new Date(t).toLocaleDateString(undefined,{day:'numeric',month:'short'});
const inDays=t=>{const a=new Date();a.setHours(0,0,0,0);const b=new Date(t);b.setHours(0,0,0,0);return Math.round((b-a)/864e5)};
const when=n=>n===0?'today':n===1?'tomorrow':`in ${n} days`;
/*golapada-moon*/
// this lab's own history: today's anniversary, or the next one coming up
if(DAY.hist&&DAY.hist.length){const t=new Date(),y=t.getFullYear();let best=null;
  for(const [md,yr,title] of DAY.hist){const [m,d]=md.split('-').map(Number);for(const yy of [y,y+1]){const at=new Date(yy,m-1,d).getTime(),n=inDays(at);if(n>=0&&n<=60&&(!best||n<best.n)){best={n,yr,title,at,ago:yy-+yr}}}}
  if(best)items.push(best.n===0?`<b>On this day</b> in ${best.yr}: ${best.title}${best.ago>0?` (${best.ago} year${best.ago>1?'s':''} ago)`:''}`:`<b>Coming up ${dshort(best.at)}</b>: ${best.title} (${best.yr}${best.ago>0?`, ${best.ago} year${best.ago>1?'s':''} ago`:''})`)}
// tonight's Moon and nakshatra
if(DAY.moon&&typeof moonApparent==='function'){const ev=new Date();ev.setHours(21,0,0,0);const jd=ev.getTime()/864e5+2440587.5,T=(jd-2451545)/36525;
  const L=nrm(280.46646+36000.76983*T),M=nrm(357.52911+35999.05029*T)*D2R,sun=nrm(L+(1.914602-0.004817*T)*Math.sin(M)+0.019993*Math.sin(2*M));
  const m=moonApparent(jd).lon,el=nrm(m-sun),lit=Math.round((1-Math.cos(el*D2R))/2*100),sid=nrm(m-(23.853+(jd-2451545)/365.25*50.29/3600));
  const NAK=['Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishtha','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati'];
  items.push(`<b>Tonight's Moon</b>: ${lit}% lit, in ${NAK[Math.floor(sid/(360/27))]}${DAY.moon==='glare'?(lit>60?'. Bright moonlight will hide faint meteors.':'. A dark sky for faint meteors.'):''}`)}
// next meteor shower peak
if(DAY.showers){const y=new Date().getFullYear();let sh=null;for(const [n,m,d,z] of DAY.showers)for(const yy of [y,y+1]){const at=new Date(yy,m-1,d,23).getTime(),k=inDays(at);if(k>=0&&(!sh||k<sh.k))sh={k,n,z}}
  if(sh)items.push(`<b>Next shower</b>: the ${sh.n} peak ${when(sh.k)}${sh.z?`, up to about ${sh.z} an hour`:''}`)}
// next total solar eclipse
if(DAY.eclipses){const e=DAY.eclipses.map(([iso,l])=>{const [y,m,d]=iso.split('-').map(Number);return [new Date(y,m-1,d).getTime(),l]}).find(e=>e[0]>now);
  if(e){const n=inDays(e[0]);items.push(`<b>Next total solar eclipse</b>: ${dshort(e[0])} ${new Date(e[0]).getFullYear()}, ${e[1].split(' · ').pop()} (${n} days to go)`)}}
// this week's closest asteroid
if(DAY.neo){const r=DAY.neo.filter(r=>Date.parse(r[1])>now-864e5).sort((a,b)=>a[2]-b[2])[0];
  if(r)items.push(`<b>Asteroid this week</b>: ${r[0]} passes ${new Date(r[1]).toLocaleDateString(undefined,{weekday:'long'})} at ${r[2]<1?'less than the Moon’s distance':r[2].toFixed(1)+' times the Moon’s distance'}, and will miss`)}
const draw=()=>{box.innerHTML=items.length?`<span class="gd-k">Today</span>${items.map(i=>`<span class="gd-i">${i}</span>`).join('')}`:'';box.hidden=!items.length};
// next launch (and next from India), from the launch list Launch Watch and the home page already keep for 30 minutes
if(DAY.launch){(async()=>{let d=null;try{const c=JSON.parse(localStorage.getItem('gp-ll-upcoming')||'null');if(c&&now-c.t<30*60e3)d=c.d}catch(e){}
  if(!d){try{const r=await fetch('https://ll.thespacedevs.com/2.3.0/launches/upcoming/?limit=25&mode=normal&hide_recent_previous=true');if(!r.ok)throw 0;const j=await r.json();
    d=j.results.map(L=>({name:L.name,net:Date.parse(L.net),prec:(L.net_precision||{}).abbrev||'',status:(L.status||{}).abbrev||'',rocket:((L.rocket||{}).configuration||{}).full_name||'',prov:(L.launch_service_provider||{}).name||'',pad:(L.pad||{}).name||'',site:((L.pad||{}).location||{}).name||'',lat:+(L.pad||{}).latitude,lon:+(L.pad||{}).longitude,cc:(((L.pad||{}).country)||{}).alpha_3_code||'',orbit:(((L.mission||{}).orbit)||{}).name||'',desc:((L.mission||{}).description||'').slice(0,240)}));
    try{localStorage.setItem('gp-ll-upcoming',JSON.stringify({t:Date.now(),d}))}catch(e){}}catch(e){return}}
  const nm=x=>x.name.split(' | ')[1]||x.name,L=d.find(x=>x.net>now),I=d.find(x=>x.cc==='IND'&&x.net>now);
  if(DAY.launch==='india'&&I)items.unshift(`<b>Next from India</b>: ${nm(I)} on ${I.rocket}, ${dshort(I.net)}`);
  else if(L)items.unshift(`<b>Next launch</b>: ${nm(L)} on ${L.rocket}, ${dshort(L.net)}${I&&I!==L?` · next from India: ${nm(I)}, ${dshort(I.net)}`:''}`);
  draw()})()}
draw();
})();
</script>
