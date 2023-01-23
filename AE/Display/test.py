import AE.Display.Animation as Animation

anim = Animation.Animation2d(window=Animation.Window())

anim.elm['C'] = Animation.element('circle',
  position = (0.5, 0.5),
  radius = 0.1,
  color = ('#444', '#ccc'),
  thickness = 2
)

anim.elm['T'] = Animation.element('text',
  position = (0.5, 0.5),
  string = 'abc',
  color = 'white'
)

anim.window.show()

# --- TO DO
# * Add text element
# * Update doc