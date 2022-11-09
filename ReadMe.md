# How to run
1. Run the server: `python3 httpfs.py -p 8080`
    - Here, you can also specifcy the directory path to read/write files in with `-d` (default: /Data)
    - You can also specify port with `-p` (default: 8080)
2. Run the client: 
    - Read from directory `python3 httpc.py GET http://localhost:8080`
    - Read from specific file in directory `python3 httpc.py GET http://localhost:8080/text.txt`
    - Write to a specific file in directory `python3 httpc.py POST http://localhost:8080/text.txt -d hello TA!`

## Todo
- Security
- Verbose logs
