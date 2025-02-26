package main

import (
    "github.com/gin-gonic/gin"
    "net/http"
)

// 摄像头结构体
type Camera struct {
    ID        string `json:"id"`
    Name      string `json:"name"`
    StreamURL string `json:"streamUrl"`
    Type      string `json:"type"`
    Status    bool   `json:"status"`
}

// 网络配置结构体
type NetworkConfig struct {
    IP        string `json:"ip"`
    SubnetMask string `json:"subnetMask"`
    Gateway   string `json:"gateway"`
    MacAddress string `json:"macAddress"`
    Connected bool   `json:"connected"`
}

var cameras = make(map[string]Camera)

func main() {
    r := gin.Default()

    // 允许跨域
    r.Use(func(c *gin.Context) {
        c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
        c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type")
        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }
        c.Next()
    })

    // 摄像头相关接口
    api := r.Group("/api")
    {
        api.GET("/camera/list", listCameras)
        api.POST("/camera/add", addCamera)
        api.POST("/camera/toggle/:id", toggleCamera)
        api.DELETE("/camera/delete/:id", deleteCamera)

        // 网络相关接口
        api.GET("/network/status", getNetworkStatus)
        api.POST("/network/update", updateNetwork)
    }

    r.Run(":8080")
}

// 获取摄像头列表
func listCameras(c *gin.Context) {
    cameraList := make([]Camera, 0)
    for _, camera := range cameras {
        cameraList = append(cameraList, camera)
    }
    c.JSON(http.StatusOK, cameraList)
}

// 添加摄像头
func addCamera(c *gin.Context) {
    var camera Camera
    if err := c.BindJSON(&camera); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"success": false, "message": "无效的请求数据"})
        return
    }

    // 生成唯一ID
    camera.ID = generateID()
    cameras[camera.ID] = camera

    c.JSON(http.StatusOK, gin.H{"success": true, "camera": camera})
}

// 切换摄像头状态
func toggleCamera(c *gin.Context) {
    id := c.Param("id")
    if camera, exists := cameras[id]; exists {
        camera.Status = !camera.Status
        cameras[id] = camera
        c.JSON(http.StatusOK, gin.H{"success": true})
    } else {
        c.JSON(http.StatusNotFound, gin.H{"success": false, "message": "摄像头不存在"})
    }
}

// 删除摄像头
func deleteCamera(c *gin.Context) {
    id := c.Param("id")
    if _, exists := cameras[id]; exists {
        delete(cameras, id)
        c.JSON(http.StatusOK, gin.H{"success": true})
    } else {
        c.JSON(http.StatusNotFound, gin.H{"success": false, "message": "摄像头不存在"})
    }
}

// 获取网络状态
func getNetworkStatus(c *gin.Context) {
    // 这里实现实际的网络状态获取逻辑
    config := NetworkConfig{
        IP:         "192.168.1.100",
        SubnetMask: "255.255.255.0",
        Gateway:    "192.168.1.1",
        MacAddress: "00:11:22:33:44:55",
        Connected:  true,
    }
    c.JSON(http.StatusOK, config)
}

// 更新网络配置
func updateNetwork(c *gin.Context) {
    var config NetworkConfig
    if err := c.BindJSON(&config); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"success": false, "message": "无效的网络配置"})
        return
    }

    // 这里实现实际的网络配置更新逻辑
    // TODO: 实现实际的网络配置更新

    c.JSON(http.StatusOK, gin.H{"success": true})
}

// 生成唯一ID
func generateID() string {
    // 简单实现，实际应使用UUID或其他唯一ID生成方法
    return fmt.Sprintf("%d", time.Now().UnixNano())
}