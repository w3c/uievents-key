# uievents-key

This repository is for the [UI Events key specification](https://w3c.github.io/uievents-key/).

If you like this spec, you might be interested in these other specs from the same publisher:

* [UI Events](https://w3c.github.io/uievents/)
* [UI Events KeyboardEvent code Values](https://w3c.github.io/uievents-code/)

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
file in your changelist. All changes should be made in the `index-source.txt`
file.
