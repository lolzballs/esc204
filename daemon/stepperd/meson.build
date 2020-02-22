gpiodep = dependency('libgpiod')

executable(
  'stepperd',
  'main.c',
  'commands.c',
  include_directories: [robot_inc],
  link_with: [lib_robot_common],
  dependencies: [gpiodep],
  install: true
)
