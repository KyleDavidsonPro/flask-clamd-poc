from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
import pyclamd
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/tmp/virus_poc/files'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'some_secret'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            return redirect(url_for('uploaded_file',filename=filename))
    return render_template('hello_world.html')


@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):

    if request.method == 'POST':
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    try:
        # Create object for using unix socket

        cd = pyclamd.ClamdUnixSocket(filename='/usr/local/var/run/clamav/clamd.sock')
        virus_found = cd.scan_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if virus_found is None:
            return render_template('file_uploaded.html', info="Virus Not Found", filename=filename)
        else:
            return render_template('file_uploaded.html', info="Virus Found", filename=filename)
    except ConnectionError:
        raise ValueError("could not connect to clamd server either by unix socket")



if __name__ == '__main__':
    app.run()
