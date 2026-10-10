# CLAUDE.md — Sirio

Inherits from `~/Master/CLAUDE.md`. This file is authoritative inside this project.

## What this is

Jesse's working folder for **Incubator Games**, the AI-business program run by Sirio Berati
(tein). Reference material, notes, and anything built while going through it.

Status: side project. Just started — purpose and scope still to be defined by Jesse.

## Layout

- `1. Incubator Games /` — source decks from the program (PDFs, image-only, not text-searchable).
- `repos/` — forks of Sirio's open-source repos. Each is its own git repo, gitignored here.
  `origin` = our fork in `JessesOS`, `upstream` = `sirioberati`. Pull his updates with
  `git pull upstream main`.
  - `Genjustsu-Open-Source-Workflow` — local UI that swaps the people in a video (depth + SAM 3
    masks + Seedance 2.5 via the Enhancor API). Needs Enhancor and Replicate keys.
    Runs at `http://127.0.0.1:8770` via `bash start.command`. Our fork carries two fixes not in
    Sirio's original (2026-10-08): phone footage is rotated upright, and the mask runs on the
    original video when the subject prompt is specific or the depth mask is incomplete.
    First successful run: barber swap on an 11.6 s phone clip, draft cost 1,750 credits.
  - `Seedance-2.0-AI-UGC` — Claude Code toolkit for AI UGC ad variants via the Enhancor API.
- `video-studio/` — Jesse's own tools (Seedance script, look transfer, background remover to
  come). Its own **private** git repo, `JessesOS/video-studio`, gitignored here. Read its
  `CLAUDE.md` before working in it.
- `Clients/` — client job folders and video, one folder per client (`Clients/letsdoyumcha`).
  Local only, gitignored. Never commit anything from it: this repo is public.
- `research_notes/`, `reports/` — research on Sirio and Enhancor. Not committed while the repo
  is public.

## Index

Status, next steps and a handover line for each Sirio workflow are in
`~/Master/Side_Projects/Workflows/Sirio/`, one file per workflow. Read the relevant file there first.

## Rules

- **This repo is public.** Nothing private goes in: no credentials, no client data, no personal
  finance.
- The program PDFs are third-party material and are gitignored. They stay local unless Jesse
  decides otherwise.
- Markdown is canonical. Notes and takeaways go in `.md` files.
- Commit and push at the end of a work session.

---
*Last updated: 2026-10-08*
