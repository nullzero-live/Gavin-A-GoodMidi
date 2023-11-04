import mido
from mido import MidiFile, MidiTrack, Message

# Define your tempo (BPM) and calculate ticks per beat (assuming 480 PPQN)
tempo = mido.bpm2tempo(80)  # 120 BPM
ticks_per_beat = 480  # Standard high resolution

# Create a new MIDI file and track
mid = MidiFile(ticks_per_beat=ticks_per_beat)
track = MidiTrack()
mid.tracks.append(track)

# Set the tempo
track.append(mido.MetaMessage('set_tempo', tempo=tempo))

# Define a simple rhythm pattern (durations in beats)
rhythm_pattern = [1, 0.5, 0.5, 1]  # Quarter, eighth, eighth, quarter

# Define a sequence of chords (list of note numbers)
chords = [[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]]

# Add chords to the track according to the rhythm pattern
time = 0  # Start time for the first chord
for chord, duration in zip(chords, rhythm_pattern):
    # Add 'note on' for each note in the chord
    for note in chord:
        track.append(Message('note_on', note=note, velocity=64, time=time))
        time = 0  # Subsequent notes in the chord have no delay

    # Calculate the duration in ticks
    ticks = int(duration * ticks_per_beat)
    
    # Add 'note off' for each note in the chord
    for note in chord:
        track.append(Message('note_off', note=note, velocity=64, time=ticks))
        ticks = 0  # Reset ticks after the first note off

# Save the MIDI file
mid.save('chord_sequence_with_rhythm.mid')
