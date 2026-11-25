import { mountCinematicStage, activityIds, cinematicScenes } from './index.js';

const params = new URLSearchParams(location.search);
let activityId = activityIds.includes(params.get('activity'))
  ? params.get('activity')
  : 'home_brush';
let autoplay = params.get('autoplay') !== '0',
  tour = false,
  stage,
  tourTimer,
  revealTimer,
  content;
let happiness = [70, 85, 100].includes(Number(params.get('happiness')))
  ? Number(params.get('happiness'))
  : 100;
const $ = (s) => document.querySelector(s),
  container = $('#cinematic-stage');
const setTimer = (fn) => {
  clearTimeout(tourTimer);
  tourTimer = setTimeout(fn, 5500);
};

function mount({ lucky = false } = {}) {
  clearTimeout(tourTimer);
  clearTimeout(revealTimer);
  stage?.destroy();
  $('#empty').hidden = true;
  $('#catalog').open = false;
  $('#mode').textContent = autoplay ? '亲自互动' : '自动演出';
  $('#mode').setAttribute('aria-pressed', String(!autoplay));
  $('#happiness').value = String(happiness);
  $('#luck').disabled = cinematicScenes[activityId].swap === 0;
  for (const button of $('#scene-list').children)
    button.setAttribute('aria-current', String(button.dataset.activity === activityId));
  params.set('activity', activityId);
  params.set('autoplay', autoplay ? '1' : '0');
  params.set('happiness', String(happiness));
  history.replaceState(null, '', `?${params}`);
  stage = mountCinematicStage(container, {
    activityId,
    owner: 'Alex',
    happiness,
    content,
    autoplay,
    quality: params.get('quality') === 'low' ? 'low' : 'auto',
    ...(lucky ? { random: () => 0 } : {}),
    onComplete(result) {
      window.lastCinematicResult = result;
      $('#receipt').textContent =
        `试映回调：${result.outcome} / ${result.delta > 0 ? '+' : ''}${result.delta} / 换分候选 ${result.triggerSwapCandidate ? '是' : '否'}`;
      if (result.triggerSwapCandidate && lucky) {
        $('#receipt').textContent += '。换分数值使用明确标记的试映样例。';
        revealTimer = setTimeout(() => {
          stage?.revealSwap({
            oldScore: happiness + result.delta,
            newScore: 168,
            targetNickname: '试映样例',
            topBonus: false,
          });
        }, 400);
      }
      if (tour)
        setTimer(() => {
          activityId = activityIds[(activityIds.indexOf(activityId) + 1) % activityIds.length];
          mount();
        });
    },
    onExit() {
      clearTimeout(tourTimer);
      clearTimeout(revealTimer);
      stage = null;
      $('#empty').hidden = false;
    },
  });
  // Read-only diagnostics used by the independent browser QA; no game-state hook.
  window.cinematicPreview = {
    getSnapshot: () => stage?.getSnapshot(),
    destroy: () => {
      stage?.destroy();
      stage = null;
    },
    get stage() {
      return stage;
    },
  };
}

try {
  const response = await fetch(new URL('../../data/content.json', import.meta.url));
  if (!response.ok) throw new Error(`content.json (${response.status})`);
  content = await response.json();
  for (const id of activityIds) {
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.activity = id;
    button.textContent = cinematicScenes[id].title;
    button.addEventListener('click', () => {
      activityId = id;
      mount();
    });
    $('#scene-list').append(button);
  }
  $('#mode').addEventListener('click', () => {
    autoplay = !autoplay;
    mount();
  });
  $('#next').addEventListener('click', () => {
    activityId = activityIds[(activityIds.indexOf(activityId) + 1) % activityIds.length];
    mount();
  });
  $('#replay').addEventListener('click', () => mount());
  $('#return').addEventListener('click', () => mount());
  $('#luck').addEventListener('click', () => {
    autoplay = true;
    mount({ lucky: true });
  });
  $('#happiness').addEventListener('change', (e) => {
    happiness = Number(e.target.value);
    mount();
  });
  $('#tour').addEventListener('click', () => {
    tour = !tour;
    $('#tour').setAttribute('aria-pressed', String(tour));
    if (tour) {
      autoplay = true;
      mount();
    } else clearTimeout(tourTimer);
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') $('#catalog').open = false;
  });
  window.addEventListener('pagehide', () => {
    clearTimeout(tourTimer);
    clearTimeout(revealTimer);
    stage?.destroy();
  });
  mount();
} catch (error) {
  $('#empty').hidden = false;
  $('#empty h1').textContent = '还差一束光';
  $('#empty p').textContent = `未能加载本地文案：${error.message}。请通过本地 HTTP 服务打开此页。`;
  $('#return').hidden = true;
}
