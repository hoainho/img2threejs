# Promotion playbook (attract stars and contributors, without spamming)

This is copy you post from your own accounts. It is deliberately honest about scope so the
project earns trust instead of a spam label. Repo: https://github.com/hoainho/img2threejs

## Ground rules (read first)

- Do NOT open issues or pull requests on three.js, react-three-fiber, or other libraries just to
  advertise this project. That is spam, gets closed, and damages your reputation.
- DO post in venues that exist for showing work, and DO submit to curated lists that accept
  entries. Post once per venue, respond to comments, do not cross-post aggressively.
- Lead with an honest scope line every time: strong for objects, stylized-only for characters.
  The demo GIF is a chest (its strongest result), not a person.

## Submitted PRs (log)

- awesome-threejs (AxiomeCG): https://github.com/AxiomeCG/awesome-threejs/pull/24 (Tools > 3D modeling)

## 1. three.js Discourse — Showcase category

Venue: https://discourse.threejs.org/ (category: Showcase)

Anti-spam / correctness rules for this forum (important):
- Post in the "Showcase" category only. Do NOT use Help/Questions or unrelated threads.
- New Discourse accounts start at trust level 0 and often CANNOT post links or images until they
  reach TL1. Reach TL1 first: read several topics, spend a few minutes in the forum, enter a few
  topics. Then your post with the repo link/GIF will not be auto-flagged.
- One topic only. Do not create duplicates, do not bump, do not paste the same link into other
  people's threads.
- Disclose it is your own project, give an honest scope line, and ask a real question or invite
  feedback/contributors — a pure "star my repo" post gets flagged.
- Reply to every comment; engagement is what separates a showcase from spam.
- Use an accurate, non-clickbait title and correct tags.

Title: img2threejs - rebuild an object photo as a code-only procedural Three.js model

Body:
> I built a skill/toolkit that reconstructs the object in a single reference image as a
> code-only, procedural Three.js model - primitives, procedural shaders, and generated geometry,
> no downloaded meshes or art packs. It runs a staged pipeline (blockout, structure, form,
> material, lighting) with a screenshot-vs-reference review loop at each step.
>
> Honest scope: it is strong for hard-surface objects and stylized/low-poly assets. Characters
> currently read as game/figurine avatars, not photoreal likeness - that is a documented limit.
>
> Repo (MIT, pure-Python stdlib tooling + generated TypeScript): https://github.com/hoainho/img2threejs
> Feedback and contributors welcome, especially on procedural material recipes.

## 2. Reddit - r/threejs and r/webgl

Title: img2threejs: turn an object photo into a procedural, code-only Three.js model (MIT)

Body:
> Open-source toolkit that rebuilds the object in one reference image as procedural Three.js code
> (no mesh downloads), gated by a staged pipeline with a render-vs-reference review loop. Strong
> for hard-surface objects; characters are stylized-only for now (documented). Would love feedback
> and contributors. Repo: https://github.com/hoainho/img2threejs

Flair: Showcase / Project. Post to r/threejs first; wait a day before r/webgl.

## 3. Hacker News - Show HN

Title: Show HN: img2threejs - rebuild an object photo as procedural Three.js code

Text:
> It reconstructs the object in a single image as a code-only procedural Three.js model, gated by
> a staged pipeline (blockout to material to lighting) with a screenshot-vs-reference review loop.
> Pure-Python stdlib tooling emits diffable TypeScript; no downloaded meshes. Honest about limits:
> great for hard-surface objects, stylized-only for people. MIT. Feedback welcome.
> https://github.com/hoainho/img2threejs

Post during US morning (weekday) for visibility. Reply to every comment.

## 4. Short social post (X / Bluesky / Mastodon)

> img2threejs: give it one photo of an object, get back a code-only procedural Three.js model -
> no mesh downloads, quality-gated by a render-vs-reference loop. MIT, contributors welcome.
> https://github.com/hoainho/img2threejs

Attach the demo GIF (assets/demo.gif).

## 5. Awesome-list submission (the welcomed "contribute to a known repo" path)

Candidate lists (verified real + active; read each repo's CONTRIBUTING and format before a PR):
- awesome-threejs: https://github.com/AxiomeCG/awesome-threejs (most active, well-categorized)
- awesome-threejs (alt): https://github.com/we-list/awesome-threejs
- awesome-three-js (alt): https://github.com/crubier/awesome-three-js
- three-js-resources: https://github.com/Fasani/three-js-resources
- awesome-webgl: https://github.com/sjfricke/awesome-webgl (see CONTRIBUTING.md at /blob/master/CONTRIBUTING.md)

Timing note: most awesome lists expect some notability/traction. Submitting a days-old repo with
~1 star can get a PR rejected or read as premature self-promotion. Do the showcase posts first,
gather a bit of traction, then submit. Pick the ONE list that best fits (AxiomeCG/awesome-threejs
under a tools/generators section), follow its exact entry format, and open a single clean PR from
your own account.

Entry line to add (match the list's existing format):
> - [img2threejs](https://github.com/hoainho/img2threejs) - Rebuild the object in a reference image as a code-only, procedural, quality-gated Three.js model.

PR description:
> Adds img2threejs, an MIT-licensed toolkit that reconstructs an object photo as procedural
> Three.js code (no downloaded assets), with a staged review pipeline. Placed under the
> tools/generators section. Happy to adjust wording or placement.

Submit from your own GitHub account, one list at a time, and follow each list's CONTRIBUTING rules.

## 6. Make the repo itself convert visitors

- Topics set: threejs, webgl, 3d, procedural-generation, image-to-3d, generative, typescript, computer-graphics, ai-agents, claude-code.
- README opens with the demo GIF and an honest scope line. Done.
- LICENSE and CONTRIBUTING present. Done.
- Consider a hosted live demo later (the chest project) and link it as the repo homepage - a
  clickable demo converts far better than a GIF.

## Metrics to watch

- Where stars come from (GitHub traffic - referrers). Double down on the venue that converts.
- Issues/PRs opened - reply within a day to keep momentum and turn visitors into contributors.
