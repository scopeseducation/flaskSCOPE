from flask import render_template, redirect, url_for, flash, request, g, stream_with_context
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, QR_image
import os
from time import sleep
from werkzeug import secure_filename
import tempfile

#file upload code from:
#http://flask.palletsprojects.com/en/1.0.x/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def activate_new_status():

   #copy current run mode to ramdisk - for continuous reading
   os.system('cp ' + os.path.join(app.config['UPLOAD_FOLDER'], "run_mode.txt") + ' /media/ramdisk/.')

   f = open('/media/ramdisk/run_mode.txt', 'r')
   current_status = f.readline()
   f.close()

   app.config['STATUS'] = current_status

   if current_status == 'DisplayScope':
      #copy current configuration file to ramdisk
      os.system("cp " + os.path.join(app.config['UPLOAD_FOLDER'], "qr_config.txt") + " /media/ramdisk/.")

      #send stop signal - to kill any script running in the background
      os.system('echo stop > /media/ramdisk/qr_code.stop')
      sleep(2)
      os.system('rm /media/ramdisk/qr_code.stop')

      #restart script to reload the config file
      os.system(os.path.join(app.config['EXT_SCRIPT_FOLDER'], "qr_read.py") + " &")

   if current_status == 'CBS':
      #copy current configuration file to ramdisk
      os.system("cp " + os.path.join(app.config['LOG_FOLDER'], "status.txt") + " /media/ramdisk/.")

      #send stop signal - to kill any script running in the background
      os.system('echo stop > /media/ramdisk/qr_code.stop')
      sleep(3)
      os.system('rm /media/ramdisk/qr_code.stop')

      print ("CBS started")

   if current_status == 'DNAScope':
      #copy current configuration file to ramdisk
      os.system("cp " + os.path.join(app.config['LOG_FOLDER'], "seq_config.txt") + " /media/ramdisk/.")

      #send stop signal - to kill any script running in the background
      os.system('echo stop > /media/ramdisk/qr_code.stop')
      sleep(3)
      os.system('rm /media/ramdisk/qr_code.stop')

      #start script to reload the config file
      os.system(os.path.join(app.config['EXT_SCRIPT_FOLDER'], "seq_scan.py") + " &")

      print ("SeqScope started")

@app.route('/')
@app.route('/index')
def index():
    #depending on whether the user is authenticated login standard user
    #if not current_user.is_authenticated:
    f = open('/media/ramdisk/run_mode.txt', 'r')
    current_status = f.readline()
    f.close()

    if current_user.is_authenticated:
        user = User.query.filter_by(username=current_user.username).first()
        username=current_user.username
        current_status = user.get_status()
    else:
        username='anonymous'

    print (current_status)

    #execute the runmode here
    if current_status == 'CBS':
        return redirect(url_for('CBS_main'))

    elif current_status == 'DisplayScope':
        #read the file from RAMDISK

        #on first request no file is there yet - display a message
        try:
            f = open('/media/ramdisk/qr_current.txt','r')
            current_file = f.read()
            f.close()

            file_parts = current_file.split('\t')

            #if os.path.splitext(file_parts[1])[1] in ('.mp3', '.mp4', '.mkv', '.mov'):
            if current_file.rsplit('.', 1)[1].lower() in ['mp3', 'mp4']:
                file_type = 'movie'
            else:
                file_type = 'image'

            return render_template('DisplayScope_main.html', title='Display Scope', user=username, file_name = url_for('static', filename = file_parts[1]), file_type = file_type)

        except:
            return render_template('DisplayScope_main.html', title='Display Scope', user=username, file_name = url_for('static', filename = 'no_img.jpg'), file_type = 'image')

    elif current_status == 'DNAScope':
        #read the file from RAMDISK

        #on first request no file is there yet - display a message
        try:
            f = open('/media/ramdisk/seq_current.txt','r')
            current_file = f.read()
            f.close()

            file_parts = current_file.split('\t')

            #allow the possibility to display a movie
            if os.path.splitext(file_parts[1])[1] in ('mp3', '.mp4', '.mkv', '.mov'):
                file_type = 'movie'
            else:
                file_type = 'image'

            return render_template('SeqScope_main.html', title='DNA Scope', user=username, file_name = url_for('static', filename = file_parts[1]), file_type = file_type)

        except:
            return render_template('SeqScope_main.html', title='DNA Scope', user=username, file_name = url_for('static', filename = 'no_valid_seq.jpg'), file_type = 'image')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('setup'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('setup'))

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    #user = User.query.filter_by(username=current_user.username).first()
    logout_user()
    #copy relevant config files to ramdisk
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        user.set_status('CBS')
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

#reset user password - might be useful
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    #here only password change of current user is allowed
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        user.set_password(form.password.data)
        db.session.commit()

        flash('new password set!')
        return render_template('setup.html', title = 'setup FlaskScope', status = app.config['STATUS'])

    return render_template('change_password.html', form=form)

@app.route('/do_config')
def do_config():
   #define dict with file infos
   dict = []

   #read the database for current user
   user = User.query.filter_by(username=current_user.username).first()
   qall = user.qr_codes.all()

   if len(qall) == 0:
      #render some error to the management page
      flash('no file uploaded!')
      return render_template('setup.html', title = 'setup FlaskScope', status = app.config['STATUS'])
   else:
      for q in qall:
         #dict[str(i)] = qall[i].image + "," + qall[i].qr_code 
         dict.append(q.image + "," + q.qr_code)

   print (dict)
   return render_template('do_config_v2.html', result = dict)

@app.route('/update_config', methods=['GET', 'POST'])
def update_config():
       #stitch together a new config file
   if request.method == 'POST':
      if 'empty' in request.form:
         return "empty"
      else:
         #initialise container
         file_IDs_toDelete = []

         #get current user
         user = User.query.filter_by(username=current_user.username).first()

         #get data from management page
         data = request.form.to_dict(flat=False)

         #initialise counter to report changed files
         updated_files = 0
         for key in data :
            #first pass - collect all files to delete
            if "del" in str(key):
               file_IDs_toDelete.append(data[key][0])
            else:
            #check if QR code changed

               if str(key) in str(user.qr_codes.all()):

                  q = user.qr_codes.filter_by(image=str(key)).all()

                  if not q[0].qr_code == data[key][0]:
                     q[0].qr_code = data[key][0]
                     updated_files = updated_files + 1

         deleted_files = 0

         for file_name in file_IDs_toDelete:
            #second pass - delete files
            deleted_files = deleted_files + 1 
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
 
            q = user.qr_codes.filter_by(image=file_name).all()
            db.session.delete(q[0])

         db.session.commit()

         #compile a status report and render page
         m_status = "updated info for " + str(updated_files) + " files and removed " + str(deleted_files) + " files"
         return render_template("setup.html", title = 'setup FlaskScope', status = app.config['STATUS'])

@app.route('/use_current_config')
def use_current_config():
   user = User.query.filter_by(username=current_user.username).first()
   qall = user.qr_codes.all()

   cur_stat=user.get_status()
   flash('current status: ' + cur_stat)

   #write current status to file
   f = open(os.path.join(app.config['UPLOAD_FOLDER'], "run_mode.txt"), "w+")
   f.write(user.get_status())
   f.close()

   if user.get_status() == 'DisplayScope':

      if len(qall) == 0:
         #this also happens if all files were deleted - clean qr_config.txt here
         flash('no file uploaded yet!')

         f = open(os.path.join(app.config['UPLOAD_FOLDER'], "qr_config.txt"), "w+")
         f.write('')
         f.close()

      else:
         f = open(os.path.join(app.config['UPLOAD_FOLDER'], "qr_config.txt"), "w+")
         for q in qall:
            f.write(q.image + "\t" + q.qr_code + "\n")
         f.close()

   activate_new_status()

   flash('saved current status')
   return render_template('setup.html', title = 'setup FlaskScope', status=app.config['STATUS'])

@app.route('/setup')
def setup():
    user = User.query.filter_by(username=current_user.username).first()
    cur_stat = user.get_status()
    flash('current status: ' + cur_stat)

    return render_template('setup.html', title = 'setup FlaskScope', status=app.config['STATUS'])

@app.route('/set_default')
def set_default():
    #read current mode
    user = User.query.filter_by(username=current_user.username).first()
    mode = request.args.get('mode')
    user.set_status(mode)
    db.session.commit()

    cur_stat = user.get_status()
    flash('current status: ' + cur_stat)

    app.config['STATUS'] = cur_stat

    return render_template('setup.html', title = 'setup FlaskScope', status=app.config['STATUS'])

@app.route('/do_upload')
def do_upload():
   return render_template('do_upload.html', title='Upload File')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        tempfile.tempdir = app.config['UPLOAD_FOLDER']

        user = User.query.filter_by(username=current_user.username).first()
        cur_stat = user.get_status()
        flash('current status: ' + cur_stat)

        # check if the post request has the file part
        if 'file' not in request.files:
           flash('upload error: no file part')
           return render_template('setup.html', title = 'setup FlaskScope', status=app.config['STATUS'])

        file = request.files['file']

        print (file)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('upload error: no file selected')
            return render_template('setup.html', title = 'setup FlaskScope', status=app.config['STATUS'])

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #chunk upload idea from here
            #with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'bw') as f:
            #   chunk_size = 4096
            #   while True:
            #      chunk = request.stream.read(chunk_size)
            #      if len(chunk) == 0:
            #         return
            #      f.write(chunk)

            #check if a file with that name was uploaded before
            if not filename in str(user.qr_codes.all()):

               q = QR_image(qr_code="add_qr_code", image=filename, author=user)
               db.session.add(q)
               db.session.commit()

               flash('file uploaded: ' + filename)
            else:
               flash('file already exists: ' +filename)
        else:
            flash('file extension not allowed: ' + file.filename)

    return render_template('setup.html', title = 'Setup FlaskScope', status=app.config['STATUS'])

#at startup copy the config file to ramdisk
@app.before_first_request
def before_request():
    print ('activating status')
    print (app.config['BASE_FOLDER'])
    activate_new_status()

