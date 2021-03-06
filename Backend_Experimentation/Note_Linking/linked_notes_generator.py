def gen_note(note, duration):
    import math
    import wave
    import struct
    note_list = [('A0', 27.50),('B0', 30.87),('C0', 16.35),('D0', 18.35),('E0', 20.60),('F0', 21.83),('G0', 24.50),
         ('A1', 55.00),('B1', 61.74	),('C1', 32.70),('D1', 36.71),('E1', 41.20),('F1', 43.65),('G1', 49.00),
         ('A2', 110.00),('B2', 123.47),('C2', 65.41),('D2', 73.42),('E2', 82.41),('F2', 87.31),('G2', 98.00),
         ('A3', 220.00),('B3', 246.94),('C3', 130.81,),('D3', 146.83),('E3', 164.81),('F3', 174.61),('G3', 196.00),
         ('A4', 440.00),('B4', 493.88),('C4', 261.63),('D4', 293.66),('E4', 329.63),('F4', 349.23),('G4', 392.00),
         ('A5', 880.00),('B5', 987.77),('C5', 523.25),('D5', 587.33),('E5', 659.25),('F5', 698.46),('G5', 783.99),
         ('A6', 1760.00),('B6', 1975.53),('C6', 1046.50),('D6', 1174.66),('E6', 1318.51),('F6', 1396.91),('G6', 1567.98),
         ('A7', 3520.00),('B7', 3951.07),('C7', 2093.00),('D7', 2349.32),('E7', 2637.02),('F7', 2793.83),('G7', 3135.96),
         ('A8',7040.00),('B8', 7902.13),('C8', 4186.01),('D8', 4698.63),('E8', 5274.04),('F8', 5587.65),('G8', 6271.93)]
    note_dic = dict(note_list)
    frequency = note_dic[note]
    sampleRate = 44100.0
    SAMPLE_LEN = sampleRate * duration
    noise_output = wave.open('{}.wav'.format(note), 'w')
    noise_output.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
    sounds = []
    for i in range(0, int(SAMPLE_LEN)):
        packed_value = struct.pack('<h', int(32767.0*math.cos(frequency*math.pi*float(i)/float(sampleRate))))
        sounds.append(packed_value)
    sounds_str = b''.join(sounds)
    noise_output.writeframes(sounds_str)
    noise_output.close()

def main():
    notes_to_play = 'C4C4C5C5B4G4A4B4C5C4C4A4A4G4G4G4G4'
    note_linking = '1000000000000101'
    UNIT_LENGTH = 2
    linked_notes = list(note_linking)
    note_list = [notes_to_play[i:i+UNIT_LENGTH] for i in range(0, len(notes_to_play), UNIT_LENGTH)]
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
main()
