from flask import Flask,redirect,url_for,render_template,request,session
from flask_mysqldb import MySQL,MySQLdb

app=Flask(__name__)
app.secret_key = '714f90b16d330688feb11eb8cb0b3a5b'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'college'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            return render_template('error.html',error='Login unsuccessful. Please check your email and password.')

    return render_template('login.html') 


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form['first_name']
        lname = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the username is already in use
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template('error.html',error='Username already in use. Please choose another username.')

        # Check if the email is already in use
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_email = cursor.fetchone()

        if existing_email:
            return render_template('error.html',error='Email address already in use. Please use another email.')

        # If username and email are unique, insert the user into the database
        cursor.execute("INSERT INTO users (first_name ,last_name ,username, email, password) VALUES (%s, %s, %s, %s, %s)", (fname ,lname ,username, email, password))
        mysql.connection.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# my statestics
## here is the secrate statictic calculation that provide the buy and sell entry and their targets and also stoploss for both entry
@app.route('/success/<float:d1h>/<float:d1l>/<float:d2h>/<float:d2l>')
def success(d1h, d1l, d2h, d2l):

    mh = max(d1h,d2h)
    ml = min(d1l,d2l)
    
    bentry = round(mh + ((mh*0.15)/100),2)   # buy entry
    sentry = round(ml - ((ml*0.15)/100),2)   # sell entry
    
    btarget = round(bentry + ((bentry * 1.5)/100),2) # buy entry's target
    starget = round(sentry - ((sentry * 1.5)/100),2) # sell entry's target
    
    bmsl =round(bentry - ((bentry * 1.5)/100),2)
    smsl =round(sentry + ((sentry * 1.5)/100),2)
    
    btsl = round(ml - ((ml * 0.15)/100),2)    # buy entry's stoploss
    stsl = round(mh + ((mh * 0.15)/100),2)    # sell entry's stoploss
    
    bsl = max(btsl,bmsl)
    ssl = min(stsl,smsl)


    return render_template('result.html',bentry=bentry,sentry=sentry,btarget=btarget,starget=starget,bsl=bsl,ssl=ssl,bmsl=bmsl,smsl=smsl,btsl=btsl,stsl=stsl)
    


@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/submit',methods=['POST','GET'])
def submit():
        if request.method=='POST':
            try:
                d1h = float(request.form['d1h'])
                d1l = float(request.form['d1l'])
            
                d2h = float(request.form['d2h'])
                d2l = float(request.form['d2l'])
            except:
                return render_template('fail.html',error='Please Enter Only Floating Numbers')
        
        if d1h>d2l and d2h>d2l:
            return redirect(url_for("success",d1h=d1h,d1l=d1l,d2h=d2h,d2l=d2l))
        else:
            return render_template('fail.html',error='Please Enter Valid Details')
        
@app.route('/buy')
def chart_link():
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup


    Charting_Link = "https://chartink.com/screener/"
    Charting_url = "https://chartink.com/screener/process"

    condition = "( {33489} ( latest high - latest low < 1 day ago high - 1 day ago low and latest high - latest low < 2 days ago high - 2 days ago low and latest high - latest low < 3 days ago high - 3 days ago low and latest high - latest low < 4 days ago high - 4 days ago low and latest high - latest low < 5 days ago high - 5 days ago low and latest high - latest low < 6 days ago high - 6 days ago low and latest high < 1 day ago high and latest low > 1 day ago low and latest close >= 100 and latest volume < 1 day ago volume ) ) "

    def GetDataFromChartink (payload):
        payload = {'scan_clause': payload}

        with requests.Session() as s:
            r = s.get(Charting_Link)
            soup = BeautifulSoup(r.text, "html.parser")
            csrf = soup.select_one("[name='csrf-token']")['content']
            s.headers['x-csrf-token'] = csrf
            r = s.post(Charting_url, data=payload)

            df = pd.DataFrame()
            for item in r.json()['data']:
                df = df.append(item, ignore_index=True)
        return df

    data = GetDataFromChartink(condition)
    data = data.to_html()
    
   
    return "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css' rel='stylesheet' integrity='sha384-4bw+/aepP/YC94hEpVNVgiZdgIC5+VKNBQNGCHeKRQN+PtmoHDEXuppvnDJzQIu9' crossorigin='anonymous'><style>table{margin: 0 auto; border: 5px solid black}td{border: 2px solid black; padding-left:10px; padding-right:10px;}h1{text-align: center;color: green}th{padding-right:50px; padding-left:10px; text-align: left; margin: 10px;padding-bottom: 20px;border: 2px solid black}</style><nav class='navbar navbar-expand-lg navbar-dark bg-dark'><a class='navbar-brand' href='/home'>MyScanner</a><div class='collapse navbar-collapse' id='navbarSupportedContent'><ul class='navbar-nav mr-auto'><li class='nav-item active'><a class='nav-link' href='/home'>Home</a></li></ul></div></nav><br><br><h1>Buy Stock for intraday</h1><br>"+data
        
if __name__=='__main__':
    app.run(debug=True)