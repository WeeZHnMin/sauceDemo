# 浏览器环境要求

## 支持的浏览器

本测试框架支持以下浏览器：

- **Microsoft Edge** (推荐)
- **Google Chrome** 
- **Mozilla Firefox**

## 环境配置

### 1. 安装浏览器驱动

框架默认使用 Edge 浏览器，请确保：

1. 安装了 Microsoft Edge 浏览器
2. 下载对应版本的 EdgeDriver
3. 将驱动路径配置到 `config/config.py` 的 `EDGE_DRIVER_PATH`

### 2. 修改浏览器类型

如需使用其他浏览器，请修改 `core/webdriver_utils.py` 中的 WebDriver 创建逻辑。

### 3. 无头模式

如需无头模式运行，请在 `config/config.py` 中取消注释：
```python
BROWSER_OPTIONS = [
    "--headless",  # 启用无头模式
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--window-size=800,600"
]
```

## 测试验证

运行以下命令验证环境配置：

```bash
# 验证框架收集测试
python -m pytest --collect-only tests/test_saucedemo_optimized.py

# 查看优化效果对比
python demo_optimization.py
```

## 故障排除

### 常见问题

1. **WebDriver not found**: 检查浏览器驱动是否正确安装和配置
2. **Browser version mismatch**: 确保浏览器版本与驱动版本匹配
3. **Permission denied**: 检查驱动文件的执行权限

### 日志查看

测试执行时的详细日志会保存在 `logs/` 目录下，可用于问题诊断。