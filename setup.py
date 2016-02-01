#!/usr/bin/env python

from distutils.core import setup

script_name = 'pyclock.py'
classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console :: Curses',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Topic :: Utilities',
]

with open(script_name) as f:
    meta = dict(
        (k.strip(' _'), eval(v)) for k, v in
        # There will be a '\n', with eval(), it's safe to ignore
        (line.split('=') for line in f if line.startswith('__'))
    )

    # renaming meta-data keys
    meta_renames = [
        ('program', 'name'),
        ('website', 'url'),
        ('email', 'author_email'),
    ]
    for old, new in meta_renames:
        if old in meta:
            meta[new] = meta[old]
            del meta[old]

    # keep these
    meta_keys = ['name', 'description', 'version', 'license', 'url', 'author',
                 'author_email']
    meta = dict([m for m in meta.items() if m[0] in meta_keys])

setup_d = dict(
    classifiers=classifiers,
    scripts=[script_name],
    **meta
)

if __name__ == '__main__':
    setup(**setup_d)
