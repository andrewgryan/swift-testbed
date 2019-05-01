#!/usr/bin/env python
'''
 Read data from a netCDF file, cut out a sub-region and save to a new file
'''
import sys
import os
import iris
import argparse


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("in_file",
                        help="file to extract region from")
    parser.add_argument("out_file",
                        help="file to write to")
    parser.add_argument("--north", default=30, type=int)
    parser.add_argument("--south", default=-18, type=int)
    parser.add_argument("--west", default=90, type=int)
    parser.add_argument("--east", default=154, type=int)
    return parser.parse_args(args=argv)


def main(argv=None):
    args = parse_args(argv=argv)
    print("Reading data from {}".format(args.in_file))
    raw_cube = iris.load(args.in_file)
    print("Extracting N, S, E, W - {}, {}, {}, {}".format(args.north,
                                                          args.south,
                                                          args.east,
                                                          args.west))
    # constraint = iris.Constraint(
    #     latitude=lambda cell: args.south < cell < args.north,
    #     longitude=lambda cell: args.west < cell < args.east)
    # sub_cube = raw_cube.extract(constraint)
    sub_cube = raw_cube.intersection(
        longitude=(args.west, args.east),
        latitude=(args.south, args.north))
    print("Writing subset to {}".format(args.out_file))
    iris.fileformats.netcdf.save(sub_cube, args.out_file, zlib=True)


if __name__ == '__main__':
    main()
