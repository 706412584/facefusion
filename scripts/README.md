# 运维脚本

在资源管理器中双击即可；脚本会先 `cd` 到仓库根目录。

| 脚本 | 用途 |
|------|------|
| `检查GPU是否工作.bat` / `check_gpu.py` | 看 CUDA / TensorRT 是否可用 |
| `验证GPU库安装.bat` | 查 cuDNN / TensorRT 文件 |
| `安装CUDA支持.bat` 等 | 安装/配置加速库 |
| `清理缓存.bat` / `清理任务队列.bat` | 清理 `.caches` / `.jobs` |
| `命令行处理.bat` / `直接处理视频.bat` | 无界面或简化处理 |
| `压缩视频.py` / `压缩超大视频.bat` | 预处理大视频 |
| `setup_proxy.py` | 代理探测（启动 bat 会调用） |

文档索引见 [`docs/README.md`](../docs/README.md)。
