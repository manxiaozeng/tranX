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
