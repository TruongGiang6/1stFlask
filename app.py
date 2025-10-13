from flask import Flask, redirect, url_for, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask import get_flashed_messages # Thêm import này
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Cấu hình SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Bảng user
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_id(self):
        return str(self.id)

# Bảng tin đăng
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    match_date = db.Column(db.String(50), nullable=False)
    skill_level = db.Column(db.String(50), nullable=False)
    time_frame = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Tạo DB
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_identity = request.form.get('login_identity')
        password = request.form.get('password')
        
        user = User.query.filter((User.username == login_identity) | (User.email == login_identity)).first()
        
        if user and user.password == password:
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Sai thông tin đăng nhập hoặc mật khẩu!', 'error')
            session['last_username'] = login_identity # Giữ lại thông tin đã nhập
            return redirect(url_for('home', _anchor='login'))
            
    # Nếu là GET request, chuyển về trang chủ và mở modal
    return redirect(url_for('home', _anchor='login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # ... (xử lý đăng ký)
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
            return redirect(url_for('home', _anchor='login')) # Chuyển hướng về home và mở modal login
        
        # Nếu đăng ký lỗi, quay lại trang chủ và mở lại modal đăng ký
        return redirect(url_for('home', _anchor='register'))

    # Nếu là GET request, chỉ hiển thị trang
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    username = current_user.username if current_user.is_authenticated else None
    messages = get_flashed_messages(with_categories=True)
    return render_template('dashboard.html', username=username, messages=messages)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Bạn đã đăng xuất!", 'success')
    return redirect(url_for('login'))

@app.route('/find_opponent', methods=['GET', 'POST'])
@login_required
def find_opponent():
    if request.method == 'POST':
        # Xử lý dữ liệu form ở đây
        title = request.form.get('title')
        location = request.form.get('location')
        match_date = request.form.get('match_date')
        skill_level = request.form.get('skill_level')
        time_frame = request.form.get('time_frame')
        notes = request.form.get('notes')
        
        new_post = Post(
            title=title,
            location=location,
            match_date=match_date,
            skill_level=skill_level,
            time_frame=time_frame,
            notes=notes,
            user_id=current_user.id,
            username=current_user.username
        )
        db.session.add(new_post)
        db.session.commit()
        
        flash(f'Đã đăng tin "{title}" thành công!', 'success')
        return redirect(url_for('find_opponent'))

    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('find_opponent.html', posts=posts)

@app.route('/find_match')
@login_required
def find_match():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('find_match.html', posts=posts)

@app.route('/map')
@login_required
def map_view():
    return render_template('map_view.html')

@app.route('/find_team')
@login_required
def find_team():
    return render_template('find_team.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
