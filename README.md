# Space-Rangers
A 2d game developed using pygame where the player travels through different planets in the solar system and play different stages in each planets<br>
<br>
The main screen includes options to 'start game', 'space navigation' and 'quit'.<br>
<br>
The 'start game' navigates you to level selection screen where there are total of 11 stages, Stage Prologue, Stage Earth, Stage Mars, Stage Venus, Stage Jupiter, Stage Saturn, Stage Neptune, Stage Uranus, Stage Mercury, Stage Sun and Stage Final Epilogue. The Stage Prologue and Stage Final Epilogue follows the beginning and the conclusion of the story of the game. The different stages have different games as follows:<br>
  Stage Earth: Dodge buildings riding an aeroplane<br>
  Stage Mars: Climbing a volcano dodging falling rocks<br>
  Stage Venus: Memory card game<br>
  Stage Jupiter: Guessing the weights of stones<br>
  Stage Saturn: Jigsaw puzzle<br>
  Stage Uranus: Pop the balloons<br>
  Stage Neptune: Travel underwater<br>
  Stage Mercury: Choose the right path<br>
  Stage Sun: Defeat the alien boss<br>
Each stages has sound effects and background music<br>
Press esc for pause menu <br>
<br>
The 'space navigation' lets the players to fly a rocket starting from Earth to different parts of the solar system. The solar system has the Sun and eight planets with visible orbits for the planets.<br>
<br>
I do not own any of the images or sounds (musics) used.<br>
image references: freepik and flaticons, AI generated images from Canva <br>
bgm references: Pokemon Rangers Batonnage (Main menu, Mars), Liar Game (Venus), Death Note (Jupiter), Pokemon Platinum (Uranus), Mario underwater theme (Neptune), Donkey Kong (Mercury), Dragon Ball (Prologue), Fairy Tail (Epilogue) <br>

## Space Navigation: Alien Invasion

Run `python "Game Jam Solar System/mainscreen.py"` with Python and pygame installed. The rebuilt standalone Windows executable is `Game Jam Solar System/Space Rangers.exe`; it includes pygame, images, and audio.

Arrow keys steer and fly; hold Space to fire lasers, Shift to cruise faster, and use the mouse wheel to zoom. Esc pauses; R resumes, N restarts the flight, and Q returns to the menu. Restart after the hull reaches zero. Aliens pursue the rocket, with encounters becoming more frequent as you defeat them.

Reach any of the eight planets to launch its existing stage. Use the stage's normal exit/return action to resume the same flight; the stage's puzzles and story are unchanged. Returning repairs the hull and clears nearby enemies. Fly away before landing at that planet again. Closing a stage window closes the game.

Orbital radii use approximate mean distances in AU (Earth = 1), with relative orbital rates following Kepler's law. Orbits are circular, time is accelerated, and planet sizes are exaggerated for playability; this is not an ephemeris or a physical flight simulator. Cruise boost makes the distant outer planets reachable.

## Build and smoke test (Windows PowerShell)

```powershell
python -m pip install --target .build-deps -r requirements-build.txt
python tests/smoke_game.py
$env:PYTHONPATH = (Resolve-Path .build-deps).Path
Push-Location "Game Jam Solar System"
python -m PyInstaller --noconfirm --workpath ../.build-output mainscreen.spec
Pop-Location
```

The build outputs `Game Jam Solar System/dist/Space Rangers.exe`. Regression tests exercise every planet victory transition, persistent gem collection, the Sun gate, stage returns, dialogue bounds at two sizes, smooth turning, armored enemies, and boss pause/victory behavior. Scripted win setups validate the transitions; they do not replace a complete human playthrough.

## Gem campaign and final approach

John starts with Leo. Victories award Aries (Earth), Cancer (Mars), Gemini and Virgo (Venus), Libra (Jupiter), Scorpio and Capricorn (Saturn), Sagittarius (Uranus), Aquarius and Pisces (Neptune), and Taurus (Mercury). Gems are saved in `%LOCALAPPDATA%/SpaceRangers/progress.json` and shared between story selection and Space Navigation. Old versions did not save wins, so old completions cannot be recovered automatically. Flight restart keeps collected gems.

All eight planets must be completed before entering the Sun, including from level selection. The orange energy barrier pushes the rocket back with a warning until all twelve gems are united. Once unlocked, the final approach inside 0.30 AU clears aliens and projectiles. Touching the Sun starts the existing boss level; its normal exit returns to space.

The rocket now continues thrusting through turns and supports diagonal arrow inputs. Sector difficulty follows story order (Earth, Mars, Venus, Jupiter, Saturn, Uranus, Neptune, Mercury), or collected-planet progress if higher: scouts have one hit point, weaving raiders have two, and guardians have four and fire projectiles. Higher tiers also increase speed, contact damage and encounter frequency.

All screens share one desktop-fitting window, up to 1280x800. Dialogue wraps using measured font widths and fits its box.

### Review findings left for a design decision

- Jupiter's scale establishes weight ratios, but there is no reference mass to determine the exact numeric answers. Consider a reference weight or a hint.
- Mercury asks for Jupiter's moon count with a hardcoded answer of 79. This is a time-sensitive trivia question; consider replacing it with a stable fact.
- Mars awards climbing height continuously, even while standing still. This currently behaves as a survival timer rather than measured climbing.

## Mouse controls and story gates

Mercury is protected by a local heat barrier until Neptune is completed and Aquarius/Pisces are collected. Both the flight arrival and stage menu enforce it. The epilogue is locked until a Sun-boss victory has been saved. Existing saves remain compatible.

Click main-menu and stage-selection entries to launch them. Story screens and planet stages now expose clickable Continue, Resume, Retry, and Menu buttons when applicable. WASD aliases the existing arrow controls in stages and flight. In space, hold left mouse to aim/fire toward the cursor; Space still fires forward. Shift boosts. Click Pause/Help for controls and flight actions. The flight HUD shows hull, gems, destination/distance, and contextual warnings only.

## Moving destinations and radar

Escape now composes and presents one finished pause frame; held/repeated Escape presses cannot repeatedly toggle the menu. Click a planet in the pause screen (or use Left/Right) to choose its live AU waypoint. Choosing a locked destination does not bypass its entry barrier. A completed selected mission advances the waypoint to the next story mission.

Planets start at distinct illustrative phases and move in circular orbits. Orbital periods follow Kepler's third law (`period = 360 seconds * AU ** 1.5`): Earth completes an orbit in six minutes of active flight, inner planets are faster, outer planets slower. These are accelerated approximate orbits, not real-date ephemerides. The world and radar timers pause in menus and planet stages.

Radar unlocks permanently after victories on both Earth and Mars, including existing saves. Press T or click Radar to scan for five seconds; activation is available again twenty seconds after the previous activation. A scan reveals the system map, marks the selected planet, and supplies a live on-screen ring or edge arrow. Earth and Mars have training beacons before the radar unlock. Shift boost is now 6x normal speed, 75% of the previous 8x speed.

Recommended story route: Earth, Mars, Venus, Jupiter, Saturn, Uranus, Neptune, Mercury, Sun. This preserves the story's gem dependencies rather than minimizing travel distance.

## Asteroid blockade and Resonance Beam

A narrow, alien-fortified asteroid belt at 2.6 AU blocks passage between Mars and Jupiter until Earth, Mars and Venus are complete. The same requirement applies to outer-planet stage selection. The four required gems power the Resonance Beam: Aries supplies energy, Cancer protects the ship, Gemini combines twin streams, and Virgo focuses them. Venus awards both Gemini and Virgo; existing saves unlock the beam automatically when the three victories are present.

Right-click fires the beam toward the cursor; F or the Gem beam button fires ahead. It cuts every asteroid touched along a broad, finite-length line and also destroys aliens in its path. It recharges in four seconds. Cleared corridors rotate with the belt during that flight, including after returning from planet stages; restarting a flight regenerates the belt. Ordinary lasers cannot break asteroids. Boosting into uncleared rocks stops the ship and damages the hull, while the locked blockade repels it with a hint. The belt is deliberately compact and densely fortified for gameplay.

The smoke suite includes gem prerequisites, outer-planet locks, boosted belt crossings at multiple headings, persistent beam corridors, cooldown/pause behavior, mouse aiming and ordinary-laser collisions.

## Rocket shield and orbiting asteroids

The asteroid belt revolves around the Sun at the accelerated orbital rate for 2.6 AU. Cut corridors move with it; destroyed rocks do not respawn until flight restart. Moving-rock collisions are checked along their travel between frames.

E or the Shield button activates the default rocket shield, available without gems. It lasts five seconds or three shield charges, whichever runs out first. Early scouts cost one charge, raiders at least two, and guardians three. Higher-tier scouts also consume more charges; late-game hits can break the whole shield. The breaking hit is fully absorbed. Enemy shots and asteroid impacts are absorbed too, but the shield does not bypass progression barriers. Recharge takes twelve seconds from activation; menus and planet stages freeze its timers. Radar now uses T, retaining its existing unlock and scan timings.
