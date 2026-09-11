'use strict';
const el = id => document.getElementById(id);
const role = document.querySelector('main').dataset.role;
const key = 'callgate-' + role;
const fragment = new URLSearchParams(location.hash.slice(1)).get('token');
if (fragment) {
  sessionStorage.setItem(key, fragment);
  history.replaceState(null, '', location.pathname);
}
const token = sessionStorage.getItem(key);
const stateNames = {UNVERIFIED:'继续听，身份尚未核实', CHALLENGED:'先核验，再操作',
  COOLING_OFF:'暂停操作，独立核验', BLOCKED:'不要分享敏感信息'};
const outcomeText = result => result.status === 'simulated_action_completed'
  ? '仅本次模拟操作已完成。没有发生真实转账。'
  : result.status === 'reviewer_denied' ? '核验者已拒绝，模拟操作未执行。' : '尚无完成结果。';
async function api(path, body) {
  if (!token) throw new Error('缺少入口凭据，请使用启动程序显示的完整链接。');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  let response;
  try {
    response = await fetch(path, {method:body === undefined ? 'GET' : 'POST',
      headers:{Authorization:'Bearer ' + token, 'Content-Type':'application/json'},
      ...(body === undefined ? {} : {body:JSON.stringify(body)}), cache:'no-store', signal:controller.signal});
  } catch (_) {
    throw new Error('服务未连接或响应超时。结果尚未确认，请刷新结果；系统不会自动重试批准。');
  } finally { clearTimeout(timer); }
  if (!response.ok) {
    if (response.status === 401) throw new Error('此入口凭据无效。请检查是否打开了正确角色的链接。');
    if (response.status === 409) throw new Error('当前状态不允许操作，或请求已经变化、过期、使用。请刷新核对。');
    if (response.status === 422) throw new Error('请检查目标、金额或台词格式。');
    throw new Error('确认服务不可用或结果未确认。请刷新查看，系统不会自动重试批准。');
  }
  return response.json();
}
function action(id, fn) {
  el(id).onclick = async () => {
    el(id).disabled = true;
    try { await fn(); } catch (error) { el('status').textContent = error.message; }
    finally { el(id).disabled = false; }
  };
}
if (role === 'participant') {
  let audio = null;
  const closeAudio = s => {
    s?.stream?.getTracks().forEach(track => track.stop());
    s?.source?.disconnect(); s?.node?.disconnect();
    if (s?.context && s.context.state !== 'closed') s.context.close().catch(() => {});
    el('level').value = 0;
  };
  const finishAudio = message => {
    const s = audio; if (!s) return;
    clearTimeout(s.limitTimer);
    clearTimeout(s.drainTimer);
    closeAudio(s); s.ws?.close(); audio = null;
    el('start-audio').disabled = false; el('stop-audio').disabled = true;
    el('audio-status').textContent = message;
  };
  const showRisk = result => {
    el('challenge').textContent = '';
    el('risk').textContent = stateNames[result.state] + ' · 风险参考分 ' + result.score + '/100';
    const explanations={UNVERIFIED:'没有检测到需要批准的高影响操作，因此不生成挑战码。',
      CHALLENGED:'检测到可二次确认的高影响操作；可以提交并生成一次性挑战码。',
      COOLING_OFF:'高影响请求伴随保密施压；必须暂停，不能通过确认立即放行。',
      BLOCKED:'检测到密码或验证码请求；这类操作不能通过确认放行。'};
    el('policy-explanation').textContent=explanations[result.state];
    el('status').textContent = '风险状态已更新；先前的待确认请求已失效。';
  };
  const refreshMetrics = async () => {
    const m=await api('/api/metrics/summary');
    if (!m.sessions) { el('metrics-summary').textContent='本次服务启动后尚无完整测试。'; return; }
    const pct=m.failure_rate === null ? '暂无可用分母' : (100*m.failure_rate).toFixed(1)+'%';
    const latency=m.alert_samples ? '提醒代理值 P50 '+m.alert_proxy_p50_ms.toFixed(1)+' ms，P95 '+
      m.alert_proxy_p95_ms.toFixed(1)+' ms' : '尚无风险提醒样本';
    el('metrics-summary').textContent='最近 '+m.sessions+' 次，完成 '+m.completed+'，失败 '+m.failed+
      '，取消 '+m.cancelled+'，断开 '+m.disconnected+'；失败率 '+pct+'（分母 '+m.failure_denominator+
      '）；'+latency+'（有效样本 '+m.alert_samples+'）。';
  };
  action('refresh-metrics', refreshMetrics);
  const download = (name, data) => {
    const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)], {type:'application/json'}));
    const link=document.createElement('a'); link.href=url; link.download=name;
    document.body.append(link); link.click(); link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  action('export-metrics', async () => download('callgate-measurements.json', await api('/api/metrics/export')));
  action('export-receipt', async () => download('callgate-receipt.json', await api('/api/receipt', {})));
  action('inspect-evidence', async () => {
    const view=await api('/api/evidence');
    el('evidence-summary').textContent='当前来源图：'+view.graph.nodes.length+' 个节点、'+view.graph.edges.length+
      ' 条关系。计分项：'+(view.contributions.map(c=>c.kind+' '+c.weight).join(' + ') || '无')+
      '；总分 '+view.score+'（上限 100，非概率）。当前状态 '+view.state+
      '；锁定状态可能源自之前的证据。';
  });
  action('consent', async () => {
    await api('/api/processing-consent', {granted:true});
    el('consent-status').textContent = '本次会话已允许处理测试内容。';
    el('status').textContent = '可以提交虚构或已同意的测试台词。';
  });
  action('decline', async () => {
    const previous=audio;
    if (previous) closeAudio(previous);
    try { await api('/api/processing-consent', {granted:false}); }
    finally { if (previous && audio===previous) finishAudio('麦克风已关闭。'); }
    el('consent-status').textContent = '处理已停止，本次风险证据和待核验操作已清除。';
    el('challenge').textContent = '';
    el('risk').textContent = '尚未分析';
    el('live-transcript').textContent='已清除实时转录。';
    el('evidence-summary').textContent='当前证据已清除。';
    el('status').textContent = '没有待确认请求，未执行操作。';
  });
  action('new-session', async () => {
    const previous=audio;
    if (previous) closeAudio(previous);
    try { await api('/api/session/reset', {}); }
    finally { if (previous && audio===previous) finishAudio('麦克风已关闭。'); }
    el('consent-status').textContent='新测试尚未取得处理同意。';
    el('challenge').textContent=''; el('risk').textContent='尚未分析';
    el('live-transcript').textContent='尚无实时转录。';
    el('evidence-summary').textContent='新会话尚无证据。';
    el('policy-explanation').textContent='请重新取得同意后开始新的独立测试。';
    el('status').textContent='新会话已创建；旧证据、挑战和结果均已清除。';
  });
  action('ingest', async () => {
    const result = await api('/api/transcript', {segment_id:'s' + crypto.randomUUID(),
      text:el('transcript').value, start_ms:0, end_ms:1000, final:true});
    showRisk(result);
  });
  el('start-audio').onclick = async () => {
    if (audio) return;
    const s = {turns:new Map()}; audio = s; el('start-audio').disabled = true;
    el('live-transcript').textContent='等待语音服务返回转录…';
    el('audio-status').textContent = '正在请求麦克风权限…';
    try {
      const status=await api('/api/status');
      if (audio !== s) return;
      if (!status.processing_allowed) { finishAudio('请先明确允许处理本次测试内容。'); return; }
      s.stream = await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,
        echoCancellation:true,noiseSuppression:true},video:false});
      if (audio !== s) { closeAudio(s); return; }
      s.context = new AudioContext({sampleRate:16000});
      if (s.context.sampleRate !== 16000) throw new Error('sample-rate');
      await s.context.audioWorklet.addModule('/pcm-worklet.js');
      if (audio !== s) { closeAudio(s); return; }
      s.ws = new WebSocket(`ws://${location.host}/api/audio`);
      await new Promise((resolve,reject) => {
        const timer=setTimeout(()=>reject(new Error('timeout')),10000);
        s.ws.onopen=()=>{clearTimeout(timer);s.ws.send(JSON.stringify({type:'authenticate',token}));resolve();};
        s.ws.onerror=()=>{clearTimeout(timer);reject(new Error('connect'));};
        s.ws.onclose=()=>{clearTimeout(timer);reject(new Error('closed'));};
      });
      if (audio !== s) { closeAudio(s); s.ws.close(); return; }
      s.ws.onmessage = ({data}) => {
        if (audio !== s) return;
        const message=JSON.parse(data);
        if (message.error === 'processing_stopped') { finishAudio('处理已停止，麦克风已关闭。'); return; }
        if (message.error) { finishAudio(message.error === 'processing_consent_required'
          ? '请先明确允许处理本次测试内容。' : message.error === 'assemblyai_not_configured'
          ? '语音服务尚未配置；可使用文本备用输入。' : '语音服务连接失败；可使用文本备用输入。'); return; }
        if (message.type === 'completed') { finishAudio('语音测试完成。'); refreshMetrics().catch(()=>{}); return; }
        if (message.metrics) {
          const m=message.metrics;
          const cost=m.estimated_asr_cost_usd === null ? '未配置 ASR 单价' : 'ASR 估算 $'+m.estimated_asr_cost_usd;
          el('metrics').textContent='已接收音频 '+(m.audio_received_ms/1000).toFixed(2)+' 秒；本地风险引擎 '+
            m.risk_engine_ms+' ms；提醒代理值 '+(m.end_of_speech_to_alert_proxy_ms === null ?
            '暂无有效时间戳' : m.end_of_speech_to_alert_proxy_ms+' ms')+
            '；服务连接 '+(m.provider_connect_ms == null ? '未测量' : m.provider_connect_ms.toFixed(1)+' ms')+
            '；首段转录等待 '+(m.provider_first_transcript_ms == null ? '未测量' : m.provider_first_transcript_ms.toFixed(1)+' ms')+
            '（含说话与服务缓冲，非纯推理耗时）；'+cost+'。';
        }
        if (message.transcript) {
          s.turns.set(message.transcript.segment_id, message.transcript);
          el('live-transcript').replaceChildren();
          for (const turn of s.turns.values()) {
            const line=document.createElement('div'); line.textContent=turn.text;
            el('live-transcript').append(line);
          }
        }
        if (message.risk) showRisk(message.risk);
      };
      s.ws.onclose=()=>{ if(audio===s) finishAudio('语音连接已关闭。'); };
      s.source=s.context.createMediaStreamSource(s.stream);
      s.node=new AudioWorkletNode(s.context,'pcm-recorder');
      s.node.port.onmessage=({data})=>{
        if (audio !== s || s.stopping) return;
        if(data.level!==undefined) el('level').value=data.level;
        if(data.pcm && s.ws.readyState===WebSocket.OPEN) {
          if (s.ws.bufferedAmount > 64000) { finishAudio('发送拥堵，麦克风已关闭。'); return; }
          s.ws.send(data.pcm);
        }
      };
      s.source.connect(s.node); s.node.connect(s.context.destination);
      el('stop-audio').disabled=false; el('audio-status').textContent='正在处理语音；说完后点击停止。';
      s.limitTimer=setTimeout(()=>{if(audio===s) el('stop-audio').click();},60000);
    } catch (_) { if (audio === s) finishAudio('无法启动麦克风；请允许权限或使用文本备用输入。'); }
  };
  el('stop-audio').onclick = () => {
    const s=audio; if(!s) return;
    s.stopping=true; clearTimeout(s.limitTimer);
    s.stream?.getTracks().forEach(track=>track.stop());
    if(s.ws?.readyState===WebSocket.OPEN) s.ws.send('{"type":"stop"}');
    closeAudio(s);
    el('stop-audio').disabled=true; el('audio-status').textContent='正在等待最后的转录…';
    s.drainTimer=setTimeout(()=>{if(audio===s) finishAudio('最后转录等待超时，已关闭麦克风。');},15000);
  };
  window.addEventListener('pagehide', ()=>{if(audio) finishAudio('页面已关闭。');});
  action('request', async () => {
    const result = await api('/api/request', {destination:el('destination').value, amount_cents:Number(el('amount').value)});
    el('challenge').textContent = '一次性挑战码：' + result.out_of_band_challenge + '。请通过演示之外的第二条渠道告诉核验者。';
    el('status').textContent = '等待核验者核对操作并输入挑战码。当前未执行操作。';
  });
  action('refresh', async () => {
    const result = await api('/api/status');
    el('status').textContent = result.outcome ? outcomeText(result.outcome) : result.pending
      ? '仍等待核验，未执行操作；过期请求需要重新提交。' : '没有当前确认请求，未执行操作。';
  });
} else {
  let pending = null;
  let busy = false;
  const disable = () => { el('approve').disabled = busy || !pending; el('deny').disabled = busy || !pending; };
  action('refresh', async () => {
    pending = null; disable();
    el('operation').textContent = '正在读取…'; el('expiry').textContent = '';
    const bundle = await api('/api/pending');
    if (!bundle) { el('operation').textContent = '没有待确认请求。'; return; }
    pending = bundle.request;
    el('operation').textContent = '目标：' + bundle.operation.destination + '\n金额：' +
      (bundle.operation.amount_cents / 100).toFixed(2) + ' USD\n会话：' + pending.session_id;
    el('expiry').textContent = '有效至：' + new Date(pending.expires_at * 1000).toLocaleTimeString();
    el('status').textContent = '核对金额和目标后，再明确选择。';
    disable();
  });
  for (const [id, approved] of [['approve', true], ['deny', false]]) {
    el(id).onclick = async () => {
      if (!pending || busy) return;
      busy = true; disable();
      try {
        const challenge = approved ? el('challenge-response').value.trim() : null;
        if (approved && !/^\d{6}$/.test(challenge)) throw new Error('批准前请输入请求人通过另一条渠道提供的六位挑战码。');
        const result = await api('/api/decide', {request_id:pending.request_id, approved,
          challenge_response:challenge});
        el('status').textContent = outcomeText(result);
      } catch (error) { el('status').textContent = error.message; }
      finally { pending = null; busy = false; disable(); }
    };
  }
}
if (token) el('status').textContent = '入口已就绪。请按页面步骤继续。';
