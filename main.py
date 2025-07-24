import os
import logging
import requests

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    make_response,
)

# ── App Setup ──
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "you-should-set-this")

# Enable development debugging
app.debug = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ── Logging ──
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GrowAGardenSite")

# ── Visitor Counter ──
VISIT_COUNT_FILE = os.path.join(app.root_path, 'visit_count.txt')


def read_visit_count():
    if not os.path.exists(VISIT_COUNT_FILE):
        return 0
    with open(VISIT_COUNT_FILE, 'r') as f:
        try:
            return int(f.read().strip() or 0)
        except ValueError:
            return 0


def get_and_increment_visit_count():
    count = read_visit_count()
    count += 1
    with open(VISIT_COUNT_FILE, 'w') as f:
        f.write(str(count))
    return count


# ── JoshLei API Setup ──
JOSHLEI_BASE = 'https://api.joshlei.com/v2/growagarden'
info_data_cache = {}


def load_info_data():
    try:
        resp = requests.get(f'{JOSHLEI_BASE}/info/', timeout=5)
        resp.raise_for_status()
        items = resp.json()
        logger.info("✅ Loaded /info data with %d items", len(items))
        return {item['item_id']: item for item in items}
    except requests.RequestException as e:
        logger.error("❌ Failed to load /info: %s", e)
        return {}


# ── Routes ──
@app.route('/')
def home():
    # Only increment on the very first visit
    already_visited = request.cookies.get('visited') == 'yes'
    if not already_visited:
        visitor_count = get_and_increment_visit_count()
    else:
        visitor_count = read_visit_count()

    resp = make_response(render_template('home.html', visitor_count=visitor_count))
    if not already_visited:
        resp.set_cookie('visited', 'yes', max_age=60*60*24*365)
    return resp


@app.route('/stock')
def stock():
    return render_template('stock.html')


@app.route('/weather')
def weather():
    return render_template('weather.html')


@app.route('/traveling')
def traveling():
    return render_template('traveling.html')


@app.route('/announcement')
def announcement():
    return render_template('announcement.html')


@app.route('/currentevent')
def currentevent():
    return render_template('currentevent.html')


# ── API Proxies ──
@app.route('/api/currentevent')
def get_currentevent():
    try:
        logger.info("🔔 Fetching /currentevent from API")
        resp = requests.get(f'{JOSHLEI_BASE}/currentevent', timeout=5)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        logger.error("❌ Failed to fetch /currentevent: %s", e)
        return jsonify({'error': 'Failed to fetch current event', 'details': str(e)}), 502


@app.route('/api/stock')
def get_stock():
    try:
        logger.info("📦 Fetching /stock from API")
        resp = requests.get(f'{JOSHLEI_BASE}/stock', timeout=5)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        logger.error("❌ Failed to fetch /stock: %s", e)
        return jsonify({'error': 'Failed to fetch stock', 'details': str(e)}), 502


@app.route('/api/weather')
def get_weather():
    try:
        logger.info("🌦️ Fetching /weather from API")
        resp = requests.get(f'{JOSHLEI_BASE}/weather', timeout=5)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        logger.error("❌ Failed to fetch /weather: %s", e)
        return jsonify({'error': 'Failed to fetch weather', 'details': str(e)}), 502


@app.route('/api/info')
def get_info():
    global info_data_cache
    if not info_data_cache:
        info_data_cache = load_info_data()
    return jsonify(info_data_cache)


# ── Entry Point ──
def run():
    port = int(os.environ.get('PORT', 3000))
    logger.info(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    run()
