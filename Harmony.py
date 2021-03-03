class Harmony:

    def __init__(self, key, mode):
        self.key = key
        self.mode = mode

        #change the key to common key if given an enharmonic
        if key == 'Cb' and mode == 'Major':
            self.key = 'B'
        elif key == 'G#' and mode == 'Minor':
            self.key = 'Ab'
        elif key == 'Gb' and mode == 'Major':
            self.key = 'F#'
        elif key == 'D#' and mode == ' Minor':
            self.key = 'Eb'
        elif key == 'Db' and mode == 'Major':
            self.key = 'C#'
        elif key == 'A#' and mode == 'Minor':
            self.key = 'Bb'

        #make the notes for each key signature
        if key == 'C':
            self.scale = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
            if mode == 'Minor':
                self.scale[2] = self.scale[2] + 'b'
                self.scale[5] = self.scale[5] + 'b'
                self.scale[6] = self.scale[6] + 'b'
        elif key == 'G':
            self.scale = ['G', 'A', 'B', 'C', 'D', 'E', 'F#']
            if mode == 'Minor':
                self.scale[2] = self.scale[2] + 'b'
                self.scale[5] = self.scale[5] + 'b'
                self.scale[6] = self.scale[6][0]
        if key == 'D':
            self.scale = ['D', 'E', 'F#', 'G', 'A', 'B', 'C#']
            if mode == 'Minor':
                self.scale[2] = self.scale[2][0]
                self.scale[5] = self.scale[5] + 'b'
                self.scale[6] = self.scale[6][0]
        elif key == 'A':
            self.scale = ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#']
            if mode == 'Minor':
                self.scale[2] = self.scale[2][0]
                self.scale[5] = self.scale[5][0]
                self.scale[6] = self.scale[6][0]
        if key == 'E':
            self.scale = ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#']
            if mode == 'Minor':
                self.scale[2] = self.scale[2][0]
                self.scale[5] = self.scale[5][0]
                self.scale[6] = self.scale[6][0]
        elif key == 'B':
            self.scale = ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#']
            if mode == 'Minor':
                self.scale[2] = self.scale[2][0]
                self.scale[5] = self.scale[5][0]
                self.scale[6] = self.scale[6][0]
        if key == 'F#':
            self.scale = ['F#', 'G#', 'A#', 'B', 'C#', 'D#', 'E#']
            if mode == 'Minor':
                self.scale[2] = self.scale[2][0]
                self.scale[5] = self.scale[5][0]
                self.scale[6] = self.scale[6][0]
        elif key == 'C#':
            self.scale = ['C#', 'D#', 'E#', 'F#', 'G#', 'A#', 'B#', 'C#']
            if mode == 'Minor':
                self.scale[2] = self.scale[2][0]
                self.scale[5] = self.scale[5][0]
                self.scale[6] = self.scale[6][0]
        if key == 'Ab':
            self.scale = ['Ab', 'Bb', 'C', 'Db', 'Eb', 'F', 'G']
            if mode == 'Minor':
                self.scale[2] = self.scale[2] + 'b'
                self.scale[5] = self.scale[5] + 'b'
                self.scale[6] = self.scale[6] + 'b'
        elif key == 'Eb':
            self.scale = ['Eb', 'F', 'G', 'Ab', 'Bb', 'C', 'D']
            if mode == 'Minor':
                self.scale[2] = self.scale[2] + 'b'
                self.scale[5] = self.scale[5] + 'b'
                self.scale[6] = self.scale[6] + 'b'
        if key == 'Bb':
            self.scale = ['Bb', 'C', 'D', 'Eb', 'F', 'G', 'A']
            if mode == 'Minor':
                self.scale[2] = self.scale[2] + 'b'
                self.scale[5] = self.scale[5] + 'b'
                self.scale[6] = self.scale[6] + 'b'
        elif key == 'F':
            self.scale = ['F', 'G', 'A', 'Bb', 'C', 'D', 'E']
            if mode == 'Minor':
                self.scale[2] = self.scale[2] + 'b'
                self.scale[5] = self.scale[5] + 'b'
                self.scale[6] = self.scale[6] + 'b'

    def note_harmony(self, note):
        if note in self.scale:
            note_indx = self.scale.index(note)

            if note_indx >= 5:
                harmony_indx = note_indx + 2 - len(self.scale)

            else:
                harmony_indx = note_indx + 2

            harmony_note = self.scale[harmony_indx]
            return harmony_note

    def triad_harmony(self, note):
        if note in self.scale:
            root = note
            III = self.note_harmony(root)
            V = self.note_harmony(III)

            triad = [root, III, V]
            return triad

    def VII_chord(self, note):
        if note in self.scale:
            root = note
            III = self.note_harmony(root)
            V = self.note_harmony(III)
            VII = self.note_harmony(V)

            chord = [root, III, V, VII]
            return chord

    def dom_VII_chord(self, note):
        root = note
        III = self.note_harmony(root)
        V = self.note_harmony(III)

        if note == self.scale[0] or note == self.scale[3]:
            VII = self.note_harmony(V) + 'b'
        elif note == self.scale[4]:
            VII = self.note_harmony(V)

        chord = [root, III, V, VII]
        return chord

    def sus_IV_chord(self, note):
        if note == self.scale[0]:
            root = note
            IV = self.scale[3]
            V = self.scale[4]

            chord = [root, IV, V]
            return chord

    def sus_IX_chord(self, note):
        if note == self.scale[0]:
            root = note
            IV = self.scale[1]
            V = self.scale[4]

            chord = [root, IV, V]
            return chord

    def major_dom(self, note):
        if note == self.scale[4] and self.mode == 'Minor':
            root = note
            III = self.note_harmony(root)
            V = self.note_harmony(III)

            if 'b' in III:
                III = III[0]
            else:
                III += '#'

            chord = [root, III, V]
            return chord

