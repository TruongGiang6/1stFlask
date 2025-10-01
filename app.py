from flask import Flask, redirect, url_for, render_template, request, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Để sử dụng session và flash

users = {}  # Lưu user tạm thời (chỉ dùng demo)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Sai tên số điện thoại/email hoặc mật khẩu!')
    last_username = session.pop('last_username', '')
    return render_template('login.html', last_username=last_username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        # Kiểm tra xác nhận mật khẩu
        if password != confirm_password:
            flash('Mật khẩu xác nhận không trùng khớp. Mời điền lại!')
        elif username in users:
            flash('Tài khoản đã tồn tại!')
        else:
            # Lưu thông tin user (demo: chỉ lưu vào dict)
            users[username] = {
                'password': password,
                'email': email,
                'phone': phone
            }
            flash('Đăng ký thành công! Hãy đăng nhập!')
            session['last_username'] = username
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)