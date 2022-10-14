# How To Run
1. `cd` into directory that has the file `httpc.py`
2. In terminal, run `python httpc.py (get|post) [-v] (-h "k:v")* [-d inline-data] [-f file] URL`
- E.g.: `python3 httpc.py get https://httpbin.org`

- python httpc.py POST https://httpbin.org/post -h Content-Type:application/json -f Extra\data.json -v

- python httpc.py post https://httpbin.org/post -h Content-Type:application/json -d '{"Assignment": 1}' -v


