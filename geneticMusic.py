import copy
from pprint import pprint
import random
import string
import pickle
import sys
import random
import os
from urllib.request import urlopen
from progress_bar import ProgressBar
from midiutil.MidiFile3 import MIDIFile

middleC = 60
base = middleC-3 #note value of middle A
octave = 12 #there are 12 potential notes in each octave
generationSize = 20 #how many songs should be generated in each generation
filename = "GeneticMusic" #.pkl will be added
songFolder = "Songs"
noteList = ['A-1','A-1#','B-1','C-1','C-1#','D-1','D-1#','E-1','F-1','F-1#','G-1','G-1#',
        'A','A#','B','C','C#','D','D#','E','F','F#','G','G#',
        'A2','A2#','B2','C2','C2#','D2','D2#','E2','F2','F2#','G2','G2#',
        'A3','A3#','B3','C3','C3#','D3','D3#','E3','F3','F3#','G3','G3#']

keys = range(base, base+octave)
notes = {}
for i in range(len(noteList)): #build dictionary of notes to lookup the name of the note later
    notes[i+base-octave] = noteList[i]

class Chord:
    def __init__(self):
        self.notes=[] 
        self.duration = int(random.triangular(1,4,1))
        self.intensity = random.randint(1, 10) * 10
    def addRandomNotes(self, count):
        self.notes = random.sample(range(48), count)
    def __repr__(self):
      return ( "%s" % (repr(self.notes)))

def randomWord(wordType):
    urls = ["http://api.wordnik.com/v4/words.json/randomWord?hasDictionaryDef=true&includePartOfSpeech=adverb,adjective&api_key=1a726d79d51b76f7664090f16750cc75292f05d3df6083875",
            "http://api.wordnik.com/v4/words.json/randomWord?hasDictionaryDef=true&includePartOfSpeech=noun,adjective,verb&api_key=1a726d79d51b76f7664090f16750cc75292f05d3df6083875"]
    words = str(urlopen(urls[wordType]).read()).replace('"', '')
    word = dict(item.split(":") for item in words[3:-2].split(','))['word']
    return ''.join(e for e in word if e.isalnum())

class Song:
    def __init__(self):
        self.generation = 0
        self.songnum = 0
        self.name = randomWord(0) + " " + randomWord(1)
        self.bpm = random.randint(100, 300)
        self.chords = []
        self.score = -1
        self.parents = None
        for _ in range(20):
            chord = Chord()
            chord.addRandomNotes(int(random.triangular(0,7,3)))
            self.chords.append(chord)
            
    def AutoScore(self):
      totScore = 0
      fourBeatChords = 0
      types= {3: {"majorTriad":[4, 3], "minorTriad":[3, 4], "augTriad":[4, 4], "dimTriad":[3, 3]},
        4: {"majorSeventh":[4, 3, 4], "minorSeventh":[3, 4, 3], "augSeventh":[4, 4, 2], "dimSeventh":[3, 3, 3], 
        "halfDimSeventh":[3, 3, 4], "minorMajorSeventh":[3, 4, 3], "domSeventh":[4, 3, 3], "augMajorSeventh":[4,4,3]},
        5: {"domNinth":[4,3,3,4]},
        6: {"domEleventh":[4,3,3,4,3]},
        7: {"domThirteenth":[4,3,3,4,3,4]}
      }
      for chord in self.chords:
        if (chord.duration == 4):
          fourBeatChords= fourBeatChords + 1
        sortedNotes = sorted(chord.notes)
        if(len(sortedNotes) <= 1):
          totScore = totScore + 6
        elif(len(sortedNotes) < 8 and len(sortedNotes) > 2):
          candidates = types[len(sortedNotes)].values()
          spacing =[sortedNotes[a+1] - sortedNotes[a] for a in range(len(sortedNotes)-1)]
          for candidate in candidates:
            if (spacing == candidate):
              totScore = totScore + 16
              break
      if (fourBeatChords < 15):
        totScore = totScore + 1
      if (fourBeatChords < 10):
        totScore = totScore + 1
      if (fourBeatChords < 8):
        totScore = totScore + 1
      if (fourBeatChords < 6):
        totScore = totScore + 1
      if (fourBeatChords < 4):
        totScore = totScore + 1
      return totScore
    def mBPM(self):
      self.bpm = random.randint(100, 300)
      
    def mChord(self, chordNum):
      self.chords[chordNum] = Chord()
      self.chords[chordNum].addRandomNotes(int(random.triangular(0,7,3)))
    
    def __repr__(self):
        return ( "Song(%s.%s: %s, Score:%s, Tempo:%s, Chords:%s)" %(repr(self.generation), repr(self.songnum), repr(self.name), repr(self.score), repr(self.bpm), repr(self.chords))) 
    

    def breed(self):
      self.score = -1
      self.name = randomWord(0) + " " + randomWord(1)
      if(random.random() < 0.1):
        self.bpm = random.randint(100, 300)
      else:
        self.bpm = self.parents[random.randrange(2)].bpm
      for i in range(20):
        if(random.random() < 0.1):
          self.chords[i] = Chord()
            self.chords[i].addRandomNotes(int(random.triangular(0,7,3)))
        else:
          self.chords[i] = self.parents[random.randrange(2)].chords[i]    
    def mutate(self):
      self.mutationPoints = 10
      mutations = [self.mBPM]
      for i in range(20):
        mutations.append(self.mChord)
      chordsAvail = [i for i in range(20)]
      self.name = randomWord(0) + " " + randomWord(1)
      while self.mutationPoints >= 1:
        mutator = random.choice(mutations)
        if mutator == self.mChord:
          self.mChord(random.randrange(len(chordsAvail)))
        else:
          mutator()
        mutations.remove(mutator)
        self.mutationPoints = self.mutationPoints - 1

    def createFile(self):
        MIDI = MIDIFile(1)
        MIDI.addTrackName(0,0,self.name)
        MIDI.addTempo(0,0, self.bpm)
        beat = 0
        for chord in self.chords:
            for note in chord.notes:
                MIDI.addNote(0,0,note+45,beat,chord.duration,chord.intensity)
            beat = beat + chord.duration
        if not os.path.exists(songFolder):
          os.makedirs(songFolder)
        midiFile = open("%s/%d.%d-%s.mid"%(songFolder, self.generation, self.songnum, self.name), 'wb')
        MIDI.writeFile(midiFile)
        midiFile.close()
        

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
    data = {0:[]}
    songs = data[max(list(data.keys()))]
    print ("Would you like to:\n\t[1]Load a previous saved generation\n\t[2]Generate a new random generation\n\t[3]Print Previous Generation Data")
    choice = prompt("Please select an option", ["1", "2", "3"], True)
    if choice == "1":
        print ("Loading last generation")
        data = pickle.load(open(filename+".pkl", "rb"))
        generation = max(list(data.keys()))
        while(True):
          print("Processing Generation %d" % (generation))
          songs = data[generation]
          for song in songs:
              print ("%d.%d: %s" % (song.generation, song.songnum, song.name))
              while song.score == -1:
                  if(generation > 99 or (generation > 19 and generation % 10 == 0)):
                      while True:
                          try:
                              score = float(prompt("Song score"))
                              song.score = score
                              pickle.dump(data, open(filename+".pkl", "wb"))
                              break
                          except ValueError:
                              print("Please enter a valid number")
                  else:
                    song.score = song.AutoScore()
              print ("Score: %s" % (song.score))
              print ()
          pickle.dump(data, open(filename+".pkl", "wb"))
          songs = sorted(songs, key=lambda song: song.score, reverse=True)
          print ("Top 5 Songs of generation %d:"%(generation))
          data[generation+1]=[]
          for i in range(5):
            print(songs[i])
            data[generation+1].append(copy.deepcopy(songs[i]))
            index = len(data[generation+1])-1
            data[generation+1][index].generation = generation+1
            data[generation+1][index].score = -1
            data[generation+1][index].songnum = index
            data[generation+1][index].createFile()
          generation = generation+1
          print ("Generation %d initialized with 5 survivors. Mutating offspring now"%(generation))
          songs = data[max(list(data.keys()))]
          for j in ProgressBar.progressbar(range(15)):
            if j % 3 != 0:
              continue
            i = int(j/3)
            # mutated clone
            parent = songs[i]
            clone = copy.deepcopy(parent)
            clone.parents = [parent]
            clone.mutate()
            clone.songnum = len(songs)
            clone.createFile()
            songs.append(clone)
            # end of mutated clone

            for k in range(i+1, 5):
              clone = copy.deepcopy(parent)
              clone.parents = [songs[i], songs[k]]
              clone.breed()
              clone.songnum = len(songs)
              clone.createFile()
              songs.append(clone)
          data[max(list(data.keys()))] = songs
          pickle.dump(data, open(filename+".pkl", "wb"))
          print ("Generation %d filled and saved to file."%(generation))
            
    elif choice == "2":
        print ("Generating Songs")
        for i in ProgressBar.progressbar(range(generationSize)):
            songs.append(Song())
            s = songs[-1]
            s.songnum = i
            s.createFile()
        pickle.dump(data, open(filename+".pkl", "wb"))
        print("Generation 0 generated and saved to file")
    else:
        data = pickle.load(open(filename+".pkl", "rb"))
        pprint(data[max(list(data.keys()))])
        
if __name__ == "__main__":
    main()
