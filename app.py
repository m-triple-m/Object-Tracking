from flask import Flask, render_template, request, jsonify, redirect, Response, session, config
from object_movement import Object_Tracker
import masking
import json
from werkzeug import secure_filename 
import os
import cv2
from object_movement import Object_Tracker
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Mask(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String(50),nullable = False)
    mask_filename = db.Column(db.String(50),nullable = False)
    mask_values = db.Column(db.String(30), nullable = False)
    created = db.Column(db.String(20), nullable = False)


db.create_all()
app.secret_key = "uywetruwyriweyru"
values = [0, 0, 0, 255, 255, 255]

app.config['UPLOAD_FOLDER'] = './static/uploads'

@app.route('/')
@app.route('/home')
def home():
    return render_template('/index.html')

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
	if request.method == 'POST':
		file = request.files.get('file')
		if file:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			session['mask_file'] = file.filename
			return redirect('/mask')
	return render_template('mask_file_upload.html')

@app.route('/selectmask')
def select():
	id = request.args.get('id')
	mask = Mask.query.filter_by(id = id).first()
	session['mask_values'] = tuple(map(int, mask.mask_values.split(',')))
	return redirect('/trackobject')


@app.route('/trackobject')
def track():
    return render_template('track.html')


@app.route('/mask')
def mask():
	return render_template('mask.html', imgpath = f"static/uploads/{session.get('mask_file')}")


@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	mask_values = session.get('mask_values')
	if mask_values:
		print('session')
		return Response(getFrame(Object_Tracker(mask_values)), mimetype = "multipart/x-mixed-replace; boundary=frame")
	else:
		print('track bar')
		return Response(getFrame(Object_Tracker(masking.get_trackbar_values('HSV'))), mimetype = "multipart/x-mixed-replace; boundary=frame")

def getFrame(frame_obj):
	while True:
		yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            frame_obj.track_object() + b'\r\n')

@app.route("/get_thresh")
def getThreshImage():
	masking.setup_trackbars('HSV')
	# return the response generated along with the specific media
	# type (mime type)
	return Response(masking.main(f"static/uploads/{session.get('mask_file')}"),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


@app.route("/input")
def chInput():
	print(request.args.keys())
	# v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = list(map(int, request.args.values()))
	# print(v1_min, v2_min, v3_min, v1_max, v2_max, v3_max)
	global values
	values = list(map(int, request.args.values()))
	print('sdasdas', values)
	return jsonify('accepted')

@app.route("/result")
def result():
	return render_template('result.html')

@app.route('/setval')
def getValues():
	print(masking.get_trackbar_values('HSV'))
	return jsonify('success')

@app.route('/savemask')
def saveMask():
	filename = f"static/uploads/{session.get('mask_file')}"
	mask_filename = masking.convertMask(filename)
	maskobj = Mask(filename = filename, mask_filename = mask_filename, mask_values = ','.join(list(map(str, masking.get_trackbar_values('HSV')))), 
	created = datetime.today().strftime('%Y-%m-%d'))

	db.session.add(maskobj)
	db.session.commit()
	
	return jsonify('success')

@app.route('/showmasks')
def showMasks():
	mask_data = Mask.query.all()
	return render_template('masklist.html', datalist = mask_data)

@app.route('/maskdetail')
def maskDetails():
	id = request.args.get('id')
	mask = Mask.query.filter_by(id = id).first()
	return render_template('maskdetail.html', maskdata = mask)

if __name__ == "__main__":
    app.run(debug= True)


# 1) camera configuration
# 2) frame extraction
# 3) background subtraction
# 4) project setting system
# 5) view display manager
# 6) object detection
# 7) Tracking system