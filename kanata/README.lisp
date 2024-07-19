(defcfg
    linux-dev "/dev/input/by-path/platform-i8042-serio-0-event-kbd"
    process-unmapped-keys yes)

(defalias
    lwr (layer-toggle lower)
    qwr (layer-switch qwerty)
    dvk (layer-switch dvorak)
    cmk (layer-switch colemak))

(defsrc
      esc  f1 f2 f3 f4 f5 f6 f7 f8 f9 f10 f11 f12 prnt ins del
      `    1  2  3  4  5  6  7  8  9  0   -   =   bspc
      tab  q  w  e  r  t  y  u  i  o  p   [   ]   ret
      caps a  s  d  f  g  h  j  k  l  ;   '   \
      lsft  z  x  c  v  b  n  m  ,  .   /   rsft
      lctl lmet  lalt  spc  ralt  rctl  lft  up  down rght)

(deflayer colemak
      esc  f1 f2 f3 f4 f5 f6 f7 f8 f9 f10 f11 f12 @cmk @qwr del
      `    1  2  3  4  5  6  7  8  9  0   '   =   bspc
      tab  q  w  f  p  b  j  l  u  y  ;   [   ]   ret
      lctl a  r  s  t  g  m  n  e  i   o   -  \
      lsft  x  c  d  v  z  k  h  ,  .  /  rsft
      lctl lmet  lalt  spc  @lwr  rctl  lft  up  down rght)

(deflayer qwerty
        esc  f1 f2 f3 f4 f5 f6 f7 f8 f9 f10 f11 f12 @cmk @qwr del
        `    1  2  3  4  5  6  7  8  9  0   -   =   bspc
        tab  q  w  e  r  t  y  u  i  o  p   [   ]   ret
        lctl a  s  d  f  g  h  j  k  l  ;   '   \
        lsft z  x  c  v  b  n  m  ,  .   /   rsft
        lctl lmet  lalt  spc  @lwr  rctl  lft  up  down rght)

(deflayer dvorak
        esc  f1 f2 f3 f4 f5 f6 f7 f8 f9 f10 f11 f12 @cmk @qwr del
        `    1  2  3  4  5  6  7  8  9  0   [   ]   bspc
        tab  '  ,  .  p  y  f  g  c  r  l   /   =   ret
        lctl a  o  e  u  i  d  h  t  n  s   -   \
        lsft ;  q  j  k  x  b  m  w  v   z   rsft
        lctl lmet  lalt  spc  @lwr  rctl  lft  up  down rght)

(deflayer lower
        _    _    _    _    _  _  _  _  _  _  _   _   _   _    _    _
        _    @cmk @qwr @dvk _  _  _  _  _  _  _   _   _   _
        _    _    _    _    _  _  _  _  _  _  _   _   _   _
        _    _    _    _    _  _  _  _  _  _  _   _   _
        _    _    _    _  _  _  _  _  _  _   _   _
        _    _    _    _    _  _  _  _  _  _)
