import SoundMusic as sm
from typing import List

class IManipulator:

    def do(self, sounds: List[sm.sound.SoundObject]) -> List[sm.sound.SoundObject]:
        raise NotImplementedError

    def get_random(self):
        raise NotImplementedError

    def tweak(self, power):
        raise NotImplementedError

class ISimpleManipulator(IManipulator):

    def get_random(self):
        return self

    def tweak(self, power):
        pass