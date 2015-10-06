#!/bin/sh

# Used to run the maven script
mvn -Pcli -Dexec.args="--sim bootdata-file --config config/server.properties --jms-url tcp://localhost:$1"

