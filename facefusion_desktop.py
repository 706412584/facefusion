#!/usr/bin/env python3
"""
FaceFusion 桌面版
使用 PyQt6 创建的独立桌面应用
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox, QSlider, QTextEdit,
    QGroupBox, QProgressBar, QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage

# 设置语言
os.environ['FACEFUSION_LANGUAGE'] = 'zh'

from facefusion import state_manager, translator
from facefusion.locales import LOCALES

# 加载翻译
translator.set_language('zh')
translator.load(LOCALES, 'facefusion')


class ProcessThread(QThread):
    """处理线程"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, source_path, target_path, output_path, processors):
        super().__init__()
        self.source_path = source_path
        self.target_path = target_path
        self.output_path = output_path
        self.processors = processors
    
    def run(self):
        """执行处理"""
        try:
            self.status.emit("正在初始化...")
            self.progress.emit(10)
            
            # 这里调用 FaceFusion 的处理逻辑
            # 由于原项目结构复杂，这里先做一个框架
            self.status.emit("正在处理...")
            self.progress.emit(50)
            
            # TODO: 实际的处理逻辑
            import time
            time.sleep(2)  # 模拟处理
            
            self.progress.emit(100)
            self.status.emit("处理完成！")
            self.finished.emit(True, "处理成功完成")
            
        except Exception as e:
            self.status.emit(f"错误: {str(e)}")
            self.finished.emit(False, str(e))


class FaceFusionDesktop(QMainWindow):
    """FaceFusion 桌面主窗口"""
    
    def __init__(self):
        super().__init__()
        self.source_path = None
        self.target_path = None
        self.output_path = None
        self.process_thread = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("FaceFusion - 人脸融合工具")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        tabs = QTabWidget()
        tabs.addTab(self.create_basic_tab(), "基础处理")
        tabs.addTab(self.create_advanced_tab(), "高级选项")
        tabs.addTab(self.create_about_tab(), "关于")
        
        main_layout.addWidget(tabs)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def create_basic_tab(self):
        """创建基础处理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 文件选择组
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout()
        
        # 源文件
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("源文件（图片/视频）:"))
        self.source_label = QLabel("未选择")
        self.source_label.setStyleSheet("color: gray;")
        source_layout.addWidget(self.source_label)
        source_layout.addStretch()
        source_btn = QPushButton("选择源文件")
        source_btn.clicked.connect(self.select_source)
        source_layout.addWidget(source_btn)
        file_layout.addLayout(source_layout)
        
        # 目标文件
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("目标文件（图片/视频）:"))
        self.target_label = QLabel("未选择")
        self.target_label.setStyleSheet("color: gray;")
        target_layout.addWidget(self.target_label)
        target_layout.addStretch()
        target_btn = QPushButton("选择目标文件")
        target_btn.clicked.connect(self.select_target)
        target_layout.addWidget(target_btn)
        file_layout.addLayout(target_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出文件:"))
        self.output_label = QLabel("未选择")
        self.output_label.setStyleSheet("color: gray;")
        output_layout.addWidget(self.output_label)
        output_layout.addStretch()
        output_btn = QPushButton("选择输出位置")
        output_btn.clicked.connect(self.select_output)
        output_layout.addWidget(output_btn)
        file_layout.addLayout(output_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 处理器选择
        processor_group = QGroupBox("处理器选择")
        processor_layout = QVBoxLayout()
        
        self.processor_combo = QComboBox()
        self.processor_combo.addItems([
            "人脸交换 (Face Swapper)",
            "人脸增强 (Face Enhancer)",
            "帧增强 (Frame Enhancer)",
            "表情恢复 (Expression Restorer)",
            "年龄修改 (Age Modifier)",
        ])
        processor_layout.addWidget(QLabel("选择处理器:"))
        processor_layout.addWidget(self.processor_combo)
        
        processor_group.setLayout(processor_layout)
        layout.addWidget(processor_group)
        
        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QHBoxLayout()
        
        self.source_preview = QLabel("源文件预览")
        self.source_preview.setFixedSize(300, 300)
        self.source_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.source_preview.setStyleSheet("border: 1px solid gray; background: #f0f0f0;")
        preview_layout.addWidget(self.source_preview)
        
        self.target_preview = QLabel("目标文件预览")
        self.target_preview.setFixedSize(300, 300)
        self.target_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.target_preview.setStyleSheet("border: 1px solid gray; background: #f0f0f0;")
        preview_layout.addWidget(self.target_preview)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 状态文本
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        self.status_text.setPlaceholderText("处理日志将显示在这里...")
        layout.addWidget(self.status_text)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.start_btn = QPushButton("开始处理")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 14px;")
        self.start_btn.clicked.connect(self.start_process)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_process)
        button_layout.addWidget(self.stop_btn)
        
        webui_btn = QPushButton("启动 Web UI")
        webui_btn.clicked.connect(self.launch_webui)
        button_layout.addWidget(webui_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def create_advanced_tab(self):
        """创建高级选项标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 人脸检测设置
        face_group = QGroupBox("人脸检测设置")
        face_layout = QVBoxLayout()
        
        # 检测模型
        face_layout.addWidget(QLabel("人脸检测模型:"))
        detector_combo = QComboBox()
        detector_combo.addItems(["yolo_face", "retinaface", "scrfd", "yunet"])
        face_layout.addWidget(detector_combo)
        
        # 置信度
        face_layout.addWidget(QLabel("检测置信度:"))
        confidence_slider = QSlider(Qt.Orientation.Horizontal)
        confidence_slider.setMinimum(0)
        confidence_slider.setMaximum(100)
        confidence_slider.setValue(50)
        confidence_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        confidence_slider.setTickInterval(10)
        face_layout.addWidget(confidence_slider)
        
        face_group.setLayout(face_layout)
        layout.addWidget(face_group)
        
        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QVBoxLayout()
        
        output_layout.addWidget(QLabel("输出质量:"))
        quality_slider = QSlider(Qt.Orientation.Horizontal)
        quality_slider.setMinimum(0)
        quality_slider.setMaximum(100)
        quality_slider.setValue(80)
        quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        quality_slider.setTickInterval(10)
        output_layout.addWidget(quality_slider)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        layout.addStretch()
        
        return widget
    
    def create_about_tab(self):
        """创建关于标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
        <h2>FaceFusion 桌面版</h2>
        <p><b>版本:</b> 3.6.1</p>
        <p><b>描述:</b> 业界领先的人脸处理平台</p>
        <br>
        <h3>功能特性:</h3>
        <ul>
            <li>人脸交换</li>
            <li>人脸增强</li>
            <li>表情恢复</li>
            <li>年龄修改</li>
            <li>帧增强</li>
        </ul>
        <br>
        <h3>使用说明:</h3>
        <ol>
            <li>选择源文件（包含要使用的人脸）</li>
            <li>选择目标文件（要处理的图片或视频）</li>
            <li>选择输出位置</li>
            <li>选择处理器</li>
            <li>点击"开始处理"</li>
        </ol>
        <br>
        <p><b>许可证:</b> OpenRAIL-AS</p>
        <p><b>项目主页:</b> <a href="https://github.com/facefusion/facefusion">GitHub</a></p>
        """)
        layout.addWidget(about_text)
        
        return widget
    
    def select_source(self):
        """选择源文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择源文件",
            "",
            "图片和视频 (*.jpg *.jpeg *.png *.mp4 *.avi *.mov);;所有文件 (*.*)"
        )
        if file_path:
            self.source_path = file_path
            self.source_label.setText(Path(file_path).name)
            self.source_label.setStyleSheet("color: black;")
            self.load_preview(file_path, self.source_preview)
            self.log_message(f"已选择源文件: {file_path}")
    
    def select_target(self):
        """选择目标文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择目标文件",
            "",
            "图片和视频 (*.jpg *.jpeg *.png *.mp4 *.avi *.mov);;所有文件 (*.*)"
        )
        if file_path:
            self.target_path = file_path
            self.target_label.setText(Path(file_path).name)
            self.target_label.setStyleSheet("color: black;")
            self.load_preview(file_path, self.target_preview)
            self.log_message(f"已选择目标文件: {file_path}")
    
    def select_output(self):
        """选择输出文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择输出位置",
            "",
            "图片 (*.jpg *.png);;视频 (*.mp4 *.avi);;所有文件 (*.*)"
        )
        if file_path:
            self.output_path = file_path
            self.output_label.setText(Path(file_path).name)
            self.output_label.setStyleSheet("color: black;")
            self.log_message(f"输出位置: {file_path}")
    
    def load_preview(self, file_path, label):
        """加载预览图"""
        try:
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                pixmap = QPixmap(file_path)
                scaled_pixmap = pixmap.scaled(
                    label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                label.setPixmap(scaled_pixmap)
            else:
                label.setText("视频文件\n(无预览)")
        except Exception as e:
            label.setText(f"预览失败\n{str(e)}")
    
    def log_message(self, message):
        """添加日志消息"""
        self.status_text.append(message)
        self.statusBar().showMessage(message)
    
    def start_process(self):
        """开始处理"""
        # 验证输入
        if not self.source_path:
            QMessageBox.warning(self, "警告", "请先选择源文件！")
            return
        
        if not self.target_path:
            QMessageBox.warning(self, "警告", "请先选择目标文件！")
            return
        
        if not self.output_path:
            QMessageBox.warning(self, "警告", "请先选择输出位置！")
            return
        
        # 禁用开始按钮，启用停止按钮
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        self.log_message("=" * 50)
        self.log_message("开始处理...")
        
        # 创建处理线程
        processor = self.processor_combo.currentText()
        self.process_thread = ProcessThread(
            self.source_path,
            self.target_path,
            self.output_path,
            processor
        )
        
        # 连接信号
        self.process_thread.progress.connect(self.update_progress)
        self.process_thread.status.connect(self.log_message)
        self.process_thread.finished.connect(self.process_finished)
        
        # 启动线程
        self.process_thread.start()
    
    def stop_process(self):
        """停止处理"""
        if self.process_thread and self.process_thread.isRunning():
            self.process_thread.terminate()
            self.log_message("处理已停止")
            self.process_finished(False, "用户取消")
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def process_finished(self, success, message):
        """处理完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if success:
            QMessageBox.information(self, "成功", message)
            self.log_message("✓ 处理成功完成！")
        else:
            QMessageBox.critical(self, "错误", message)
            self.log_message(f"✗ 处理失败: {message}")
    
    def launch_webui(self):
        """启动 Web UI"""
        reply = QMessageBox.question(
            self,
            "启动 Web UI",
            "是否要启动 Web 界面？\n这将在浏览器中打开 FaceFusion。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            import subprocess
            subprocess.Popen([sys.executable, "facefusion.py", "run", "--language", "zh"])
            self.log_message("Web UI 启动中...")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = FaceFusionDesktop()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
