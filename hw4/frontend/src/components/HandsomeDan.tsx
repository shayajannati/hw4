/**
 * Original "Handsome Dan"-inspired bulldog mascot, drawn in SVG for this project
 * (not traced or copied from any existing artwork). Decorative only: hidden from
 * screen readers and never captures clicks.
 */
const INK = '#2a2346' // cartoon outline
const FUR = '#fbf8f2'
const TAN = '#c9946a'
const TAN_LIGHT = '#e2c3a4'
// Smile: a concave curve between the jowl flaps. The tongue is clipped to the area below it.
const SMILE = 'M84 112 Q100 124 116 112'

export function HandsomeDan({ size = 160, className = '' }: { size?: number; className?: string }) {
  const head = 'M42 90 C40 56 66 40 100 40 C134 40 160 56 158 90 C158 120 134 136 100 136 C66 136 42 120 42 90 Z'
  return (
    <svg
      className={`handsome-dan ${className}`}
      width={size}
      height={size}
      viewBox="0 0 200 200"
      aria-hidden="true"
      focusable="false"
      style={{ pointerEvents: 'none' }}
    >
      <defs>
        <clipPath id="dan-head-clip">
          <path d={head} />
        </clipPath>
        <clipPath id="dan-below-smile">
          <path d={`${SMILE} L116 150 L84 150 Z`} />
        </clipPath>
      </defs>
      <g strokeLinejoin="round" strokeLinecap="round">
        {/* Yale sweater */}
        <path d="M34 198 C34 154 60 130 100 130 C140 130 166 154 166 198 Z" fill="#00356b" stroke={INK} strokeWidth="4" />
        <path d="M44 178 H156" stroke="#f7f3ea" strokeWidth="5" />
        <path d="M40 188 H160" stroke="#f7f3ea" strokeWidth="5" />
        <text x="100" y="172" textAnchor="middle" fontFamily="Georgia, 'Times New Roman', serif" fontWeight="700" fontSize="28" fill="#f7f3ea">Y</text>

        {/* head: tan cap with a white stripe (blaze) down the forehead */}
        <path d={head} fill={FUR} />
        <g clipPath="url(#dan-head-clip)">
          <path d="M30 36 H170 V92 C150 86 128 86 112 90 L108 54 C104 46 96 46 92 54 L88 90 C72 86 50 86 30 92 Z" fill={TAN} />
        </g>
        <path d={head} fill="none" stroke={INK} strokeWidth="4" />

        {/* floppy folded ears: attached at the top of the head, flopping over and hanging down beside it */}
        <path d="M74 44 C58 38 40 42 30 54 C24 62 26 78 34 92 C37 98 45 98 47 91 C48 80 50 68 58 58 C62 52 68 48 74 46 Z" fill={TAN} stroke={INK} strokeWidth="4" />
        <path d="M62 52 C52 52 42 58 38 66 C38 76 40 84 43 88 C44 78 47 68 54 60 C56 56 59 54 62 52 Z" fill={TAN_LIGHT} />
        <path d="M126 44 C142 38 160 42 170 54 C176 62 174 78 166 92 C163 98 155 98 153 91 C152 80 150 68 142 58 C138 52 132 48 126 46 Z" fill={TAN} stroke={INK} strokeWidth="4" />
        <path d="M138 52 C148 52 158 58 162 66 C162 76 160 84 157 88 C156 78 153 68 146 60 C144 56 141 54 138 52 Z" fill={TAN_LIGHT} />

        {/* big round, friendly eyes: large sparkle at the top and a small glint at the bottom */}
        <circle cx="81" cy="67" r="9.5" fill={INK} />
        <circle cx="119" cy="67" r="9.5" fill={INK} />
        <circle cx="84.5" cy="63" r="3.6" fill="#fff" />
        <circle cx="122.5" cy="63" r="3.6" fill="#fff" />
        <path d="M75 70 C76 74 79 75 82 75" fill="none" stroke="#fff" strokeWidth="2" />
        <path d="M113 70 C114 74 117 75 120 75" fill="none" stroke="#fff" strokeWidth="2" />

        {/* big muzzle: the outline arches over the nose and wraps down into both jowls */}
        <path
          d="M56 112 C52 94 64 80 82 78 C90 77 95 80 100 80 C105 80 110 77 118 78 C136 80 148 94 144 112 C142 130 128 142 114 138 C108 136 104 134 100 134 C96 134 92 136 86 138 C72 142 58 130 56 112 Z"
          fill={FUR}
          stroke={INK}
          strokeWidth="4"
        />
        {/* jowl wrinkle creases */}
        <path d="M70 98 C66 104 66 112 70 118" fill="none" stroke={INK} strokeWidth="2.5" />
        <path d="M130 98 C134 104 134 112 130 118" fill="none" stroke={INK} strokeWidth="2.5" />
        <path d="M74 126 C80 130 86 130 90 128" fill="none" stroke="#c8d3e6" strokeWidth="3" />
        <path d="M126 126 C120 130 114 130 110 128" fill="none" stroke="#c8d3e6" strokeWidth="3" />

        {/* mushroom-shaped nose (rounded cap + short stem) + line down to the smile */}
        <path d="M86 91 C86 85.5 92.5 83 100 83 C107.5 83 114 85.5 114 91 C114 95 109 96.5 104.5 96.5 L103.5 100.5 C102.6 102 97.4 102 96.5 100.5 L95.5 96.5 C91 96.5 86 95 86 91 Z" fill="#3c3f5c" stroke={INK} strokeWidth="3" />
        <ellipse cx="95" cy="87" rx="4" ry="1.7" fill="#fff" opacity="0.45" />
        <path d="M100 101.5 V118" stroke={INK} strokeWidth="3" />

        {/* tongue: clipped to below the smile, so it hangs from the line with no gap */}
        <g clipPath="url(#dan-below-smile)">
          <ellipse cx="100" cy="122" rx="8" ry="10" fill="#f29bb5" stroke={INK} strokeWidth="3" />
          <path d="M100 119 V127" stroke="#d9728f" strokeWidth="2" />
        </g>
        {/* smile, drawn last so it sits on the tongue's top edge */}
        <path d={SMILE} fill="none" stroke={INK} strokeWidth="3" />
      </g>
    </svg>
  )
}
