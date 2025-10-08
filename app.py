from flask import Flask, redirect, url_for, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask import get_flashed_messages # Thêm import này

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Cấu hình SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Bảng user
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))

# Tạo DB
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Lưu username vào session khi đăng nhập thành công
            session['username'] = user.username
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu!', 'error')
    
    # Lấy tên người dùng cuối cùng đã đăng ký để điền sẵn vào form login
    last_username = session.pop('last_username', '')
    # Truyền flash messages vào template login.html
    return render_template('login.html', last_username=last_username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        phone = request.form.get('phone')

        if password != confirm_password:
            flash('Mật khẩu xác nhận không trùng khớp. Mời điền lại!', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Tên người dùng đã tồn tại!', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email này đã được sử dụng!', 'error')
        else:
            new_user = User(username=username, password=password, email=email, phone=phone)
            db.session.add(new_user)
            db.session.commit()
            flash('Đăng ký thành công! Hãy đăng nhập!', 'success')
            session['last_username'] = username
            return redirect(url_for('login'))
            
    # Truyền flash messages vào template register.html
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    # Thêm get_flashed_messages() để thông báo được hiển thị
    messages = get_flashed_messages(with_categories=True)
    return render_template('dashboard.html', username=username, messages=messages)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Bạn đã đăng xuất!", 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
