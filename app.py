from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import sqlite3
from translations import translations

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your-secret-key-here-change-it'

DB_PATH = 'restaurant.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_ar TEXT,
            name_fr TEXT,
            description TEXT,
            description_ar TEXT,
            description_fr TEXT,
            price REAL NOT NULL,
            category TEXT,
            image TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            guests INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES menu(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loyalty_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT UNIQUE NOT NULL,
            points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT,
            quantity INTEGER DEFAULT 1,
            total REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES menu(id)
        )
    ''')

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def add_notification(message):
    conn = get_db()
    conn.execute('INSERT INTO notifications (message) VALUES (?)', (message,))
    conn.commit()
    conn.close()


@app.context_processor
def inject_globals():
    lang = session.get('lang', 'en')
    conn = get_db()
    unread = conn.execute('SELECT COUNT(*) FROM notifications WHERE is_read = 0').fetchone()[0]
    conn.close()
    return dict(t=translations[lang], current_lang=lang, unread_notifications=unread)


@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in translations:
        session['lang'] = lang
    return redirect(request.referrer or url_for('home'))


@app.route('/')
def home():
    conn = get_db()
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    lang = session.get('lang', 'en')

    if search:
        items = conn.execute(
            "SELECT * FROM menu WHERE name LIKE ? OR name_ar LIKE ? OR name_fr LIKE ?",
            (f'%{search}%', f'%{search}%', f'%{search}%')
        ).fetchall()
    elif category:
        items = conn.execute(
            "SELECT * FROM menu WHERE category = ?", (category,)
        ).fetchall()
    else:
        items = conn.execute('SELECT * FROM menu').fetchall()

    categories = conn.execute('SELECT DISTINCT category FROM menu').fetchall()
    conn.close()

    return render_template('index.html', items=items, categories=categories, search=search, current_category=category, lang=lang)


@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        date = request.form['date']
        time = request.form['time']
        guests = request.form['guests']
        conn = get_db()
        conn.execute(
            'INSERT INTO reservations (name, phone, date, time, guests) VALUES (?, ?, ?, ?, ?)',
            (name, phone, date, time, guests)
        )
        conn.execute('''
            INSERT INTO loyalty_points (customer_name, points) VALUES (?, 5)
            ON CONFLICT(customer_name) DO UPDATE SET points = points + 5
        ''', (name,))
        conn.commit()
        conn.close()
        add_notification(f"New reservation from {name}")
        return redirect(url_for('reserve_success'))
    return render_template('reserve.html')


@app.route('/reserve/success')
def reserve_success():
    return render_template('reserve_success.html')


@app.route('/order/<int:product_id>', methods=['GET', 'POST'])
def order(product_id):
    conn = get_db()
    product = conn.execute('SELECT * FROM menu WHERE id = ?', (product_id,)).fetchone()

    if not product:
        conn.close()
        return "Product not found", 404

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        phone = request.form['phone']
        quantity = int(request.form['quantity'])
        total = product['price'] * quantity

        conn.execute('''
            INSERT INTO orders (product_id, customer_name, phone, quantity, total)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, customer_name, phone, quantity, total))
        conn.commit()
        conn.close()

        add_notification(f"New order from {customer_name}: {product['name']} x{quantity}")

        return render_template('order_success.html', product=product, customer_name=customer_name, quantity=quantity, total=total)

    conn.close()
    return render_template('order.html', product=product)


@app.route('/reviews')
def reviews():
    conn = get_db()
    reviews = conn.execute('SELECT * FROM reviews ORDER BY created_at DESC').fetchall()
    avg = conn.execute('SELECT AVG(rating) FROM reviews').fetchone()[0]
    conn.close()
    avg = round(avg, 1) if avg else 0
    return render_template('reviews.html', reviews=reviews, avg=avg)


@app.route('/review', methods=['GET', 'POST'])
def add_review():
    if request.method == 'POST':
        name = request.form['name']
        rating = int(request.form['rating'])
        comment = request.form['comment']
        conn = get_db()
        conn.execute(
            'INSERT INTO reviews (name, rating, comment) VALUES (?, ?, ?)',
            (name, rating, comment)
        )
        conn.commit()
        conn.close()
        add_notification(f"New restaurant review from {name}")
        return redirect(url_for('reviews'))
    return render_template('add_review.html')


@app.route('/product_reviews')
def product_reviews():
    conn = get_db()
    items = conn.execute('''
        SELECT menu.id, menu.name, menu.name_ar, menu.name_fr, menu.image,
               AVG(product_reviews.rating) as avg_rating,
               COUNT(product_reviews.id) as review_count
        FROM menu
        LEFT JOIN product_reviews ON menu.id = product_reviews.product_id
        GROUP BY menu.id
    ''').fetchall()
    conn.close()
    return render_template('product_reviews.html', items=items)


@app.route('/product_review/<int:product_id>', methods=['GET', 'POST'])
def add_product_review(product_id):
    conn = get_db()
    if request.method == 'POST':
        name = request.form['name']
        rating = int(request.form['rating'])
        comment = request.form['comment']
        conn.execute(
            'INSERT INTO product_reviews (product_id, name, rating, comment) VALUES (?, ?, ?, ?)',
            (product_id, name, rating, comment)
        )
        conn.commit()
        conn.close()
        add_notification(f"New dish review from {name}")
        return redirect(url_for('product_reviews'))

    product = conn.execute('SELECT * FROM menu WHERE id = ?', (product_id,)).fetchone()
    reviews = conn.execute('SELECT * FROM product_reviews WHERE product_id = ? ORDER BY created_at DESC', (product_id,)).fetchall()
    conn.close()
    return render_template('add_product_review.html', product=product, reviews=reviews)


@app.route('/loyalty', methods=['GET', 'POST'])
def loyalty():
    if request.method == 'POST':
        name = request.form['name']
        conn = get_db()
        customer = conn.execute('SELECT * FROM loyalty_points WHERE customer_name = ?', (name,)).fetchone()
        if not customer:
            conn.execute('INSERT INTO loyalty_points (customer_name, points) VALUES (?, 0)', (name,))
            conn.commit()
            customer = conn.execute('SELECT * FROM loyalty_points WHERE customer_name = ?', (name,)).fetchone()
        conn.close()
        return render_template('loyalty.html', customer=customer, searched=True)
    return render_template('loyalty.html', searched=False)


@app.route('/loyalty/add', methods=['POST'])
def add_loyalty_points():
    name = request.form['name']
    points = int(request.form['points'])
    conn = get_db()
    conn.execute('''
        INSERT INTO loyalty_points (customer_name, points) VALUES (?, ?)
        ON CONFLICT(customer_name) DO UPDATE SET points = points + ?
    ''', (name, points, points))
    conn.commit()
    conn.close()
    return redirect(url_for('loyalty'))


@app.route('/notifications')
def notifications():
    conn = get_db()
    notifs = conn.execute('SELECT * FROM notifications ORDER BY created_at DESC LIMIT 20').fetchall()
    conn.execute('UPDATE notifications SET is_read = 1')
    conn.commit()
    conn.close()
    return render_template('notifications.html', notifications=notifs)


@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js', mimetype='application/javascript')


@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/json')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)