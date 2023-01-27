from AE.Display.Animation import * 

anim = Animation2d()

anim.add(ellipse, 'Ell',
  position = [0.5,0.5],
  major = 0.1,
  minor = 0.2,
  colors = ('#444', 'white'),
  thickness = 2,
  linestyle = '--',
  movable = True
)

anim.add(ellipse, 'Ell',
  position = [0.7,0.5],
  major = 0.1,
  minor = 0.1,
  colors = ('#444', 'red'),
)

# anim.elm['G'] = Animation.element('group',
#   position = [0.5, 0.5],
#   movable = True)

# anim.elm['C'] = Animation.ellipse(
#   parent = 'G',
#   position = [0,0],
#   radius = 0.1,
#   colors = ('#444', 'white'),
#   thickness = 2,
#   linestyle = '--'
# )

# anim.elm['T'] = Animation.element('text',
#   parent = 'G',
#   position = [0,0],
#   string = 'a&#946;c',
#   color = 'white',
#   center = (True, True),
#   fontsize = 10
# )

# anim.elm['L'] = Animation.element('polygon',
#   points = [[0.7,0.7],[0.8,0.8],[0.8,0.1]],
#   colors = ['green','red'],
#   movable = True
# )

anim.show()

