# Virtual Web Shooter 🕸️

A real-time computer vision project that turns your hand into a Spider-Man style web shooter — no gloves, no sensors, just a webcam and hand-tracking. Point your index finger to aim, extend your pinky to arm the shooter, and flick your thumb out to fire a web that sticks to whatever you aimed at.

---

## 1. The Idea

I wanted to build something with MediaPipe's hand-tracking that went beyond simple gesture recognition demos (like counting fingers or a volume-control slider) and turned it into something that actually *felt* like a small interactive game. The web shooter concept was a natural fit: it needed three independent hand signals working together — a direction, an arm/disarm state, and a discrete trigger event — which map cleanly onto three fingers:

- **Index finger** → aiming direction
- **Pinky finger** → arm / disarm the shooter
- **Thumb** → fire

The core challenge wasn't just detecting these gestures — it was making the *feel* right: a web that flies convincingly, lands where you aimed (even near the edges of the frame), lingers on screen instead of vanishing instantly, and doesn't misfire from hand jitter.

---

## 2. How It's Built

### 2.1 Hand Tracking Foundation

The project sits on top of **MediaPipe Hands**, wrapped in a reusable `handDetector` class (`HandTrackingModule.py`). This module was written first as a standalone exploratory script (`HandTrack.py`) to understand MediaPipe's landmark output, then refactored into a class with two methods:

- `findHands(img)` — runs detection and draws the 21 hand landmarks + connections on the frame
- `findPosition(img)` — returns a list of `[id, x, y]` pixel coordinates for every landmark, which is what all the gesture logic downstream is built on

Every gesture in this project is derived from a handful of these 21 landmark points — no separate gesture-classification model needed. This keeps the whole system lightweight and running comfortably in real time.

### 2.2 Reading Gestures from Landmarks

Rather than working with raw pixel distances (which change with how far your hand is from the camera), every gesture check is expressed as a **ratio relative to the hand's own size** (the distance between landmarks 5 and 17, i.e. the base of the index finger to the base of the pinky). This makes the thresholds work consistently whether your hand is close to the camera or further away.

- **Aiming (index finger):** ratio of index fingertip-to-base distance vs. hand size. Above a threshold, the finger counts as extended, and a direction vector is drawn from the fingertip outward — this vector is also what the web travels along when fired.
- **Arming (pinky finger):** same idea, applied to the pinky. The shooter is only "ARMED" when both the index *and* pinky are extended together.
- **Firing (thumb):** the trickiest one. Measured as the thumb tip's distance to the pinky tip (relative to hand size) — extending the thumb outward increases this ratio. A single-frame threshold crossing was originally used to detect "thumb extended," but that turned out to be noisy in practice (see below).

### 2.3 The Web Projectile

When a fire event happens, a projectile position is initialized at the index fingertip and advanced frame-by-frame along the aim direction saved at the moment of firing (so it doesn't curve if your hand moves mid-flight). Once it travels far enough, it "lands" and becomes a web splatter — a transparent PNG blended onto the frame at the landing point using alpha compositing.

---

## 3. Evolution & Key Fixes

The project went through a few iterations before landing on the current behavior. The short version:

- **Splat lifecycle bug:** early on, the splatter-drawing code was nested inside the "projectile still flying" check, so it only ever rendered for a single frame before disappearing. Fixed by giving the splatter its own independent update loop.
- **Edge clipping:** the overlay function originally rejected the entire web image if *any* part of it would land outside the frame, so firing toward corners drew nothing. Fixed by clipping the overlay to whatever portion actually fits on screen instead of an all-or-nothing check.
- **Single splat → multi-splat with fade:** initially only one web could exist on screen at a time, and it vanished abruptly via a hard countdown timer. This was reworked into a list-based system (`splats`) so multiple webs can coexist, each fading out smoothly over its own lifetime rather than popping out of existence.
- **Double-fire jitter:** the thumb's extend/retract ratio would occasionally jitter around its threshold, causing a single trigger pull to register as multiple fires. Fixed with **hysteresis** — separate "extend" and "retract" thresholds with a dead zone between them, so small noise near the boundary can't flip the fire state repeatedly.

Two working versions were kept during development: `main1.py` (single-splat, hard-timer version) and `main2.py` (the current multi-splat, fading version) — the latter is the final implementation described below.

---

## 4. Final Implementation (`main2.py`)

### Gesture State Machine
| Gesture | Landmarks used | Meaning |
|---|---|---|
| Index extended | 5, 8, 17 | Aiming direction is drawn and locked in |
| Pinky extended | 5, 17, 20 | Shooter is armed |
| Thumb extend/retract | 4, 2, 20 | Fire trigger (edge-detected, with hysteresis) |

A web only fires when the shooter is **armed** (index + pinky both extended) **and** the thumb transitions from retracted to extended — a single clean trigger pull, not a held state.

### Web Lifecycle
1. **Flight** — a white circle travels from the fingertip along the locked aim direction at a fixed speed.
2. **Landing** — once it covers enough distance, it's added to a `splats` list as `{x, y, timer, max_timer}`.
3. **Fading** — every frame, each splat in the list is drawn with its alpha scaled by `timer / max_timer`, so it visibly dissolves rather than cutting out. Once a splat's timer hits zero, it's removed from the list.
4. **Capacity** — the list is capped (`MAX_SPLATS`), so firing a new web beyond the cap drops the oldest one, keeping only the most recent few visible at once — matching the "sticks around for the next couple of shots" behavior.

### Overlay Blending
The spider-web PNG is composited onto the camera frame using its alpha channel, clipped to the visible screen region so it renders correctly even near the frame's edges, and scaled by the current fade factor for the dissolve effect.

---

## 5. How to Run It

**Requirements:**
```
pip install opencv-python mediapipe numpy
```

**Files needed in the same folder:**
- `main2.py`
- `HandTrackingModule.py`
- `white-spider-web-png-9.png` (the splat image, with transparency)

**Run:**
```
python main2.py
```

**Controls:**
- Point your **index finger** in the direction you want to aim.
- Extend your **pinky** at the same time to arm the shooter (you'll see "WEB SHOOTER: ARMED" on screen).
- Flick your **thumb** outward to fire — one flick, one web.
- Press **`q`** to quit.

If the webcam doesn't open, try changing the camera index in `cv2.VideoCapture(0)` to `1` or `2`.

---

## 6. Possible Next Steps

A few directions this could still go:
- A **thwip sound effect** on fire, using `pygame.mixer` for non-blocking playback during the frame loop.
- A **screen-shake effect** on fire — briefly nudging the frame with a decaying random offset for extra impact.
- Allowing **multiple webs in flight simultaneously**, rather than a new fire overwriting the currently-traveling one (currently rare to notice given the projectile's speed, but would matter if flight time were slowed down for a more dramatic swing-in effect).
- Exporting gameplay directly to video via `cv2.VideoWriter`, for clean demo recordings without screen-capture artifacts.

---

*A computer vision mini-project built with OpenCV and MediaPipe, exploring real-time gesture-driven interaction beyond basic classification.*
