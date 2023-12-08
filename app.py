from serverConf import EnvConf
from config import Text

from datetime import datetime, date as d_te
import json
import io
import re
import os
from PIL import Image
from flask import Flask, render_template, make_response, request, redirect, url_for, session, send_file
from email.message import EmailMessage
import smtplib
import pymongo
import hashlib
import string
import random
import requests
today = d_te.today


app = Flask(__name__, template_folder=EnvConf.template_folder)
app.secret_key = EnvConf.secret_key
elements_dir = EnvConf.elements_dir
style_path = EnvConf.style_path
client = pymongo.MongoClient(
    EnvConf.mongo_str
)
db = client.intensetales


class Utils:
    @staticmethod
    def hash(str_con):
        return hashlib.sha3_224(str_con.encode()).hexdigest()

    @staticmethod
    def random_string(number):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=number))

    @staticmethod
    def load_cookies():
        if request.cookies.get('username') is not None and request.cookies.get('ID') is not None:
            session['username'] = request.cookies.get('username')
            session['ID'] = request.cookies.get('ID')

    @staticmethod
    def check_account(auto_redirect=False):
        if not ('username' in session and 'ID' in session):
            if auto_redirect:
                return redirect(url_for('signin'))
            return False, False
        user = db.users.find_one({'username': session['username']})
        if user is None:
            if auto_redirect:
                return redirect(url_for('signin'))
            return False, False
        if request.headers.get('User-Agent') not in user['user-agent']:
            if auto_redirect:
                return redirect(url_for('signin'))
            return False, False
        if user['user-agent'][request.headers.get('User-Agent')]['ID'] != session['ID']:
            if auto_redirect:
                return redirect(url_for('signin'))
            return False, False
        if not user['user-agent'][request.headers.get('User-Agent')]['valid']:
            if auto_redirect:
                return redirect(url_for('validation'))
            return True, False
        return True, True

    @staticmethod
    def reformat_date(date):
        split_date = date.split('-')
        months = {
            '01': "Gen",
            '02': "Feb",
            '03': "Mar",
            '04': "Apr",
            '05': "May",
            '06': "Jun",
            '07': "Jul",
            '08': "Aug",
            '09': "Sep",
            '10': "Oct",
            '11': "Nov",
            '12': "Dic"
        }
        return split_date[2] + ' ' + months[split_date[1]] + ' ' + split_date[0]

    @staticmethod
    def put_content_on_file(content):
        buffer = io.StringIO()
        buffer.write(content)
        mem = io.BytesIO()
        mem.write(buffer.getvalue().encode())
        mem.seek(0)
        return mem

    @staticmethod
    def past_date(date):
        return datetime.timestamp(datetime.now()) > datetime.timestamp(datetime.strptime(date, '%d %b %Y'))

    @staticmethod
    def check_ban(text):
        black_list = []
        ip_addr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        for listed in black_list:
            if re.match(f'^{listed}', ip_addr):
                return render_template(
                    'banned.html',
                    text=text,
                    page={
                        'title': text.title('banned'),
                        'description': text.description('banned')
                    },
                    errors=[]
                )
        return False

    def translate(text, lang):
        lang_to_code = {
            'english': 'EN',
            'italiano': 'IT'
        }
        translations = {lang: text}
        del lang_to_code[lang]
        for lang in lang_to_code:
            req = requests.post(
                "https://api-free.deepl.com/v2/translate",
                headers={'Authorization': 'DeepL-Auth-Key 2c37f3ab-e66c-2b62-8266-da91a62d043e:fx'},
                data={
                    'text': text,
                    'target_lang': lang_to_code[lang]
                }
            )
            translations[lang] = req.json()['translations'][0]['text']
        return translations


class Check:
    @staticmethod
    def username(username, text):
        errors = []
        if len(username) < 3:
            errors.append(text.error('username_len'))
        if '@' in username:
            errors.append(text.error('@_username'))
        if db.users.find_one({'username': username}) is not None:
            errors.append(text.error('username_used'))
        return errors

    @staticmethod
    def email(email, text):
        errors = []
        if db.users.find_one({'email': email}) is not None:
            errors.append(text.error('email_used'))
        return errors

    @staticmethod
    def password(password, rep_password, text):
        errors = []
        if len(password) < 4:
            errors.append(text.error('password_len'))
        if password != rep_password:
            errors.append(text.error('different_passwords'))
        return errors

    @staticmethod
    def title(title, text):
        errors = []
        if db.stories.find_one({'title': title}) is not None:
            errors.append(text.error('title_already_exist'))
        if not title:
            errors.append(text.error('no_title'))
        return errors

    @staticmethod
    def genre(genre, text):
        errors = []
        if not genre:
            errors.append(text.error('no_genre'))
        return errors

    @staticmethod
    def description(description, text):
        errors = []
        if len(description) < 64:
            errors.append(text.error('description_len'))
        return errors

    @staticmethod
    def lang(lang, text):
        errors = []
        if lang not in text.supported_langs:
            errors.append(text.error('invalid_lang'))
        return errors

    @staticmethod
    def publish_date(date, text):
        errors = []
        if Utils.past_date(Utils.reformat_date(date)):
            errors.append(text.error('past_date'))
        return errors


class SendMail:
    @staticmethod
    def template(address, content, subject):
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = 'noreply@intensetales.com'
        message["To"] = address
        message.set_content(
            f"""\
            <div style="background-color: #f6f6f6;">
                <div style="
                    font-size: 0.8rem;
                    border-radius: 3rem;
                    background-color: white;
                    margin: 2rem;
                    padding: 3rem;
                    color: #90A4AE;
                    align-items: center;">
                    {content}
                </div>
            </div>
            """,
            subtype='html'
        )
        server = smtplib.SMTP_SSL('smtps.aruba.it', 465)
        server.login('noreply@intensetales.com', 'MfNdgHZ8WMrTi4X#$')
        server.send_message(message)
        # server.sendmail('noreply@intensetales.com', address, message.as_string())

    @staticmethod
    def validation(address, validation_id, text):
        SendMail.template(
            address,
            f"""
                <h1>{text.title('validation_code')}</h1>{text.mail('validation')}<br>
                <div style="background-color: ghostwhite;
                             font-size: 1.2rem;
                             border-radius: 2rem;
                             padding: 0.5rem;">
                    {validation_id}
                </div>
            """,
            text.title('validation_code')
        )

    @staticmethod
    def reset_password(address, code, text):
        SendMail.template(
            address,
            f"""<h1>{text.title('reset_password')}</h1><br>
            {text.mail('reset_password')}<br>
            <div style="background-color: ghostwhite;
                             font-size: 1.2rem;
                             border-radius: 2rem;
                             padding: 0.5rem;">
                {code}
            </div>""",
            text.title('reset_password')
        )


@app.route('/styler/', methods=['GET'])
def styler():
    return send_file(EnvConf.style_path)


@app.route('/elements/<element>/', methods=['GET'])
def elements(element):
    files = {
        'logo': "logo.png",
        'big_logo': "bigLogo.png",
        'heart': "heart.png",
        'edit': "edit.png",
        'DeepL': "DeepL.png"
    }
    return send_file(EnvConf.elements_dir + files[element])


@app.route('/', methods=['GET', 'POST'])
def home():
    Utils.load_cookies()
    text = Text()
    ban = Utils.check_ban(text)
    if ban:
        return ban
    errors = []
    page = {
        'title': "Intense Tales",
        'description': text.description('home'),
        'citation': text.citation()
    }
    return render_template(
        'home.html',
        text=text,
        page=page,
        errors=errors,
        stories=[story for story in db.stories.find() if Utils.past_date(story['publish_date'])]
    )


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    text = Text()
    ban = Utils.check_ban(text)
    if ban:
        return ban
    errors = []
    last = {
        'username': "",
        'email': ""
    }
    if request.method == 'POST':
        if 'signup_sub' in request.form:
            last['username'] = request.form['username']
            last['email'] = request.form['email']
            errors += Check.username(request.form['username'], text)
            errors += Check.email(request.form['email'], text)
            errors += Check.password(request.form['password'], request.form['rep_password'], text)
            if not errors:
                session['username'] = request.form['username']
                db.users.insert_one({
                    'username': request.form['username'],
                    'email': request.form['email'],
                    'password': Utils.hash(request.form['password']),
                    'user-agent': {},
                    'creator': False
                })
                resp = make_response(redirect(url_for('validation')))
                resp.set_cookie('username', request.form['username'], max_age=315360000)
                return resp
    page = {
        'title': text.title('signup'),
        'description': text.description('signup')
    }
    return render_template(
        'signup.html',
        text=text,
        page=page,
        errors=errors,
        last=last
    )


@app.route('/validation/', methods=['GET', 'POST'])
def validation():
    Utils.load_cookies()
    text = Text()
    ban = Utils.check_ban(text)
    if ban:
        return ban
    errors = []
    user = db.users.find_one({'username': session['username']})
    if user is None:
        return redirect(url_for('signin'))
    if request.headers.get('User-Agent') not in user['user-agent']:
        user['user-agent'][request.headers.get('User-Agent')] = {
            'ID': Utils.random_string(40),
            'valid': False
        }
        db.users.update_one(
            {'username': session['username']},
            {'$set': {'user-agent': user['user-agent']}}
        )
    if request.method == 'POST':
        if 'validation_sub' in request.form:
            if 'code' in request.form:
                if user['user-agent'][request.headers.get('User-Agent')]['ID'] != request.form['code']:
                    errors.append(text.error('wrong_id'))
                if not errors:
                    user['user-agent'][request.headers.get('User-Agent')]['valid'] = True
                    db.users.update_one(
                        {'username': session['username']},
                        {'$set': {'user-agent': user['user-agent']}}
                    )
                    resp = make_response(redirect(url_for('home')))
                    resp.set_cookie('ID', request.form['code'], max_age=315360000)
                    return resp
    SendMail.validation(user['email'], user['user-agent'][request.headers.get('User-Agent')]['ID'], text)
    page = {
        'title': text.title('validation'),
        'description': text.description('validation')
    }
    return render_template(
        'validation.html',
        text=text,
        page=page,
        errors=errors,
        email=user['email']
    )


@app.route('/signin/', methods=['GET', 'POST'])
def signin():
    Utils.load_cookies()
    text = Text()
    ban = Utils.check_ban(text)
    if ban:
        return ban
    errors = []
    last = {
        'username_email': ""
    }
    if request.method == 'POST':
        if 'signin_sub' in request.form:
            last['username_email'] = request.form['username_email']
            if '@' in request.form['username_email']:
                user = db.users.find_one({'email': request.form['username_email']})
                if user is None:
                    errors.append(text.error('no_user'))
            else:
                user = db.users.find_one({'username': request.form['username_email']})
                if user is None:
                    errors.append(text.error('no_email'))
            if user is not None:
                if user['password'] != Utils.hash(request.form['password']):
                    errors.append(text.error('wrong_password'))
            if not errors:
                session['username'] = user['username']
                if request.headers.get('User-Agent') in user['user-agent']:
                    session['ID'] = user['user-agent'][request.headers.get('User-Agent')]['ID']
                    resp = make_response(redirect(url_for('home')))
                    resp.set_cookie('username', session['username'], max_age=315360000)
                    resp.set_cookie('ID', session['ID'], max_age=315360000)
                    return resp
                else:
                    resp = make_response(redirect(url_for('validation')))
                    resp.set_cookie('username', session['username'], max_age=315360000)
                    return resp
    page = {
        'title': text.title('signin'),
        'description': text.description('signin')
    }
    return render_template(
        'signin.html',
        text=text,
        page=page,
        errors=errors,
        last=last
    )


@app.route('/reset_password/', methods=['GET', 'POST'])
def reset_password():
    Utils.load_cookies()
    text = Text()
    ban = Utils.check_ban(text)
    if ban:
        return ban
    errors = []
    last = {
        'email': ""
    }
    if request.method == 'POST':
        if 'reset_password_sub' in request.form:
            last['email'] = request.form['email']
            user = db.users.find_one({'email': request.form['email']})
            if user is None:
                errors.append(text.error('no_email'))
            if not errors:
                SendMail.reset_password(
                    request.form['email'],
                    user['user-agent'][request.headers.get('User-Agent')]['ID'],
                    text
                )
                session['email'] = request.form['email']
        if 'code_sub' in request.form:
            user = db.users.find_one({'email': session['email']})
            if user is None:
                errors.append(text.error('no_email'))
            else:
                if user['user-agent'][request.headers.get('User-Agent')]['ID'] != request.form['code']:
                    errors.append('wrong_id')
            errors += Check.password(request.form['password'], request.form['rep_password'], text)
            if not errors:
                db.users.update_one(
                    {'email': session['email']},
                    {'$set': {'password': Utils.hash(request.form['password'])}}
                )
            session.pop('email', None)
            return redirect(url_for('signin'))
        if 'close_sub' in request.form:
            session.pop('email', None)
    page = {
        'title': text.title('reset_password'),
        'description': text.description('reset_password')
    }
    return render_template(
        'reset_password.html',
        text=text,
        page=page,
        errors=errors,
        last=last
    )


@app.route('/account/', methods=['GET', 'POST'])
def account():
    Utils.load_cookies()
    auto_redirect = Utils.check_account(auto_redirect=True)
    if auto_redirect != (True, True):
        return auto_redirect
    text = Text()
    ban = Utils.check_ban(text)
    if ban:
        return ban
    errors = []
    if request.method == 'POST':
        if 'download_data' in request.form:
            user = db.users.find_one({'username': session['username']})
            del user['_id']
            return send_file(
                Utils.put_content_on_file(json.dumps(user)),
                as_attachment=True,
                download_name=f"{session['username']}.json"
            )
        if 'email_sub' in request.form:
            errors += Check.email(request.form['email'], text)
            if not errors:
                if 'changes' not in session:
                    session['changes'] = {}
                session['changes']['email'] = request.form['email']
        if 'password_sub' in request.form:
            errors += Check.password(request.form['password'], request.form['rep_password'], text)
            if not errors:
                if 'changes' not in session:
                    session['changes'] = {}
                session['changes']['password'] = request.form['password']
        if 'signout' in request.form:
            if 'changes' not in session:
                session['changes'] = {}
            session['changes']['account'] = text.input('signout')
        if 'delete' in request.form:
            if 'changes' not in session:
                session['changes'] = {}
            session['changes']['account'] = text.input('delete_account')
        if 'conf_close' in request.form and 'changes' in session:
            session.pop('changes')
        if 'conf_sub' in request.form and 'changes' in session:
            user = db.users.find_one({'username': session['username']})
            if Utils.hash(request.form['conf_password']) != user['password']:
                errors.append(text.error('wrong_password'))
            if not errors:
                if 'email' in session['changes']:
                    errors += Check.email(session['changes']['email'], text)
                    if not errors:
                        user_agent = {}
                        for agent in user['user-agent']:
                            user_agent[agent] = {}
                            user_agent[agent]['ID'] = user['user-agent'][agent]['ID']
                            user_agent[agent]['valid'] = False
                        db.users.update_one(
                            {'username': session['username']},
                            {'$set': {'email': session['changes']['email']}}
                        )
                        db.users.update_one(
                            {'username': session['username']},
                            {'$set': {'user-agent': user_agent}}
                        )
                        return redirect(url_for('validation'))
                if 'password' in session['changes']:
                    errors += Check.password(session['changes']['password'], session['changes']['password'], text)
                    if not errors:
                        db.users.update_one(
                            {'username': session['username']},
                            {'$set': {'password': Utils.hash(session['changes']['password'])}}
                        )
                if 'account' in session['changes']:
                    if text.input('delete_account') == session['changes']['account']:
                        resp = make_response(redirect(url_for('signup')))
                        db.users.delete_one({'username': session['username']})
                    else:
                        resp = make_response(redirect(url_for('signin')))
                    resp.set_cookie('username', '', expires=0)
                    resp.set_cookie('ID', '', expires=0)
                    session.pop('username')
                    session.pop('ID')
                    session.pop('changes')
                    return resp
            session.pop('changes')
    actions = {
        'True': True,
        'False': False,
        None: False
    }
    page = {
        'title': text.title('account'),
        'description': text.description('account'),
        'actions': actions[request.args.get('actions')]
    }
    return render_template(
        'account.html',
        text=text,
        page=page,
        errors=errors,
        user=db.users.find_one({'username': session['username']})
    )


@app.route('/creator/<username>/', methods=['GET', 'POST'])
def creator(username):
    Utils.load_cookies()
    logged = Utils.check_account()
    text = Text()
    ban = Utils.check_ban(text)
    if ban:
        return ban
    errors = []
    creator_user = db.users.find_one({'username': username})
    your_account = False
    if logged == (True, True):
        if session['username'] == username:
            your_account = True
    exist_creator = False
    if creator_user is None:
        description = text.error('no_creator_user')
    elif your_account:
        description = text.description('become_creator')
        if creator_user['creator'] is not False:
            exist_creator = True
    elif creator_user['creator'] is False:
        description = text.error('no_creator')
        exist_creator = True
    else:
        description = ""
    if request.method == 'POST':
        if your_account:
            if 'become_creator' in request.form and exist_creator is False:
                db.users.update_one(
                    {'username': session['username']},
                    {'$set': {
                        'creator': True
                    }}
                )
            if 'publish_story' in request.form and exist_creator:
                return redirect(url_for('publish_story'))
        elif 'become_creator' in request.form or 'publish_story' in request.form or 'publish_story_sub' in request.form:
            errors.append(text.error('not_your_account'))
    page = {
        'title': username,
        'description': description,
        'your_account': your_account,
        'exist_creator': exist_creator
    }
    return render_template(
        'creator.html',
        text=text,
        page=page,
        errors=errors,
        stories=[story for story in db.stories.find({'creator': username}) if
                 Utils.past_date(story['publish_date']) or your_account]
    )


@app.route('/publish_story/', methods=['POST', 'GET'])
def publish_story():
    Utils.load_cookies()
    auto_redirect = Utils.check_account(auto_redirect=True)
    if auto_redirect != (True, True):
        return auto_redirect
    text = Text()
    ban = Utils.check_ban(text)
    if ban:
        return ban
    errors = []
    last = {
        'title': "",
        'description': "",
        'mention': "",
        'publish_date': "",
        'genre': ""
    }
    if request.method == 'POST':
        if 'publish_story' in request.form:
            last['title'] = request.form['title']
            last['description'] = request.form['description']
            last['publish_date'] = request.form['publish_date']
            last['genre'] = request.form['genre']
            errors += Check.title(request.form['title'], text)
            errors += Check.genre(request.form['genre'], text)
            errors += Check.description(request.form['description'], text)
            errors += Check.lang(request.form['lang'], text)
            errors += Check.publish_date(request.form['publish_date'], text)
            if 'file_content' not in request.files:
                errors.append(text.error('no_story_file'))
            mention = ""
            if 'mention' in request.form:
                last['mention'] = request.form['mention']
                mention = request.form['mention']
            if not errors:
                try:
                    image_format = re.search('\..*$', request.files['file_image'].filename)[0]
                    image = Image.open(request.files['file_image'])
                    image = image.resize((300, 300))
                    image.save(EnvConf.images_dir + request.form['title'] + image_format)
                except:
                    errors.append(text.error('cannot_load_image'))
                if not errors:
                    db.stories.insert_one({
                        'creator': session['username'],
                        'lang': request.form['lang'],
                        'publish_date': Utils.reformat_date(request.form['publish_date']),
                        'genre': request.form['genre'].replace(',', '').split(' '),
                        'title': request.form['title'],
                        'description': Utils.translate(request.form['description'], request.form['lang']),
                        'mention': Utils.translate(mention, request.form['lang']),
                        'content': {
                            today().strftime("%d %b %Y"): Utils.translate(
                                request.files['file_content'].read().decode("utf-8"),
                                request.form['lang']
                            )
                        },
                        'likes': [session['username']],
                        'comments': []
                    })
                    return redirect(url_for('creator', username=session['username']))
    page = {
        'title': text.title('publish_story'),
        'description': text.description('publish_story')
    }
    return render_template(
        'publish_story.html',
        text=text,
        page=page,
        errors=errors,
        last=last
    )


@app.route('/story/<title>/', methods=['GET', 'POST'])
def story_page(title):
    Utils.load_cookies()
    text = Text()
    ban = Utils.check_ban(text)
    if ban:
        return ban
    errors = []
    story = db.stories.find_one({'title': title})
    if not story:
        return redirect(url_for('home'))
    if request.args.get('original') is None:
        original = False
    else:
        original = eval(request.args.get('original'))
    story['rev_num'] = len(story['content'])
    story['content'] = story['content'][sorted(
        [date_ for date_ in story['content']],
        key=lambda d: datetime.strptime(d, '%d %b %Y'),
        reverse=True
    )[0]]
    if original:
        story['content'] = story['content'][story['lang']]
        story['mention'] = story['mention'][story['lang']]
        story['description'] = story['description'][story['lang']]
    else:
        story['content'] = story['content'][text.lang]
        story['mention'] = story['mention'][text.lang]
        story['description'] = story['description'][text.lang]
    if not Utils.past_date(story['publish_date']):
        if Utils.check_account() != (True, True) or session['username'] != story['creator']:
            return redirect(url_for('creator', username=story['creator']))
    if request.method == 'POST':
        if 'like' in request.form or 'edit' in request.form or 'comment_sub':
            auto_redirect = Utils.check_account(True)
            if auto_redirect != (True, True):
                return auto_redirect
        if 'like' in request.form:
            if session['username'] in story['likes']:
                story['likes'].remove(session['username'])
            else:
                story['likes'].append(session['username'])
            db.stories.update_one(
                {'title': title},
                {'$set': {'likes': story['likes']}}
            )
        if 'comment_sub' in request.form:
            story['comments'].append({
                'username': session['username'],
                'time': datetime.now().strftime('%d %b %y %H:%M'),
                'content': request.form['comment']
            })
            db.stories.update_one(
                {'title': title},
                {'$set': {'comments': story['comments']}}
            )
        if 'edit' in request.form:
            return redirect(url_for('story_edit', title=title))
    page = {
        'title': title + ' ~ ' + story['creator'],
        'description': story['description']
    }
    return render_template(
        'story.html',
        text=text,
        page=page,
        errors=errors,
        story=story,
        original=original
    )


@app.route('/story/<title>/edit/', methods=['GET', 'POST'])
def story_edit(title):
    Utils.load_cookies()
    text = Text()
    ban = Utils.check_ban(text)
    if ban:
        return ban
    auto_redirect = Utils.check_account(auto_redirect=True)
    if auto_redirect != (True, True):
        return auto_redirect
    errors = []
    story = db.stories.find_one({'title': title})
    if session['username'] != story['creator']:
        return redirect(url_for('story_page', title=title))
    story['genre'] = "".join([genre + ' ' for genre in story['genre']])
    if request.method == 'POST':
        if 'conf_close' in request.form and 'changes' in session:
            session.pop('changes')
        if 'change_title' in request.form:
            errors += Check.title(request.form['title'], text)
            if not errors:
                if 'changes' not in session:
                    session['changes'] = {}
                session['changes'][text.input('change_title')] = request.form['title']
        if 'change_description' in request.form:
            errors += Check.description(request.form['description'], text)
            if not errors:
                if 'changes' not in session:
                    session['changes'] = {}
                session['changes'][text.input('change_description')] = request.form['description']
        if 'change_mention' in request.form:
            errors += Check.mention(request.form['mention'], text)
            if not errors:
                if 'changes' not in session:
                    session['changes'] = {}
                session['changes'][text.input('change_mention')] = request.form['mention']
        if 'change_lang' in request.form:
            errors += Check.lang(request.form['lang'], text)
            if not errors:
                if 'changes' not in session:
                    session['changes'] = {}
                session['changes'][text.input('change_lang')] = request.form['lang']
        if 'change_publish_date' in request.form:
            errors += Check.publish_date(request.form['publish_date'], text)
            if not errors:
                if 'changes' not in session:
                    session['changes'] = {}
                session['changes'][
                    text.input('change_publish_date')
                ] = Utils.reformat_date(request.form['publish_date'])
        if 'change_genre' in request.form:
            errors += Check.genre(request.form['genre'], text)
            if not errors:
                if 'changes' not in session:
                    session['changes'] = {}
                session['changes'][text.input('change_genres')] = request.form['genre']
        if 'delete_story' in request.form:
            if 'changes' not in session:
                session['changes'] = {}
            session['changes']['story'] = text.input('delete_story')
        if 'change_file_image' in request.form:
            try:
                image_format = re.search('\..*$', request.files['file_image'].filename)[0]
                image = Image.open(request.files['file_image'])
                image = image.resize((300, 300))
                image.save(EnvConf.images_dir + title + image_format)
            except:
                errors.append(text.error('cannot_load_image'))
        if 'conf_sub' in request.form and 'changes' in session:
            user = db.users.find_one({'username': session['username']})
            if Utils.hash(request.form['conf_password']) != user['password']:
                errors.append(text.error('wrong_password'))
            if not errors:
                if text.input('change_title') in session['changes']:
                    errors += Check.title(session['changes'][text.input('change_title')], text)
                    if not errors:
                        db.stories.update_one(
                            {'title': title},
                            {'$set': {'title': session['changes'][text.input('change_title')]}}
                        )
                        for image in os.listdir(EnvConf.images_dir):
                            if re.match(f'^{title}\..*$', image):
                                image_format = re.search('\..*$', image)[0]
                                os.rename(
                                    EnvConf.images_dir + image,
                                    EnvConf.images_dir + session['changes'][text.input('change_title')] + image_format
                                )
                                break
                        title = session['changes'][text.input('change_title')]
                if text.input('change_lang') in session['changes']:
                    errors += Check.lang(session['changes'][text.input('change_lang')], text)
                    if not errors:
                        db.stories.update_one(
                            {'title': title},
                            {'$set': {'lang': session['changes'][text.input('change_lang')]}}
                        )
                if text.input('change_description') in session['changes']:
                    errors += Check.description(session['changes'][text.input('change_description')], text)
                    if not errors:
                        db.stories.update_one(
                            {'title': title},
                            {'$set': {'description': Utils.translate(
                                session['changes'][text.input('change_description')],
                                story['lang']
                            )}}
                        )
                if text.input('change_mention') in session['changes']:
                    errors += Check.mention(session['changes'][text.input('change_mention')], text)
                    if not errors:
                        db.stories.update_one(
                            {'title': title},
                            {'$set': {'mention': Utils.translate(
                                session['changes'][text.input('change_mention')],
                                story['lang']
                            )}}
                        )
                if text.input('change_publish_date') in session['changes']:
                    errors += Check.mention(session['changes'][text.input('change_mention')], text)
                    if not errors:
                        db.stories.update_one(
                            {'title': title},
                            {'$set': {'mention': session['changes'][text.input('change_mention')]}}
                        )
                if text.input('change_genres') in session['changes']:
                    errors += Check.genre(session['changes'][text.input('change_genres')], text)
                    if not errors:
                        db.stories.update_one(
                            {'title': title},
                            {'$set': {
                                'genre': session['changes'][text.input('change_genres')].replace(',', '').split(' ')
                            }}
                        )
                if text.input('delete_story') in session['changes']['story']:
                    db.stories.delete_one({'title': title})
                    return redirect(url_for('creator', username=session['username']))
            session.pop('changes')
            return redirect(url_for('story_edit', title=title))
    page = {
        'title': text.title('edit', title=title),
        'description': text.description('edit')
    }
    return render_template(
        'edit.html',
        text=text,
        page=page,
        errors=errors,
        story=story
    )


@app.route('/story/<title>/image', methods=['GET'])
def story_image(title):
    for image in os.listdir(EnvConf.images_dir):
        if re.match(f'^{title}\..*$', image):
            return send_file(EnvConf.images_dir + image)


@app.route('/story/<title>/revisions/', methods=['GET', 'POST'])
def story_revisions(title):
    Utils.load_cookies()
    text = Text()
    ban = Utils.check_ban(text)
    if ban:
        return ban
    errors = []
    auto_redirect = Utils.check_account(True)
    if auto_redirect != (True, True):
        return auto_redirect
    story = db.stories.find_one({'title': title})
    upload_new_revision = False
    if request.method == 'GET':
        if request.args.get('date_download') is not None:
            return send_file(
                Utils.put_content_on_file(
                    story['content'][request.args.get('date_download')][story['lang']]
                ),
                as_attachment=True,
                download_name=f"{title} ~ {request.args.get('date_download')}.txt"
            )
        if request.args.get('upload_new_revision') is not None:
            upload_new_revision = eval(request.args.get('upload_new_revision'))
    if request.method == 'POST':
        if 'file_content' in request.files and session['username'] == story['creator']:
            story['content'][today().strftime("%d %b %Y")] = Utils.translate(
                request.files['file_content'].read().decode("utf-8"),
                story['lang']
            )
            db.stories.update_one(
                {'title': title},
                {'$set': {'content': story['content']}}
            )
    page = {
        'title': text.title('revisions', title=title),
        'description': text.description('revisions')
    }
    return render_template(
        'revisions.html',
        text=text,
        page=page,
        errors=errors,
        story=story,
        upload_new_revision=upload_new_revision
    )


@app.route('/robots.txt', methods=['GET'])
def robots():
    return send_file('robots.txt')


@app.route('/sitemap.txt', methods=['GET'])
def sitemap():
    return send_file(
        Utils.put_content_on_file("".join(
            [url_for(page, _external=True) + "\n" for page in ['home', 'signin', 'signup']] + [
                url_for(
                    'story_page',
                    title=story['title'],
                    _external=True
                ) + "\n" for story in db.stories.find() if Utils.past_date(story['publish_date'])
            ] + [
                url_for(
                    'creator',
                    username=user['username'],
                    _external=True
                ) + "\n" for user in db.users.find() if user['creator'] is not False
            ]
        )),
        download_name='sitemap.txt'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('fullchain.pem', 'privkey.pem'))
