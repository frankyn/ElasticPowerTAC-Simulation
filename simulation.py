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

            # Copy Simulation Config
            cmd_copy = ['cp',
                        'ElasticPowerTAC-Simulation-Config/%s' % (simulation['simulation']),
                        'simulation-%d/'%x]
            subprocess.call(cmd_copy)

            # Untar
            os.chdir('./simulation-%d'%x)
            cmd_extract = ['tar', '-xzf', '%s'%(simulation['simulation'])]
            subprocess.call(cmd_extract)

            # extracted directory
            extracted_directory = simulation['simulation'].replace('.tar.gz','')

            # Move config
            cmd_move = ['mv', './%s/FactoredCustomers.xml'%(extracted_directory), './config/']
            subprocess.call(cmd_move)
            cmd_move = ['mv', './%s/server.properties'%(extracted_directory), './config/']
            subprocess.call(cmd_move)
            cmd_move = ['mv', './%s/VillageType1.properties'%(extracted_directory), './config/']
            subprocess.call(cmd_move)
            cmd_move = ['mv', './%s/bootstrap-data'%(extracted_directory),'./']
            os.chdir('../')
            x += 1

    # start simulation scenarios
    def start_slave_simulations(self):
        print("Starting Slave")
        self._process_handles = []
        # Start each simulation and hold process handle until they all finish...
        x = 1
        port = 61616
        for simulation in self._config['simulations']:
            cmd_cp = ['cp','runner.sh','./simulation-%d'%x]
            subprocess.call(cmd_cp)

            os.chdir('./simulation-%d'%x)
            cmd_chmod = ['chmod','a+x','runner.sh']
            subprocess.call(cmd_chmod)

            cmd_start = ['./runner.sh',str(port)]
            self._process_handles.append(subprocess.Popen(cmd_start))
            x += 1
            port += 1
            os.chdir('../')
        for process in self._process_handles:
            process.wait()

        print("simulations are finished...")

    # save results in a tar ball with simulation config name
    def save_simulation_results(self):
        today = date.today()
        x = 1
        for simulation in self._config['simulations']:
            extracted_directory = simulation['simulation'].replace('.tar.gz','')

            # Compress log file
            cmd_tar = ['tar','-czf','%s-%s.tar.gz'%(simulation['name'],today.isoformat()),'simulation-%d/log'%x]
            subprocess.call(cmd_tar)

            # Transmit back to master
            cmd_scp = ['scp','%s-%s.tar.gz'%(extracted_directory,today.isoformat()),
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

