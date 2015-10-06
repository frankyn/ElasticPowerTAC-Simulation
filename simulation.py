from DigitalOceanAPIv2.docean import DOcean
import subprocess
import json
import time
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

        # Create a simulation server for each simulation config
        for simulation in self._config['simulations']:
            # Copy server-distribution powertac
            cmd_copy = ['cp', '-r', 'server-distribution', 'simulation-1']
            subprocess.call(cmd_copy)

            # Copy Simulation Config
            cmd_copy = ['cp',
                        'ElasticPowerTAC-Simulation-Config/%s' % (simulation['simulation']),
                        'simulation-1/']
            subprocess.call(cmd_copy)

            # Untar
            cmd_extract = ['tar', 'xzf', simulation['simulation']]
            subprocess.call(cmd_extract)

            # Move config
            cmd_move = ['mv', 'FactoredCustomers.xml', 'simulation-1/config/']
            subprocess.call(cmd_move)
            cmd_move = ['mv', 'server.properties', 'simulation-1/config/']
            subprocess.call(cmd_move)
            cmd_move = ['mv', 'VillageType1.properties', 'simulation-1/config/']
            subprocess.call(cmd_move)


    # start simulation scenarios
    def start_slave_simulations(self):
        print("Starting Slave")
        self._process_handles = []
        # Start each simulation and hold process handle until they all finish...
        x = 0
        for simulation in self._config['simulations']:
            cmd_start = ['cd %s;mvn -Pcli -Dexec.args="--sim --boot-data bootstrap-data --config config/server.properties --jms-url tcp://localhost:616%d;'%(10+x)]
            self._process_handles.append(subprocess.Popen(cmd_start))
            x += 1
        for process in self._process_handles:
            process.wait()

        print("simulations are finished...")

    # save results in a tar ball with simulation config name
    def save_simulation_results(self):
        today = date.today()

        for simulation in self._config['simulations']:
            # Compress log file
            cmd_tar = ['tar','-czf','%s-%s.tar.gz'%(simulation['simulation'],today.isoformat()),'']
            subprocess.call(cmd_tar)

            # Transmit back to master
            cmd_scp = ['scp','%s-%s.tar.gz'%(simulation['simulation'],today.isoformat()),
                       'log@%s:~/'%(self._config['master-ip'])]
            
        # That's it.


if __name__ == "__main__":
    # Initialize Setup
    elastic_powertac_simulation = ElasticPowerTAC_Simulation()

    # Setup Simulation Environment
    elastic_powertac_simulation.setup_simulation_environment()

    # Start Simulations
    elastic_powertac_simulation.start_slave_simulations()

    # Save Results & Transmit Results
    elastic_powertac_simulation.save_simulation_results()

