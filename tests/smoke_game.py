"""Regression tests run with SDL dummy video/audio; no real save is modified."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from collections import defaultdict
from importlib import import_module
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / '.build-deps'), str(ROOT / 'Game Jam Solar System')]
os.chdir(ROOT / 'Game Jam Solar System')
import pygame
import campaign as progress_module
from campaign import Campaign, STORY_ORDER
import display_settings
from solarsystem import SolarSystem

class GameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.progress = Campaign(Path(self.temp.name) / 'progress.json')
        self.original_progress = progress_module.campaign
        progress_module.campaign = self.progress
        pygame.init()
        display_settings._size = (1280, 800)

    def tearDown(self):
        pygame.quit()
        progress_module.campaign = self.original_progress
        self.temp.cleanup()

    def test_persistence_and_gate(self):
        self.assertEqual(self.progress.gems, ('Leo',))
        for name in STORY_ORDER[:-1]: self.progress.complete(name)
        self.assertFalse(self.progress.sun_unlocked)
        self.progress.complete(STORY_ORDER[-1])
        self.progress.complete('earth')
        loaded = Campaign(self.progress.path)
        self.assertTrue(loaded.sun_unlocked)
        self.assertEqual(len(loaded.gems), 12)
        self.progress.path.write_text('bad data')
        self.assertFalse(Campaign(self.progress.path).sun_unlocked)

    def test_sun_barrier_and_quiet_approach(self):
        game = SolarSystem(self.progress)
        r = game.solar_zone
        game.previous_pos = [r, 0]
        game.spaceship_pos = [-r, 0]
        with patch.object(game, 'launch_stage') as launch:
            game.check_arrival()
            launch.assert_not_called()
            self.assertGreater(game.spaceship_pos[0], 0)
            self.assertTrue(game.warning)
            for name in STORY_ORDER: self.progress.complete(name)
            game.previous_pos = [r, 0]
            game.spaceship_pos = [0, 0]
            game.check_arrival()
            launch.assert_called_once_with('sun')
        game.enemies = [{'pos': pygame.Vector2(10, 10)}]
        game.enemy_lasers = [[pygame.Vector2(), pygame.Vector2(1, 0), 1]]
        game.update_combat(1)
        self.assertFalse(game.enemies or game.enemy_lasers)

    def test_flight_turns_without_stopping(self):
        game = SolarSystem(self.progress)
        before = pygame.Vector2(game.spaceship_pos)
        keys = defaultdict(bool, {pygame.K_LEFT: True})
        with patch('pygame.key.get_pressed', return_value=keys): game.update_spaceship(1/60)
        self.assertGreater(before.distance_to(game.spaceship_pos), 0)
        self.assertNotEqual(game.spaceship_angle, 0)
        self.assertLess(abs(game.spaceship_angle), 3.14)

    def test_armour_damage_and_progression(self):
        game = SolarSystem(self.progress)
        ship = pygame.Vector2(game.spaceship_pos)
        self.assertEqual(game.encounter_tier(), 1)
        for name in STORY_ORDER[:5]: self.progress.complete(name)
        self.assertGreaterEqual(game.encounter_tier(), 6)
        enemy = {'pos': ship + pygame.Vector2(70, 0), 'kind': 'guardian', 'hp': 4, 'max_hp': 4, 'tier': 6, 'cooldown': 10, 'phase': 0}
        game.enemies = [enemy]
        for hp in (3, 2, 1, 0):
            game.lasers = [[ship.copy(), pygame.Vector2(2200, 0), 1]]
            game.update_combat(0.05)
            self.assertEqual(enemy['hp'], hp)
        self.assertEqual(game.score, 1)
        self.assertFalse(game.enemies)
        game.enemy_lasers = [[ship - pygame.Vector2(50, 0), pygame.Vector2(2200, 0), 1]]
        game.update_combat(0.05)
        self.assertEqual(game.health, 82)

    def test_all_arrivals_do_not_award_on_exit(self):
        game = SolarSystem(self.progress)
        for name in STORY_ORDER:
            if name == 'jupiter':
                for early in ('earth', 'mars', 'venus'): self.progress.complete(early)
            if name == 'mercury': self.progress.complete('neptune')
            earned_before = set(self.progress.completed)
            cls = getattr(import_module(name.title()), name.title())
            position = game.planet_position(name)
            game.landing_lock = None
            game.previous_pos = list(position - pygame.Vector2(300, 0))
            game.spaceship_pos = list(position + pygame.Vector2(300, 0))
            with patch.object(cls, 'run' if name == 'saturn' else 'main', return_value='main_menu') as run:
                game.check_arrival()
                self.assertEqual(run.call_count, 1, name)
                game.check_arrival()
                self.assertEqual(run.call_count, 1, name)
            self.assertEqual(self.progress.completed, earned_before)
            self.assertEqual(game.screen.get_size(), (1280, 800))

    def test_stage_victory_paths_and_layouts(self):
        output = ROOT / '.test-output'
        output.mkdir(exist_ok=True)
        for name in STORY_ORDER:
            with self.subTest(planet=name):
                pygame.init()
                stage = getattr(import_module(name.title()), name.title())()
                self.assertEqual(stage.screen.get_size(), (1280, 800))
                frames = [0]
                def events():
                    frames[0] += 1
                    if frames[0] > 12: self.fail('stage did not exit: ' + name)
                    if frames[0] == 2:
                        stage.game_state = 'playing'
                    if frames[0] == 4:
                        if name == 'earth': stage.score = 20; stage.create_buildings()
                        elif name == 'mars': stage.score = stage.target_score; stage.rocks = []
                        elif name == 'venus': stage.matched_pairs = 6
                        elif name == 'jupiter':
                            stage.entering_guesses = True
                            stage.gold_guess, stage.silver_guess, stage.copper_guess = '7', '4', '5'
                            return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode='')]
                        elif name == 'saturn':
                            stage.grid = list(range(9)); stage.dragging_piece = 0
                            return [pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(stage.center_x+5, stage.center_y+5))]
                        elif name == 'uranus':
                            stage.player_score = 4
                            balloon = stage.balloons[0]; balloon.x = 300; balloon.y = 200; balloon.speed = 0
                            stage.balloons = [balloon]
                            stage.arrow = stage.Arrow(300, 200, 300, 100, stage.RED, stage)
                            stage.arrow.dx = 0; stage.arrow.dy = -1
                        elif name == 'neptune':
                            stage.distance_travelled = 500; stage.coins_collected = 10
                            stage.obstacles = []; stage.fishes = []
                        elif name == 'mercury':
                            stage.current_question = 5; stage.correct_answers = 5
                            stage.trolley_x = stage.screen_width + 10; stage.at_divergence = True
                    if frames[0] == 7: return [pygame.event.Event(pygame.QUIT)]
                    return []
                def capture():
                    if frames[0] in (1, 3, 5):
                        snapshot = stage.screen.copy()
                        if frames[0] in (1, 5):
                            old_reveal = stage.text_box.reveal_index
                            stage.text_box.reveal_index = 10000
                            stage.text_box.draw(snapshot)
                            stage.text_box.reveal_index = old_reveal
                        pygame.image.save(snapshot, str(output / f'{name}-{frames[0]}.png'))
                with patch('pygame.event.get', events), patch('pygame.display.flip', capture), patch('pygame.display.update', capture):
                    try: getattr(stage, 'run' if name == 'saturn' else 'main')()
                    except SystemExit: pass
                self.assertIn(name, self.progress.completed)
        self.assertTrue(self.progress.sun_unlocked)

    def test_victory_exit_controls(self):
        for name in ('Venus', 'Jupiter'):
            stage = getattr(import_module(name), name)()
            stage.game_state = 'victory'
            if name == 'Venus': stage.level_complete = True
            with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q, unicode='q')]):
                self.assertEqual(stage.main(), 'main_menu')

    def test_boss_pause_and_victory(self):
        from Sun import Sun
        stage = Sun()
        stage.game_state = 'playing'
        stage.paused = True
        stage.playerX_change = 10
        start = stage.playerX
        frames = [0]
        def paused_events():
            frames[0] += 1
            return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q, unicode='q')] if frames[0] == 4 else []
        with patch('pygame.event.get', paused_events): stage.main()
        self.assertEqual(stage.playerX, start)
        stage = Sun()
        stage.game_state = 'playing'
        stage.hp_value = 10
        stage.laser_state = 'fire'
        stage.laserX = stage.enemyX[0]
        stage.laserY = stage.enemyY[0] + 20
        frames[0] = 0
        def win_events():
            frames[0] += 1
            if frames[0] > 6: self.fail('boss did not finish')
            if frames[0] == 3:
                pygame.image.save(stage.screen, str(ROOT / '.test-output' / 'sun-victory.png'))
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q, unicode='q')]
            return []
        with patch('pygame.event.get', win_events): self.assertEqual(stage.main(), 'main_menu')
        self.assertIn('sun', self.progress.completed)

    def test_menu_sun_gate(self):
        import mainscreen
        frames = [0]
        def events():
            frames[0] += 1
            key = pygame.K_RETURN if frames[0] in (1, 11) else pygame.K_DOWN
            if frames[0] == 12:
                pygame.image.save(pygame.display.get_surface(), str(ROOT / '.test-output' / 'menu-locked.png'))
                return [pygame.event.Event(pygame.QUIT)]
            return [pygame.event.Event(pygame.KEYDOWN, key=key, unicode='')]
        with patch.object(mainscreen, 'campaign', self.progress), patch('pygame.event.get', events), patch.object(mainscreen, 'import_module') as launch:
            mainscreen.main_screen()
            launch.assert_not_called()

    def test_mercury_barrier_and_unlock(self):
        game = SolarSystem(self.progress)
        pos = game.planet_position('mercury')
        game.previous_pos = list(pos + pygame.Vector2(300, 0))
        game.spaceship_pos = list(pos - pygame.Vector2(300, 0))
        with patch.object(game, 'launch_stage') as launch:
            game.check_arrival()
            launch.assert_not_called()
            self.assertGreater(game.spaceship_pos[0], pos.x)
            self.assertIn('Aquarius', game.warning)
            self.progress.complete('neptune')
            game.previous_pos = list(pos + pygame.Vector2(300, 0))
            game.spaceship_pos = list(pos)
            game.check_arrival()
            launch.assert_called_once_with('mercury')

    def test_epilogue_requires_boss(self):
        for name in STORY_ORDER: self.progress.complete(name)
        self.assertTrue(self.progress.lock_reason('final'))
        self.progress.complete('sun')
        self.assertFalse(Campaign(self.progress.path).lock_reason('final'))

    def test_mouse_stage_menu_gates(self):
        import mainscreen
        for selection in (8, 10):
            frames = [0]
            def events():
                frames[0] += 1
                if frames[0] == 3: return [pygame.event.Event(pygame.QUIT)]
                rect = mainscreen.menu_buttons(1280, 800, frames[0] == 2)[selection if frames[0] == 2 else 0]
                return [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)]
            with patch.object(mainscreen, 'campaign', self.progress), patch('pygame.event.get', events), patch.object(mainscreen, 'import_module') as launch:
                mainscreen.main_screen()
                launch.assert_not_called()

    def test_wasd_and_mouse_aim(self):
        from input_controls import get_events, pressed_keys
        keys = defaultdict(bool, {pygame.K_w: True})
        with patch('pygame.key.get_pressed', return_value=keys):
            self.assertTrue(pressed_keys()[pygame.K_UP])
        with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, unicode='a')]):
            self.assertEqual(list(get_events())[0].key, pygame.K_LEFT)
        game = SolarSystem(self.progress)
        game.mouse_shot = (game.WIDTH // 2, 0)
        game.block_mouse_fire = False
        with patch('pygame.mouse.get_pressed', return_value=(False,False,False)):
            game.update_combat(.016)
        self.assertEqual(len(game.lasers), 1)
        self.assertAlmostEqual(game.lasers[0][1].x, 0)
        self.assertLess(game.lasers[0][1].y, 0)
        before = game.spaceship_pos.copy()
        with patch('pygame.key.get_pressed', return_value=keys): game.update_spaceship(.016)
        self.assertNotEqual(before, game.spaceship_pos)

    def test_clickable_flight_pause(self):
        game = SolarSystem(self.progress)
        frames = [0]
        def events():
            frames[0] += 1
            if frames[0] > 3: self.fail('pause quit was ignored')
            if frames[0] == 1: point = game.pause_button.center
            else: point = next(rect.center for _, action, rect in game.pause_options() if action == 'quit')
            return [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=point)]
        with patch('pygame.event.get', events): game.main()
        self.assertFalse(game.lasers)

    def test_mouse_pause_menu_for_all_stages(self):
        from ui_controls import buttons
        for name in ('Earth', 'Mars', 'Venus', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Mercury', 'Sun'):
            stage = getattr(import_module(name), name)()
            frames = [0]
            def events():
                frames[0] += 1
                if frames[0] > 3: self.fail('mouse menu failed: ' + name)
                stage.game_state = 'playing'
                stage.paused = True
                if name == 'Saturn': stage.pause_menu_active = True
                if name == 'Mercury': stage.show_pause_menu = True
                point = next(rect.center for label, _, rect in buttons(stage) if label == 'Menu')
                return [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=point)]
            with patch('pygame.event.get', events):
                self.assertEqual(getattr(stage, 'run' if name == 'Saturn' else 'main')(), 'main_menu', name)

    def test_pause_presents_once_and_escape_repeat(self):
        game = SolarSystem(self.progress)
        with patch('pygame.display.update') as present:
            game.pause_menu()
            self.assertEqual(present.call_count, 1)
        frames = [0]
        def events():
            frames[0] += 1
            if frames[0] == 1:
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
            if frames[0] == 2:
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, repeat=True),
                        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
            if frames[0] == 3:
                self.assertTrue(game.paused)
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q)]
            self.fail('Escape repeat resumed the game')
        with patch('pygame.event.get', events): game.main()

    def test_orbit_ratios_frame_independence_and_pause(self):
        game = SolarSystem(self.progress)
        self.assertGreater(len(set(game.angles.values())), 1)
        earth_speed = game.PLANETS['earth'][2]
        self.assertAlmostEqual(earth_speed * 360, 2 * 3.141592653589793)
        self.assertAlmostEqual(earth_speed / game.PLANETS['mars'][2], 1.524 ** 1.5)
        initial = game.planet_position('neptune')
        game.update_navigation(1)
        self.assertGreater(initial.distance_to(game.planet_position('neptune')), 10)
        expected = dict(game.angles)
        other = SolarSystem(self.progress)
        for _ in range(60): other.update_navigation(1/60)
        for name in expected: self.assertAlmostEqual(expected[name], other.angles[name])
        game.set_paused(True)
        game.update_navigation(60)
        self.assertEqual(expected, game.angles)

    def test_radar_unlock_scan_recharge_and_pause(self):
        game = SolarSystem(self.progress)
        self.assertFalse(game.activate_radar())
        self.progress.complete('earth')
        self.assertFalse(game.activate_radar())
        self.progress.complete('mars')
        self.assertTrue(Campaign(self.progress.path).radar_unlocked)
        self.assertTrue(game.activate_radar())
        game.update_navigation(2)
        self.assertEqual(game.radar_remaining, 3)
        game.set_paused(True)
        game.update_navigation(100)
        self.assertEqual(game.radar_remaining, 3)
        game.set_paused(False)
        game.update_navigation(3)
        self.assertEqual(game.radar_remaining, 0)
        self.assertFalse(game.activate_radar())
        game.update_navigation(15)
        self.assertTrue(game.activate_radar())

    def test_destination_selection_and_live_distance(self):
        game = SolarSystem(self.progress)
        game.select_destination('neptune')
        before = game.destination_distance()
        game.update_navigation(15)
        self.assertNotEqual(before, game.destination_distance())
        frames = [0]
        def events():
            frames[0] += 1
            if frames[0] == 1: return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
            if frames[0] == 2:
                rect = next(rect for name, rect in game.destination_options() if name == 'saturn')
                return [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)]
            if frames[0] == 3:
                self.assertEqual(game.destination, 'saturn')
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q)]
            self.fail('destination menu did not exit')
        with patch('pygame.event.get', events): game.main()

    def test_boost_is_three_quarters_previous_speed(self):
        game = SolarSystem(self.progress)
        before = pygame.Vector2(game.spaceship_pos)
        keys = defaultdict(bool, {pygame.K_d: True, pygame.K_LSHIFT: True})
        with patch('pygame.key.get_pressed', return_value=keys): game.update_spaceship(1/60)
        self.assertAlmostEqual(before.distance_to(game.spaceship_pos), game.spaceship_speed * 8 * .75)

    def test_moving_planet_swept_arrival(self):
        game = SolarSystem(self.progress)
        earth = game.planet_position('earth')
        game.spaceship_pos = list(earth + pygame.Vector2(100, 0))
        game.previous_pos = game.spaceship_pos.copy()
        game.previous_planet_positions = {'earth': earth + pygame.Vector2(200, 0)}
        with patch.object(game, 'launch_stage') as launch:
            game.check_arrival()
            launch.assert_called_once_with('earth')

    def test_shield_duration_recharge_and_pause(self):
        game = SolarSystem(self.progress)
        self.assertTrue(game.activate_shield())
        self.assertFalse(game.activate_shield())
        game.update_navigation(2)
        game.set_paused(True)
        game.update_navigation(20)
        self.assertEqual(game.shield_remaining, 3)
        self.assertEqual(game.shield_cooldown, 10)
        self.assertFalse(game.activate_shield())
        game.set_paused(False)
        game.update_navigation(3)
        self.assertEqual(game.shield_charges, 0)
        game.take_damage(12)
        self.assertEqual(game.health, 88)
        game.update_navigation(7)
        self.assertTrue(game.activate_shield())
        game.health = 0
        game.shield_cooldown = 0
        self.assertFalse(game.activate_shield())

    def test_shield_enemy_collisions_and_projectiles(self):
        game = SolarSystem(self.progress)
        ship = pygame.Vector2(game.spaceship_pos)
        for kind, tier, hits in [('scout', 1, 3), ('raider', 4, 2), ('guardian', 6, 1), ('scout', 8, 1)]:
            game.shield_cooldown = 0
            game.health = 100
            game.activate_shield()
            for _ in range(hits):
                game.enemies = [dict(pos=ship.copy(), kind=kind, tier=tier)]
                game.update_combat(0)
                self.assertEqual(game.health, 100)
            self.assertEqual(game.shield_remaining, 0)
            game.take_damage(18)
            self.assertEqual(game.health, 82)
        game.shield_cooldown = 0
        game.activate_shield()
        game.enemy_lasers = [[ship - pygame.Vector2(50, 0), pygame.Vector2(2200, 0), 1, 3]]
        game.update_combat(.05)
        self.assertEqual(game.health, 82)
        self.assertEqual(game.shield_charges, 0)
        self.assertFalse(game.enemy_lasers)

    def test_shield_and_radar_key_bindings(self):
        game = SolarSystem(self.progress)
        for name in ('earth', 'mars'): self.progress.complete(name)
        batches = iter([[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)],
                        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_t)],
                        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE),
                         pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q)]])
        with patch('pygame.event.get', side_effect=lambda: next(batches)), patch.object(game, 'check_arrival'):
            game.main()
        self.assertGreater(game.shield_remaining, 0)
        self.assertGreater(game.radar_remaining, 0)

    def test_belt_orbit_pause_and_cleared_corridor(self):
        game = SolarSystem(self.progress)
        belt = game.belt
        rock = belt.rocks[0]
        original = rock.position.copy()
        radius = original.length()
        removed = belt.cut(pygame.Vector2(belt.inner - 180, 0), pygame.Vector2(belt.outer + 200, 0), 110)
        remaining_ids = set(belt.rocks)
        self.assertTrue(removed)
        game.update_navigation(1)
        self.assertEqual(set(belt.rocks), remaining_ids)
        # Use a surviving rock to validate orbit and rebuilt spatial lookup.
        index, rock = next(iter(belt.rocks.items()))
        before = rock.position.copy()
        game.update_navigation(1)
        expected = before.rotate_rad(belt.angular_speed)
        self.assertLess(rock.position.distance_to(expected), .00001)
        self.assertAlmostEqual(rock.position.length(), before.length())
        self.assertIn(index, [i for i, _ in belt.candidates(rock.position, rock.position)])
        game.set_paused(True)
        frozen = rock.position.copy()
        game.update_navigation(10)
        self.assertEqual(rock.position, frozen)
        # A moving asteroid can strike a stationary rocket between frames.
        rock.previous_position = rock.position - pygame.Vector2(200, 0)
        belt.max_motion = 200
        ship = rock.position - pygame.Vector2(100, 0)
        self.assertIsNotNone(belt.first_collision(ship, ship, 10, moving=True))

    def test_belt_gem_unlock_and_outer_gates(self):
        game = SolarSystem(self.progress)
        for name in ('earth', 'mars'): self.progress.complete(name)
        self.assertFalse(self.progress.beam_unlocked)
        self.assertFalse(game.fire_gem_beam())
        self.assertIn('Gemini', game.warning)
        for name in ('jupiter', 'saturn', 'uranus', 'neptune'):
            self.assertTrue(self.progress.lock_reason(name))
        self.progress.complete('venus')
        self.assertTrue(Campaign(self.progress.path).beam_unlocked)
        self.assertIn('Gemini', self.progress.gems)
        self.assertIn('Virgo', self.progress.gems)
        for name in ('jupiter', 'saturn', 'uranus', 'neptune'):
            self.assertFalse(self.progress.lock_reason(name))

    def test_belt_blocks_boost_crossing_at_every_heading(self):
        game = SolarSystem(self.progress)
        import math
        for angle in range(0, 360, 30):
            direction = pygame.Vector2(1, 0).rotate(angle)
            game.previous_pos = list(direction * (game.belt.inner - 400))
            game.spaceship_pos = list(direction * (game.belt.outer + 900))
            game.update_belt(.016)
            self.assertLess(pygame.Vector2(game.spaceship_pos).length(), game.belt.inner)
            self.assertEqual(game.health, 100)
        # A segment traversing the whole system must also stop on the outer side.
        start = pygame.Vector2(game.belt.outer + 1000, 0)
        blocked = game.belt.locked_position(start, -start, game.spaceship_radius)
        self.assertGreater(blocked.x, game.belt.outer)

    def test_beam_clears_all_intersections_and_keeps_corridor(self):
        game = SolarSystem(self.progress)
        for name in ('earth', 'mars', 'venus'): self.progress.complete(name)
        game.spaceship_pos = [game.belt.inner - 180, 0]
        game.previous_pos = game.spaceship_pos.copy()
        start = pygame.Vector2(game.spaceship_pos)
        end = pygame.Vector2(game.belt.outer + 200, 0)
        self.assertIsNotNone(game.belt.first_collision(start, end, game.spaceship_radius))
        before = len(game.belt.rocks)
        self.assertTrue(game.fire_gem_beam())
        cleared = len(game.belt.rocks)
        self.assertLessEqual(cleared, before - 4)
        self.assertGreater(cleared, before * .95)  # A corridor, not the entire ring.
        self.assertIsNone(game.belt.first_collision(start, end, game.spaceship_radius))
        self.assertFalse(game.fire_gem_beam())
        game.spaceship_pos = list(end)
        game.update_belt(.1)
        self.assertEqual(pygame.Vector2(game.spaceship_pos), end)
        self.assertEqual(len(game.belt.rocks), cleared)
        self.assertEqual(game.health, 100)
        game.set_paused(True)
        remaining = game.beam_cooldown
        game.update_belt(20)
        self.assertEqual(game.beam_cooldown, remaining)
        game.set_paused(False)
        game.previous_pos = game.spaceship_pos.copy()
        game.update_belt(4)
        self.assertTrue(game.fire_gem_beam())

    def test_uncleared_asteroids_block_boost_and_normal_lasers(self):
        game = SolarSystem(self.progress)
        for name in ('earth', 'mars', 'venus'): self.progress.complete(name)
        start = pygame.Vector2(game.belt.inner - 180, 0)
        end = pygame.Vector2(game.belt.outer + 200, 0)
        game.previous_pos = list(start)
        game.spaceship_pos = list(end)
        game.update_belt(.016)
        self.assertLess(game.spaceship_pos[0], game.belt.outer)
        self.assertEqual(game.health, 88)
        self.assertGreater(game.belt_hit_cooldown, 0)
        count = len(game.belt.rocks)
        game.lasers = [[start.copy(), (end - start) / .05, 1.0]]
        game.update_combat(.05)
        self.assertEqual(len(game.belt.rocks), count)
        self.assertFalse(game.lasers)

    def test_beam_mouse_direction_pause_and_dead_ship(self):
        game = SolarSystem(self.progress)
        for name in ('earth', 'mars', 'venus'): self.progress.complete(name)
        self.assertTrue(game.fire_gem_beam((game.WIDTH // 2, 0)))
        self.assertAlmostEqual(game.beam_end.x, game.beam_start.x)
        self.assertLess(game.beam_end.y, game.beam_start.y)
        game.beam_cooldown = 0
        game.set_paused(True)
        self.assertFalse(game.fire_gem_beam())
        game.set_paused(False)
        game.health = 0
        self.assertFalse(game.fire_gem_beam())

    def test_restart_and_small_dialogue(self):
        from Jupiter import Jupiter
        from Sun import Sun
        from Mercury import Mercury
        from prologue import Prologue
        for size in ((1280, 800), (960, 600)):
            display_settings._size = size
            for module, cls in [('Earth','Earth'), ('Mars','Mars'), ('Venus','Venus'), ('Jupiter','Jupiter'), ('Saturn','Saturn'), ('Uranus','Uranus'), ('Neptune','Neptune'), ('Mercury','Mercury'), ('Sun','Sun'), ('prologue','Prologue'), ('final','Epilogue')]:
                stage = getattr(import_module(module), cls)()
                text = getattr(stage, 'intro_text', None) or stage.full_story[0]
                stage.text_box.set_text(text)
                box = stage.text_box
                self.assertLessEqual(len(box.text_content) * (box.font.get_height()+box.line_spacing), box.rect.height-20)
                self.assertTrue(stage.screen.get_rect().contains(box.rect), module)
            stage = Jupiter(); stage.reset_game()
            self.assertEqual(len(stage.stones), 30)
        stage = Mercury()
        initial = stage.trolley_x
        count = [0]
        def events():
            count[0] += 1
            return [pygame.event.Event(pygame.QUIT)] if count[0] == 4 else []
        with patch('pygame.event.get', events): stage.main()
        self.assertEqual(stage.trolley_x, initial)

if __name__ == '__main__': unittest.main(verbosity=2)
