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
    constraint = iris.Constraint(
            latitude=lambda cell: args.south < cell < args.north,
            longitude=lambda cell: args.west < cell < args.east)
    print("Reading data from {}".format(args.in_file))
    cubes = iris.load(args.in_file)
    print("N, S, E, W: {}".format(
        (args.north, args.south, args.east, args.west)))
    # Cut out a domain
    small_cubes = []
    for cube in cubes:
        print(cube.name())
        try:
            small_cube = cube.intersection(
                longitude=(args.west, args.east),
                latitude=(args.south, args.north))
        except:
            small_cube = cube.extract(constraint)
        if small_cube is not None:
            print(small_cube)
            small_cubes.append(small_cube)

    print("Writing subset to {}".format(args.out_file))
    iris.save(small_cubes, args.out_file)


if __name__ == '__main__':
    main()
