# UI Events KeyboardEvent key Values

This repository is for the [UI Events key](https://w3c.github.io/uievents-key/)
specification.

## Building

This spec was created using [bikeshed](https://github.com/tabatkins/bikeshed).
If you would like to contribute edits, please make sure that your changes
build correctly.

To **build** this spec:

1. Clone this repo into a local directory.
1. Install [bikeshed](https://github.com/tabatkins/bikeshed)
1. Run `python build.py` in your local directory.

To **make edits** to the spec:

1. Edit the `index-source.txt` file.
2. Build (as above). This will create `index.bs` and `index.html` files.

When submitting pull requests, make sure you don't include the `index.bs`
file in your changelist - it's part of `.gitignore` so that you don't include
it accidentally. All changes should be made in the `index-source.txt`
file.

## Visitors Who Read This Spec Also Read

* [UI Events](https://w3c.github.io/uievents/)
* [UI Events KeyboardEvent code Values](https://w3c.github.io/uievents-code/)

