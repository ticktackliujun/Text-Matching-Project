from PyQt5.QtCore import QThread, pyqtSignal
import os
import re
from collections import defaultdict
import csv


class SearchWorker(QThread):
    """后台搜索工作线程"""
    search_progress = pyqtSignal(int, str)  # 进度百分比, 当前文件
    search_finished = pyqtSignal(list)  # 搜索结果列表
    error_occurred = pyqtSignal(str)  # 错误信息

    def __init__(self, file_list_path, keyword, algorithm="keyword", threshold=0.5):
        super().__init__()
        self.file_list_path = file_list_path
        self.keyword = keyword.lower()
        self.algorithm = algorithm
        self.threshold = threshold
        self.results = []

    def run(self):
        try:
            # 读取文件列表
            with open(self.file_list_path, 'r', encoding='utf-8') as f:
                files = [line.strip() for line in f if line.strip()]

            total_files = len(files)
            if total_files == 0:
                self.error_occurred.emit("没有可搜索的文件")
                return

            for i, file_path in enumerate(files):
                if not os.path.exists(file_path):
                    continue

                # 更新进度
                progress = int((i + 1) / total_files * 100)
                self.search_progress.emit(progress, f"正在搜索: {os.path.basename(file_path)}")

                # 根据算法搜索
                if self.algorithm == "keyword":
                    matches = self.search_by_keyword(file_path)
                elif self.algorithm == "tfidf":
                    matches = self.search_by_tfidf(file_path)
                else:  # 默认关键词搜索
                    matches = self.search_by_keyword(file_path)

                if matches:
                    self.results.extend(matches)

            # 发送最终结果
            self.search_finished.emit(self.results)

        except Exception as e:
            self.error_occurred.emit(f"搜索失败: {str(e)}")

    def search_by_keyword(self, file_path):
        """关键词搜索算法"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()

            matches = []
            for match in re.finditer(r'\b{}\b'.format(re.escape(self.keyword)), content):
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 20)
                context = content[start:end].replace('\n', ' ')
                matches.append({
                    'file': os.path.basename(file_path),
                    'path': file_path,
                    'keyword': self.keyword,
                    'context': f"...{context}...",
                    'confidence': 1.0  # 关键词匹配默认置信度1.0
                })

            return matches

        except Exception:
            return []

    def search_by_tfidf(self, file_path):
        """TF-IDF搜索算法（简化版）"""
        # 这里实现简化的TF-IDF算法，实际项目中可以使用scikit-learn等库
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()

            words = re.findall(r'\w+', content)
            total_words = len(words)
            if total_words == 0:
                return []

            # 计算词频
            word_counts = defaultdict(int)
            for word in words:
                word_counts[word] += 1

            # 计算TF-IDF分数（简化版）
            tf = word_counts.get(self.keyword, 0) / total_words
            idf = 1.0  # 实际项目中需要计算全局IDF

            score = tf * idf
            if score >= self.threshold:
                # 找到关键词出现位置
                matches = []
                for match in re.finditer(r'\b{}\b'.format(re.escape(self.keyword)), content):
                    start = max(0, match.start() - 20)
                    end = min(len(content), match.end() + 20)
                    context = content[start:end].replace('\n', ' ')
                    matches.append({
                        'file': os.path.basename(file_path),
                        'path': file_path,
                        'keyword': self.keyword,
                        'context': f"...{context}...",
                        'confidence': round(score, 2)
                    })
                return matches

            return []

        except Exception:
            return []

    @staticmethod
    def export_to_csv(results, output_path):
        """导出结果到CSV"""
        try:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['file', 'path', 'keyword', 'context', 'confidence'])
                writer.writeheader()
                writer.writerows(results)
            return True
        except Exception as e:
            raise Exception(f"导出失败: {str(e)}")