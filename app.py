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
    pitch = db.Column(db.String(100), nullable=False)
    match_date = db.Column(db.String(50), nullable=False)
    skill_level = db.Column(db.String(50), nullable=False)
    time_frame = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='open')
    ratings = db.relationship('Rating', backref='post', lazy=True)

# Bảng đánh giá
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rated_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define relationships to get user objects
    rater = db.relationship('User', foreign_keys=[rater_id])
    rated_user = db.relationship('User', foreign_keys=[rated_user_id])

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
        pitch = request.form.get('pitch')
        match_date = request.form.get('match_date')
        skill_level = request.form.get('skill_level')
        time_frame = request.form.get('time_frame')
        notes = request.form.get('notes')
        
        new_post = Post(
            title=title,
            location=location,
            pitch=pitch,
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

    # Lấy các bài đăng của riêng người dùng hiện tại
    posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.id.desc()).all()
    
    # Lấy các đánh giá liên quan đến các bài đăng này
    post_ids = [post.id for post in posts]
    ratings = Rating.query.filter(Rating.post_id.in_(post_ids), Rating.rater_id == current_user.id).all()
    ratings_by_post = {rating.post_id: rating for rating in ratings}

    return render_template('find_opponent.html', posts=posts, ratings=ratings_by_post)

@app.route('/find_match')
@login_required
def find_match():
    posts = Post.query.filter_by(status='open').order_by(Post.id.desc()).all()
    return render_template('find_match.html', posts=posts)

@app.route('/map')
@login_required
def map_view():
    return render_template('map_view.html')

@app.route('/find_team')
@login_required
def find_team():
    return render_template('find_team.html')

@app.route('/admin')
@login_required
def admin():
    if current_user.username != 'admin':
        flash('Bạn không có quyền truy cập trang này!', 'error')
        return redirect(url_for('dashboard'))
    
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('admin.html', posts=posts)

@app.route('/admin/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    if current_user.username != 'admin':
        flash('Bạn không có quyền thực hiện hành động này!', 'error')
        return redirect(url_for('admin'))
        
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash(f'Đã xóa bài đăng "{post.title}".', 'success')
    return redirect(url_for('admin'))

@app.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_user_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('Bạn không có quyền xóa bài đăng này!', 'error')
        return redirect(url_for('find_opponent'))
    
    db.session.delete(post)
    db.session.commit()
    flash(f'Đã xóa bài đăng "{post.title}".', 'success')
    return redirect(url_for('find_opponent'))

@app.route('/post/close/<int:post_id>', methods=['POST'])
@login_required
def close_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('Bạn không có quyền đóng bài đăng này!', 'error')
        return redirect(url_for('find_opponent'))
    
    post.status = 'closed'
    db.session.commit()
    flash(f'Đã đóng tin "{post.title}". Giờ bạn có thể đánh giá đối thủ.', 'success')
    return redirect(url_for('find_opponent'))

@app.route('/rate_opponent/<int:post_id>', methods=['POST'])
@login_required
def rate_opponent(post_id):
    post = Post.query.get_or_404(post_id)
    # The user being rated is the author of the post
    rated_user_id = post.user_id
    
    # Check if the current user has already rated this post/opponent
    existing_rating = Rating.query.filter_by(post_id=post.id, rater_id=current_user.id).first()
    if existing_rating:
        flash('Bạn đã đánh giá trận đấu này rồi.', 'error')
        return redirect(url_for('find_opponent'))

    stars = request.form.get('rating')
    comment = request.form.get('comment')

    if not stars:
        flash('Bạn phải chọn số sao để đánh giá.', 'error')
        return redirect(url_for('find_opponent'))

    new_rating = Rating(
        stars=int(stars),
        comment=comment,
        post_id=post.id,
        rater_id=current_user.id,
        rated_user_id=rated_user_id
    )
    db.session.add(new_rating)
    db.session.commit()

    flash('Cảm ơn bạn đã gửi đánh giá!', 'success')
    return redirect(url_for('find_opponent'))




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
