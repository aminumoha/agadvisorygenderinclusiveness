import os
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, send_file, render_template, flash, url_for, session
from agadvisory import generate_similarity, process_review

UPLOAD_FOLDER = '/uploads/'
Gender_Files_Folder = '/experimentation/gender_files/'
Gender_Inclusive_Folder = '/experimentation/gender_inclusive/'
All_Articles_Folder = '/experimentation/all_articles/'
# app = Flask(__name__)
app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 *1024

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# Upload API
@app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("saved file successfully")

            # dosimilairty comparision
            is_gen_inclusive = generate_similarity(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            isok = is_gen_inclusive.split(',')[0]
            if (isok == 'true'):
                flash(filename + "-  is predicted to be Gender Inclusive with average similarity index of : " +
                      is_gen_inclusive.split(',')[1] + "  with gender docs.")
                return redirect(url_for('upload_file'))
            else:
                flash(filename + "- is predicted NOT to be gender inclusive  with average similarity index of : " +
                      is_gen_inclusive.split(',')[1] + "  with gender docs.")
                return redirect(url_for('upload_file'))
                # return redirect('/downloadall')

    return render_template('upload_file.html')


# Download API
@app.route("/downloadfile/<filename>", methods=['GET'])
def download_file(filename):
    return render_template('download.html', value=filename)


@app.route("/downloadall", methods=['GET'])
def download_all():
    path = os.getcwd() + "/experimentation/gender_inclusive/"
    files = os.listdir(path)
    return render_template('downloadall.html', value=files)


@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = os.getcwd() + "/experimentation/gender_inclusive/" + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


@app.route('/return-files-from-source/<filename>')
def return_files_fromsource(filename):
    file_path = os.getcwd() + "/experimentation/all_articles/" + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


@app.route('/return-non-inclusive-files/<filename>')
def return_files_tutnon(filename):
    file_path = "/uploads/" + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


@app.route('/accept-review', methods=['GET','POST'])
def accept_review():
    review_result=request.form['review']
    message=request.form['msg']
    filename = request.form['filename']
    info=process_review(os.path.join(app.config['UPLOAD_FOLDER'], filename),review_result,message)
    return render_template('expert-review.html', value=review_result,info=info)


@app.route('/testalldownloadeddocs', methods=['GET'])
def test_files():
    result = []
    files = os.listdir(os.getcwd() + "/experimentation/all_articles/")
    count = 0
    for filename in files:
        rest = filename
        rest += "*" + filename
        is_gen_inclusive = generate_similarity(os.getcwd() + "/experimentation/all_articles/" + filename)
        rest += "*" + is_gen_inclusive.split(',')[1]
        result.append(rest)
        count = count + 1
        if count == 10:
            break
    return render_template('testalldocs.html', value=result)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
