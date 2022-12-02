# How to run
Note: use `python3` command instead of `python` if on Mac.

1. Run the Router: `cd Router && router_x64.exe --port=3000 --drop-rate=0.2 --max-delay=10ms --seed=1`
2. Run the server: `cd Server && python httpfs.py -p 8080 -v`
    - Here, you can also specifcy the directory path to read/write files in with `-d` (default: /Data)
    - You can also specify port with `-p` (default: 8080)
3. Run the client: 
    - Read from directory `cd Client && python httpc.py GET http://localhost:8080`
    - Read from specific file in directory `cd Client && python httpc.py GET http://localhost:8080/text.txt`
    - Write to a specific file in directory `cd Client && python httpc.py POST http://localhost:8080/text.txt -d "hello TAA!"`
    - Test cannot read outside of default directory: `cd Client && python httpc.py GET http://localhost:8080/../cannot-access.txt`
    - Test content type and content disposition: `python httpc.py GET http://localhost:8080/hello.json -v`
    - Test multiple connections
        - Uncomment the time.sleep(10) line in HTTPServerLibrary.py
        - Spin up 2 new terminal instances and type:
            - `cd Client && python httpc.py GET http://localhost:8080`
            - `cd Client && python httpc.py POST http://localhost:8080/text.txt -d "hello TAA - 1!"`
            - `cd Client && python httpc.py POST http://localhost:8080/text.txt -d "hello TAA - 2!"`


## RoadMap

- Change TCP methods to UDP

- All data must be sent as indivual packets of size 1024
    - For each packet, prepare the header
    - Add 1013 bytes of body data
    - If body data is left, create another packet and repeat the steps
    - This must be done at the client and at the server side
    - Note: UDP headers are different frmo HTTP headers

- Implement the 3 way handshake

-  Implement Selective Repeat ARQ / Selective Reject ARQ
    - Seqeunce numbers
    - ACK and SYN
    - Intial sequnce number decided during handshake or is it 0?


### Selective Repeat

- Sender sends a packet with a sequence number a
    - Sender sets a timeout for that packet
    - If does not received a ACK before the timeout, resend the packet and reset the timer
    - If received a ACK before the timeout, close the timeout
    - Note: This needs to be done asynchronously

- Sender sends a packet with a sequence number a + 1 without waiting for ACK of packet a
    - Repeat the same thing as above asynchronously

- If sender receives a NAK with a sequence number b, means that the receiver didn't receive this packet
    - Resend the packet with sequence number b and reset it's timer


- Receiver receives a packet with a sequence number c
    - If c = {expected sequence number}, send a ACK of sequence number c
        - Increment the {expected sequence number} to c + 1
    - If already received this packet, i.e c < {expected sequence number}, discard it
    - If c > {expected sequence number}, means we received a out of order packet
        - Buffer it and send a NAK of {expected sequence number}
        - Send a ACK of c?

- Buffering?
- Packet number: Data, SYN, ACK, etc