#!/usr/bin/env  python
import iris.exceptions
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
import argparse
import os
import sys
import configparser
import iris


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pressures', type=csv_float)
    return parser.parse_args()


def csv_float(value):
    return [float(x) for x in value.split(',')]


def main():
    args = parse_args()
    in_files = os.environ['IN_FILES']
    out_file = os.environ['OUT_FILE']
    var_list_path = os.environ['VAR_LIST_PATH']
    try:
        compression_level = int(os.environ['COMPRESSION_LEVEL'])
    except KeyError:
        compression_level = None
    except ValueError:
        compression_level = None
    stash_codes = load_fields_dict(var_list_path)
    print(iris.__version__)
    print(stash_codes)
    if isinstance(in_files, str):
        in_files = in_files.split()

    print(in_files)
    print(out_file)
    print(stash_codes)
    print(compression_level)
    print(args.pressures)

    convert_files(in_files, out_file, stash_codes, compression_level,
                  pressures=args.pressures)


def convert_files(in_files, out_file, stash_codes, compression_level,
                  pressures=None):
    """Convert a collection of UM diagnostic files to a single NetCDF file

    A dictionary of Stash codes can be used to select a subset of
    the available diagnostics
    """
    all_cubes = []
    for field, settings in stash_codes.items():
        print('creating single cube of {0}'.format(field))
        prefix = settings['filename']
        stash_section = settings['stash_section']
        stash_item = settings['stash_item']
        accumulate = settings['accumulate']
        paths = select_files(in_files, prefix)
        if len(paths) == 0:
            print("could not find: '{}'".format(prefix))
            sys.exit(1)
        print('merging fields for the following input files:')
        print('\n'.join(paths))
        if accumulate:
            def cube_func(cube):
                return (cube.attributes['STASH'].section == stash_section and
                        cube.attributes['STASH'].item == stash_item and
                        len(cube.cell_methods) > 0)
        else:
            def cube_func(cube):
                return (cube.attributes['STASH'].section == stash_section and
                        cube.attributes['STASH'].item == stash_item and
                        len(cube.cell_methods) == 0)
        constraint = iris.Constraint(cube_func=cube_func)
        cubes = []
        for path in paths:
            print(path, stash_section, stash_item)
            try:
                cube = iris.load_cube(path, constraint)
            except (ValueError, iris.exceptions.ConstraintMismatchError):
                continue
            print(cube)
            if pressures is not None:
                dims = [d for d in cube.coords() if d.name() == 'pressure']
                if len(dims) > 0:
                    try:
                        cube = cube.interpolate(
                            [('pressure', pressures)],
                            iris.analysis.Nearest())
                    except ValueError:
                        print("could not interpolate: {}".format(path))
                        continue
            print(cube)
            cubes.append(cube)
        if len(cubes) == 0:
            continue

        cube_list = iris.cube.CubeList(cubes)
        unify_time_units(cube_list)
        equalise_attributes(cube_list)
        concatted_cube = cube_list.concatenate_cube()
        all_cubes.append(concatted_cube)

    if len(all_cubes) == 0:
        print("NO CUBES FOUND")
        sys.exit(0)  # Hack to bail out without error code

    cubelist = iris.cube.CubeList(all_cubes)
    print(cubelist)

    print('writing concatenated cubelist to {0}'.format(out_file))
    if compression_level:
        msg = ('writing data to compressed netcdf file, '
               'complevel={0}'.format(compression_level))
        print(msg)
        iris.save(cubelist,
                  out_file,
                  zlib=True,
                  complevel=compression_level)
    else:
        print('writing data to uncompressed netcdf file')
        iris.save(cubelist, out_file)


def load_fields_dict(path):
    parser = configparser.RawConfigParser()
    parser.read(path)
    fields = {}
    for section in parser.sections():
        fields[section] = dict(parser.items(section))
        try:
            fields[section]['stash_section'] = int(fields[section]['stash_section'])
            fields[section]['stash_item'] = int(fields[section]['stash_item'])
            fields[section]['accumulate'] = fields[section]['accumulate'] == 'True'
        except ValueError:
            print('stash values not converted to numbers.')
    return fields


def select_files(paths, stem):
    """Select files by their file stem"""
    return [path for path in paths if stem in os.path.basename(path)]


def single_cube(paths, stash_section, stash_item, accumulate=False):
    '''
    Create a single cube of a fields from a list of files. Each
    file contains multiple fields at multiple times, and this function collects
    all times for a particular field in a single cube.
    '''
    if accumulate:
        def cube_func(cube):
            return (cube.attributes['STASH'].section == stash_section and
                    cube.attributes['STASH'].item == stash_item and
                    len(cube.cell_methods) > 0)
    else:
        def cube_func(cube):
            return (cube.attributes['STASH'].section == stash_section and
                    cube.attributes['STASH'].item == stash_item and
                    len(cube.cell_methods) == 0)
    constraint = iris.Constraint(cube_func=cube_func)
    cubes = [iris.load_cube(path, constraint) for path in paths]
    return iris.cube.CubeList(cubes).concatenate_cube()


if __name__ == '__main__':
    main()
