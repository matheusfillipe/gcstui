# Work in progress

# GSTUI

A Text User Interface for exploring Google Cloud Storage. Fast and cached.

## Intallation

```sh
pip install -U gstui
```

## Usage

Run `gstui` or `gstui --help` to see more options.

Loading buckets or the inital listing for the first time can take a long time to cache. You can create an initial cache of everything with: `gstui -a`.

The first picker is for selecting the bucket and the second is for selecting the blob to download.

# Development

Be free to submit a PR. Check the formatting with flake8 and for new features try to write tests.

## Tests


```sh
poetry run tests
```

Or manually

```sh
poetry run pytest tests -n 4 -vvv
```

## TODO

- [ ] Better thread management
- [ ] Don't rely on `time.sleep` for cache tests
- [ ] [urwid](https://github.com/urwid/urwid) UI

# Related Projects

* [gsutil](https://github.com/GoogleCloudPlatform/gsutil) A command line tool for interacting with cloud storage services. 
* [gcsfuse](https://github.com/GoogleCloudPlatform/gcsfuse) A user-space file system for interacting with Google Cloud Storage 
