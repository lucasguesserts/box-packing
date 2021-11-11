"""Box Packing
"""

from setuptools import setup

DOCLINES = (__doc__ or '').split("\n")

setup(
    # Metadata
    name='box_packing',
    version='0.0.0-rc.1',
    url='https://github.com/lucasguesserts/box_packing',
    author='Lucas Guesser Targino da Silva',
    author_email='lucasguesserts@gmail.com',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering',
    ],
    description = DOCLINES[0],
    long_description = "\n".join(DOCLINES[2:]),
	keywords=[
        'engineering',
    ],
    # Options
    install_requires=[
        'numpy',
        'pandas',
        'pytest',
    ],
    python_requires='>=3.0',
)
