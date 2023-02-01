from AE.Display.Animation import * 

anim = Animation2d()

anim.add(ellipse, 'E0',
  position = [0.5,0.5],
  major = 0.005,
  minor = 0.005,
  colors = ('white', None),
)

# anim.add(group, 'G',
#   position = [0.5,0.5],
#   orientation = 0.5,
#   draggable = True
# )

# anim.add(ellipse, 'E1',
#   parent = 'G',
#   position = [0,0],
#   major = 0.2,
#   minor = 0.1,
#   colors = (None, 'white'),
#   thickness = 2,
#   linestyle = '--',
# )

# anim.add(circle, 'C',
#   parent = 'G',
#   position = [0.2,0],
#   radius = 0.05,
#   colors = ('#444', 'red'),
# )

# anim.add(text, 'T',
#   parent = 'G',
#   position = [0,0],
#   string = 'a&#946;c',
#   color = 'white',
#   fontsize = 12,
#   center = True
# )

# anim.add(rectangle, 'R',
#   position = [0.15,0.15],
#   width = 0.3,
#   height = 0.3,
#   colors = ('darkcyan', 'white'),
#   orientation = 0.5,
# )

# anim.add(line, 'L',
#   points = [[0.1,0.1],[0.2,0.15]],
#   color = 'yellow',
#   thickness = 2,
#   draggable = True
# )

# anim.add(polygon, 'P',
#   points = [[0.7,0.7],[0.8,0.8],[0.8,0.1]],
#   colors = ['green','red'],
#   thickness = 3,
#   draggable = True
# )

# anim.add(path, 'P',
#   points = [[0.7,0.7],[0.8,0.8],[0.8,0.1]],
#   colors = ['green','red'],
#   thickness = 3,
#   draggable = True
# )

anim.add(arrow, 'A', 
  points = [[0.1,0.1],[0.2,0.15]],
  color = 'darkcyan',
  thickness = 5,
  draggable = True
)

#  anim.composite['A'].points = [[0.1,0.1],[0.3,0.35]]
# anim.composite['A'].locus = 0.5
# anim.composite['A'].shape = 'disk'


anim.show()
