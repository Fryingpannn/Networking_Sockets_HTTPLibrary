# How to run
1. Run the following commandL: `cd Server && pip install requirements.txt`
2. Run the server: `cd Server && python3 httpfs.py -p 8080`
    - Here, you can also specifcy the directory path to read/write files in with `-d` (default: /Data)
    - You can also specify port with `-p` (default: 8080)
3. Run the client: 
    - Read from directory `cd Client && python3 httpc.py GET http://localhost:8080`
    - Read from specific file in directory `cd Client && python3 httpc.py GET http://localhost:8080/text.txt`
    - Write to a specific file in directory `cd Client && python3 httpc.py POST http://localhost:8080/text.txt -d hello TA!`

## Todo
- Security
