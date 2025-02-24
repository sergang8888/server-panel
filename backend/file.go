package main

import (
    "io"
    "os"
    "path/filepath"
    "github.com/gin-gonic/gin"
)

// 列出文件
func listFiles(c *gin.Context) {
    dir := c.DefaultQuery("path", "/tmp") // 默认路径为/tmp
    files, err := os.ReadDir(dir)
    if err != nil {
        c.JSON(500, gin.H{"error": "Failed to list files"})
        return
    }

    var fileList []map[string]interface{}
    for _, file := range files {
        info, _ := file.Info()
        fileList = append(fileList, map[string]interface{}{
            "name":  file.Name(),
            "size":  info.Size(),
            "isDir": file.IsDir(),
        })
    }
    c.JSON(200, gin.H{"files": fileList})
}

// 上传文件
func uploadFile(c *gin.Context) {
    file, err := c.FormFile("file")
    if err != nil {
        c.JSON(400, gin.H{"error": "No file uploaded"})
        return
    }

    dst := filepath.Join("/tmp", file.Filename) // 保存到/tmp目录
    if err := c.SaveUploadedFile(file, dst); err != nil {
        c.JSON(500, gin.H{"error": "Failed to save file"})
        return
    }
    c.JSON(200, gin.H{"message": "File uploaded successfully"})
}