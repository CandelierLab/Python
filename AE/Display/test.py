import AE.Display.Animation as Animation

anim = Animation.Animation2d(window=Animation.Window())

anim.elm['C'] = Animation.element('circle',
  position = [0.1, 0.1],
  radius = 0.1,
  colors = ('#444', 'white'),
  thickness = 2,
  linestyle = '--'
)

anim.elm['T'] = Animation.element('text',
  position = [0.1, 0.1],
  string = 'a&#946;c',
  color = 'white',
  center = (True, True),
  fontsize = 10
)

anim.elm['A'] = Animation.element('arrow',
  points = [(0.2, 0.2), (0.5,0.4)],
  shape = 'disk',
  thickness = 2
)

# anim.elm['A'] = Animation.element('polygon',
#   points = [(0,0), (-0.05,0.1), (0.1,0), (-0.05,-0.1), (0,0)],
#   color = 'red',
#   thickness = 2
# )

anim.window.show()

# --- TO DO
# * Tête ronde