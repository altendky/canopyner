from setuptools import setup, find_packages
setup(
    name = "CANopyner",
    version = "0.1",
    packages = find_packages(),
    entry_points={'gui_scripts': ['canopyner = canopyner.canopyner:main']}
)
