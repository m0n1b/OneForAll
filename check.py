from flask import Flask, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import threading
from datetime import datetime, timedelta
import time
import sqlite3


# Telegram Bot Setup
TELEGRAM_TOKEN = '7481588348:AAHXz_PB4haHyjOhzdEZegxkckyTFBQ5dPo'  # Replace with your bot's token
TELEGRAM_CHAT_ID = '-4200200606'  # Replace with your chat ID

def send_telegram_notification(url):
    message = f"网站检测失败,请排查,这个网站将在两个小时候重新检查:{url}"
    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.post(send_url, data=data)
    #print(response.text)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

# Login Manager Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS task (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            match_text TEXT,
            ua TEXT,
            refer TEXT,
            next_time INTEGER NOT NULL,
            status INTEGER NOT NULL DEFAULT 1,
            task_time INTEGER NOT NULL DEFAULT 60
        )
    ''')
    conn.commit()
    conn.close()

def check_website(id, url, ua, refer, match_text, retries=0):
    #print(url)
    try:
        headers = {'User-Agent': ua, 'Referer': refer}
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        if  response.status_code == 200 and match_text =="*":
            return True
        if response.status_code == 200 and match_text in response.text:
            return True
        else:
            if retries < 3:
                time.sleep(10)
                #print("next")
                check_website(id, url, ua, refer, match_text, retries + 1)
            else:
                add_time(id,7200)
                send_telegram_notification(url)
                
    except Exception as e:
        #print(f"Error checking website {url}: {e}")
        #print(retries)
        if retries < 3:
                print("next")
                time.sleep(10)
                
                check_website(id, url, ua, refer, match_text, retries + 1)
        else:
                add_time(id,7200)
                send_telegram_notification(url)
                

def add_time(id,time):
    try:
        #print(id)
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        current_timestamp = int(datetime.now().timestamp())
        new_next_time = current_timestamp + time
        c.execute('UPDATE task SET next_time = ? WHERE id = ?', (new_next_time, id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        #print("add_time")
        #print(e)
        return False
    
def task_checker():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    current_timestamp = int(datetime.now().timestamp())
    #print(current_timestamp)
    c.execute('SELECT * FROM task WHERE status = 1 AND next_time <= ?', (current_timestamp,))
    tasks = c.fetchall()
    #print(tasks)
    for task in tasks:
        
        threading.Thread(target=check_website, args=(task[0], task[1], task[3], task[4], task[2])).start()
        new_next_time = current_timestamp + task[7]
        #print("-------------------------------")
        #print(task[5])
        #print("-------------------------------")
        if current_timestamp>=task[5]:
            c.execute('UPDATE task SET next_time = ? WHERE id = ?', (new_next_time, task[0]))
    conn.commit()
    conn.close()

scheduler = BackgroundScheduler()
scheduler.add_job(func=task_checker, trigger='interval', seconds=10, max_instances=180)

#scheduler.add_job(func=task_checker, trigger='interval', minutes=1)
scheduler.start()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
 
        password = request.form['password']
        if  password == "Aw121212!!!":
            user = User("admin")
            login_user(user)
            return redirect(url_for('manage_tasks'))
        else:
            return 'Invalid username or password'
    return '''
        <form method="post">
          
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/manage_tasks', methods=['GET', 'POST'])
@login_required
def manage_tasks():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    if request.method == 'POST':
        if 'delete' in request.form:
            c.execute('DELETE FROM task WHERE id = ?', (request.form['delete'],))
        elif 'add' in request.form:
            url = request.form['url']
            match_text = request.form.get('match_text', '*')
            ua = request.form.get('ua', 'Googlebot/2.1 (+http://www.google.com/bot.html)')
            refer = request.form.get('refer', 'http://www.google.com')
            task_time = int(request.form.get('task_time', 600))
            next_time = int(datetime.now().timestamp()) + task_time
            c.execute('INSERT INTO task (url, match_text, ua, refer, next_time, task_time, status) VALUES (?, ?, ?, ?, ?, ?, 1)',
                      (url, match_text, ua, refer, next_time, task_time))
        elif 'toggle_status' in request.form:
            task_id = request.form['toggle_status']
            c.execute('UPDATE task SET status = 1 - status WHERE id = ?', (task_id,))

        conn.commit()

    order_by = request.args.get('order_by', 'id')
    direction = request.args.get('direction', 'ASC')
    c.execute(f'SELECT * FROM task ORDER BY {order_by} {direction}')
    tasks = c.fetchall()
    conn.close()

    direction = 'DESC' if direction == 'ASC' else 'ASC'

    tasks_table = '<table border="1">'
    tasks_table += '<tr><th>ID</th><th><a href="?order_by=url&direction=' + direction + '">URL</a></th><th>Match Text</th><th>UA</th><th>Refer</th><th>Next Check</th><th>Task Time</th><th>Status</th><th>Actions</th></tr>'
    for task in tasks:
        tasks_table += f'''
            <tr>
                <td>{task[0]}</td>
                <td>{task[1]}</td>
                <td>{task[2]}</td>
                <td>{task[3]}</td>
                <td>{task[4]}</td>
                <td>{datetime.fromtimestamp(task[5]).strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>{task[7]}</td>
                <td>{'Active' if task[6] == 1 else 'Inactive'}</td>
                <td>
                    <form method="post">
                        <button type="submit" name="toggle_status" value="{task[0]}">Toggle Status</button>
                        <button type="submit" name="delete" value="{task[0]}">Delete</button>
                    </form>
                </td>
            </tr>
        '''
    tasks_table += '</table>'

    return f'''
        <h1>Manage Tasks</h1>
        <form method="post">
            URL: <input type="text" name="url" required><br>
            Match Text: <input type="text" name="match_text" value="*"><br>
            User-Agent: <input type="text" name="ua" value="Googlebot/2.1 (+http://www.google.com/bot.html)"><br>
            Referer: <input type="text" name="refer" value="http://www.google.com"><br>
            Task Time (seconds): <input type="number" name="task_time" value="600"><br>
            <input type="submit" name="add" value="Add Task">
        </form>
        <div>{tasks_table}</div>
        <a href="/logout">Logout</a>
    '''

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0",debug=False)
