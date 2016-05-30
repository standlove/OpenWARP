# -*- coding: utf-8 -*-
"""
This module defined the cli.
"""

__author__ = "TCSASSEMBLER"
__copyright__ = "Copyright (C) 2016 TopCoder Inc. All rights reserved."
__version__ = "1.0"

from openwarp import services
from openwarp import helper
from openwarp.services import *

import os
import threading

from logutils.queue import QueueListener
import multiprocessing

import json
import cmd


class OpenWarpCLI(cmd.Cmd):
    """
    Open Warp Command Line Interface
    """

    # the command prompt
    prompt = '> '

    # the introduction
    intro = "OpenWarp CLI\n"

    def __init__(self):
        '''
        Initialization
        '''
        cmd.Cmd.__init__(self)

        self.simulation_done = False
        self.simulation_dir = None
        self.logger = logging.getLogger(__name__ + '.OpenWarpCLI')

        self.start()

    def start(self):
        '''
        Start the queue listener
        '''
        self.queue = multiprocessing.Queue(-1)
        # Solve this problem? http://stackoverflow.com/questions/25585518/python-logging-logutils-with-queuehandler-and-queuelistener
        self.ql = QueueListener(self.queue, *logging.getLogger().handlers)
        self.ql.start()

    def stop(self):
        '''
        Stop the queue listener
        '''
        self.ql.stop()
    
    def do_m(self, json_file):
        '''
        Shortcut for the generate mesh command
        Args:
            json_file: the json file containing all the parameters
        '''
        self.do_meshing(json_file)
    
    def do_meshing(self, json_file):
        '''
        Launch Mesh Generator to generate mesh.
        Args:
            json_file: the json file containing all the parameters
        '''
        signature = __name__ + '.OpenWarpCLI.do_meshing()'
        helper.log_entrance(self.logger, signature, {'json_file' : json_file})

        try:
            json_obj = self.load_json(json_file)

            # Prepare meshing directory
            self.logger.info('Preparing meshing directory')
            meshing_dir = services.prepare_dir('meshing_')
            self.logger.info('Meshing files will be located at ' + str(meshing_dir))

            # Call generate_mesh service
            log = services.generate_mesh(meshing_dir, MeshingParameters(**json_obj))
            print log
            helper.log_exit(self.logger, signature, [ { 'log': log }])
        except Exception as e:
            helper.log_exception(self.logger, signature, e)
            ret = { 'error' : str(e) }
            helper.log_exit(self.logger, signature, [ret])
            print e
        
    def do_s(self, json_file):
        '''
        Shortcut for the run simulation command
        Args:
            json_file: the json file containing all the parameters
        '''
        self.do_simulation(json_file)

    def do_simulation(self, json_file):
        '''
        Run simulation 
        Args:
            json_file: the json file containing all the parameters
        '''
        signature = __name__ + '.OpenWarpCLI.do_simulation()'
        helper.log_entrance(self.logger, signature, {'json_file' : json_file})
        try:
            json_obj = self.load_json(json_file)

            # Prepare simulation directory
            self.logger.info('Preparing simulation directory')
            self.simulation_dir = services.prepare_dir('simulation_')
            self.logger.info('Simulations files will be located at ' + str(self.simulation_dir))
            
            # determine ponits and panels
            bodies = json_obj.get('floating_bodies')
            if bodies is not None and isinstance(bodies, list):
                for body in bodies:
                    mesh_file = body.get('mesh_file')
                    with open(mesh_file, 'r') as fd:
                        points, panels = helper.determine_points_panels(fd)
                        body['points'] = str(points)
                        body['panels'] = str(panels)

            # Call simulate service
            self.simulation_done = False
            log = services.simulate(self.simulation_dir, services.construct_simulation_parameters(json_obj), self.queue)
            print log
            self.simulation_done = True

            helper.log_exit(self.logger, signature, [ { 'log': log }])
        except Exception as e:
            helper.log_exception(self.logger, signature, e)
            ret = { 'error' : str(e) }
            helper.log_exit(self.logger, signature, [ret])
            print e
        

    def do_p(self, json_file):
        '''
        The shortcut for the run post-processing command
        Args:
            json_file: the json file containing all the parameters
        '''
        self.do_postprocessing(json_file)

    def do_postprocessing(self, json_file):
        '''
        Run post-processing.
        Args:
            json_file: the json file containing all the parameters            
        '''
        signature = __name__ + '.OpenWarpCLI.do_postprocessing()'
        helper.log_entrance(self.logger, signature, {'json_file' : json_file})

        if not self.simulation_done:
            ret = { 'error' : 'Simulation must be run first.' }
            helper.log_exit(self.logger, signature, [ret])
            print ret['error']
            return

        try:
            json_obj = self.load_json(json_file)
            log = services.postprocess(self.simulation_dir, services.construct_postprocess_parameters(json_obj), self.queue)
            print log
            helper.log_exit(self.logger, signature, [ { 'log': log }])
        except Exception as e:
            helper.log_exception(self.logger, signature, e)
            ret = { 'error' : str(e) }
            helper.log_exit(self.logger, signature, [ret])
            print e

    def do_q(self, line):
        '''
        The shortcut for the quit command
        '''
        return self.do_quit(line)

    def do_quit(self, line):
        '''
        Quit the cli.
        '''

        self.stop()
        return True

    def load_json(self, json_file):
        '''
        Load json from file
        Args:
            json_file: the json file
        '''
        with open(json_file, 'r') as fd:
            return json.load(fd)



    


