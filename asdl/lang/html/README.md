# Support for HTML

This readme covers all changes relevant to the addition of HTML as a
supported language. This includes some more general features like support
for Floydhub.

## Environment
There is a conda environment `py2torch3`, use by:
```
$ conda activate py2torch3
```

## Floydhub

### Launch

See `./launch_train_run.sh` in the root dir.

```
./launch_train_run.sh "Smoke test 100 CPU" 1h-vid
```

Where `1h-vid` is a name of a dataset found in `./datasets/html/dev-data/`

Manually edit that file to change between gpu/cpu.

To launch and start the web server.
```
floyd run --env pytorch-0.3:py2 --cpu --mode serve
```

### Example data
https://www.w3schools.com/html/mov_bbb.mp4

### Running the server
I modified the server to only display HTML as a supported language, and tweaked the styles a bit. Run the server with:
```
$ cd path/to/tranx
$ python server/app.py --config_file data/server/config_py2.json
```
Where config_py2.json should include an entry for `html`, like:
```
"html": {
  "parser": "default_parser",
  "example_processor": "html_example_processor",
  "model_path": "data/pretrained_models/html-162.bin",
  "beam_size": 15
}
```

The html-162.bin was downloaded from a training run on Floydhub. See 162/files/saved_models/html/mturk-12k-fuzzed-simple-urls
