#!/bin/sh

# Used to run the maven script
mvn -Pcli -Dexec.args="--sim --boot-data bootstrap-data --config config/server.properties --jms-url tcp://localhost:$1"

