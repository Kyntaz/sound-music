import SoundMusic

# Settings:
midi_file = './midi/pavane.musicxml'
sound_file = './dataset/ducks.wav'
output = './output/pavane.wav'

# Render the audio.
system = SoundMusic.alt.Midi.MidiSystem()
system.instrument_generator.instrument_classes = [SoundMusic.Instruments.MelodicSample]
audio, debug = system.process(SoundMusic.Audio.from_path(sound_file), output, midi_file)