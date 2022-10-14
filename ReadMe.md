# How To Run
1. `cd` into directory that has the file `httpc.py`
2. In terminal, run `python httpc.py (get|post) [-v] (-h "k:v")* [-d inline-data] [-f file] URL`
- E.g.: `python3 httpc.py get https://httpbin.org`

#### Output to file
`python httpc.py GET https://httpbin.org/status/418 -v -o Extra\teapot.txt` 

#### Body data from file
`python httpc.py POST https://httpbin.org/post -h Content-Type:application/json -f Extra\data.json -v`

#### Inline data
`python httpc.py post https://httpbin.org/post -h Content-Type:application/json -d '{"Assignment":1}' -v`

#### Multiple Headers
`python httpc.py post https://httpbin.org/post -h "Content-Type:application/json" -h "Connection: keep-alive" -h "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0)" -d '{"Assignment":1}'` 

