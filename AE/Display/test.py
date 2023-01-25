import AE.Display.Animation as Animation

anim = Animation.Animation2d(window=Animation.Window())

anim.elm['G'] = Animation.element('group',
  position = [0.5, 0.5],
  movable = True)

anim.elm['C'] = Animation.element('circle',
  parent = 'G',
  position = [0,0],
  radius = 0.1,
  colors = ('#444', 'white'),
  thickness = 2,
  linestyle = '--'
)

anim.elm['T'] = Animation.element('text',
  parent = 'G',
  position = [0,0],
  string = 'a&#946;c',
  color = 'white',
  center = (True, True),
  fontsize = 10
)

anim.window.show()