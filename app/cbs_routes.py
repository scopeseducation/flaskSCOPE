import os
import datetime, time
import glob
from PIL import Image
from app import app
from flask import send_from_directory, render_template, redirect, url_for, flash, request, g
from app import app

#app = Flask(__name__, static_url_path='/static')

def inString(main_string, sub_string):
    if main_string.find(sub_string) > -1:
        return True
    else:
        return False

def read_status(document_path):
    f = open(document_path, "r")
    lines = f.read()
    f.close()
    app.config['CBS_STATUS'] = lines

@app.route('/CBS_main')
def CBS_main():
    #initialise messages
    tar_message = ''
    rm_message = ''
    done_message = ''

    #first determine the status of device
    #document_path = os.path.abspath(os.path.dirname(__file__)) + '/logs/status.txt'
    document_path = '/media/ramdisk/status.txt'

    #all python scripts show up as python
    x = os.system("pgrep CBS")

    #if app.config['CBS_STATUS'] == '':
    f = open(document_path, "r")
    lines = f.read()
    f.close()
    app.config['CBS_STATUS'] = lines
    #else:
    #    print ('status already saved')
    #    lines = app.config['CBS_STATUS']

    print ('lines: ', lines)

    if inString(lines, 'running'):

        #x = os.system("pgrep ScopesTimelapse")

        if (x==0):
            #process still running
            status = 'running'
        else:
            flash('timelapse ended unexpectedly, images might have been saved, please download and/or delete images for new run')
            status = 'done'

    if inString(lines, 'done'):
        #nothing to do
        status='done'

    if inString(lines, 'idle'):
        #nothing to do
        status='idle'
        flash('start new timelapse')

    if inString(lines, 'creating_container'):
        #x = os.system("pgrep tar")

        if (x==0):
            #still running
            status = 'creating_container'
            flash('still creating container')

        else:
            #double check that tar process did not end just after page refresh was invoked
            time.sleep(1)
            f = open(document_path, "r")
            lines = f.read()
            f.close()
            app.config['CBS_STATUS'] = lines
            print (lines)

            if inString(lines, 'container_ready'):
                #indeed process finished correctly - force refresh
                return redirect(url_for('CBS_main'))
            else:
                #something went wrong during perparation of the container
                flash('creating image container ended unexpectedly, please try again')
                status = 'done'

    if inString(lines, 'container_ready'):
        #nothing to do
        status = 'container_ready'
        flash('image container ready for download')

    if inString(lines, 'doing_rm'):
        #x = os.system("pgrep rmImages")

        if (x==0):
            #still running
            status = "doing_rm"
            flash('removal still in process')
        else:
            #check
            #read new status
            read_status(document_path)

            if app.config['CBS_STATUS'] == 'idle':
                status = 'idle'
                flash('image removal successful')
                flash('ready to start new timelapse')
            else:
                status = "done"
                flash('something went wrong during file removal, please try again')

    #write out new status
    if not inString(lines, status):
        f = open(document_path, "w")
        f.write(status)
        f.close()
        app.config['CBS_STATUS'] = status

    return render_template("CBS_main_page.html", CBS_status = status)

@app.route('/start_timelapse', methods = ['GET', 'POST'])
def start_timelapse():
   if request.method == 'POST':
      result = request.form.to_dict()

      start_time = time.time()
      document_path = os.path.abspath('/media/ramdisk/tl_setup.config.txt')

      f = open(document_path, "w")
      f.write(str(result) + '\n')
      f.write(str(start_time))
      f.close()

      document_path = os.path.abspath(os.path.dirname(__file__)) + '/logs/status.txt'
      f = open(document_path, "w")
      f.write("running\n")
      f.close()

      f = open('/media/ramdisk/status.txt', "w")
      f.write("running\n")
      f.close()

      app.config['CBS_STATUS'] = 'running'

      tl_script = os.path.abspath(os.path.dirname(__file__)) + '/ext_scripts/CBS_timelapse.py ' + os.path.dirname(__file__) + ' 2> /media/ramdisk/cbs_tl.err > /media/ramdisk/cbs_tl.out &'
      print (tl_script)

      os.system(tl_script)

      flash('timelapse started')
   else:
      flash('something went wrong')

   return redirect(url_for('CBS_main'))

@app.route('/setup_timelapse')
def setup_timelapse():
   return render_template("CBS_tl_setup.html", title='set up new timelapse')

@app.route('/get_status')
def get_status():

   #identify here the number of images taken so far
   file_list = [os.path.basename(x) for x in glob.glob(os.path.abspath(os.path.dirname(__file__)) + '/static/images/*.jpg')]
   file_list.sort()

   #to do: catch case where the first image has not yet been taken!
   if (len(file_list) == 0):
       flash('no image taken yet!')
       return redirect(url_for("CBS_main"))

   #identify here the dimensions of the newest image - using PIL
   im = Image.open(os.path.abspath(os.path.dirname(__file__)) + '/static/images/' + file_list[len(file_list)-1])
   actual_width, actual_height = im.size

   #status page with some infos on running timelapse
   document_path = '/media/ramdisk/tl_setup.config.txt'
   f = open(document_path, "r")
   lines=f.read()
   f.close()

   elapsed_time = time.time() - float(lines.split('\n')[1])

   time_to_display = str(datetime.timedelta(seconds = elapsed_time))

   image_fn = '/static/images/' + file_list[len(file_list)-1]
   return render_template("CBS_show_current.html", title = 'Current status', img_name = image_fn, img_taken_number = str(len(file_list)), runtime = time_to_display)

@app.route('/create_container')
def create_container():

   #report new status
   document_path = os.path.abspath(os.path.dirname(__file__)) + '/logs/status.txt'
   f = open(document_path, "w")
   f.write("creating_container\n")
   f.close()

   f = open('/media/ramdisk/status.txt', "w")
   f.write("creating_container\n")
   f.close()

   app.config['CBS_STATUS'] = "creating_container"

   tarImages_script = os.path.abspath(os.path.dirname(__file__)) + '/ext_scripts/scopesCBS_tar.py ' + os.path.dirname(__file__) + ' &'
   os.system(tarImages_script)

   return redirect(url_for("CBS_main"))

@app.route('/download_container')
def download_container():
    document_path = os.path.abspath(os.path.dirname(__file__)) + '/static/images/'

    #find all tar.gz files
    file_list = [os.path.basename(x) for x in glob.glob(document_path + '*.tar.gz')]
    #document_path = os.path.abspath(os.path.dirname(__file__)) + '/static/images'
    #find the tar.gz file to create the link
    #note that this file has a datetime stamp so changes every time
    print(document_path, file_list[0])

    return send_from_directory(document_path, file_list[0], as_attachment=True)

#not used up to now
@app.route('/download_movie')
def download_movie():
   return render_template("movie_page_templ.html", img_width = 250, img_height = 250, main_page_URL = url_for("main_screen"))

@app.route('/delete_files')
def delete_files():
    #run python script to remove files
    rmImages_script = os.path.abspath(os.path.dirname(__file__)) + '/ext_scripts/rmImagesCBS.py ' + os.path.dirname(__file__) + ' &'
    os.system(rmImages_script)

    #report new status
    document_path = os.path.abspath(os.path.dirname(__file__)) + '/logs/status.txt'
    f = open(document_path, "w")
    f.write("doing_rm\n")
    f.close()

    f = open('/media/ramdisk/status.txt', "w")
    f.write("doing_rm\n")
    f.close()

    app.config['CBS_STATUS'] = "doing_rm"

    time.sleep(1)
    return redirect(url_for("CBS_main"))

@app.route('/stop_timelapse')
def stop_timelapse():

    #stops a running timelapse by sending a signal via file on ramdisk
    f = open("/media/ramdisk/abort_signal", "w")
    f.write("1")
    f.close()

    document_path = os.path.abspath(os.path.dirname(__file__)) + '/logs/status.txt'
    f = open(document_path, "w")
    f.write("done\n")
    f.close()

    f = open('/media/ramdisk/status.txt', "w")
    f.write("done\n")
    f.close()

    app.config['CBS_STATUS'] = "done"

    #write out status
    #report success in status page - wait 2 seconds for stopping to happen
    time.sleep(2)

    return redirect(url_for("CBS_main"))

#not used so far
@app.route('/create_movie')
def create_movie():
   with open("/media/ramdisk/root_cmd.txt", 'w') as f:
      f.write("/var/www/FlaskApp/Scopes_CBS/createMovie.py")
      f.close()

   return redirect(url_for("CBS_main"))

@app.route('/shutdown')
def shutdown():
    #run shutdown program
    os.system('flask_sd')
    return redirect(url_for("CBS_main"))

if __name__ == '__main__':
   app.run(debug = False)
