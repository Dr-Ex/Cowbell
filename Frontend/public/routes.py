from flask import g, render_template, request, redirect, send_from_directory, flash
from werkzeug import secure_filename
from public import website
from generator import Song
from preview_generator import Preview
import cloud_save
from flask import jsonify, request
import os
import json
import sqlite3

###########
#Global Variables Start
###########
SERVER_DB_NAME = 'cloud_save.db'
SERVER_DB_DIRECTORY = 'public/static/db'
###########
#Global Variables End
###########


#
#    VISIBLE PAGES
#

#HOMEPAGE/NOTE AMOUNT ENTER
@website.route('/')
def index():
	return render_template('index.html')

#NEW PROJECT PAGE
@website.route('/newproject/', methods=['GET', 'POST'])
def newproject():
	error = None
	if request.method == 'POST':
		noteamt = request.form.get('notes')
		if noteamt == "" or noteamt == "0":
			error = "Please enter a non-zero integer."
			return render_template('newproject.html', error=error)
		else:
			noteamt = abs(int(noteamt))
			return redirect('/synth/{}'.format(str(noteamt)))
	else:
		return render_template('newproject.html')

#EXISTING PROJECT PAGE
@website.route('/oldproject/')
def oldproject():
	return render_template('oldproject.html')

#SYNTH PAGE
@website.route('/synth/<notes>/')#, methods=['GET', 'POST'])
def synth(notes = None):
	return render_template('synth.html', notes=notes, notes_no=None, values_to_set=None, project_data=None)


#DISPLAYS WHEN WAV EXPORTED
@website.route('/exported/', methods=['GET', 'POST'])
def exported():
	# if "audioformats" in request.form:
	# 	audioformat = request.form.get("audioformats")
	# 	return redirect('downloader/audiofile/{}'.format(audioformat))

	#Dictionary of the slider values that correspond to the note values
	noteDict = {0:"C4", 1:"D4", 2:"E4", 3:"F4", 4:"G4", 5:"A4", 6:"B4", 7:"C5"}
	sliderValues = {}
	noteValues = []
	sliderKeys = []
	linked_notes_dict = {}
	linked_note_keys = []
	linked_notes = []
	#Get the submitted slider values from the previous page
	rawSliderValues = request.values if request.method == "GET" else request.values
	#Extract the data from rawSliderValues and add it to sliderValues (Also get rid of "exporttowav")
	print(rawSliderValues)
	for key in rawSliderValues:
		if "slider" in key:
			print(key)
			temp_key = int(key[6:])
			sliderValues[temp_key] = rawSliderValues[key]
		elif "link" in key:
			temp_key = int(key[10:])
			linked_notes_dict[temp_key] = rawSliderValues[key]

	#Create a sorted list of the keys from slider values
	sliderKeys = sorted(sliderValues)
	linked_note_keys = sorted(linked_notes_dict)
	print(sliderKeys)
	#  Get each note value from the noteDict in order using the sorted sliderKeys 
	#  list to call values from sliderValues in the original order
	for item in sliderKeys:
		noteValues.append(noteDict[int(sliderValues[item])])
	for item in linked_note_keys:
		linked_notes.append(noteDict[int(linked_notes_dict[item])])
	#Convert noteValues to string
	sNoteValues = ''.join(noteValues)
	str_linked_notes = ''.join(linked_notes)
	jsondata = json.dumps({"songdata":sNoteValues, 
                        "linked_notes":str_linked_notes,
                        "author_name":'Anon', 
                        "outfile_name":None, 
                        "cloud_db_pos":None})
	print("JSON: ".format(jsondata))
	print(type(jsondata))
	#Return the exported page and attach the filename of the exported WAV file
	return render_template('exported.html', jsondata=jsondata)

#HELP PAGE
@website.route('/help/')
def help():
	return render_template('help.html')

@website.route('/projects/', methods = ['GET', 'POST'])
def userprojects():
	if request.method == 'POST':
		uid = request.form.get('uid')
		db = sqlite3.connect('{}/{}'.format(SERVER_DB_DIRECTORY, SERVER_DB_NAME))
		cursor = db.cursor()
		cursor.execute("SELECT author_name FROM users WHERE UID = ?",(uid,))
		author_name = cursor.fetchall()
		author_name = author_name[0][0]
		projects = cloud_save.list_projects(SERVER_DB_NAME, SERVER_DB_DIRECTORY, uid)
		print(type(uid))
		print(projects)
		print(type(author_name))
		return render_template("projects.html", author=author_name, projects=projects, uid=uid)
	else:
		return "Go back, you didn't enter a UID!"




##
#	BACKEND ROUTES (downloading and uploading files, play and stop preview in synth)
##

# When a user is directed to this page, it downloads the file they request from the output directory
@website.route('/return-file/<wavfilename>/')
def return_file(wavfilename):
	directory = '{}{}'.format(os.getcwd(),'/wav_outfiles/')
	return send_from_directory(directory, wavfilename, attachment_filename=wavfilename, as_attachment=True, mimetype='audio/wav')
	
@website.route('/uploader/', methods = ['GET', 'POST'])
def uploader_file():
	'''Handles the uploading of cowbell files'''
	if request.method == 'POST':
		noteDict = {"C4":0, "D4":1, "E4":2, "F4":3, "G4":4, "A4":5, "B4":6, "C5":7}
		f = request.files['file']
		f.save(secure_filename(f.filename))
		song_read = Song()
		song_read.read_from_database(f.filename)
		notes = len(song_read.notes_to_play) / 2
		notes_to_set = [song_read.notes_to_play[i:i+2] for i in range(0, len(song_read.notes_to_play) - 1, 2)]
		values_to_set = [noteDict[i] for i in notes_to_set]
		print(values_to_set)
	return render_template('synth.html', notes=notes, values_to_set=values_to_set, project_data=None)

@website.route('/return-db/<databasename>/')
def return_db(databasename):
	'''When a user is directed to a page, the database that is specified is downloaded'''
	directory = '{}/database_outfiles/'.format(os.getcwd())
	return send_from_directory(directory, databasename, attachment_filename=databasename, as_attachment=True)


@website.route('/preview/')
def preview_generator():
	'''Constructs a WAV file for preview on the synth page'''
	print("IN PREVIEW")
	note_nums_temp = request.args.get('param_send', '00000000')
	note_nums = list(note_nums_temp)
	noteDict = {0:"C4", 1:"D4", 2:"E4", 3:"F4", 4:"G4", 5:"A4", 6:"B4", 7:"C5"}
	slider_values = []
	for note in note_nums:
			slider_values.append(noteDict[int(note)])
	slider_values_string = ''.join(slider_values)
	preview_song = Preview(slider_values_string)
	previewFileName = preview_song.make_wav()
	previewFileName = previewFileName.replace('public','..')
	return jsonify(previewname=previewFileName)

@website.route('/downloader/', methods=['GET', 'POST'])
def downloader():
	'''Manages the download of zips'''
	if request.method =="POST":
		returnedjson = json.loads(request.form.get("returnedjson"))
		for i in returnedjson:
			print("value{}".format(i))
			print(i)
		
		# Generate the song from the json data
		#	REMEMBER TO ADD NOTE LINKING TO JSON

		song = Song(returnedjson["songdata"], 'dummy', returnedjson["author_name"], returnedjson["outfile_name"], returnedjson["cloud_db_pos"])
		

		if "audioformats" in request.form:
			#Create WAV file from the string version of noteValues
			# json_data = request.get_json()
			# print(type(json_data))
			#"songdata":sNoteValues, "author_name":'Anon', "outfile_name":None, "cloud_db_pos":None}
			#	REMEMBER TO ADD NOTE LINKING TO JSON
			
			wavFileName = song.make_wav(request.form.get("audioformats"))
			wavFileName = wavFileName.replace('wav_outfiles/','')

			return redirect('/return-file/{}'.format(wavFileName))


		elif "databasename" in request.form:

			databasename = song.write_to_database()
			return redirect('/return-db/{}'.format(databasename))
	return "You shouldn't be here. GO BACK!"

@website.route('/get_uid/')
def get_uid():
	'''Generates a new UID and checks if its already in the database'''
	import uuid
	used_uids = cloud_save.get_uids(SERVER_DB_NAME, SERVER_DB_DIRECTORY)
	uid = uuid.uuid4().hex
	while uid in used_uids:
		uid = uuid.uuid4().hex
	cloud_save.add_user(SERVER_DB_NAME, SERVER_DB_DIRECTORY, uid)
	print(uid)
	return jsonify(uid=uid)

@website.route('/get_project/<uid>/', methods=['GET', 'POST'])
def get_project(uid):
	if request.method == "POST":
		project_ID = request.form.get("project_ID")
		project_data = cloud_save.open_project(SERVER_DB_NAME, SERVER_DB_DIRECTORY, uid, int(project_ID))
		noteDict = {"C4":0, "D4":1, "E4":2, "F4":3, "G4":4, "A4":5, "B4":6, "C5":7}
		song_read = Song(notes_to_play=project_data[0][1], author_name=project_data[0][2], project_name=project_data[0][4], cloud_db_pos=project_data[0][0])
		notes = len(song_read.notes_to_play) / 2
		notes_to_set = [song_read.notes_to_play[i:i+2] for i in range(0, len(song_read.notes_to_play) - 1, 2)]
		values_to_set = [noteDict[i] for i in notes_to_set]
		return render_template('synth.html', notes=notes, values_to_set=values_to_set, user_song=True, project_data=project_data)
	else:
		return "You shouldn't be here! Go back and select a project."

@website.route('/add_project/<uid>/<project_data>/')
def add_project(uid, project_data):
	
	cloud_save.add_project()
	return None

@website.route('/get_projects/<uid>/')
def get_project_list(uid):
	projects = cloud_save.list_projects(SERVER_DB_NAME, SERVER_DB_DIRECTORY, uid)
	return render_template('project_list.html', projects=projects, uid=uid)
