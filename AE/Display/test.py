from AE.Display.Animation import * 

anim = Animation2d()

anim.add(ellipse, 'E0',
  position = [0.5,0.5],
  major = 0.01,
  minor = 0.01,
  colors = ('red', None),
  zvalue = 0
)

anim.add(group, 'G',
  position = [0.5,0.5],
  draggable = True
)

anim.add(ellipse, 'E1',
  parent = 'G',
  position = [0,0],
  major = 0.2,
  minor = 0.1,
  colors = ('None', 'white'),
  thickness = 2,
  linestyle = '--',
  orientation = 2,
)

anim.add(ellipse, 'E2',
  parent = 'G',
  position = [0.2,0],
  major = 0.1,
  minor = 0.1,
  colors = ('#444', 'red'),
)

# anim.add(text, 'T',
#   parent = 'G',
#   position = [0,0],
#   string = 'a&#946;c',
#   color = 'white',
#   fontsize = 12
# )

# anim.item['T'].position = (0.2,0.3)
# anim.item['T'].move(0.1, -0.1)

# anim.elm['L'] = Animation.element('polygon',
#   points = [[0.7,0.7],[0.8,0.8],[0.8,0.1]],
#   colors = ['green','red'],
#   movable = True
# )

anim.show()
