from mido import Message, MidiFile, MidiTrack, MetaMessage

# Define some MIDI constants
NOTE_ON = 'note_on'
NOTE_OFF = 'note_off'
PROGRAM_CHANGE = 'program_change'

# Define a function to add a note to a track
def add_note(track, note, time, velocity, duration):
    track.append(Message(NOTE_ON, note=note, velocity=velocity, time=time))
    track.append(Message(NOTE_OFF, note=note, velocity=0, time=duration))

# Define a function to create a basic chord progression
def add_chord_progression(track, root_note, pattern, time, velocity, duration):
    chord_notes = {
        'Cm': [root_note, root_note + 3, root_note + 7],
        'G': [root_note + 7, root_note + 11, root_note + 14],
        'Fm': [root_note + 5, root_note + 8, root_note + 12]
    }
    
    for chord in pattern:
        for note in chord_notes[chord]:
            add_note(track, note, time if note == chord_notes[chord][0] else 0, velocity, duration)
        time = 0  # Subsequent chord notes are simultaneous

# Create a new MIDI file and add tracks
mid = MidiFile()
piano_track = MidiTrack()
bass_track = MidiTrack()
drum_track = MidiTrack()

# Add tracks to the MIDI file
mid.tracks.extend([piano_track, bass_track, drum_track])

# Program change: Acoustic Grand Piano for piano track
piano_track.append(Message(PROGRAM_CHANGE, program=0, time=0))
# Program change: Synth Lead for lead synth (using piano track here)
piano_track.append(Message(PROGRAM_CHANGE, program=80, time=0))
# Program change: Electric Bass for bass track
bass_track.append(Message(PROGRAM_CHANGE, program=33, time=0))
# Drums are usually on channel 10, but we set the program for completeness
drum_track.append(Message(PROGRAM_CHANGE, program=0, time=0, channel=9))

# Add a Cm, G, Fm chord progression to the piano track
chord_pattern = ['Cm', 'G', 'Fm']
root_note = 60  # Middle C (C4)
add_chord_progression(piano_track, root_note, chord_pattern, time=480, velocity=64, duration=480)

# Add a bass line that follows the root notes of the chords
for chord in chord_pattern:
    note = root_note if chord == 'Cm' else root_note + 7 if chord == 'G' else root_note + 5
    add_note(bass_track, note, time=480, velocity=64, duration=960)

# Add a simple drum line - just a kick on the first beat and a snare on the third
add_note(drum_track, note=36, time=480, velocity=64, duration=120)  # Kick drum
add_note(drum_track, note=38, time=0, velocity=64, duration=120)  # Snare drum
add_note(drum_track, note=36, time=360, velocity=64, duration=120)  # Kick drum
add_note(drum_track, note=38, time=0, velocity=64, duration=120)  # Snare drum

# Save the MIDI file
midi_file_path = '/mnt/data/sombre_c_minor_progression.mid'
mid.save(midi_file_path)

midi_file_path
