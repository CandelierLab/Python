from AE.Display.Animation import * 

anim = Animation2d()

anim.add(ellipse, 'E0',
  position = [0.5,0.5],
  major = 0.005,
  minor = 0.005,
  colors = ('white', None),
)

anim.add(group, 'G',
  position = [0.5,0.5],
  orientation = 0.5,
  draggable = True
)

anim.add(ellipse, 'E1',
  parent = 'G',
  position = [0,0],
  major = 0.2,
  minor = 0.1,
  colors = (None, 'white'),
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

anim.add(text, 'T',
  parent = 'G',
  position = [0,0],
  string = 'a&#946;c',
  color = 'white',
  fontsize = 12,
  center = True
)

# anim.elm['L'] = Animation.element('polygon',
#   points = [[0.7,0.7],[0.8,0.8],[0.8,0.1]],
#   colors = ['green','red'],
#   movable = True
# )

# anim.item['T'].center = True


anim.show()
