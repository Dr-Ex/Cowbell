class Song:
        
    #   REMEMBER TO ADD NOTE LINKING TO JSON

    def __init__(self, notes_to_play='C4C4C5C5B4G4A4B4C5C4C4A4A4G4G4G4G4', note_linking='dummy', author_name='Anon', project_name='My Project', outfile_name=None, cloud_db_pos=None):
        """ Constructs the song object """
        import datetime
        self.cloud_db_pos = cloud_db_pos
        self.CROSSFADE_LENGTH = 50
        self.UNIT_LENGTH = 2
        self.notes_to_play = notes_to_play
        self.project_name = project_name
        self.creation_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        self.DB_DIRECTORY = 'database_outfiles/'
        self.WAV_DIRECTORY = 'wav_outfiles/'
        if note_linking == 'dummy':
            self.linked_notes = "0" * int((len(notes_to_play) / 2))
        else:
            self.linked_notes = note_linking
        if outfile_name == None:
            self.outfile_name = "{}music{}".format(self.WAV_DIRECTORY,self.creation_date)
        else:
            self.outfile_name = "{}{}".format(self.WAV_DIRECTORY,outfile_name)
        self.database_name = "music{}.cowbell".format(self.creation_date)
        self.outfile = str('{}'.format(self.outfile_name))
        self.author_name = author_name
        
    def make_wav(self, fileformat="wav"):
        """ Makes the song from notes_to_play"""
        from pydub import AudioSegment
        outfile_name = "{}.{}".format(self.outfile, fileformat)
        print(outfile_name)
        self.generated_notes = []
        if '1' in self.linked_notes:
            notes = self._linked_note_parser()
            infiles = []
            for note in notes:
                if isinstance(note, list):
                    note_length = len(note)
                    self._gen_note(note[0], note_length)
                    infiles.append('gened_notes/{}{}.wav'.format(note[0], note_length))
                    self.generated_notes.append('gened_notes/{}{}.wav'.format(note[0], note_length))
                else:
                    infiles.append('sound_array/{}.wav'.format(note))
        else:
            notes = [self.notes_to_play[i:i+self.UNIT_LENGTH] for i in range(0, len(self.notes_to_play), self.UNIT_LENGTH)]
            infiles = ['sound_array/{}.wav'.format(x) for x in notes]
        combinedAudio = AudioSegment.from_wav(infiles[0])
        infiles.pop(0)
        for infile in infiles:
            combinedAudio = combinedAudio.append(AudioSegment.from_wav(infile), crossfade=self.CROSSFADE_LENGTH)
        combinedAudio.export(outfile_name, format=fileformat, tags={'artist': self.author_name})
        self.garbage_gen_notes()
        return outfile_name
    
    def garbage(self, fileformat):
        """ Deletes the file (Hopefully this will be automated one day) """
        import os
        if fileformat == "cowbell":
            os.remove("{}{}".format(self.DB_DIRECTORY, self.database_name))    
        else:
            os.remove("{}{}".format(self.WAV_DIRECTORY, self.outfile))
        
    def garbage_gen_notes(self):
        """ Removes any notes made during son compilation """
        import os
        for file in set(self.generated_notes):
            os.remove(file)
        
    def write_to_database(self):
        """ Writes the song to an SQLite3 Database """
        import sqlite3
        db = sqlite3.connect('{}{}'.format(self.DB_DIRECTORY,self.database_name))
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE song_data
             (row_id INTEGER PRIMARY KEY, song_notes TEXT, author_name TEXT, creation_date TEXT, project_name TEXT)''')
        cursor.execute("INSERT INTO song_data VALUES (1,?,?,?,?)",(self.notes_to_play, self.author_name, self.creation_date, self.outfile_name))
        db.commit()
        db.close()
        return self.database_name

    def read_from_database(self, database_name):
        """ This might need to be moved to somewhere else. (As the song has already been constructed) """
        import os
        import sqlite3
        db = sqlite3.connect(database_name)
        cursor = db.cursor()
        cursor.execute("select song_notes from song_data")
        self.notes_to_play = cursor.fetchall()
        self.notes_to_play = "".join(map("".join, self.notes_to_play))
        cursor.execute("select author_name from song_data")
        self.author_name = cursor.fetchall()
        self.author_name = "".join(map("".join, self.author_name))
        cursor.execute("select creation_date from song_data")
        self.creation_date = cursor.fetchall()
        self.creation_date = "".join(map("".join, self.creation_date))
        cursor.execute("select project_name from song_data")
        self.outfile_name = cursor.fetchall()
        self.outfile_name = "".join(map("".join, self.outfile_name))
        self.outfile = str(self.outfile_name)
        db.close()
        os.remove(database_name)
        
    def _linked_note_parser(self):
        """ Parses a song with linked notes """
        linked_notes = list(self.linked_notes)
        note_list = [self.notes_to_play[i:i+self.UNIT_LENGTH] for i in range(0, len(self.notes_to_play), self.UNIT_LENGTH)]
        linked_notes_dup = linked_notes
        list_with_groups = []
        note_index = 0
        cur = linked_notes_dup[0]
        while len(linked_notes_dup) > 0:
            if cur == '1' and note_list[note_index] == note_list[note_index + 1]:
                group = [note_list[note_index]]
                while cur == '1' and note_list[note_index] == note_list[note_index + 1]:
                    group.append(note_list[note_index])
                    linked_notes_dup.pop(0)
                    if len(linked_notes_dup) == 0:
                        break
                    note_index += 1
                    cur = linked_notes_dup[0]
                list_with_groups.append(group)
            else:
                list_with_groups.append(note_list[note_index])
            if len(linked_notes_dup) == 0:
                break
            note_index += 1
            linked_notes_dup.pop(0)
            cur = linked_notes_dup[0]
        return list_with_groups

    def _gen_note(self, note, duration):
        import math
        import wave
        import struct
        # Calculate Semitones
        semi_tones = 0
        
        # Add Octaves
        semi_tones += 12 * int(note[1])
        
        # Adjust for note
        if "b" in str.lower(note[0]):
            semi_tones += 3
        elif "c" in str.lower(note[0]):
            semi_tones -= 9
        elif "d" in str.lower(note[0]):
            semi_tones -= 7
        elif "e" in str.lower(note[0]):
            semi_tones -= 5
        elif "f" in str.lower(note[0]):
            semi_tones -= 4
        elif "g" in str.lower(note[0]):
            semi_tones -= 2
        
        # Complicated math. Calculate Equal Temperament frequency. 
        frequency = 27.5 * (2**(1/float(12))) ** semi_tones
        
        sampleRate = 44100.0
        SAMPLE_LEN = sampleRate * duration * 0.5
        noise_output = wave.open('gened_notes/{}{}.wav'.format(note,duration), 'w')
        noise_output.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
        sounds = []
        for i in range(0, int(SAMPLE_LEN)):
            packed_value = struct.pack('<h', int(32767.0*math.cos(frequency*math.pi*float(i)/float(sampleRate))))
            sounds.append(packed_value)
        sounds_str = b''.join(sounds)
        noise_output.writeframes(sounds_str)
        noise_output.close()
