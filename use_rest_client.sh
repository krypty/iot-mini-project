#/bin/bash
echo "=== VALVE COMMANDS ==="
echo "Set valve at 50% for floor 4, block 1"
python3 rest_client.py 0 4 1 --value 128
sleep 1


echo "Set valve at 25% for floor 4, block 2"
python3 rest_client.py 0 4 2 --value 64
sleep 1



echo "\n\n"
echo "=== BLIND COMMANDS ==="
echo "Close blind for floor 4, block 1"
python3 rest_client.py 1 4 1 --value 0
sleep 3


echo "Open blind for floor 4, block 1"
python3 rest_client.py 1 4 1 --value 1
sleep 3


echo "Set blind value at 50% for floor 4, block 1"
python3 rest_client.py 3 4 1 --value 128
sleep 3
