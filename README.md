# SketchToDroidRes

This tool generate Android ressources as .png out of artboards in Sketch (http://bohemiancoding.com/sketch/).
This is an opinionated vision of ressources generation and might not fit to everyone's workflow.

## Creation of .sketch files
One artboard is one asset. Artboards need to be named carefully as assets will have the artboard's name.
The .sketch file can contain as many pages as you want


## Using the tool
```bash
./SketchToDroidRes -i /xxx/mySketches -o /xxx/src/main/res -r mdpi -r xxxhdpi
```

It will scan all .sketch in /xxx/mySketches and will generate mdpi and xxxhdpi
resolutions of assets and store them in /xxx/src/main/res.

```
$ ./SketchToDroidRes --help
usage: sketchToDroidRes.py [-h] [-i INPUT] [-o OUTPUT]
                           [-s {mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}]
                           [-r {mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}] [-c CONFIG]
                           [--print-config] [--print-args] [--version]

Generate Android ressource from .sketch files.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Directory or file containing .sketch files
  -o OUTPUT, --output OUTPUT
                        "res" directory of the Android app
  -s {mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}, --reference-res {mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}
                        Sketch files resolution. i.e.: mdpi -> 1 sketch's
                        pixel = 1dpi on device
  -r {mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}, --resolutions {mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}
                        Resolutions to generate
  -c CONFIG, --config CONFIG
                        Path to the config file
  --version             show program's version number and exit
```

## Running the example
```bash
git clone https://github.com/bydavy/sketchtodroidres.git
cd example
../sketchToDroidRes.py
```

## Configuration file

You can skip arguments when using the tool if you have a SketchToDroidRes.config file in your working directory;

### Example of SketchToDroidRes.config
```
[Config]
input=/xxx/mySketches
inputResolution=xxhdpi
output=/xxx/src/main/res
outputResolutions=xxhdpi,xxxhdpi
```

