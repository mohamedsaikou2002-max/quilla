'use strict';
const el = (id) => document.getElementById(id);
const native = window.QuillaNative;
const history = [];
let busy = false;
let hasConversation = false;
function tryParse(s){try{return JSON.parse(s);}catch(e){return {error:'Invalid response from bridge.'};}}
function showChat(){hasConversation=true;el('hero').hidden=true;el('chatview').hidden=false;}
function add(role,text){showChat();const bubble=document.createElement('div');bubble.className='message '+role;bubble.textContent=String(text);el('messages').appendChild(bubble);el('messages').scrollTop=el('messages').scrollHeight;return bubble;}
function setBusy(v){busy=v;el('send').disabled=v;el('prompt').disabled=v;}
function openSettings(){const d=el('settings');const s=tryParse(native.settings());el('endpoint').value=s.endpoint||'';el('token').value='';el('settingsResult').textContent='';d.showModal();}
function check(){el('connection').textContent='CHECKING LAPTOP…';native.status();}
window.QUILLA={
 onConfigured(data){const r=tryParse(data);el('settingsResult').textContent=r.error||'Saved. Testing laptop connection…';if(!r.error){check();}},
 onStatus(data){const r=tryParse(data);const up=Boolean(r.connected && r.modelLoaded);el('indicator').classList.toggle('up',up);el('indicator').setAttribute('aria-label',up?'Connected':'Disconnected');el('connection').textContent=up?'LM STUDIO CONNECTED · '+(r.model||'MODEL READY'):r.error||(!r.connected?'CANNOT REACH MODEL SERVER':'MODEL NOT LOADED');if(up)el('settings').close();},
 onChat(data){const r=tryParse(data);document.querySelector('.typing')?.remove();if(r.error){add('assistant error',r.error);}else{const reply=String(r.reply||'Empty response');add('assistant',reply);history.push({role:'assistant',content:reply});}setBusy(false);el('prompt').focus();}
};
el('settingsBtn').addEventListener('click',openSettings);
el('getStarted').addEventListener('click',openSettings);
el('closeSettings').addEventListener('click',()=>el('settings').close());
el('saveSettings').addEventListener('click',()=>native.configure(el('endpoint').value,el('token').value));
function send(){const text=el('prompt').value.trim();if(!text||busy)return;if(!tryParse(native.settings()).paired){openSettings();return;}add('user',text);history.push({role:'user',content:text.slice(0,4000)});el('prompt').value='';setBusy(true);const typing=add('assistant typing','QUILLA is thinking…');typing.classList.add('typing');native.chat(JSON.stringify({messages:history.slice(-20)}));}
el('send').addEventListener('click',send);
el('prompt').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
const stored=tryParse(native.settings());if(stored.paired){showChat();check();} else {el('connection').textContent='CONNECT YOUR LAPTOP TO BEGIN';}
