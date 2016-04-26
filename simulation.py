import subprocess
import json
import time
import os
from datetime import date

'''
    main.py
        * Setup Simulations defined by "config.json"
        * Start Simulations
        * Store Results

'''


class ElasticPowerTAC_Simulation:
    # constructor
    def __init__(self):
        self._config = None

        # Load config
        self.load_config()


    # load_config
    def load_config(self):
        # load from "config.json"
        try:
            config_file = "config.json"
            self._config = None
            with open(config_file, 'r') as f:
                self._config = f.read()

            self._config = json.loads(self._config)
        except:
            print('config.json must be defined.')
            exit()

    # setup slave environment
    def setup_slave_simulations(self):
        print("Slaves have been initialized!")
        x = 1
        # Create a simulation server for each simulation config
        for simulation in self._config['simulations']:
            # Copy server-distribution powertac
            cmd_copy = ['cp', '-r', 'server-distribution', 'simulation-%d'%x]
            subprocess.call(cmd_copy)

            # Create classes folder
            cmd_create = ['mkdir','-p','simulation-%d/target/classes'%x]
            subprocess.call(cmd_create)

            # Copy Simulation Config
            cmd_copy = ['cp',
                        'scenarios/%s' % (simulation['simulation-file-name']),
                        'simulation-%d/'%x]
            subprocess.call(cmd_copy)

            # Go to simulation directory
            os.chdir('./simulation-%d'%x)

            # Uncompress simulation configuration payload
            cmd_extract = ['tar', '-xzf', '%s'%(simulation['simulation-file-name'])]
            subprocess.call(cmd_extract)

            # extracted directory
            extracted_directory = simulation['simulation-file-name'].replace('.tar.gz','')

            # Move config
            # Use simulation file mappings
            for mapping in simulation['file-mapping']:
                cmd_move = ['mv',
                            './%s/%s'%(extracted_directory,mapping['file']),
                            './%s'%mapping['location']]
                subprocess.call(cmd_move)

            # Exit simulation directory
            os.chdir('../')

            x += 1

    # Generate runner.sh
    # Create runner.sh with specified configuration params for maven
    def generate_runner(self,simulation):
        if 'maven-params' in simulation:
            self._backward_compat_runner(simulation)

        elif 'shell' in simulation:
            with open('runner.sh', 'w+') as f:
                f.write('#!/bin/sh\n')
                for value in simulation['shell']:
                    f.write(value+'\n')




    def _backward_compat_runner(self, simulation):
        # Build additional parameters for maven script
        maven_params = ''
        # Process key value pairs
        for key,value in simulation['maven-params'].iteritems():
            maven_params += '%s %s '%(key,value)

        # Write runner.sh.
        with open('runner.sh','w+') as f:
            f.write('#!/bin/sh\n')
            f.write('mvn -Pcli -Dexec.args="--jms-url tcp://localhost:$1 %s"'%maven_params)



    # start simulation scenarios
    def start_slave_simulations(self):
        print("Starting Slave")
        self._process_handles = []
        # Start each simulation and hold process handle until they all finish...
        x = 1
        port = 61616
        for simulation in self._config['simulations']:
            # Go to simulation directory
            os.chdir('./simulation-%d'%x)



            # Generate Runner.sh Script
            self.generate_runner(simulation)

            # Add execution permissions
            cmd_chmod = ['chmod','a+x','runner.sh']
            subprocess.call(cmd_chmod)

            # Run it.
            cmd_start = ['./runner.sh',str(port)]
            self._process_handles.append(subprocess.Popen(cmd_start))

            # Exit simulation directory
            os.chdir('../')

            x += 1
            port += 1

        for process in self._process_handles:
            process.wait()

        print("simulations are finished...")

    # save results in a tar ball with simulation config name
    def save_simulation_results(self):
        today = date.today()
        x = 1
        for simulation in self._config['simulations']:

            # Copy system log file
            cmd_cp = ['cp','/tmp/slave-log','simulation-%d/log'%x]
            subprocess.call(cmd_cp)

            # Compress log file
            cmd_tar = ['tar','-czf','%s-%s.tar.gz'%(simulation['name'],today.isoformat()),'simulation-%d/log'%x]
            subprocess.call(cmd_tar)

            if not self._config['google-drive']:
                cmd_scp = ['scp','-o StrictHostKeyChecking=no','%s-%s.tar.gz'%(simulation['name'],today.isoformat()),
                       'log@%s:~/'%(self._config['master-ip'])]
                subprocess.call(cmd_scp)
            x += 1
        # That's it.


if __name__ == "__main__":
    # Initialize Setup
    elastic_powertac_simulation = ElasticPowerTAC_Simulation()

    # Setup Simulation Environment
    elastic_powertac_simulation.setup_slave_simulations()

    # Start Simulations
    elastic_powertac_simulation.start_slave_simulations()

    # Save Results & Transmit Results
    elastic_powertac_simulation.save_simulation_results()

