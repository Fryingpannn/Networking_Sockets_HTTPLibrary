package main

import (
	"bytes"
	"encoding/binary"
	"flag"
	"fmt"
	"io"
	"log"
	"math/rand"
	"net"
	"os"
	"sync/atomic"
	"time"
)

var (
	queueSize = int32(0)
	incrQueue = func() int32 { return atomic.AddInt32(&queueSize, 1) }
	decrQueue = func() int32 { return atomic.AddInt32(&queueSize, -1) }
	currQueue = func() int32 { return atomic.LoadInt32(&queueSize) }
)

const (
	minLen = 11
	maxLen = 1024
)

// Packet represents a simulated network packet.
type Packet struct {
	// Type is the type of the packet which is either ACK or DATA (1 byte).
	Type uint8
	// SeqNum is the sequence number of the packet. It's 4 bytes in BigEndian format.
	SeqNum uint32
	// ToAddr is the destination address of the packet.
	// It include 4 bytes for IPv6 and 2 bytes in BigEndian for port number.
	ToAddr *net.UDPAddr
	// FromAddr is the address of the sender. It's not included in the raw data.
	// It's inferred from the recvFrom method.
	FromAddr *net.UDPAddr
	// Payload is the real data of the packet.
	Payload []byte
}

// Raw returns the raw representation of the packet is to be sent in BigEndian.
func (p Packet) Raw() []byte {
	var buf bytes.Buffer
	append := func(data interface{}) {
		binary.Write(&buf, binary.BigEndian, data)
	}
	append(p.Type)
	append(p.SeqNum)

	// Swap the peer value from ToAddr to FromAddr; and uses 4bytes version.
	append(p.FromAddr.IP.To4())
	append(uint16(p.FromAddr.Port))

	append(p.Payload)
	return buf.Bytes()
}

func (p Packet) String() string {
	return fmt.Sprintf("#%d, %s -> %s, sz=%d", p.SeqNum, p.FromAddr, p.ToAddr, len(p.Payload))
}

// parsePacket extracts, validates and creates a packet from a slice of bytes.
func parsePacket(fromAddr *net.UDPAddr, data []byte) (*Packet, error) {
	if len(data) < minLen {
		return nil, fmt.Errorf("packet is too short: %d bytes", len(data))
	}
	if len(data) > maxLen {
		return nil, fmt.Errorf("packet is exceeded max length: %d bytes", len(data))
	}
	curr := 0
	next := func(n int) []byte {
		bs := data[curr : curr+n]
		curr += n
		return bs
	}
	u16, u32 := binary.BigEndian.Uint16, binary.BigEndian.Uint32
	p := Packet{}
	p.Type = next(1)[0]
	p.SeqNum = u32(next(4))
	p.FromAddr = fromAddr
	toAddr, err := net.ResolveUDPAddr("udp", fmt.Sprintf("%s:%d", net.IP(next(4)), u16(next(2))))
	// If toAddr is loopback, it should be as same as the host of fromAddr.
	if toAddr.IP.IsLoopback() {
		toAddr.IP = fromAddr.IP
	}
	p.ToAddr = toAddr
	p.Payload = data[curr:]
	return &p, err
}

// send sends the packet the associated destination of the packet.
func send(conn *net.UDPConn, p Packet) {
	decrQueue()
	if _, err := conn.WriteToUDP(p.Raw(), p.ToAddr); err != nil {
		logger.Printf("failed to deliver %s: %v\n", p, err)
		return
	}
	logger.Printf("[queue=%d] packet %s is delivered\n", currQueue(), p)
}

// process processes the received packet. It can be discarded or deliver with a delayed duration.
func process(conn *net.UDPConn, p Packet) {
	if rand.Float64() < *dropRate {
		logger.Printf("[queue=%d] packet %s is dropped\n", currQueue(), p)
		return
	}
	incrQueue()
	// if maxDelay 0 or negative, we should guarantee the order by not scheduling.
	if *maxDelay <= 0 {
		send(conn, p)
		return
	}
	delay := time.Duration(rand.Intn(100)) * *maxDelay / time.Duration(100)
	logger.Printf("[queue=%d] packet %s is delayed for %s\n", currQueue(), p, delay)

	time.AfterFunc(delay, func() {
		send(conn, p)
	})
}

var (
	dropRate = flag.Float64("drop-rate", 0.0, "")
	maxDelay = flag.Duration("max-delay", 0, "")
	seed     = flag.Int64("seed", time.Now().UnixNano(), "")
	port     = flag.Int("port", 3000, "")
)

func usage() {
	fmt.Println(`
Router is a logical router dispatches UDP packets between applications.
It receives UDP packets, then dispatches to the associated destination of the packet.
During the delivery the value of a peer address will be changed from 'toAddr' to 'fromAddr'.

Usage: 
    router --port int --drop-rate float --max-delay duration --seed int
		
    --port int-number
        port number that the router is listening for the incoming packet.
        default value is 3000.
	
    --drop-rate float-number
        drop rate is the probability of packets will be dropped during on the way.
        use 0 to disable the drop feature.

    --max-delay duration (eg. 5ms, 4s, or 1m)
        max delay the maximum duration that any packet can be delayed. 
		any packet will be subject to a delay duration between 0 and this value.
        the duration is in format 5s, 10ms. Uses 0 to route packets immediately.

    --seed int
        seed is used to initialize the random generator.
        if the same seed is provided, the random behaviors are expected to repeat.

Example: 
    router --port=3000 --drop-rate=0.2 --max-delay=10ms --seed=1`)
}

var logger *log.Logger

func init() {
	logf, err := os.OpenFile("router.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0660)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to open log file: %v", err)
		panic(err)
	}
	logger = log.New(io.MultiWriter(logf, os.Stderr), "", log.Ltime|log.Lmicroseconds)
}

func main() {
	flag.Usage = usage
	flag.Parse()

	// override the rand with either user-provided value or a random seed.
	rand.Seed(*seed)
	logger.Printf("config: drop-rate=%.2f, max-delay=%s, seed=%d\n", *dropRate, *maxDelay, *seed)

	addr, err := net.ResolveUDPAddr("udp", fmt.Sprintf(":%d", *port))
	if err != nil {
		logger.Fatalln("failed to resolve address:", err)
	}
	conn, err := net.ListenUDP("udp", addr)
	if err != nil {
		logger.Fatalln("failed to listen on port", err)
	}
	defer conn.Close()
	logger.Println("router is listening at", addr)

	for {
		buf := make([]byte, 2048)
		n, fromAddr, err := conn.ReadFromUDP(buf)
		if err != nil {
			logger.Println("failed to receive message:", err)
			continue
		}
		p, err := parsePacket(fromAddr, buf[:n])
		if err != nil {
			logger.Println("invalid packet:", err)
			continue
		}
		process(conn, *p)
	}
}
