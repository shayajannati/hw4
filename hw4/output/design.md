# Campus Customs storefront design (Problem 10)

## Design direction

The goal was a **classic Yale collegiate look that's polished but cute and playful**:
the feel of a varsity sweater, a college pennant and a friendly bulldog, rather than a
corporate store. Every decoration uses one shared palette, type system and set of
motifs (Yale blue, cream, varsity stripes, crests, paw prints), so the page reads as a
single Campus Customs / Yale storefront rather than separate add-ons. The centre of the
page, where people shop, stays clean.

## Color palette

| Role | Color | Used for |
|---|---|---|
| Yale Blue | `#00356B` | header, headings, price chips, buttons, frames and outlines |
| Lighter Yale blue | `#286DC0` | accents, links, the "pennant" offset shadows, the paw prints |
| Light blue | `#DFEAF7` / `#B5CDE8` | chips, borders, the hero gradient, the header tagline |
| White | `#FFFFFF` | product image backgrounds, cards, chat bubbles |
| Cream | `#F7F3EA` | page background (with a faint dot texture), card footers, chat panel |
| Sand | `#E9E2D3` | soft card borders and dashed dividers |
| Ink / muted | `#1D2733` / `#56616F` | body text and secondary text |

Yale blue is the centre of the palette, with light blue, white and cream around it.
This also keeps the project's light blue / navy / white theme.

**Contrast:** all main text and background pairs meet WCAG AA (4.5:1 or more):

- cream on Yale blue: 11.0:1;
- body text on cream: 13.6:1;
- muted text on cream: 5.7:1;
- accent blue on cream: 4.7:1.

## Typography

There are no web-font files: everything uses fonts already on the visitor's computer,
so there are no licensing or redistribution issues and nothing to download.

- **Headings, product names, footer:** a collegiate, editorial serif stack: `Iowan Old
  Style`, `Palatino Linotype`, `Palatino`, `Book Antiqua`, `Georgia`, `serif`.
- **Body and UI text:** a clean rounded sans stack: `Avenir Next`, `Avenir`,
  `Segoe UI`, `Helvetica Neue`, `system-ui`.
- **Small "cute" accents only** (the "Boola Boola! Go Bulldogs" eyebrow, the header
  tagline, the product-page garment type): a handwritten stack, `Chalkboard SE`,
  `Segoe Print`, `Bradley Hand`, `cursive`. It's limited to short labels so reading
  stays easy.

## Mascot: a Handsome Dan-inspired bulldog

- **The asset:** an **original bulldog drawn in SVG for this project**
  (`frontend/src/components/HandsomeDan.tsx`). It isn't copied from any existing
  mascot artwork or website.
- **The look:** a chunky cartoon bulldog with a bold dark outline:
  - a tan "cap" with a white stripe (blaze) down the forehead;
  - floppy ears that fold over at the top of the head and hang beside it;
  - big round, friendly eyes with a large sparkle and a small glint;
  - **one big muzzle** whose outline arches over a mushroom-shaped nose and wraps down
    into both jowls, with wrinkle creases;
  - a short smile with a little pink tongue hanging from it (no teeth);
  - a **Yale-blue sweater** with cream varsity stripes and a serif "Y".

  The tongue is clipped to the area below the smile line, so it always hangs from the
  mouth with no gap. The cartoon style took cues from reference images you shared, but
  the drawing is original SVG, not traced or copied from them.
- **Where it appears:**
  1. in the hero, with a gentle bob animation;
  2. as the round brand badge in the header;
  3. as the chat assistant's avatar in the chat panel header.
- **Decorative only:** `aria-hidden="true"` and `pointer-events: none`, so it never
  blocks clicks or clutters screen readers.

## Campus-inspired side borders

- **The asset:** `frontend/public/decor/campus-border.svg` is **original line art**
  made for this project. It's a vertical collage of:
  - a Gothic tower inspired by Harkness Tower's silhouette;
  - a college archway / gate;
  - a "Y" shield crest;
  - lancet windows;
  - a bulldog paw medallion;
  - an ivy vine running down the frame.

  It's drawn in thin Yale-blue lines on cream, which echoes Yale's collegiate Gothic
  campus. No campus photographs were downloaded.
- **Placement:** `CampusBorders.tsx` shows it as fixed side frames (the right side is
  mirrored), each finished with a double Yale-blue rule. The shopping area is
  centred between them and never overlaps them.
- **Narrower screens:** the frames only show at 1400 px wide or more; below that they
  disappear, so the content gets the full width.
- **Not interactive:** decorative only (`aria-hidden`, `pointer-events: none`).

## Paw-print cursor trail

`frontend/src/components/PawTrail.tsx`:

- **What it does:** moving the mouse leaves small blue bulldog paw prints, one every
  ~42 px. They alternate left and right and are rotated in the direction of travel.
  Each fades and shrinks over 0.75 s and is then removed, with at most 10 on screen.
- **It can never block anything:** the trail layer and every print are
  `pointer-events: none`, so clicks pass straight through to buttons, cards, the
  search box and the chat.
- **It respects reduced motion:** if the visitor's system asks for reduced motion
  (`prefers-reduced-motion: reduce`), no prints are created at all and the trail layer
  is hidden. The mascot's bob animation and the typing-dot animation also stop.
- **Touch-only devices** (`pointer: fine` doesn't match) get no trail, since there's no
  cursor.

## Other styling

- **Header:** Yale blue with a cream pinstripe underneath, a round bulldog badge, and
  the serif "Campus Customs" title.
- **Hero:** a pennant-like card with a Yale-blue outline, an offset "shadow" in the
  lighter blue, a varsity-stripe base, and the mascot. The search box is a rounded
  pill.
- **Product cards:** "trading card" style. White photo area, cream footer with a dashed
  divider, the serif product name, and the price in a Yale-blue pill. They tilt
  slightly on hover.
- **Product page:** the same framed-card style, with the price pill and light-blue
  color chips.
- **Chat:** a Yale-blue launcher with a cream ring; the panel has a cream message area
  and the mascot avatar.
- **Footer:** a small Yale-blue shield with "Y", and "Lux et Veritas".

## Responsive and accessibility considerations

- **Narrow screens:**
  - the side frames disappear below 1400 px;
  - on phones (≤640 px) the hero stacks the mascot above the text and shrinks it;
  - the header tightens at ≤520 px so "Log in" / "Sign up" stay on one line;
  - there's no sideways scrolling at 390 px, and the chat panel fits the screen.
- **Decorations stay out of the way:** they're `aria-hidden` and never take clicks. A
  real-browser check confirmed clicks on product cards, search, login and the chat
  launcher land on those controls.
- **Visible focus:** keyboard focus shows a light-blue outline on links, buttons and
  product cards.
- **Contrast and motion:** all text pairs meet WCAG AA (see above), and reduced motion
  turns off the trail, the mascot bob and hover tilts.

## Why this fits Campus Customs

Campus Customs sells Yale apparel to students, families and fans. Yale blue and cream
read instantly as "Yale" and as "college sweater". The bulldog gives the store a warm,
giftable personality, and the line-art campus frame adds a sense of place without
competing with the products. Because the decorations stay at the edges and never
intercept clicks, the products, prices and chat assistant remain the focus.

## What was tested

These ran in real Google Chrome, headless, via `playwright-core`, against the live
backend and the `gpt-5.6-luna` chatbot. All 21 checks passed:

- 102 products render;
- decorations are present, `aria-hidden` and `pointer-events: none`, and the side
  frames don't overlap the content;
- clicks on a product card, the search box, Log in and the chat launcher land on those
  controls;
- moving the mouse creates paw prints (at most 10), they never capture clicks, a
  product card clicked mid-trail still opens its page, and the prints are gone within
  about 1 s;
- the no-results state and Clear work;
- logging in through the real dialog works;
- saved chat history loads, New chat works, and a live chat reply's product card opens
  the same product page;
- there are no console errors (apart from the expected 401 "not logged in" checks);
- with reduced motion: no paw prints, and the mascot animation is off;
- at 390 px: the side frames are hidden, there's no horizontal overflow, the chat
  panel fits, and the header buttons stay on one line.
