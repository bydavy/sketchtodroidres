#!/usr/bin/env python

import ConfigParser

import argparse
import json
import os
import re
import subprocess
import sys

from os import listdir
from os.path import isfile, join, isdir, abspath, isabs

DEBUG = True

DEFAULT_DESIGN_RES = "mdpi"
ANDROID_RES = ["mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"]
RES_TO_SCALE = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2,
                "xxhdpi": 3, "xxxhdpi": 4}

SKETCH_SCALE_PATTERN = "@[0-9]*(.[0-9]*)?x"
RESOLUTION_SEPARATOR = ","

DEFAULT_CONFIG_FILENAME = 'sketchToDroidRes.config'

VERSION = "1.0"


def check_sketchtool():
    """
    Exit if sketchtool is not installed
    """
    try:
        subprocess.check_output("sketchtool --version", shell=True)
    except subprocess.CalledProcessError:
        print "sketchtool is not installed!\n\
        Go to http://bohemiancoding.com/sketch/tool/"
        sys.exit(2)


def is_sketch_file(file):
    """
    Return true if file is a file with the sketch extension, false otherw

    @type file: string
    @param file: file to check
    @return: true if file is a .sketch file, false otherwise
    """
    if not isfile(file):
        return False

    return os.path.splitext(file)[1][1:] == "sketch"


def get_artboards(file):
    """
    Return a list of artboard names

    @type file: string
    @param file: sketch file
    """
    # Create a list of artboard name
    names = []

    cmd = "sketchtool list artboards \"%s\"" % file
    output = subprocess.check_output(cmd, shell=True)
    pages = json.loads(output)["pages"]
    for page in pages:
        for artboard in page["artboards"]:
            n = artboard["name"]
            names.append(n)

    return names


def generate_assets(file, scale, output):
    """
    Generate assets for a file and a scale

    @type file: string
    @param file: sketch file to use for assets generation
    @type scale: string
    @param file: export scale 1x, 1.5x, 2x, etc
    @type output: string
    @param output: output directory
    """
    scale_str = sketch_scale(scale)
    cmd = "sketchtool export artboards \"%s\" --overwriting \
--formats=png --scales=%s --output=%s" % (file, scale_str, output)
    result = subprocess.check_output(cmd, shell=True)

    generated = []
    for line in result.split('\n'):
        if re.search('^Exported *', line):
            efile = line.split('Exported ')[1]
            efile = strip_sketch_scale_suffix(output, efile)
            generated.append(efile)
    return generated


def strip_sketch_scale_suffix(output, file):
    """
    Remove the scale appended by Sketch to exported files

    @type output: string
    @param output: file's directorty
    @type file: string
    @param file: file to rename
    @return the renamed filename
    """
    if re.search(SKETCH_SCALE_PATTERN, file):
        filepath = join(output, file)
        rfile = re.sub(SKETCH_SCALE_PATTERN, "", file)
        rfilepath = join(output, rfile)
        os.rename(filepath, rfilepath)
        file = rfile
    return file


def sketch_scale(scale):
    """
    Convert a scale to a sketch scale.
    i.e.: 1.5 to 1.5x

    @type scale: float
    @param scale: scale
    """
    return "%fx" % scale


def compute_scaling_factor(inputRes, outputRes):
    """
    Compute the scaling factor to go from input to output resolution

    @type inputRes: string see ANDROID_RES
    @param inputRes: input resolution
    @type outputRes: string see ANDROID_RES
    @param outputRes: output resolution
    @return the scaling factor as a float
    """
    in_scale = RES_TO_SCALE[inputRes]
    out_scale = RES_TO_SCALE[outputRes]

    return out_scale / in_scale


def generate_assets_in_dir(sketchDir, inputRes, resDir, outputRes):
    """
    Generate assets for all sketch files in sketchDir

    @type sketchDir: string
    @param: path of the dir to scan for sketch files
    @type inputRes: string see ANDROID_RES
    @param inputRes: input resolution
    @type resDir: string
    @param resDir: "res" directory of the android app
    @type outputRes: list of strings see ANDROID_RES
    @param outputRes: list of output resolutions
    """
    for f in listdir(sketchDir):
        file = join(sketchDir, f)
        if is_sketch_file(file):
            generate_assets_from_file(file, inputRes, resDir, outputRes)


def generate_assets_from_file(file, inputRes, resDir, outputRes):
    """
    Generate assets from a Sketch file.

    @type file: string
    @param file: sketch file
    @type inputRes: string see ANDROID_RES
    @param inputRes: input resolution
    @type resDir: string
    @param resDir: "res" directory of the android app
    @type outputRes: list of strings see ANDROID_RES
    @param outputRes: list of output resolutions
    """
    if not is_sketch_file(file):
        print "The input file is not a .sketch file: %s" % file
        sys.exit(2)
        return

    baseName = os.path.basename(file)
    print "File: " + baseName

    artboards = get_artboards(file)
    if len(artboards) == 0:
        print "No artboard"
        return

    print "(%d artboards)" % len(artboards)

    for r in outputRes:
        scale = compute_scaling_factor(inputRes, r)
        outputDir = join(resDir, "drawable-%s" % r)

        assets = generate_assets(file, scale, outputDir)
        if len(assets) != len(artboards):
            print "Something doesn't match.\n"
            print "artboards: %s" % artboards
            print "generated: %s" % repr(assets)
            sys.exit(2)

        print "\t%s" % r
        print "\t\t%s" % repr(assets)
    print "\n"


def get_from_config_default(configParser, section, key, default):
    """
    Get from config if key exists, otherwise returns the default value

    @type configParser: ConfigParser
    @param confiParser: configParser to read from
    @type section: string
    @param section: section of the key
    @type key: string
    @param key: key to look for
    @type default: string
    @param default: default value if key doesn't exist
    @return key's value or default if key doesn't exist
    """
    value = default
    try:
        if configParser.has_option(section, key):
            value = configParser.get(section, key)
    except ConfigParser.NoOptionError:
        pass

    return value


def help():
    """
    Print out the help
    """
    get_arg_parser().print_help()


def get_arg_parser():
    parser = argparse.ArgumentParser(
        description='Generate Android ressource from .sketch files.')
    parser.add_argument(
        '-i', '--input',
        dest='input',
        help='Directory or file containing .sketch files')
    parser.add_argument(
        '-o', '--output',
        dest='output',
        help='"res" directory of the Android app')
    parser.add_argument(
        '-s', '--reference-res',
        dest='inputRes',
        choices=ANDROID_RES,
        help='Sketch files resolution. i.e.: mdpi -> 1 sketch\'s pixel = 1dpi on device')
    parser.add_argument(
        '-r', '--resolutions',
        dest='outputRes',
        action='append',
        choices=ANDROID_RES,
        help='Resolutions to generate')
    parser.add_argument(
        '-c', '--config',
        dest='config',
        help='Path to the config file')
    if DEBUG:
        parser.add_argument(
            '--print-config',
            dest='print_config',
            action='store_true',
            help='(debug) print the config file read and exit')
        parser.add_argument(
            '--print-args',
            dest='print_args',
            action='store_true',
            help='(debug) print generation args and exit')
    parser.add_argument(
        '--version',
        action='version',
        version=VERSION)

    return parser


def get_config_path(path):
    if path is not None:
        if not isfile(path):
            sys.exit("File %s doesn't exist" % path)
    elif isfile(DEFAULT_CONFIG_FILENAME):
        # Default config filename
        path = DEFAULT_CONFIG_FILENAME

    return path


def get(value, default):
    if value is None:
        return default
    return value


def main(argv):
    check_sketchtool()

    # Read args
    args = get_arg_parser().parse_args()

    config_path = get_config_path(args.config)
    if not isabs(config_path):
        config_path = join(os.getcwd(), config_path)

    inputDir = None
    outputDir = None
    inputRes = DEFAULT_DESIGN_RES
    outputRes = ANDROID_RES

    # Load configuration from file
    if config_path is not None:
        config_head, config_tail = os.path.split(config_path)
        try:
            config = ConfigParser.ConfigParser()
            config.readfp(open(config_path))
            inputDir = get_from_config_default(
                config, 'Config', 'input', inputDir)
            if not isabs(inputDir):
                inputDir = join(config_head, inputDir)
            outputDir = get_from_config_default(
                config, 'Config', 'output', outputDir)
            if not isabs(outputDir):
                outputDir = join(config_head, outputDir)
            inputRes = get_from_config_default(
                config, 'Config', 'inputResolution', inputRes)
            outputRes = get_from_config_default(
                config, 'Config', 'outputResolutions', outputRes)
            if type(outputRes) is str:
                outputRes = outputRes.split(RESOLUTION_SEPARATOR)
        except:
            sys.exit("Syntax error in config file: %s" % config_path)

    if args.print_config:
        print """input=%s
output=%s
inputRes=%s
outputResolutions=%s""" % (inputDir, outputDir, inputRes, outputRes)
        sys.exit(0)

    # Override configuration with arguments
    inputDir = get(args.input, inputDir)
    outputDir = get(args.output, outputDir)
    inputRes = get(args.inputRes, inputRes)
    outputRes = get(args.outputRes, outputRes)

    if args.print_args:
        print """input=%s
output=%s
inputRes=%s
outputResolutions=%s""" % (inputDir, outputDir, inputRes, outputRes)
        sys.exit(0)

    # Check args validity
    if inputDir is None:
        print "No input dir specified!"
        help()
        sys.exit(2)

    if not isdir(inputDir) and not isfile(inputDir):
        print "%s doesn't exist" % inputDir
        sys.exit(2)

    if outputDir is None:
        print "No ouput dir specified!"
        help()
        sys.exit(2)

    if not isdir(outputDir):
        print "%s doesn't exist" % outputDir
        sys.exit(2)

    # Allow relative paths
    inputDir = abspath(inputDir)
    outputDir = abspath(outputDir)

    print "Input resolution: %s" % inputRes
    print "Output resolutions: %s\n" % outputRes

    # Execute command
    if isfile(inputDir):
        generate_assets_from_file(
            inputDir, inputRes, outputDir, outputRes)
    else:
        generate_assets_in_dir(
            inputDir, inputRes, outputDir, outputRes)


if __name__ == "__main__":
    main(sys.argv[1:])
