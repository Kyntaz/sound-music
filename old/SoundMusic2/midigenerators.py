# Music generators that take an audio chunk to initialize and render midi data.

class IMidiGenerator:
    def get_parameters(self): raise NotImplementedError
    def set_parameters(self, params): raise NotImplementedError
    def process_audio(self, audio): raise NotImplementedError
    def generate(self, line): raise NotImplementedError