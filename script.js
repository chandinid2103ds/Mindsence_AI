const $=s=>document.querySelector(s), $$=s=>document.querySelectorAll(s);
addEventListener('load',()=>setTimeout(()=>$('#loader').classList.add('done'),500));
const io=new IntersectionObserver(es=>es.forEach(e=>e.isIntersecting&&e.target.classList.add('visible')),{threshold:.12});
$$('.reveal').forEach(x=>io.observe(x));

const labels={calm:'Calm',positive:'Positive',warm:'Warmth',balanced:'Balance',alert:'Alertness'};
function theme(t){document.body.dataset.theme=t;$('#theme').textContent=labels[t];localStorage.theme=t}
$$('.color').forEach(x=>x.onclick=()=>theme(x.dataset.theme));
if(localStorage.theme)theme(localStorage.theme);

$('#login').onclick=()=>$('#modal').classList.add('open');
$('#close').onclick=()=>$('#modal').classList.remove('open');
$('#modal').onclick=e=>{if(e.target.id==='modal')$('#modal').classList.remove('open')};
$('#go').onclick=()=>{if(!$('#email').value.trim()||!$('#pass').value.trim())return alert('Enter any demo username/email and password.');$('#modal').classList.remove('open');alert('Demo login successful! Connect this UI to Flask authentication for the full application.')};

const qs=[
['How would you describe your mental well-being this week?',['Very good','Good','Okay','Low','Very low']],
['How would you rate your stress this week?',['0 — No stress','1','2','3','4','5 — Very high']],
['How many hours do you usually sleep?',['Less than 4','4–5 hours','5–6 hours','6–7 hours','7–8 hours','More than 8']],
['How motivated have you felt?',['Very high','High','Moderate','Low','Very low']],
['How connected do you feel to people you trust?',['Very connected','Connected','Neutral','Somewhat isolated','Very isolated']]
];
let n=0,vals=[];
function render(){let [q,os]=qs[n];$('#q').innerHTML='<span style="font-size:9px;color:#999">0'+(n+1)+'</span><h3>'+q+'</h3>';$('#opts').innerHTML=os.map((x,i)=>`<button data-i="${i}">${x}</button>`).join('');$('#qcount').textContent=`Question ${n+1} of ${qs.length}`;$('#pct').textContent=Math.round((n+1)/qs.length*100)+'%';$('#bar').style.width=((n+1)/qs.length*100)+'%';$$('#opts button').forEach(b=>b.onclick=()=>{vals[n]=+b.dataset.i;$$('#opts button').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');setTimeout(()=>{if(n<qs.length-1){n++;render()}else finish()},250)})}
function finish(){let wellness=vals[0]??2,stress=vals[1]??3,sleep=vals[2]??3,mot=vals[3]??2,con=vals[4]??2;let score=Math.max(25,Math.min(95,Math.round(100-(wellness*8)-(stress*5)+(sleep*4)+(mot*5)+(con*4))));$('#score').textContent=score;$('#stress').textContent=stress<2?'Low':stress<4?'Moderate':'High';$('#sleep').textContent=sleep<2?'< 5 h':sleep===2?'5–6 h':sleep===3?'6–7 h':'7+ h';$('#mot').textContent=mot<2?'Low':mot===2?'Moderate':'Good';$('#connect').textContent=con<2?'Needs support':con===2?'Neutral':'Good';let t=stress>=4?'balanced':wellness>=3&&mot>=3?'positive':mot<=1?'calm':'balanced';theme(t);let st=score>=75?'Positive':score>=60?'Balanced':score>=45?'Needs attention':'Low wellness';$('#state').textContent=st;$('#result').textContent=score>=60?'Your reported pattern looks fairly balanced.':'Some areas may deserve a little more attention.';document.querySelector('#insights').scrollIntoView({behavior:'smooth'})}
render();
