## RoadMap

- Change TCP methods to UDP
- All data must be sent as indivual packets of size 1024
    - For each packet, prepare the header
    - Add 1013 bytes of body data
    - If body data is left, create another packet and repeat the steps
    - This must be done at the client and at the server side
    - Note: UDP headers are different frmo HTTP headers
-  Selective Repeat ARQ / Selective Reject ARQ
    - Seqeunce numbers
    - ACK and SYN