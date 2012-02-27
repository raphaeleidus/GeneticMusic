import copy
import pprint
import random
import string
import pickle
import sys
import random
from urllib.request import urlopen
from progress_bar import ProgressBar

base = 41 #note value of middle A
octave = 12 #there are 12 potential notes in each octave
generationSize = 20 #how many songs should be generated in each generation
filename = "GeneticMusic" #.pkl will be added
noteList = ['A-1','A-1#','B-1','C-1','C-1#','D-1','D-1#','E-1','F-1','F-1#','G-1','G-1#',
        'A','A#','B','C','C#','D','D#','E','F','F#','G','G#',
        'A2','A2#','B2','C2','C2#','D2','D2#','E2','F2','F2#','G2','G2#',
        'A3','A3#','B3','C3','C3#','D3','D3#','E3','F3','F3#','G3','G3#']

keys = range(base, base+octave)
notes = {}
for i in range(len(noteList)): #build dictionary of notes to lookup the name of the note later
    notes[i+base-octave] = noteList[i]

class Mode:
    def __init__(self, name, notes):
        self.name = name
        self.notes = notes

modes = [
    Mode("Ionian", [0,2,4,5,7,9,11]),
    Mode("Dorian", [0,2,3,5,7,9,10]),
    Mode("Phrygian", [0,1,3,5,7,8,10]),
    Mode("Freygish", [0,1,4,5,7,9,11]),
    Mode("Lydian", [0,2,4,6,7,9,11]),
    Mode("Mixolydian", [0,2,4,5,7,9,10]),
    Mode("Aeolian", [0,2,3,5,7,8,10]),
    Mode("Locrian", [0,1,3,5,6,8,10])
    ]

class Scale:
    def __init__(self, key, mode):
        self.start = key
        self.key = notes[key]
        self.mode = mode
        self.scaleNotes = []
        for note in self.mode.notes:
            self.scaleNotes.append(note+self.start-octave)
        for note in self.mode.notes:
            self.scaleNotes.append(note+self.start)
        for note in self.mode.notes:
            self.scaleNotes.append(note+self.start+octave)
        self.scaleNotes.append(self.start+(2*octave)) #repeat the first scale degree 2 octaves up
    def mainOctave(self):
        return self.scaleNotes[8-1:(2*8)]

def randomWord(wordType):
    urls = ["http://api.wordnik.com/v4/words.json/randomWord?hasDictionaryDef=true&includePartOfSpeech=adverb,adjective&api_key=1a726d79d51b76f7664090f16750cc75292f05d3df6083875",
            "http://api.wordnik.com/v4/words.json/randomWord?hasDictionaryDef=true&includePartOfSpeech=noun,adjective,verb&api_key=1a726d79d51b76f7664090f16750cc75292f05d3df6083875"]
    words = str(urlopen(urls[wordType]).read()).replace('"', '')
    return dict(item.split(":") for item in words[3:-2].split(','))['word']

class Song:
    def __init__(self):
        self.mutationPoints = 10
        self.generation = 0
        self.songnum = 0
        self.name = randomWord(0) + " " + randomWord(1)
        self.bpm = random.randint(100, 200)
        self.key = random.randint(base,base+octave-1)
        self.mode = random.choice(modes)
        self.scale = Scale(self.key, self.mode)
        self.score = -1
    def __repr__(self):
        return ( "Song('name' : %s, 'number' : %s.%s, 'scale' : %s )" %(repr(self.name), repr(self.generation), repr(self.songnum), repr(self.scale))) 

    def getKey(self):
        return notes[self.key]

def prompt(prompt, options = [], required = False):
    if len(options) > 0:
        prompt = prompt + '[' + '|'.join(options) + ']'
    prompt = prompt + ': '
    resp = input(prompt)
    while (required and resp == "") or (len(options)> 0 and resp not in options and not (not required and resp == "")):
        print ("Please enter a valid option")
        resp = input(prompt)
    return resp

def main(argv=None):
    if argv is None:
        argv = sys.argv
    data = {"Generation": 0, "Songs": []}
    songs = data["Songs"]
    print ("Would you like to:\n\t[1]Load a previous saved generation\n\t[2]Generate a new random generation\n\t[3]Exit")
    choice = prompt("Please select an option", ["1", "2", "3"], True)
    if choice == "1":
        print ("Loading last generation")
        data = pickle.load(open(filename+".pkl", "rb"))
        songs = data["Songs"]
        for song in songs:
            print ("%d.%d: %s" % (song.generation, song.songnum, song.name))
            if song.score == -1:
                while True:
                    try:
                        score = float(prompt("Song score"))
                        song.score = score
                        pickle.dump(data, open(filename+".pkl", "wb"))
                        break
                    except ValueError:
                        print("Please enter a valid number")
            else:
                print ("Score: %s" % (song.score))
            print ()
            
    elif choice == "2":
        print ("Generating Songs")
        for i in ProgressBar.progressbar(range(generationSize)):
            songs.append(Song())
            s = songs[-1]
            s.songnum = i
        pickle.dump(data, open(filename+".pkl", "wb"))
        print("Generation 0 generated and saved to file")
    else:
        print("goodbye")
        data = pickle.load(open(filename+".pkl", "rb"))
        pprint.pprint(data)
        
if __name__ == "__main__":
    main()
