# index_worker.py
from PyQt5.QtCore import QThread, pyqtSignal, QFileInfo, QDateTime
import os

class IndexWorker(QThread):
    """后台文件索引工作线程"""
    progress_updated = pyqtSignal(str)  # 更新进度消息
    file_found = pyqtSignal(str)        # 发现新文件
    indexing_finished = pyqtSignal(list)  # 索引完成，传递文件列表

    def __init__(self, directory, extensions=None):
        super().__init__()
        self.directory = directory
        self.extensions = extensions or []

    def run(self):
        """线程执行的主要方法"""
        try:
            if not self.directory or not os.path.exists(self.directory):
                self.progress_updated.emit("目录不存在")
                self.indexing_finished.emit([])
                return

            self.progress_updated.emit(f"开始索引目录: {self.directory}")
            files = []
            total_files = 0

            # 先计算总文件数（用于进度显示）
            for root, _, filenames in os.walk(self.directory):
                for filename in filenames:
                    if not self.extensions or any(filename.lower().endswith(f'.{ext}') for ext in self.extensions):
                        total_files += 1

            processed = 0
            for root, _, filenames in os.walk(self.directory):
                for filename in filenames:
                    if not self.extensions or any(filename.lower().endswith(f'.{ext}') for ext in self.extensions):
                        full_path = os.path.join(root, filename)
                        files.append(full_path)
                        processed += 1

                        # 发送进度更新（每100个文件或完成时）
                        if processed % 100 == 0 or processed == total_files:
                            progress = int(processed / total_files * 100) if total_files != 0 else 0
                            self.progress_updated.emit(f"已处理 {processed}/{total_files} 文件")
                            self.file_found.emit(full_path)

            self.progress_updated.emit(f"索引完成，共找到 {len(files)} 个文件")
            self.indexing_finished.emit(files)

        except Exception as e:
            self.progress_updated.emit(f"索引失败: {str(e)}")
            self.indexing_finished.emit([])