# Hasbro Proton Pack Modding Guide

A community-sourced, fully attributed guide to modifying the **Hasbro 1984 Proton Pack and Neutrona Wand**, written for the [GBFans.com wiki](https://www.gbfans.com/wiki). It turns a 91-post forum build thread into a structured reference: disassembly, accuracy fixes, hardware upgrades, inner cyclotron detailing, electronics, the wand, 3D printing, and wearing the pack. Every step links to the post it came from.

**Status:** first draft, **not yet verified against the original posts**. See [Verification](#verification).

| | |
|---|---|
| Scope (v0.1) | Hasbro 1984 Proton Pack and Neutrona Wand |
| Primary source | GBFans thread [Hasbro 1984 Proton Pack BIG Overhaul and Customisation](https://forum.gbfans.com/t/hasbro-1984-proton-pack-big-overhaul-and-customisation/219236), posts #1–91 |
| Wiki draft | [`docs/wiki/hasbro-1984-proton-pack-modding.md`](docs/wiki/hasbro-1984-proton-pack-modding.md), about 3,400 words, 60 posts cited |
| Attribution | footnote on every claim, one per post; [verification checklist](docs/VERIFICATION.md) per post |
| Next scope | HasLab Spengler's Proton Pack and Spirit Halloween packs (see [related threads](docs/SOURCES.md#related-threads-not-yet-mined)) |

This guide builds directly on the work of gbrich, nomake-wan, spooky, mcspain, cantignie and other GBFans members. See **[Credits](#credits)**.

---

## Contents

- [Why this exists](#why-this-exists)
- [How it's made](#how-its-made)
- [Status labels](#status-labels)
- [Verification](#verification)
- [Files](#files)
- [Updating the guide](#updating-the-guide)
- [Credits](#credits)
- [Legal](#legal)

Detailed documentation: [Source index](docs/SOURCES.md) · [Verification checklist](docs/VERIFICATION.md) · [Research log](docs/RESEARCH.md) · [Wiki page workflow](docs/wiki/) · [Outreach](docs/wiki/forum_posts.md)

---

## Why this exists

The Hasbro 1984 overhaul thread is the most-viewed active thread in the GBFans Equipment section (about 1,000 views and 89 replies in its first three months). It holds answers to the questions people keep asking: how to remove the HGA, how to split the cyclotron lid, what size tube replaces the emitter tubes. But the answers are spread through a long build log.

The GBFans wiki documents the screen-used props in detail, but it has no page on modding the consumer packs, and the forum's Proton Pack index thread dates from 2011. This guide fills that gap.

## How it's made

1. **Read the whole thread.** Every post is indexed in [docs/SOURCES.md](docs/SOURCES.md) with what it contributes.
2. **Extract techniques, measurements and lessons**, keeping each one tied to its post number and author.
3. **Reorganize by task** rather than by date, so a builder can go straight to "remove the HGA" or "rebuild the emitter tubes".
4. **Paraphrase, don't copy.** Steps are rewritten in plain language. Members' photos are not reproduced. The page links to the posts instead.
5. **Footnote every claim** using the wiki's footnote syntax, one footnote per post, linking directly to that post.
6. **Verify every statement against its post** before publishing ([checklist](docs/VERIFICATION.md)).
7. **Contact the authors** before publishing, to share the draft, ask for corrections and ask permission to use any of their photos ([outreach drafts](docs/wiki/forum_posts.md)).

## Status labels

The source is builder reports, not reference footage, so the labels differ from the Ecto-1A project:

| Label | Meaning |
|---|---|
| **reported** | one builder did this on their own pack |
| **corroborated** | a second builder confirmed the same method or result |
| **as reported at the time** | prices, stock, lead times and vendor policies, which change |
| *(unlabeled)* | stated in the thread without dispute, for example a part being glued |

Opinions (for example "the inner cyclotron is the weakest area") are attributed to the person who said them.

## Verification

The first draft was compiled from structured summaries of each thread page, so exact figures and part names may have drifted. Before the page goes live, every statement needs checking against the original post:

```bash
python tools/check_wiki.py
```

This checks the footnotes and links, and regenerates [docs/VERIFICATION.md](docs/VERIFICATION.md): one section per cited post, listing every statement on the page that cites it. Open the post, check each statement, tick the post off, and add a `- Note:` line for any correction. Ticks and notes survive regeneration.

## Files

| Path | What |
|---|---|
| [`docs/wiki/hasbro-1984-proton-pack-modding.md`](docs/wiki/hasbro-1984-proton-pack-modding.md) | The wiki page (Markdown, as accepted by the wiki editor: no tables, `[^id]` footnotes) |
| [`docs/wiki/page.json`](docs/wiki/page.json) | Title, proposed URL and location, tags, edit summary, version |
| [`docs/wiki/forum_posts.md`](docs/wiki/forum_posts.md) | Outreach drafts and a record of forum correspondence |
| [`docs/SOURCES.md`](docs/SOURCES.md) | Index of all 91 posts, coverage, related threads to mine next |
| [`docs/VERIFICATION.md`](docs/VERIFICATION.md) | Generated per-post verification checklist |
| [`docs/RESEARCH.md`](docs/RESEARCH.md) | Method and revision history |
| [`tools/check_wiki.py`](tools/check_wiki.py) | Footnote, link and format checker; builds the checklist |

## Updating the guide

1. Edit the wiki page here first, then publish to the wiki, so the two never drift apart.
2. Run `python tools/check_wiki.py`. It fails on undefined or unused footnotes, a post footnote that links to the wrong post, or a Markdown table.
3. Tick off newly verified posts in `docs/VERIFICATION.md`.
4. Bump `version` in `docs/wiki/page.json` and add a line to the revision log in [docs/wiki/README.md](docs/wiki/README.md).
5. Commit with the same summary as the wiki edit.

## Credits

The content of this guide comes from the GBFans thread **[Hasbro 1984 Proton Pack BIG Overhaul and Customisation](https://forum.gbfans.com/t/hasbro-1984-proton-pack-big-overhaul-and-customisation/219236)**:

- **gbrich** — started and documented the build: nearly every technique, measurement and lesson on the page.
- **nomake-wan** — the non-destructive HGA removal method, GPStar support as one of its developers, and historical context.
- **spooky** — HGA tips, the barrel extension, and fitting compatibility notes.
- **mcspain**, **cantignie**, **flashlight_buff** and everyone else who posted questions and progress.
- Video tutorials referenced in the thread by **Imperial Tech Shop** and **RSquad911**.

Compiled by **Ryan Brumback**, with AI assistance (Anthropic's Claude) for organizing the thread.

## Legal

Fan project for non-commercial use. *Ghostbusters* and related marks are the property of Columbia Pictures / Sony Pictures. Hasbro, HasLab, GPStar, Redman Studio Workshop and other product names belong to their owners. This project is not affiliated with or endorsed by any of them. Modifying the pack may void its warranty; you do so at your own risk.

The guide text is released under [CC BY 4.0](LICENSE) and the checker script under the MIT license (see [LICENSE](LICENSE)). The techniques belong to the forum members who shared them and are credited throughout. Forum posts and photos are not reproduced here.
