#!/bin/bash
for TOTO in {1..1000} 
do
        curl -H "Content-Type: application/json" -X POST -d '{"value":30}' http://localhost:5000/block/0_4_1
done

