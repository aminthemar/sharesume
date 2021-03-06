from flask import Flask, render_template, request, redirect, session, flash
from os import stat, urandom
import sqlite3, time

site = Flask(__name__)

db = sqlite3.connect('sharesume.db')
cur = db.cursor()

if stat('sharesume.db').st_size < 1 :
    cur.execute('CREATE TABLE users (user_name nvarchar(25) UNIQUE, user_password nvarchar(25), user_fname nvarchar(25), user_lname nvarchar(25), res_title nvarchar(80), res_date unix, res_body text)')
    cur.execute('CREATE TABLE comments (cmt_receiver nvarchar(25), cmt_sender nvarchar(25), cmt_date unix, cmt_body text)')
    cur.execute("INSERT INTO users VALUES ('admin', 'admin', 'حبیب‌الله', 'خسروی', NULL, 0, NULL)")
    cur.execute("INSERT INTO users VALUES ('pythoncoder', 'pythoncoder', 'پدرام', 'میرزایی', 'فوق تخصص در طراحی و برنامه‌نویسی وب', 9911111, 'هر رزومه ساختار مشخصی دارد به صورتی که محتویات رزومه باید در قسمتهای مجزا و با ترتیبی معین نوشته شود. معمولا در ابتدای شروع هر بخش، عنوان اصلی آن ابتدا و بعد توضیحات مربوط به آن آورده می شود. این امر موجب می شود خواننده بسهولت و سرعت مطالب دلخواه را در متن رزومه بیابد. البته رزومه ها انواع مختلفی دارد که در اینجا به رزومه های شغلی پرداخته می شود.')")
    cur.execute("INSERT INTO users VALUES ('mastermind', 'mastermind', 'اهورا', 'سعیدی', 'مهندسی در زمینه‌ی داده کاوی و مبانی بازیابی اطلاعات', 9922222, 'هر رزومه ساختار مشخصی دارد به صورتی که محتویات رزومه باید در قسمتهای مجزا و با ترتیبی معین نوشته شود. معمولا در ابتدای شروع هر بخش، عنوان اصلی آن ابتدا و بعد توضیحات مربوط به آن آورده می شود. این امر موجب می شود خواننده بسهولت و سرعت مطالب دلخواه را در متن رزومه بیابد. البته رزومه ها انواع مختلفی دارد که در اینجا به رزومه های شغلی پرداخته می شود.')")
    cur.execute("INSERT INTO users VALUES ('godOFjar', 'godOFjar', 'محمدرضا', 'انصاری', 'برنامه‌نویسی پایتون و بک-اند سرور', 9944454, 'هر رزومه ساختار مشخصی دارد به صورتی که محتویات رزومه باید در قسمتهای مجزا و با ترتیبی معین نوشته شود. معمولا در ابتدای شروع هر بخش، عنوان اصلی آن ابتدا و بعد توضیحات مربوط به آن آورده می شود. این امر موجب می شود خواننده بسهولت و سرعت مطالب دلخواه را در متن رزومه بیابد. البته رزومه ها انواع مختلفی دارد که در اینجا به رزومه های شغلی پرداخته می شود.')")
    cur.execute("INSERT INTO comments VALUES ('godOFjar', 'pythoncoder', 954154719, 'با من تماس بگیرید')")
    cur.execute("INSERT INTO comments VALUES ('godOFjar', 'admin', 854154719, 'خوش آمدید!!')")
    cur.execute("INSERT INTO comments VALUES ('godOFjar', 'مهمان', 954154720, 'سلام، شما خیلی حرفه‌ای هستید!!')")
    cur.execute("INSERT INTO comments VALUES ('pythoncoder', 'admin', 854154719, 'خوش آمدید!!')")
    cur.execute("INSERT INTO comments VALUES ('mastermind', 'مهمان', 954154720, 'سلام، شما خیلی حرفه‌ای هستید!!')")
    cur.execute("INSERT INTO comments VALUES ('mastermind', 'admin', 854154719, 'خوش آمدید!!')")
    db.commit()
cur.close()
db.close()

@site.route('/')
def GetHome():
    fullname = ''
    db = sqlite3.connect('sharesume.db')
    cur = db.cursor()
    cur.execute("SELECT user_fname, user_lname, res_title, datetime(res_date, 'unixepoch'), user_name FROM users WHERE res_body IS NOT NULL ORDER BY res_date DESC")
    _rows = cur.fetchall()
    if session.get('logged_in') :
        cur.execute("SELECT user_fname, user_lname FROM users WHERE user_name IS ?", (session['username'],))
        _user = cur.fetchone()
        fullname = _user[0] + ' ' + _user[1]
    cur.close()
    db.close()
    return render_template("homePage.html", login = session.get('logged_in'), FULL_NAME = fullname, ROWS = _rows)

@site.route('/login')
def GetLogin():
    return render_template("loginPage.html", login = session.get('logged_in'))

@site.route('/register')
def GetSignUp():
    return render_template("registerPage.html", login = session.get('logged_in'))

@site.route('/logout')
def SignOut():
    session['logged_in'] = False
    return render_template("feedback.html", login = session.get('logged_in'), ERR_MSG = "شما با موفقیت از سیستم خارج شدید")

@site.route("/resumes/<string:user_name>/")
def GetResume(user_name):
    db = sqlite3.connect('sharesume.db')
    cur = db.cursor()
    cur.execute("SELECT user_fname, user_lname, res_title, res_body, user_name FROM users WHERE user_name = ?", (user_name,))
    _row = cur.fetchone()
    cur.execute("SELECT cmt_sender, datetime(cmt_date, 'unixepoch'), cmt_body FROM comments WHERE cmt_receiver = ? ORDER BY cmt_date DESC", (user_name,))
    _cmt = cur.fetchall()
    cur.close()
    db.close()
    isAdmin = False
    if session.get('logged_in') == True and session['username'] == 'admin':
        isAdmin = True
    return render_template('resumePage.html', login = session.get('logged_in'), ROW = _row, CMT = _cmt, PRIVILAGE = isAdmin)

@site.route("/sendComment/<string:user_name>", methods = ['POST'])
def SetComment(user_name):
    input_form = request.form
    if not input_form['cmt_body'] == "" :
        db = sqlite3.connect('sharesume.db')
        cur = db.cursor()
        sender = "مهمان"
        if session.get('logged_in') == True :
            sender = session['username']
        cur.execute('INSERT INTO comments VALUES(?, ?, ?, ?)', (user_name, sender, time.time(), input_form['cmt_body'],))
        db.commit()
        cur.close()
        db.close()
        return render_template("feedback.html", login = session.get('logged_in'), ERR_MSG = "نظر شما ارسال شد")
    return GetResume(user_name)

@site.route('/docs')
def GetDocs():
    if session.get('logged_in') :
        if session['username'] == 'admin' :
            f = open('docs.dat', 'r', encoding="utf-8")
            doc = f.read()
            f.close()
            return render_template("docsPage.html", login = session.get('logged_in'), doc_body = doc)
        else :
            return render_template("feedback.html", login = session.get('logged_in'), ERR_MSG = "این فایل به شما مربوط نمی‌شود")
    return render_template("loginPage.html", login = False)

@site.route('/editDocs')
def EditDocs():
    if session.get('logged_in'):
        if session['username'] == 'admin':
            f = open('docs.dat', 'r', encoding="utf-8")
            doc = f.read()
            f.close()
            return render_template("editDocs.html", login = True, DOCUMENT = doc)
        else:
            return render_template("feedback.html", login = session.get('logged_in'), ERR_MSG = "این فایل به شما مربوط نمی‌شود")
    else:
        return render_template("loginPage.html", login = False)

@site.route('/updateDocs', methods = ['POST'])
def UpdateDocs():
    inp = request.form['docBody']
    f = open('docs.dat', 'w', encoding = 'utf-8', newline='')
    f.writelines(inp)
    f.close()
    return GetDocs()

@site.route('/sourceCode')
def GetCode():
    if session.get('logged_in'):
        if session['username'] == 'admin':
            f = open('source.dat', 'r', encoding="utf-8")
            code = f.read()
            f.close()
            return render_template("sourcePage.html", login = True, SOURCE = code)
        else:
            return render_template("feedback.html", login = session.get('logged_in'), ERR_MSG = "این فایل به شما مربوط نمی‌شود")
    else:
        return render_template("loginPage.html", login = False)

@site.route('/panel')
def GetPanel():
    if session.get('logged_in') :
        resm = True
        db = sqlite3.connect('sharesume.db')
        cur = db.cursor()
        cur.execute('SELECT res_title FROM users WHERE user_name = ?', (session['username'],))
        if cur.fetchone()[0] is None :
            resm = False
        cur.close()
        db.close()
        return render_template("panelPage.html", login = session.get('logged_in'), RESUME = resm, USER = session['username'])
    else :
        return render_template("loginPage.html", login = False)

@site.route("/delete/<string:user_name>", methods = ['POST'])
def DeleteResume(user_name):
    db = sqlite3.connect('sharesume.db')
    cur = db.cursor()
    cur.execute('UPDATE users SET res_title = NULL , res_date = NULL , res_body = NULL WHERE user_name = ?', (user_name,))
    db.commit()
    cur.close()
    db.close()
    return render_template("feedback.html", login = session.get('logged_in'), ERR_MSG = "رزومه‌ با موفقیت پاک شد")

@site.route("/edit/<string:user_name>", methods = ['POST'])
def EditResume(user_name):
    db = sqlite3.connect('sharesume.db')
    cur = db.cursor()
    cur.execute('SELECT res_title, res_body, user_name FROM users WHERE user_name = ?', (user_name,))
    _row = cur.fetchone()
    cur.close()
    db.close()
    return render_template("editPage.html", login = session.get('logged_in'), ROW = _row)

@site.route("/update/<string:user_name>", methods = ['POST'])
def UpdateResume(user_name):
    input_form = request.form
    db = sqlite3.connect('sharesume.db')
    cur = db.cursor()
    cur.execute('UPDATE users SET res_title = ? , res_date = ? , res_body = ? WHERE user_name = ?', (input_form['title'], time.time(), input_form['body'], user_name,))
    db.commit()
    cur.close()
    db.close()
    return render_template("feedback.html", login = session.get('logged_in'), ERR_MSG = "رزومه با موفقیت ویرایش شد")

@site.route('/result', methods = ['POST'])
def isLegit():
    input_form = request.form
    if not (input_form['un'] == "" or input_form['pw'] == "" or input_form['fname'] == "") :
        try :
            db = sqlite3.connect('sharesume.db')
            cur = db.cursor()
            cur.execute('INSERT INTO users (user_name, user_password, user_fname, user_lname) VALUES (?, ?, ?, ?)', (input_form['un'], input_form['pw'], input_form['fname'], input_form['lname'],))
            db.commit()
            cur.close()
            db.close()
            session['logged_in'] = True
            session['username'] = input_form['un']
            return render_template("feedback.html", login = session.get('logged_in'), ERR_MSG = "شما با موفقیت وارد سیستم شدید")
        except sqlite3.IntegrityError :
            cur.close()
            db.close()
            return render_template("registerPage.html", UNIQUE_ERR = "نام کاربری تکراری است", login = session.get('logged_in'))
    return render_template("registerPage.html", EMPTY_ERR = "فرم را کامل کنید", login = session.get('logged_in'))

@site.route('/enter', methods = ['POST'])
def isUser():
    input_form = request.form
    if not (input_form['un'] == "" or input_form['pw'] == "") :
        db = sqlite3.connect('sharesume.db')
        cur = db.cursor()
        cur.execute("SELECT user_fname, user_lname FROM users WHERE user_name = ? AND user_password = ?", (input_form['un'], input_form['pw'],))
        row = cur.fetchone()
        if row is None :
            cur.close()
            db.close()
            return render_template("loginPage.html", login = session.get('logged_in'), WRONG_ERR = "نام کاربری یا رمزعبور اشتباه است")
        else :
            cur.close()
            db.close()
            session['logged_in'] = True
            session['username'] = input_form['un']
            return render_template("feedback.html", login = session.get('logged_in'), ERR_MSG = "شما با موفقیت وارد سیستم شدید")
    return render_template("loginPage.html", EMPTY_ERR = "فرم را کامل کنید", login = session.get('logged_in'))

@site.route('/submit', methods = ['POST'])
def SubmitRes():
    input_form = request.form
    if not input_form['title'] == "" :
        db = sqlite3.connect('sharesume.db')
        cur = db.cursor()
        cur.execute('UPDATE users SET res_title = ? , res_date = ? , res_body = ? WHERE user_name = ?', (input_form['title'], time.time(), input_form['body'], session['username'],))
        db.commit()
        cur.close()
        db.close()
        return render_template("feedback.html", login = session.get('logged_in'), ERR_MSG = "رزومه با موفقیت ثبت شد")
    return render_template("panelPage.html", EMPTY_ERR = "فرم را کامل کنید", login = session.get('logged_in'), RESUME = False)

@site.route('/password', methods = ['POST'])
def ChangePass():
    input_form = request.form
    if not (input_form['old'] == "" or input_form['new'] == "" or input_form['renew'] == "") :
        if input_form['new'] != input_form['renew'] :
            return render_template("panelPage.html", WRONG_PASS = "رمزهای جدید همخوانی ندارند", login = session.get('logged_in'))
        db = sqlite3.connect('sharesume.db')
        cur = db.cursor()
        cur.execute('SELECT user_password FROM users WHERE user_name = ?', (session['username'],))
        _password = cur.fetchone()[0]
        if input_form['old'] != _password:
            cur.close()
            db.close()
            return render_template("panelPage.html", WRONG_PASS = "رمز فعلی همخوانی ندارد", login = session.get('logged_in'))
        cur.execute('UPDATE users SET user_password = ? WHERE user_name = ?', (input_form['new'], session['username'],))
        db.commit()
        cur.close()
        db.close()
        return render_template("feedback.html", login = session.get('logged_in'), ERR_MSG = "رمزعبور با موفقیت تغییر کرد")
    return render_template("panelPage.html", WRONG_PASS = "فرم را کامل کنید", login = session.get('logged_in'))

if __name__=="__main__":
    site.secret_key = urandom(12)
    site.run(debug=True)