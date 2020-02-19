project('tof_test', 'c')

tofdep = dependency('tof')
gpiodep = dependency('libgpiod')

executable('tof_test',
	files('main.c'),
	dependencies: [tofdep, gpiodep],
)
