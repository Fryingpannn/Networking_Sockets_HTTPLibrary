# How to run
Note: use `python` command instead of `python3` if on Windows.
1. Run the server: `cd Server && python3 httpfs.py -p 8080 -v`
    - Here, you can also specifcy the directory path to read/write files in with `-d` (default: /Data)
    - You can also specify port with `-p` (default: 8080)
2. Run the client: 
    - Read from directory `cd Client && python3 httpc.py GET http://localhost:8080`
    - Read from specific file in directory `cd Client && python3 httpc.py GET http://localhost:8080/text.txt`
    - Write to a specific file in directory `cd Client && python3 httpc.py POST http://localhost:8080/text.txt -d "hello TAA!"`
    - Test cannot read outside of default directory: `cd Client && python3 httpc.py GET http://localhost:8080/../cannot-access.txt`
    - Test content type and content disposition: `python3 httpc.py GET http://localhost:8080/hello.json -v`
    - Test multiple connections
        - Uncomment the time.sleep(10) line in HTTPServerLibrary.py
        - Spin up 2 new terminal instances and type:
            - `cd Client && python3 httpc.py GET http://localhost:8080`
            - `cd Client && python3 httpc.py POST http://localhost:8080/text.txt -d "hello TAA - 1!"`
            - `cd Client && python3 httpc.py POST http://localhost:8080/text.txt -d "hello TAA - 2!"`