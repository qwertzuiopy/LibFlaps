pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'libflaps')
gnome = import('gnome')

gnome.compile_resources('libflaps',
  'libflaps.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'libflaps.in',
  output: 'libflaps',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

libflaps_sources = [
  '__init__.py',
  'main.py',
  'lib_draw.py',
  'lib_io.py',
  'lib_menu.py',
  'library.py',
  'test.py',
  'lib_toolbar.py'
]

install_data(libflaps_sources, install_dir: moduledir)
