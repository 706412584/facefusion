# FaceFusion 三种工作流程完整说明

## 问题根源

你遇到的问题是：**job_runner 不会创建任务，只会运行已存在的任务**

当任务编号显示 "none" 时，说明队列中没有任务，所以无法运行。

---

## 三种工作流程对比

### 1. instant_runner（即时运行器）⭐ 推荐新手

**特点：**
- 最简单，一键完成
- 自动创建任务并立即运行
- 适合快速测试和单个文件处理

**使用步骤：**
1. 上传源文件（人脸照片）
2. 上传目标文件（视频）
3. 选择处理器（face_swapper）
4. 勾选 CUDA
5. 点击"开始"
6. 等待完成

**优点：**
- 操作简单
- 不需要管理任务

**缺点：**
- 无法批量处理
- 无法查看任务队列
- 任务失败后不易调试

---

### 2. job_runner（任务运行器）

**特点：**
- 运行已创建的任务
- 可以看到任务队列
- 适合运行预先准备好的任务

**重要：job_runner 不会创建任务！**

**使用步骤：**
1. 先用其他方式创建任务（instant_runner 或 job_manager）
2. 切换到 job_runner
3. 选择任务操作：
   - job-run：运行单个任务
   - job-run-all：运行所有队列任务
   - job-retry：重试失败的任务
   - job-retry-all：重试所有失败任务
4. 选择任务编号
5. 点击"开始"

**任务操作说明：**
- **job-run**：运行队列中的指定任务
- **job-run-all**：运行队列中的所有任务
- **job-retry**：重新运行失败的任务
- **job-retry-all**：重新运行所有失败的任务

**优点：**
- 可以管理多个任务
- 可以重试失败的任务
- 适合批量处理

**缺点：**
- 需要先创建任务
- 不能直接从界面创建任务

---

### 3. job_manager（任务管理器）⭐ 推荐高级用户

**特点：**
- 完整的任务管理功能
- 可以创建、编辑、删除任务
- 可以添加多个处理步骤
- 适合复杂的批量处理

**使用步骤：**

#### 步骤 1：创建任务
1. 任务操作：选择 "job-create"
2. 点击"应用"
3. 会生成一个任务 ID（例如：ui-2026-04-26-12-00-00）

#### 步骤 2：添加处理步骤
1. 任务操作：选择 "job-add-step"
2. 任务编号：选择刚创建的任务 ID
3. 配置参数：
   - 上传源文件
   - 上传目标文件
   - 设置输出路径
   - 选择处理器
   - 勾选 CUDA
4. 点击"应用"

#### 步骤 3：提交任务
1. 任务操作：选择 "job-submit"
2. 任务编号：选择任务 ID
3. 点击"应用"
4. 任务会进入队列（queued）

#### 步骤 4：运行任务
1. 切换到 job_runner 工作流程
2. 或者在 job_manager 中选择 "job-run"
3. 点击"开始"

**其他操作：**
- **job-delete**：删除任务
- **job-remove-step**：删除步骤
- **job-remix-step**：重新混合步骤

**优点：**
- 功能最完整
- 可以创建复杂的处理流程
- 可以批量处理多个文件

**缺点：**
- 操作复杂
- 学习曲线陡峭

---

## 你的问题解决方案

### 问题：job_runner 显示任务编号 "none"

**原因：**
- job_runner 不会创建任务
- 队列中没有任务
- 所以显示 "none"

**解决方案 1：切换到 instant_runner（推荐）**

1. 关闭 FaceFusion
2. 运行：`启动FaceFusion.bat`（已修改为 instant_runner）
3. 直接上传文件并处理

**解决方案 2：使用 job_manager 创建任务**

1. 在界面切换到 job_manager
2. 按照上面的步骤创建任务
3. 切换回 job_runner 运行任务

**解决方案 3：使用命令行（最稳定）**

```bash
python facefusion.py run --source-paths "源文件.jpg" --target-path "目标视频.mp4" --output-path "输出.mp4" --processors face_swapper --execution-providers cuda tensorrt
```

---

## 推荐配置

### 新手推荐：instant_runner
- 简单直接
- 一键完成
- 适合学习和测试

### 日常使用：instant_runner 或 job_manager
- instant_runner：单个文件快速处理
- job_manager：批量处理多个文件

### 高级用户：job_manager + job_runner
- job_manager：创建和管理任务
- job_runner：批量运行任务

---

## 当前建议

1. **立即操作：**
   - 关闭 FaceFusion
   - 运行：`启动FaceFusion.bat`
   - 现在默认是 instant_runner 模式
   - 直接上传文件并处理

2. **如果还是有问题：**
   - 使用命令行模式
   - 运行：`scripts/命令行处理.bat`
   - 输入文件路径
   - 直接处理

3. **GPU 加速已经配置好：**
   - CUDA: YES ✓
   - TensorRT: YES ✓
   - RTX 4060 正常工作 ✓
   - 处理速度会很快（20-40 帧/秒）

---

## 总结

- **instant_runner**：自动创建并运行任务（推荐）
- **job_runner**：只运行已存在的任务（不创建）
- **job_manager**：完整的任务管理（创建、编辑、删除）

你之前的问题是用 job_runner 但没有任务，现在切换到 instant_runner 就可以了。
