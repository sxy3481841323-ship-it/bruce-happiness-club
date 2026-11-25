// Reactive single source of truth for Bruce Happiness Club

const STORAGE_KEY = "bruce_club_session_v1";

class GameStore {
  constructor() {
    this.state = {
      content: null,
      player: null, // { nickname, pin, owner, happiness }
      leaderboard: [],
      ticker: [],
      view: "map", // "map" | "home" | "street" | "shop"
      activeActivityId: null,
    };
    this.listeners = new Set();
  }

  subscribe(fn) {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  emit() {
    for (const fn of this.listeners) fn(this.state);
  }

  setContent(content) {
    this.state.content = content;
    this.emit();
  }

  setPlayer(player) {
    this.state.player = player;
    if (player) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        nickname: player.nickname,
        pin: player.pin,
        owner: player.owner,
      }));
    }
    this.emit();
  }

  loadSavedSession() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (_) {
      return null;
    }
  }

  setLeaderboardAndTicker(leaderboard, ticker) {
    if (Array.isArray(leaderboard)) this.state.leaderboard = leaderboard;
    if (Array.isArray(ticker)) this.state.ticker = ticker;
    this.emit();
  }

  setHappiness(nextValue) {
    if (!this.state.player) return;
    this.state.player = {
      ...this.state.player,
      happiness: Math.max(0, Math.min(9999, Math.round(nextValue))),
    };
    this.emit();
  }

  setView(view, activeActivityId = null) {
    this.state.view = view;
    this.state.activeActivityId = activeActivityId;
    this.emit();
  }

  isSulking() {
    return (this.state.player?.happiness ?? 100) < 80;
  }

  canAffordCheapestTreat() {
    return (this.state.player?.happiness ?? 0) >= 5;
  }
}

export const store = new GameStore();
