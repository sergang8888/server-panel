package main

import (
	"encoding/json"
	"log"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

type Client struct {
	conn   *websocket.Conn
	send   chan []byte
	active bool
	mutex  sync.RWMutex
}

type Hub struct {
	clients    map[*Client]bool
	broadcast  chan []byte
	register   chan *Client
	unregister chan *Client
	mutex      sync.RWMutex
}

type WSMessage struct {
	Type string      `json:"type"`
	Data interface{} `json:"data"`
}

var hub = &Hub{
	clients:    make(map[*Client]bool),
	broadcast:  make(chan []byte),
	register:   make(chan *Client),
	unregister: make(chan *Client),
}

func init() {
	go hub.run()
	go startSystemMonitor()
}

// WebSocket连接处理
func handleWebSocket(c *gin.Context) {
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		return
	}

	client := &Client{
		conn:   conn,
		send:   make(chan []byte, 256),
		active: true,
	}

	hub.register <- client

	// 启动客户端的读写协程
	go client.writePump()
	go client.readPump()
}

// Hub运行循环
func (h *Hub) run() {
	for {
		select {
		case client := <-h.register:
			h.mutex.Lock()
			h.clients[client] = true
			h.mutex.Unlock()
			log.Printf("Client connected. Total clients: %d", len(h.clients))

		case client := <-h.unregister:
			h.mutex.Lock()
			if _, ok := h.clients[client]; ok {
				delete(h.clients, client)
				close(client.send)
			}
			h.mutex.Unlock()
			log.Printf("Client disconnected. Total clients: %d", len(h.clients))

		case message := <-h.broadcast:
			h.mutex.RLock()
			for client := range h.clients {
				select {
				case client.send <- message:
				default:
					close(client.send)
					delete(h.clients, client)
				}
			}
			h.mutex.RUnlock()
		}
	}
}

// 客户端写入循环
func (c *Client) writePump() {
	ticker := time.NewTicker(54 * time.Second)
	defer func() {
		ticker.Stop()
		c.conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.send:
			c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if !ok {
				c.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			w, err := c.conn.NextWriter(websocket.TextMessage)
			if err != nil {
				return
			}
			w.Write(message)

			if err := w.Close(); err != nil {
				return
			}

		case <-ticker.C:
			c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

// 客户端读取循环
func (c *Client) readPump() {
	defer func() {
		hub.unregister <- c
		c.conn.Close()
		c.mutex.Lock()
		c.active = false
		c.mutex.Unlock()
	}()

	c.conn.SetReadLimit(512)
	c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
	c.conn.SetPongHandler(func(string) error {
		c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
		return nil
	})

	for {
		_, message, err := c.conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("WebSocket error: %v", err)
			}
			break
		}

		// 处理客户端消息
		var wsMsg WSMessage
		if err := json.Unmarshal(message, &wsMsg); err == nil {
			c.handleMessage(wsMsg)
		}
	}
}

// 处理客户端消息
func (c *Client) handleMessage(msg WSMessage) {
	switch msg.Type {
	case "ping":
		// 响应ping消息
		response := WSMessage{
			Type: "pong",
			Data: "pong",
		}
		c.sendMessage(response)

	case "get_system_info":
		// 发送系统信息
		go c.sendSystemInfo()

	case "get_camera_status":
		// 发送摄像头状态
		go c.sendCameraStatus()
	}
}

// 发送消息给客户端
func (c *Client) sendMessage(msg WSMessage) {
	c.mutex.RLock()
	active := c.active
	c.mutex.RUnlock()

	if !active {
		return
	}

	data, err := json.Marshal(msg)
	if err != nil {
		return
	}

	select {
	case c.send <- data:
	default:
		close(c.send)
		hub.unregister <- c
	}
}

// 发送系统信息
func (c *Client) sendSystemInfo() {
	// 这里可以获取实时系统信息
	// 为了简化，使用模拟数据
	sysInfo := SystemInfo{
		CPUUsage:    50.0,
		MemoryUsage: 60.0,
		DiskUsage:   30.0,
		Uptime:      "2小时 30分钟",
		Timestamp:   time.Now().Unix(),
	}

	msg := WSMessage{
		Type: "system_info",
		Data: sysInfo,
	}

	c.sendMessage(msg)
}

// 发送摄像头状态
func (c *Client) sendCameraStatus() {
	var duration int64 = 0
	if cameraManager.Recording {
		duration = int64(time.Since(cameraManager.StartTime).Seconds())
	}

	status := RecordingInfo{
		Recording: cameraManager.Recording,
		Filename:  cameraManager.RecordingFile,
		StartTime: cameraManager.StartTime.Format("2006-01-02 15:04:05"),
		Duration:  duration,
	}

	msg := WSMessage{
		Type: "camera_status",
		Data: status,
	}

	c.sendMessage(msg)
}

// 广播消息给所有客户端
func broadcastMessage(msgType string, data interface{}) {
	msg := WSMessage{
		Type: msgType,
		Data: data,
	}

	msgData, err := json.Marshal(msg)
	if err != nil {
		return
	}

	hub.broadcast <- msgData
}

// 系统监控循环
func startSystemMonitor() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			// 每5秒广播一次系统信息
			if len(hub.clients) > 0 {
				// 这里可以获取实际的系统信息
				// 为了简化，使用模拟数据
				sysInfo := SystemInfo{
					CPUUsage:    float64(time.Now().Unix()%100),
					MemoryUsage: float64((time.Now().Unix()+10)%100),
					DiskUsage:   float64((time.Now().Unix()+20)%100),
					Uptime:      formatUptime(time.Duration(time.Now().Unix()) * time.Second),
					Timestamp:   time.Now().Unix(),
				}
				broadcastMessage("system_info", sysInfo)
			}
		}
	}
}