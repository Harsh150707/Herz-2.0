/* Herz 2.0 front end: drawing and UI only. Every graph result comes from server.py through /api. */
const $=id=>document.getElementById(id),esc=s=>s.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const CAT=[["Sports","⚽"],["Movies","🎬"],["Music","🎵"],["Gaming","🎮"],["Tech","💻"],["Travel","✈️"]];
const AL=[["bfs","BFS"],["dfs","DFS"],["comp","Components"],["sp","Shortest path (BFS)"],["dij","Dijkstra"],["kru","MST: Kruskal"],["pri","MST: Prim"],["cyc","Cycle"],["bip","Bipartite"],["eul","Euler"],["col","Coloring"]];
let U=[],A=[],me=-1,tab="d",cur=-1,sel=new Set,P=[],hl={n:new Set,e:new Set,c:null},out="Pick an algorithm to run.",CH={},RQ={o:new Set,i:new Set},dirty=1,u0={},last="",lastG="",prevF=-1;
const tip=m=>{const t=$("t");t.textContent=m;t.style.display="block";clearTimeout(tip.h);tip.h=setTimeout(()=>t.style.display="none",2200)};
const con=(a,b)=>{A[a].add(b);A[b].add(a);dirty=1},key=(a,b)=>a<b?a+"-"+b:b+"-"+a;
const sh=(a,b)=>U[a].i.filter(x=>U[b].i.includes(x)).length;
const E=()=>{const r=[];A.forEach((s,a)=>s.forEach(b=>a<b&&r.push([a,b])));return r};
function face(i,s=38,nm){const n=nm||U[i].n,h=[...n].reduce((a,c)=>(a*31+c.charCodeAt(0))>>>0,7),sk=["#f3d2b3","#e0ac7f","#c68642","#8d5524","#f1c9a5"][h%5],hr=["#2b1d14","#4a2c17","#1c1c1f","#7a4a21","#a0522d"][(h>>3)%5],bg=h%360,st=(h>>5)%3;
return `<svg viewBox="0 0 40 40" width="${s}" height="${s}"><defs><clipPath id="fc"><circle cx="20" cy="20" r="20"/></clipPath></defs><g clip-path="url(#fc)"><rect width="40" height="40" fill="hsl(${bg} 70% 80%)"/><path d="M6 40c1-9 8-12 14-12s13 3 14 12z" fill="hsl(${(bg+140)%360} 55% 45%)"/><circle cx="20" cy="17" r="8" fill="${sk}"/>${st==0?`<path d="M11.5 17a8.5 9 0 0 1 17 0c-3-4-11-4-17 0z" fill="${hr}"/>`:st==1?`<path d="M11 19c-1-9 5-12 9-12s10 3 9 12c-1-5-4-7-9-7s-8 2-9 7z" fill="${hr}"/><rect x="10.5" y="16" width="3" height="10" rx="1.5" fill="${hr}"/><rect x="26.5" y="16" width="3" height="10" rx="1.5" fill="${hr}"/>`:`<path d="M12 15a8 8 0 0 1 16 0z" fill="${hr}"/>`}<circle cx="17" cy="18" r="1" fill="#222"/><circle cx="23" cy="18" r="1" fill="#222"/><path d="M17.5 21.5q2.5 2 5 0" stroke="#222" stroke-width="1" fill="none"/></g></svg>`}
function hero(){const P=[["Aarav",56,50],["Priya",344,40],["Isha",352,168],["Riya",200,200],["Meera",48,172]];return `<svg viewBox="0 0 400 230" aria-hidden="true"><polygon points="${P.map(p=>p[1]+","+p[2]).join(" ")}" fill="var(--bb)" fill-opacity=".5" stroke="var(--ac)" stroke-opacity=".35" stroke-width="2"/>${P.map(p=>`<line x1="200" y1="92" x2="${p[1]}" y2="${p[2]}" stroke="var(--ac)" stroke-opacity=".35" stroke-width="2"/>`).join("")}<circle cx="200" cy="92" r="34" fill="var(--sf)" stroke="var(--bb)" stroke-width="6"/><path transform="translate(200 92) scale(1.6)" d="M0 14C-28-4-20-26 0-14C20-26 28-4 0 14z" fill="var(--ac)"/>${P.map(p=>`<g transform="translate(${p[1]-26} ${p[2]-26})">${face(0,52,p[0])}</g>`).join("")}</svg>`}
const chips=l=>l.map(i=>`<span class="chip">${CAT[i][1]} ${CAT[i][0]}</span>`).join("");
/* ---------- talking to server.py: ALL graph algorithms run there ---------- */
const api=(p,o)=>fetch("/api/"+p,o&&{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(o)}).then(r=>r.json());
async function sync(){if(me<0)return;let s;try{s=await api("state?me="+me)}catch(e){return}
const j=JSON.stringify(s);if(j==last)return;last=j;const g=JSON.stringify([s.users,s.edges]);if(g!=lastG){lastG=g;dirty=1}
U=s.users;A=U.map(()=>new Set);s.edges.forEach(([a,b])=>{A[a].add(b);A[b].add(a)});RQ={i:new Set(s.incoming),o:new Set(s.outgoing)};CH=s.chats;
if(prevF>=0&&A[me].size>prevF)tip("You have a new connection");prevF=A[me].size;
if(tab=="c"&&$("mi")){const v=$("mi").value;vc();$("mi").value=v;$("mi").focus()}else if(!document.activeElement||document.activeElement.tagName!="INPUT")app()}
/* layout below is drawing only */
function lay(){const n=A.length;while(P.length<n){const t=P.length*2.4;P.push([300+170*Math.cos(t),210+130*Math.sin(t)])}
for(let it=0;it<250;it++){const F=P.map(()=>[0,0]);for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){const dx=P[i][0]-P[j][0],dy=P[i][1]-P[j][1],d=Math.hypot(dx,dy)||1,f=2600/(d*d);F[i][0]+=dx/d*f;F[i][1]+=dy/d*f;F[j][0]-=dx/d*f;F[j][1]-=dy/d*f}
A.forEach((s,a)=>s.forEach(b=>{if(a<b){const dx=P[b][0]-P[a][0],dy=P[b][1]-P[a][1],d=Math.hypot(dx,dy)||1,f=(d-60)*.05;F[a][0]+=dx/d*f;F[a][1]+=dy/d*f;F[b][0]-=dx/d*f;F[b][1]-=dy/d*f}}));
P.forEach((p,i)=>{p[0]+=(300-p[0])*.01+Math.max(-8,Math.min(8,F[i][0]));p[1]+=(210-p[1])*.01+Math.max(-8,Math.min(8,F[i][1]));p[0]=Math.max(25,Math.min(575,p[0]));p[1]=Math.max(25,Math.min(395,p[1]))})}}
/* ---------- onboarding ---------- */
function s0(){$("app").innerHTML=`<div class="card hero">${hero()}<h1>Herz 2.0</h1><p class="m">Meet new people through the friends you already share.</p><label>Your name</label><input id="nm" autocomplete="name"><label>Email address</label><input id="em" type="email" placeholder="you@example.com"><button class="p" onclick="s1()">Continue</button></div>`}
function s1(){const n=$("nm").value.trim(),e=$("em").value.trim();if(!n||!/^\S+@\S+\.\S+$/.test(e))return tip("Enter your name and a valid email");u0={n,e};
$("app").innerHTML=`<div class="card"><h1>Hi ${esc(n)}, what are you into?</h1><p class="m">Pick at least one. Shared interests set the edge weights in the graph.</p><div class="chips" id="ch"></div><button class="p" onclick="s2()">Start connecting</button></div>`;ch()}
function ch(){$("ch").innerHTML=CAT.map((c,i)=>`<button class="tile t${i} ${sel.has(i)?"on":""}" onclick="tg(${i})"><span>${c[1]}</span>${c[0]}</button>`).join("")}
function tg(i){sel.has(i)?sel.delete(i):sel.add(i);ch()}
async function s2(){if(!sel.size)return tip("Pick at least one interest");try{const r=await api("login",{name:u0.n,email:u0.e,interests:[...sel]});me=r.me;await sync();setInterval(sync,2000)}catch(e){tip("Cannot reach the server. Run server.py first.")}}
function app(){const rq=RQ.i.size;$("app").innerHTML=`<div class="top"><div class="av">${face(me)}</div><div><h1>Herz 2.0</h1><span class="m">${esc(U[me].n)}, ${esc(u0.e)}: ${A[me].size} connection(s)</span></div></div><div class="tabs">${[["d","Discover"],["r","Requests"+(rq?` (${rq})`:"")],["c","Chat"],["g","Graph Lab"]].map(t=>`<button class="${tab==t[0]?"on":""}" onclick="tab='${t[0]}';app()">${t[1]}</button>`).join("")}</div><div id="v"></div>`;({d:vd,r:vr,c:vc,g:vg})[tab]()}
/* ---------- discover, requests, chat ---------- */
function vd(){$("v").innerHTML=`<input id="q" placeholder="Search people by name" oninput="dl()"><div id="dl"></div>`;dl()}
async function dl(){const R=await api("recommendations?me="+me);if(!$("dl"))return;const q=$("q").value.toLowerCase(),L=R.filter(r=>U[r.v].n.toLowerCase().includes(q));
$("dl").innerHTML=L.map(({v,N,s,d})=>{const f=A[me].has(v);const btn=f?`<button class="p" onclick="oc(${v})">Chat</button>`:RQ.o.has(v)?`<button disabled>Requested</button>`:RQ.i.has(v)?`<button class="p" onclick="ac(${v})">Accept</button>`:`<button class="p" onclick="sd(${v})">Add friend</button>`;
return `<div class="card row"><div class="row" style="justify-content:flex-start"><div class="av">${face(v)}</div><div><b>${U[v].n}</b> ${chips(U[v].i)}<div class="m">${N.length?N.length+" mutual: "+N.map(z=>U[z].n).join(", ")+"; ":""}${s} shared interest(s); ${f?"connected":d?d+" hops away":"no path yet"}</div></div></div>${btn}</div>`}).join("")||`<p class="m">No one matches that name.</p>`}
async function sd(v){await api("request",{me,to:v});RQ.o.add(v);tip("Request sent to "+U[v].n);dl();setTimeout(sync,1800)}
async function ac(v){await api("accept",{me,from:v});tip("You’re now connected with "+U[v].n);last="";await sync()}
async function dc(v){await api("decline",{me,from:v});last="";await sync()}
function oc(v){cur=v;tab="c";app()}
function vr(){$("v").innerHTML=[...RQ.i].map(v=>`<div class="card row"><div class="row" style="justify-content:flex-start"><div class="av">${face(v)}</div><div><b>${U[v].n}</b> wants to connect<div class="m">${sh(me,v)} shared interest(s)</div></div></div><div><button class="p" onclick="ac(${v})">Accept</button> <button onclick="dc(${v})">Decline</button></div></div>`).join("")||`<p class="m">No pending requests. Send one from Discover.</p>`}
function vc(){const F=[...A[me]];if(!F.length){$("v").innerHTML=`<p class="m">Chat opens once a friend accepts your request.</p>`;return}if(!F.includes(cur))cur=F[0];
$("v").innerHTML=`<div class="card chat"><div>${F.map(f=>`<button style="width:100%;margin-bottom:6px;${f==cur?"border-color:var(--ac)":""}" onclick="cur=${f};vc()">${U[f].n}</button>`).join("")}</div><div><div class="row" style="justify-content:flex-start;margin-bottom:6px"><div class="av">${face(cur)}</div><b>${U[cur].n}</b></div><div class="msgs" id="ms">${(CH[cur]||[]).map(m=>`<div class="b ${m.f==me?"me":""}">${esc(m.t)}</div>`).join("")}</div><div class="row"><input id="mi" placeholder="Write a message" onkeydown="if(event.key=='Enter')sm()"><button class="p" onclick="sm()">Send</button></div></div></div>`;$("ms").scrollTop=1e9}
async function sm(){const t=$("mi").value.trim();if(!t)return;const c=cur;(CH[c]=CH[c]||[]).push({f:me,t});vc();$("mi").focus();await api("chat",{me,to:c,text:t});last=""}
/* ---------- graph lab ---------- */
async function vg(){if(dirty){lay();dirty=0}const G=await api("graph/stats"),o=U.map((u,i)=>`<option value="${i}">${u.n}</option>`).join(""),st=G.stats;
$("v").innerHTML=`<div class="card"><div class="g2">${st.map(s=>`<div class="s"><span class="m">${s[0]}</span><b>${s[1]}</b></div>`).join("")}</div></div>
<div class="card"><div class="g2"><div><span class="m">Source A</span><select id="ga">${o}</select></div><div><span class="m">Target B</span><select id="gb">${o}</select></div></div><div class="chips">${AL.map(a=>`<button onclick="run('${a[0]}')">${a[1]}</button>`).join("")}</div><div class="m">Edge weight w = 1 + number of interests the two people do not share.</div><pre id="out"></pre></div><svg id="gs" viewBox="0 0 600 420"></svg>
<div class="card"><details><summary>Adjacency list</summary><pre>${G.adj_list.join("\n")}</pre></details><details><summary>Adjacency matrix</summary><div class="sc"><table><tr><th></th>${U.map((_,i)=>`<th>${i}</th>`).join("")}</tr>${G.matrix.map((r,i)=>`<tr><th>${i}</th>${r.map(x=>`<td class="${x?"o":""}">${x}</td>`).join("")}</tr>`).join("")}</table></div></details></div>`;
$("ga").value=me;$("gb").value=0;hl={n:new Set,e:new Set,c:null};out="Pick an algorithm to run. You are the highlighted ring.";gr()}
function gr(){$("out").textContent=out;$("gs").innerHTML=draw()}
function draw(){const pal=["#7F77DD","#1D9E75","#D85A30","#378ADD","#D4537E","#BA7517","#639922","#888780"];
return E().map(([a,b])=>{const h=hl.e.has(key(a,b));return `<line x1="${P[a][0]}" y1="${P[a][1]}" x2="${P[b][0]}" y2="${P[b][1]}" stroke="${h?"#D85A30":"var(--bd)"}" stroke-width="${h?3.5:1.3}"/>`}).join("")+
U.map((u,i)=>{const c=hl.c?pal[hl.c[i]%8]:hl.n.has(i)?"#D85A30":null;return `<circle cx="${P[i][0]}" cy="${P[i][1]}" r="${i==me?11:9}" fill="${c||"var(--bb)"}" stroke="${i==me?"var(--tx)":"var(--ac)"}" stroke-width="${i==me?2.5:1.2}"/><text x="${P[i][0]}" y="${P[i][1]-13}" text-anchor="middle" font-size="10" fill="var(--tx)">${i==me?"You":u.n}</text>`}).join("")}
async function run(k){const r=await api(`graph/run?algo=${k}&a=${$("ga").value}&b=${$("gb").value}`);hl={n:new Set(r.nodes),e:new Set(r.edges.map(([x,y])=>key(x,y))),c:r.colors};out=r.out;gr()}
s0();
