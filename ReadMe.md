# Smit and Pan's CLI HTTP library
### How To Run
1. `cd` into directory that has the file `httpc.py`.
2. In terminal, run `python httpc.py (get|post) [-v] (-h "k:v")* [-d inline-data] [-f file] URL`.
- E.g.: `python3 httpc.py get https://httpbin.org/ip`
- Python 3.x is required.

### Notes
- The input and output file paths should be absolute
- Inline data should not have spaces
- If you're using Windows OS, file paths should use back-slashes ('\'), else paths should be forward-slashes ('/').


### Examples
##### Help display (-help)
- `python3 httpc.py -help`

##### GET from `httpbin.org` with verbose (-v)
- `python3 httpc.py GET https://httpbin.org/status/418 -v`

##### Output to file
- Windows: `python httpc.py GET https://httpbin.org/status/418 -v -o Extra\teapot.txt` 
- Mac: `python3 httpc.py GET https://httpbin.org/status/418 -v -o Extra/teapot.txt`

##### Body data from file (-f)
- Windows:
`python httpc.py POST https://httpbin.org/post -h Content-Type:application/json -f Extra\data.json -v`
- Mac:
`python3 httpc.py POST https://httpbin.org/post -h Content-Type:application/json -f Extra/data.json -v`

##### Inline data (-d)
- `python3 httpc.py post https://httpbin.org/post -h Content-Type:application/json -d '{"Assignment":1}' -v`

##### Multiple Headers (-h)*
- `python3 httpc.py post https://httpbin.org/post -h "Content-Type:application/json" -h "Connection: keep-alive" -h "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0)" -d '{"Assignment":1}'` 

##### Redirect URL
Note: Need to run `redirectServer.py` before executing this script
- `python3 httpc.py GET http://localhost:8000 -v`

#### Expected to return errors
##### Not inputing URL
- `python3 httpc.py GET`

##### Using GET with -d or -f
- `python3 httpc.py get https://httpbin.org/post -d someData`
- `python3 httpc.py get https://httpbin.org/post -f somePath`

##### Using POST with both -d and -f
- `python3 httpc.py post https://httpbin.org/post -d someData -f somePath`

##### Using HTTP method other than GET or POST
- `python3 httpc.py PATCH https://httpbin.org/patch`
