# How to run
Note: use `python3` command instead of `python` if on Mac.

1. Run the Router: 
    - Relibale: `cd Router && router_x64.exe --port=3000 --drop-rate=0.0 --max-delay=0ms --seed=1`
    - Delay: `cd Router && router_x64.exe --port=3000 --drop-rate=0.0 --max-delay=4000ms --seed=1`
    - Drop Rate: `cd Router && router_x64.exe --port=3000 --drop-rate=0.5 --max-delay=0ms --seed=1`
    - Both: `cd Router && router_x64.exe --port=3000 --drop-rate=0.5 --max-delay=2000ms --seed=1`
    - Note: We are using a delay of 5s as server and client times out at 3s

2. Run the server: `cd Server && python httpfs.py -p 8080 -v`
    - Here, you can also specifcy the directory path to read/write files in with `-d` (default: /Data)
    - You can also specify port with `-p` (default: 8080)

3. Run the client: 
    - Read from directory `cd Client && python httpc.py GET http://localhost:8080`
    - Read from specific file in directory `cd Client && python httpc.py GET http://localhost:8080/text.txt`
    - Write to a specific file in directory `cd Client && python httpc.py POST http://localhost:8080/text.txt -d "hello TAA!"`
    - Test cannot read outside of default directory: `cd Client && python httpc.py GET http://localhost:8080/../cannot-access.txt`
    - Test content type and content disposition: `cd Client && python httpc.py GET http://localhost:8080/hello.json -v`
    - Test multiple connections
        - Uncomment the time.sleep(10) line in HTTPServerLibrary.py
        - Spin up 2 new terminal instances and type:
            - `cd Client && python httpc.py GET http://localhost:8080`
            - `cd Client && python httpc.py POST http://localhost:8080/text.txt -d "hello TAA - 1!"`
            - `cd Client && python httpc.py POST http://localhost:8080/text.txt -d "hello TAA - 2!"`


### Handshake Logic

- Client sends a SYN and then waits for a SYN-ACK with a timout set
    - If the SYN is dropped, then it wont reached the server and therefore the server won't send a SYN-ACK, therefore the client will timeout and send the SYN again

- Server receives the SYN and then sends the SYN-ACK
    - If the SYN-ACK is dropped, then the client will timeout and send the SYN again, starting the handshake over again

- If the client receives the SYN-ACK, it sends the ACK and marks the handshake complete
