// static/js/currentevent-notifs.js
console.log('⏱ current-event notifications script loaded');

const PREF_KEY = 'cg_notifs';
const LAST_KEY = 'cg_last_notif_start';

// Load user preference (default = enabled)
let notifEnabled = localStorage.getItem(PREF_KEY) !== 'false';

// If notifications are denied, force-disable
if ('Notification' in window && Notification.permission === 'denied') {
  notifEnabled = false;
  localStorage.setItem(PREF_KEY, 'false');
}

// Given a minute-of-hour, compute the next start Date
function nextStartDate(minute) {
  const now = new Date();
  const d   = new Date(now);
  d.setMinutes(minute, 0, 0);
  if (d <= now) d.setHours(d.getHours() + 1);
  return d;
}

// Minutes until that next start
function minutesUntilStart(minute) {
  const now   = new Date();
  const start = nextStartDate(minute);
  const diff  = start - now;
  return diff <= 0 ? 0 : Math.ceil(diff / 60000);
}

// Fetch payload and conditionally notify
async function fetchAndNotify() {
  if (!notifEnabled || Notification.permission !== 'granted') return;
  try {
    const res     = await fetch('/api/currentevent');
    const { current } = await res.json();
    const startTs = nextStartDate(current.start.minute).getTime();
    const lastTs  = parseInt(localStorage.getItem(LAST_KEY), 10) || 0;
    const mins    = minutesUntilStart(current.start.minute);

    // Only notify if:
    //  • more than 0 minutes remain
    //  • AND this start timestamp is new
    if (mins > 0 && startTs !== lastTs) {
      new Notification('Grow a Garden Tracker', {
        body: `${current.name} starts in ${mins} m`,
        icon: current.icon
      });
      localStorage.setItem(LAST_KEY, startTs);
    }
  } catch (err) {
    console.error('[currentevent-notifs] fetch error', err);
  }
}

// Kick off immediately if already granted, then every minute
if (Notification.permission === 'granted') {
  fetchAndNotify();
  setInterval(fetchAndNotify, 60_000);
}

// Export helper for use after user grants permission
export function startCurrentEventNotifs() {
  if (Notification.permission === 'granted' && notifEnabled) {
    fetchAndNotify();
    setInterval(fetchAndNotify, 60_000);
  }
}
