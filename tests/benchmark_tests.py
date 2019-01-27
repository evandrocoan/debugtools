#! /usr/bin/env python
# -*- coding: utf-8 -*-

####################### Licensing #######################################################
#
#   Copyright 2019 @ Evandro Coan
#   Benchmark this module versus logging and print methods
#
#  Redistributions of source code must retain the above
#  copyright notice, this list of conditions and the
#  following disclaimer.
#
#  Redistributions in binary form must reproduce the above
#  copyright notice, this list of conditions and the following
#  disclaimer in the documentation and/or other materials
#  provided with the distribution.
#
#  Neither the name Evandro Coan nor the names of any
#  contributors may be used to endorse or promote products
#  derived from this software without specific prior written
#  permission.
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or ( at
#  your option ) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################################
#
import logging
from debug_tools import logger

import sys
import pstats
import cProfile

from io import StringIO

def average(stats, count):
    stats.total_calls /= count
    stats.prim_calls /= count
    stats.total_tt /= count

    for func, source in stats.stats.items():
        cc, nc, tt, ct, callers = source
        stats.stats[func] = (cc/count, nc/count, tt/count, ct/count, callers)

    return stats

def profile_something(profile_function, count=1):
    output_stream = StringIO()
    profiler_status = pstats.Stats( stream=output_stream )

    for index in range(count):
        profiler = cProfile.Profile()
        profiler.enable()

        profile_function()
        profiler.disable()
        profiler_status.add( profiler )
        print( 'Profiled', '%.3f' % profiler_status.total_tt, 'seconds at', index, 'for', profile_function.__name__, flush=True )

    average(profiler_status, count)
    profiler_status.sort_stats( "time" )
    profiler_status.print_stats()

    return "\nProfile results for %s\n%s" % ( profile_function.__name__, output_stream.getvalue() ), profiler_status

output = 1500
log_debug_counts = 10

def run_profiling(first_function, second_function):
    first_function_results, first_function_stats = profile_something( first_function, log_debug_counts )
    second_function_results, second_function_stats = profile_something( second_function, log_debug_counts )
    difference = first_function_stats.total_tt - second_function_stats.total_tt

    print( '\n', first_function_results[0:output] )
    print( '\n', second_function_results[0:output] )
    print( '\nTotal difference %.3f' % difference )


log_debug_iterations = 1000000
def debug_tools_log_debug_off(iterations=log_debug_iterations):
    log = logger.getLogger( 127, "benchmark", tick=False )
    log.setLevel( "DEBUG" )
    log.setLevel( "WARNING" )

    for index in range( iterations ):
        # log( 1, 'Message' )
        log.debug( 'Message' )

def logging_mod_log_debug_off(iterations=log_debug_iterations):
    date_format = "%H:%M:%S"
    string_format = "%(asctime)s:%(msecs)010.6f - %(name)s.%(funcName)s:%(lineno)d - %(message)s"

    stream = logging.StreamHandler()
    formatter = logging.Formatter( string_format, date_format )
    stream.setFormatter( formatter )

    log = logging.getLogger( "benchmark" )
    log.addHandler( stream )
    log.setLevel( "DEBUG" )
    log.setLevel( "WARNING" )

    for index in range( iterations ):
        log.debug( 'Message' )

run_profiling( debug_tools_log_debug_off, logging_mod_log_debug_off )


