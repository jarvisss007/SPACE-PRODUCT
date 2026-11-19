"""Generate Golapada's home page (index.html) from one list of labs.

Add a lab: add a line to LABS (file, title, one line, use cases, school topics, accent colour),
then run  py tools/make_index.py  and  py build_site.py.
"""
from pathlib import Path
import html, sys, json

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "index.html"
# file, title, one line, use cases, school topics, accent
LABS = [
 ("tonight.html","Tonight's Sky","What you can see tonight with your own eyes: the planets and where to look, the Moon, and the space station passing over.","tonight","night",'#9db8ff'),
 ("earth-from-above.html","Earth from Above","Today's photographs of the whole sunlit Earth from NASA's camera 1.5 million km away. Spin the day and find India.","tonight explore","",'#6ec3ff'),
 ("space-weather.html","Space Weather Now","Live from NOAA and NASA: the Sun right now, solar flares, the solar wind and storm levels, plus a storm launcher that predicts when a solar cloud hits Earth.","tonight explore learn india","energy",'#ffb347'),
    ("meteor-showers.html","Meteor Showers","The next showers from your city, hour by hour with the Moon, and each shower's date worked out from its parent comet's orbit.","tonight learn","night orbits",'#9ee7ff'),
    ("eclipse-lab.html","Eclipse Lab","Solar eclipses from your city to the second, from NASA's own numbers: the 2027 total eclipse, the 18-year Saros family, and the story from Rahu and Aryabhata to Aditya-L1.","tonight learn india ancient","night light",'#ffe3a3'),
    ("isro-launches.html","ISRO Launches","Every Indian orbital launch since 1979 on one chart: the failures, the comebacks, what flies next, and the road from a church in Thumba to Gaganyaan.","india mission learn","motion orbits",'#ff9933'),
 ("satellite-watch.html","Satellite Watch","The space stations, Hubble, NavIC and the brightest satellites live on a world map, and when each one passes over your city.","tonight india","orbits",'#7ee0c8'),
    ("gaganyaan-lab.html","Gaganyaan Lab","India's crew capsule: escape a failing rocket, orbit at 400 km and splash down under parachutes, checked against ISRO's 2018 and 2023 abort tests.","mission india learn","motion gravity orbits",'#ff9a3c'),
 ("chandrayaan-3.html","Chandrayaan-3 Moon Lab","India's 40-day road to the Moon flown again from ISRO's own orbit reports, then land Vikram yourself with four 800 N engines.","mission india","gravity orbits",'#ff9933'),
 ("mangalyaan.html","Mangalyaan Mars Lab","ISRO's Mars Orbiter Mission rebuilt from its burn log, with every engine burn's length predicted and a launch-window chart.","mission india","orbits",'#e0774a'),
 ("navic-lab.html","NavIC Lab","India's own GPS: how a receiver finds its position, the quality map across the region, and why three working satellites meant no fix.","india learn","orbits",'#ff9933'),
 ("lagrange-lab.html","Lagrange Point Lab","The five balance points of the Sun and Earth, which ones hold a spacecraft, and Aditya-L1's halo orbit computed to its real period.","india learn","gravity orbits",'#ffc24a'),
 ("space-debris-lab.html","Space Debris Lab","Break up a satellite and watch the pieces fall: Mission Shakti at 283 km against a collision at 789 km, where junk stays for decades.","india learn","energy orbits",'#ff8f6b'),
 ("rocket-lab.html","Rocket Lab","Build a rocket from real engines, from Raptor and the F-1 to ISRO's Vikas and CE-20, and see whether it reaches orbit, the Moon or Mars.","mission learn india","motion",'#ff7a5c'),
 ("starship-catch.html","Starship Catch","Fly a Starship launch and catch the booster on the tower arms, with hot staging, failure modes and a manual landing.","mission","motion",'#ffa24a'),
 ("mars-landing-lab.html","Mars Landing Lab","The seven minutes from 5.8 km/s to standing still on Mars: heat shield, supersonic parachute and a sky crane you fly.","mission learn","energy motion",'#e0774a'),
 ("mars-campaign.html","Mars Campaign","Refuel a ship in orbit with tanker flights, pick a real launch window and fly to the Moon or Mars and home again.","mission","orbits",'#e0774a'),
 ("reentry-lab.html","Re-entry Lab","Bring Apollo, Orion, Gaganyaan, Soyuz or Stardust home through the air without skipping off or burning up.","mission learn india","energy motion",'#ff7a3c'),
 ("gravity-assist-lab.html","Gravity Assist Lab","How Voyager borrowed speed from Jupiter and Saturn, re-derived from planet positions, and when the next grand tour is possible.","learn explore","motion orbits",'#e8c46a'),
 ("ion-engine-lab.html","Ion Engine Lab","How NASA's Dawn went further than any spacecraft before it on a push the weight of a sheet of paper.","learn","motion",'#7fb2ff'),
 ("touch-the-sun.html","Touch the Sun","Why the Sun is the hardest place to reach, and Parker Solar Probe's seven Venus flybys down to 191 km/s.","learn mission","gravity orbits",'#ffb347'),
 ("one-sky-lab.html","One Sky Lab","What if every space agency worked as one? Shared deep-space dishes, all six navigation systems live over your city, a Mars trip nearly five times lighter, and one Moon base instead of two.","explore india learn","orbits energy",'#7fe0ff'),
 ("planetary-defense-lab.html","Planetary Defense Lab","NASA's DART asteroid hit re-measured from its orbit, then plan the deflection of an asteroid headed for Earth.","learn explore","motion",'#c9a27e'),
 ("telescope-lab.html","Telescope Lab","How sharp Hubble, Webb, AstroSat and your eye can see, what each can make out on the Moon and Mars, and why Webb is kept so cold.","learn explore","light",'#d8b4ff'),
 ("voyager-now.html","Voyager Now","Where both Voyagers are as you read this, how long a message takes to reach them, and their fading power.","explore","orbits",'#e8c46a'),
 ("solar-system-lab.html","Solar System Lab","Every planet and big moon with NASA's numbers, an orrery from 499 CE to 2100, and landing trials on each world.","explore learn","night gravity",'#74c7ff'),
 ("milky-way-atlas.html","Milky Way Atlas","One zoom from the planets through the nearest stars to the whole galaxy and Andromeda, with travel times.","explore","night",'#b6a4ff'),
 ("exoplanet-explorer.html","Exoplanet Explorer","All of the confirmed planets around other stars, a transit you can watch, and the rocky worlds with Earth-like light.","explore","light",'#5fd6c4'),
 ("black-hole-lab.html","Black Hole and Wormhole Lab","A black hole drawn from general relativity, the real ones we know, and what a wormhole would need.","explore","gravity light",'#ffb347'),
 ("spacecraft-archive.html","Spacecraft Archive","Every solar system mission since Sputnik on a clickable timeline, with the firsts and NASA's own pictures.","explore india","",'#e8c46a'),
 ("schools.html","Golapada for Schools","For teachers: which lab fits which NCERT chapter, eight ready 40-minute lesson plans with answers, and an offline download.","learn","",'#5fd6a0'),
 ("worksheets.html","Worksheets","Printable worksheets for school physics topics, each question tied to a lab, with a teacher answer key.","learn","",'#a8e6a1'),
 ("aryabhata-lab.html","Aryabhata Lab","Aryabhata's spinning Earth, value of π and table of sines, implemented from his verses and put to work on space problems.","ancient india learn","maths night",'#e8c46a'),
 ("nalanda.html","Nalanda","A working rebuild of Nalanda's water clock from an eyewitness account, and the manuscripts that survived.","ancient india","maths",'#c4623f'),
 ("starship-through-time.html","Starship Through Time","Hand a spacecraft to Aryabhata or Brahmagupta and fly to Mars on their own planetary numbers.","ancient india","orbits",'#e8c46a'),
 ("clues-in-old-books.html","Clues in Old Books","Old Indian and Chinese records tested against modern science: planet gatherings, ancient eclipses and a supernova.","ancient india","night",'#e8c46a'),
]
USES = [("all","Everything"),("tonight","Look up tonight"),("learn","Learn a topic"),("mission","Fly a mission"),("india","India in space"),("explore","Explore the universe"),("ancient","Ancient astronomy")]
TOPICS = [
 ("gravity","Gravitation","Why things fall, why the Moon stays up, and how far a planet's pull reaches. A core topic in Class 11 physics (the new Class 9 book, Exploration, leaves it out)."),
 ("orbits","Satellites and orbits","Orbital speed, escape speed, geostationary orbits and how satellites find your position."),
 ("motion","Laws of motion and momentum","Newton's laws in action: rockets, collisions with asteroids, and stealing speed from a planet. Class 9 and Class 11 physics."),
 ("energy","Energy, drag and heat","Where a spacecraft's energy goes when air slows it down, and why re-entry is so hot."),
 ("light","Light and telescopes","Diffraction, how sharp a telescope can see, and the glow of warm objects."),
 ("night","The night sky and the solar system","The planets, the Moon's phases and finding your way around the sky."),
 ("maths","Mathematics from history","π, the sine and big numbers from Aryabhata's and Nalanda's India."),
]
WS = {'gravity':'gravity','orbits':'gravity','motion':'motion','energy':'energy','light':'light','night':'sky'}
e = html.escape
cards = "\n".join(
  f'      <a class="lab" href="{f}" data-use="{u}" data-topic="{tp}" data-text="{e((t+" "+d).lower())}" style="--acc:{c}"><b>{e(t)}</b><span>{e(d)}</span><em>{" · ".join(dict(USES)[x] for x in u.split())}</em></a>'
  for f,t,d,u,tp,c in LABS)
chips = "".join(f'<button type="button" class="chip" data-f="{k}" aria-pressed="{str(k=="all").lower()}">{e(v)}</button>' for k,v in USES)
topics = "\n".join(
  f'      <div class="topic"><h3>{e(n)}</h3><p>{e(d)}</p><div class="tl">' + "".join(f'<a href="{f}">{e(t)}</a>' for f,t,_,_,tp,_ in LABS if k in tp.split()) + (f'<a class="ws" href="worksheets.html?topic={WS[k]}">Printable worksheet</a>' if k in WS else '') + '</div></div>'
  for k,n,d in TOPICS)
page = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="claude:viewport-fit-sides" content="cover">
<title>Golapada</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=Tiro+Devanagari+Sanskrit&display=swap">
<style>
/* Layout: a front door. A sky hero with the name and two ways in, then the labs filtered by what you want to do, then the same labs by school topic, then what makes them trustworthy. Single dark look. */
:root{{color-scheme:dark;--void:#04060b;--panel:#0b1017;--panel2:#121a25;--line:#1f2a38;--ink:#e7edf3;--dim:#8a97a8;--flame:#ffa24a;--lox:#74c7ff;--gold:#e8c46a;--violet:#b6a4ff;--mars:#e0774a;--saffron:#ff9933;
  --display:"Saira Condensed","Arial Narrow","Helvetica Neue",sans-serif;--body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;--deva:"Tiro Devanagari Sanskrit","Noto Serif Devanagari",serif}}
html,body{{background:var(--void)}}body{{color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.55;margin:0}}*{{box-sizing:border-box}}
.wrap{{max-width:1180px;margin:0 auto;padding-block:0 56px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:28px}}
.hero{{position:relative;min-height:min(78vh,620px);display:flex;flex-direction:column;justify-content:flex-end;padding:56px 0 28px;overflow:hidden}}
#sky{{position:absolute;inset:0;width:100%;height:100%;z-index:0}}
.hero>*:not(canvas){{position:relative;z-index:1}}
.deva{{font-family:var(--deva);font-size:clamp(28px,5vw,44px);color:var(--gold);line-height:1;margin:0 0 6px}}
h1{{font-family:var(--display);font-weight:700;font-size:clamp(56px,12vw,128px);line-height:.86;margin:0;letter-spacing:.01em;text-transform:uppercase}}
.lede{{font-size:clamp(17px,2.1vw,21px);max-width:44ch;color:#d5dde6;margin:14px 0 6px}}
.meaning{{font-size:13.5px;color:var(--dim);max-width:62ch;margin:0 0 18px}}
.ctas{{display:flex;flex-wrap:wrap;gap:10px}}
.cta{{display:inline-flex;align-items:center;gap:8px;padding:12px 18px;border-radius:999px;font-family:var(--display);font-weight:700;letter-spacing:.06em;text-transform:uppercase;font-size:15px;text-decoration:none}}
.cta.main{{background:var(--gold);color:#1b1404}}.cta.alt{{border:1px solid #3a4a60;color:var(--ink);background:rgba(11,16,23,.6)}}
.cta:focus-visible,.chip:focus-visible,.lab:focus-visible,#q:focus-visible{{outline:2px solid var(--lox);outline-offset:2px}}
h2{{font-family:var(--display);font-weight:700;font-size:clamp(24px,3.4vw,34px);margin:0 0 6px;text-transform:uppercase}}
.sub{{color:var(--dim);margin:0 0 14px;max-width:70ch}}
.bar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:14px}}
.chip{{font:inherit;cursor:pointer;border:1px solid var(--line);background:var(--panel);color:#c3ccd6;border-radius:999px;padding:7px 13px;font-size:13.5px}}
.chip[aria-pressed="true"]{{background:var(--ink);color:#0a0d12;border-color:var(--ink)}}
#q{{font:inherit;flex:1 1 220px;min-width:0;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:999px;padding:8px 14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}}
.lab{{display:flex;flex-direction:column;gap:6px;text-decoration:none;color:var(--ink);background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-top:3px solid var(--acc);border-radius:10px;padding:16px;min-width:0;transition:transform .15s,border-color .15s,box-shadow .15s}}
.lab:hover{{transform:translateY(-3px);box-shadow:0 10px 28px rgba(0,0,0,.45);border-color:#2c3a4d;border-top-color:var(--acc)}}
.lab b{{font-family:var(--display);font-weight:700;font-size:24px;line-height:1.05;text-transform:uppercase}}.lab span{{font-size:14px;color:#c3ccd6}}.lab em{{font-style:normal;font-size:12px;color:var(--dim);margin-top:auto;padding-top:6px}}
.lab[hidden]{{display:none}}
#none{{color:var(--dim)}}
.topics{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px}}
.topic{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px}}.topic h3{{margin:0 0 4px;font-family:var(--display);font-size:20px;text-transform:uppercase}}.topic p{{margin:0 0 10px;font-size:13.5px;color:#c3ccd6}}
.tl{{display:flex;flex-wrap:wrap;gap:6px}}.tl a{{font-size:13px;color:var(--ink);text-decoration:none;background:var(--panel2);border:1px solid var(--line);border-radius:999px;padding:4px 10px}}.tl a:hover{{border-color:var(--lox)}}.tl a.ws{{background:rgba(168,230,161,.12);border-color:#3f6b3a;color:#cdeec8}}
.trust{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}}.trust div{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px}}.trust b{{font-family:var(--display);font-size:20px;text-transform:uppercase;display:block;margin-bottom:4px}}.trust span{{font-size:13.5px;color:#c3ccd6}}
footer{{color:var(--dim);font-size:12.5px;max-width:100ch;line-height:1.6}}
@media (max-width:560px){{.hero{{min-height:72vh;padding-top:36px}}}}
</style>

<div class="wrap">
  <header class="hero">
    <canvas id="sky" aria-hidden="true"></canvas>
    <p class="deva" lang="sa">गोलपाद</p>
    <h1>Golapada</h1>
    <p class="lede">Space science you can play with. {len(LABS)} interactive labs built on real mission data, from tonight’s sky to the edge of the galaxy.</p>
    <p class="meaning"><i>Golapada</i>, “the chapter on the sphere”, is the part of Aryabhata’s <i>Aryabhatiya</i> (499 CE) where he explained the turning Earth, the sky and eclipses.</p>
    <div class="ctas"><a class="cta main" href="tonight.html">What’s in my sky tonight?</a><a class="cta alt" href="#labs">Explore all {len(LABS)} labs</a><a class="cta alt" href="schools.html">For schools</a></div>
  </header>

  <section id="labs">
    <h2>What would you like to do?</h2>
    <p class="sub">Every lab runs in the browser on a phone or a laptop, with nothing to install.</p>
    <div class="bar">{chips}<input id="q" type="search" placeholder="Search: Moon, ISRO, rockets, black holes…" aria-label="Search the labs"></div>
    <div class="grid" id="grid">
{cards}
    </div>
    <p id="none" hidden>No lab matches that yet. Try another word.</p>
  </section>

  <section>
    <h2>Learn by topic</h2>
    <p class="sub">For students and teachers: the same labs grouped by the science they teach. Each one turns a textbook idea into something you can change and watch.</p>
    <div class="topics">
{topics}
    </div>
  </section>

  <section>
    <h2>Why you can trust it</h2>
    <div class="trust">
      <div><b>Real numbers</b><span>Mission figures come from ISRO, NASA, ESA and JPL, cited at the bottom of every lab.</span></div>
      <div><b>Checked against reality</b><span>Each lab ends with a table comparing the model with what really happened, including where it falls short.</span></div>
      <div><b>Live where it matters</b><span>Satellite orbits refresh every day from public tracking data; the planets and Moon are worked out for the moment you open the page.</span></div>
      <div><b>Free and open</b><span>No account, no ads, no tracking. It works on any phone with a browser.</span></div>
    </div>
  </section>

  <footer>Golapada is an independent project, not affiliated with ISRO, NASA, ESA, JPL, SpaceX or CelesTrak. Mission data from their public reports and from the sources cited on each page. Satellite orbits from CelesTrak; orbit library satellite.js (MIT).</footer>
</div>
<script>
(()=>{{
'use strict';
// the hero sky: slow-turning stars with the planets' orbits sketched in
const c=document.getElementById('sky'),g=c.getContext('2d');let W=0,H=0,stars=[];
function size(){{const r=Math.min(2,devicePixelRatio||1);W=c.clientWidth;H=c.clientHeight;c.width=Math.round(W*r);c.height=Math.round(H*r);g.setTransform(r,0,0,r,0,0);let s=11;const R=()=>{{s=(s*16807)%2147483647;return s/2147483647}};stars=Array.from({{length:Math.round(W*H/2600)}},()=>[R()*2-1,R()*2-1,R(),R()])}}
const still=matchMedia('(prefers-reduced-motion: reduce)').matches;
function draw(t){{const cx=W*0.72,cy=W<600?H*0.16:H*0.36,M=Math.max(W,H);g.clearRect(0,0,W,H);const bg=g.createRadialGradient(cx,cy,0,cx,cy,M*0.9);bg.addColorStop(0,'#101a35');bg.addColorStop(.55,'#060a18');bg.addColorStop(1,'#04060b');g.fillStyle=bg;g.fillRect(0,0,W,H);
  const a=still?0:t*0.000012;for(const [x,y,m,tw] of stars){{const X=cx+(x*Math.cos(a)-y*Math.sin(a))*M,Y=cy+(x*Math.sin(a)+y*Math.cos(a))*M;if(X<0||X>W||Y<0||Y>H)continue;g.globalAlpha=.25+m*.6*(still?1:.75+.25*Math.sin(t*0.002+tw*20));g.fillStyle='#fff';g.fillRect(X,Y,m>0.93?1.8:1.1,m>0.93?1.8:1.1)}}g.globalAlpha=1;
  const sun=g.createRadialGradient(cx,cy,0,cx,cy,26);sun.addColorStop(0,'#fff6d8');sun.addColorStop(.4,'#ffcf6b');sun.addColorStop(1,'rgba(255,180,80,0)');g.fillStyle=sun;g.beginPath();g.arc(cx,cy,26,0,7);g.fill();
  const P=[[60,0.000060,'#c9c0b5',2.2],[95,0.000044,'#fff3c4',3.2],[135,0.000037,'#4aa3ff',3.6],[180,0.000030,'#ff8a5c',3],[250,0.000016,'#f0d7a8',6],[330,0.000012,'#e8cf8a',5]];
  for(const [r,w,col,s] of P){{const rr=r*Math.min(1.4,M/1100);g.strokeStyle='rgba(157,184,255,.10)';g.beginPath();g.ellipse(cx,cy,rr,rr*0.42,-0.25,0,7);g.stroke();const th=(still?1:t*w)+r;const x=cx+Math.cos(th)*rr*Math.cos(-0.25)-Math.sin(th)*rr*0.42*Math.sin(-0.25),y=cy+Math.cos(th)*rr*Math.sin(-0.25)+Math.sin(th)*rr*0.42*Math.cos(-0.25);g.fillStyle=col;g.beginPath();g.arc(x,y,s,0,7);g.fill()}}
  const fade=g.createLinearGradient(0,H*0.45,0,H);fade.addColorStop(0,'rgba(4,6,11,0)');fade.addColorStop(1,'rgba(4,6,11,.96)');g.fillStyle=fade;g.fillRect(0,0,W,H);
  if(!still)requestAnimationFrame(draw)}}
size();new ResizeObserver(()=>{{size();if(still)draw(0)}}).observe(c);requestAnimationFrame(draw);
// filters and search
const labs=[...document.querySelectorAll('.lab')],q=document.getElementById('q');let use='all';
function apply(){{const s=q.value.trim().toLowerCase();let n=0;for(const l of labs){{const ok=(use==='all'||l.dataset.use.split(' ').includes(use))&&(!s||l.dataset.text.includes(s)||l.dataset.use.includes(s));l.hidden=!ok;if(ok)n++}}document.getElementById('none').hidden=n>0}}
document.querySelectorAll('.chip').forEach(b=>b.onclick=()=>{{use=b.dataset.f;document.querySelectorAll('.chip').forEach(x=>x.setAttribute('aria-pressed',x===b));apply()}});
q.addEventListener('input',apply);
}})();
</script>
'''
OUT.write_text(page, encoding="utf-8")
print("labs", len(LABS))
