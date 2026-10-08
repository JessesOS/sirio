# Seedance 2.5 edit mode via the Enhancor API — what we learned

First tests, 2026-10-08. Three jobs: a person swap (Genjutsu app), a product-shot restyle, and
an interview relight. All drafts at 480p.

## How to run it

`tools/seedance_edit.py <job folder> draft` submits `source.mp4` (+ optional
`look-reference.jpg`) with `prompt.txt` to Seedance 2.5 edit mode, polls, and saves `draft.mp4`.
`... final` renders that draft at 1080p. It borrows the API key, media upload and callback
address from the Genjutsu app in `repos/`, so that app must be running.

## Rules of the API that cost us time

- **Edit mode needs a 4–30 second video.** Shorter clips must be slowed or padded first.
- **A video input is billed twice.** Billable seconds = input + output. A 5 s draft is about
  730 credits, 6 s about 875, 16.7 s about 2,480. 1080p is roughly 5.6x the draft rate.
- **A draft can only be finished at 1080p.** There is no 720p finish of an approved draft; a
  720p render is a fresh generation and will not match the draft.
- **Nothing can be tweaked in place.** Any prompt change is a whole new generation that only
  resembles the last one. There is no seed setting.
- **Output filters misfire.** One draft failed with "may be related to copyright restrictions"
  and the identical resubmission passed.
- **Phone footage** carries a rotation tag; make it upright before sending.

## What steers the result

- **A reference still dominates the prompt.** With a look reference attached, Seedance
  reproduces that still and treats the wording as a minor nudge. Asking for "more" in words did
  almost nothing.
- **Without a reference, the wording steers hard** and tends to overshoot (saturated teal,
  heavy red, a dark face). Name what you do not want as well as what you do.
- **Best control:** push the reference still itself to the look you want, then attach it.
- **Do free things in the edit, not in Seedance:** push-ins, trims, volume, music, upscaling.

## Checks before anything goes to a client

- Small print on packaging (badges, weights, barcodes, back-of-pack text) is likely garbled.
  Prefer front-on shots and inspect the 1080p frame by frame.
- A relit real person is a redrawn face. Check likeness and lip sync against the original audio.
- Media is uploaded to a temporary public file host on its way to Enhancor.
