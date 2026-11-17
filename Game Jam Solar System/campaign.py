"""Shared campaign progress. Only actual victories award gems."""
import json
import os
from pathlib import Path

PLANET_GEMS = {
    'earth': ('Aries',), 'mars': ('Cancer',), 'venus': ('Gemini', 'Virgo'),
    'jupiter': ('Libra',), 'saturn': ('Scorpio', 'Capricorn'),
    'uranus': ('Sagittarius',), 'neptune': ('Aquarius', 'Pisces'),
    'mercury': ('Taurus',),
}
STORY_ORDER = tuple(PLANET_GEMS)

class Campaign:
    def __init__(self, path=None):
        self.path = Path(path) if path else Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'SpaceRangers' / 'progress.json'
        self.completed = set()
        self.save_error = ''
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            values = data.get('completed', [])
            if isinstance(values, list):
                self.completed = {name for name in values if isinstance(name, str) and name in (*STORY_ORDER, 'sun')}
        except FileNotFoundError:
            pass
        except (OSError, ValueError, AttributeError):
            self.save_error = 'Could not read saved gems; progress is kept for this session.'

    @property
    def gems(self):
        return ('Leo',) + tuple(gem for planet in STORY_ORDER if planet in self.completed for gem in PLANET_GEMS[planet])

    @property
    def sun_unlocked(self):
        return all(planet in self.completed for planet in STORY_ORDER)

    @property
    def radar_unlocked(self):
        return {'earth', 'mars'}.issubset(self.completed)

    @property
    def beam_unlocked(self):
        return {'earth', 'mars', 'venus'}.issubset(self.completed)

    @property
    def mercury_unlocked(self):
        return {'Aquarius', 'Pisces'}.issubset(self.gems)

    @property
    def epilogue_unlocked(self):
        return 'sun' in self.completed

    def lock_reason(self, stage):
        if stage in ('jupiter', 'saturn', 'uranus', 'neptune') and not self.beam_unlocked:
            return 'Asteroid blockade: complete Earth, Mars and Venus to power the gem beam.'
        if stage == 'mercury' and not self.mercury_unlocked:
            return 'Mercury is too hot. Find Aquarius and Pisces on Neptune.'
        if stage == 'sun' and not self.sun_unlocked:
            return 'The Sun is sealed. Complete all eight planets to unite the gems.'
        if stage == 'final' and not self.epilogue_unlocked:
            return 'Defeat the Sun boss to unlock the epilogue.'
        return ''

    def complete(self, planet):
        if planet not in (*STORY_ORDER, 'sun') or planet in self.completed:
            return
        self.completed.add(planet)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix('.tmp')
            temporary.write_text(json.dumps({'version': 1, 'completed': sorted(self.completed)}), encoding='utf-8')
            temporary.replace(self.path)
            self.save_error = ''
        except OSError:
            self.save_error = 'Gems earned, but saving failed. Progress lasts for this session.'

campaign = Campaign()

def complete_level(name):
    campaign.complete(name)
