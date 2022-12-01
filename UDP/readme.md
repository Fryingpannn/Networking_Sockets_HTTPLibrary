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