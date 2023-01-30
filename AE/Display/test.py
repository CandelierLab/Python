from AE.Display.Animation import * 

anim = Animation2d()

anim.add(group, 'G',
  position = [0.5,0.5],
)

anim.add(ellipse, 'E1',
  parent = 'G',
  position = [0,0],
  major = 0.2,
  minor = 0.1,
  colors = ('#444', 'white'),
  thickness = 2,
  linestyle = '--',
)

anim.add(ellipse, 'E2',
  parent = 'G',
  position = [0.2,0],
  major = 0.1,
  minor = 0.1,
  colors = ('#444', 'red'),
)

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

