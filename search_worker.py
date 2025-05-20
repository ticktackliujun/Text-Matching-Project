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

    def __init__(self, file_list_path, keyword, algorithm="keyword", threshold=0.5, file_max_results=10):
        super().__init__()
        self.file_list_path = file_list_path
        self.keyword = keyword.lower()
        self.algorithm = algorithm
        self.threshold = threshold
        self.file_max_results = file_max_results  # 单文件最大结果数
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
                elif self.algorithm == "boolean":
                    matches = self.search_by_boolean(file_path)
                elif self.algorithm == "vector":
                    matches = self.search_by_vector(file_path)
                else:  # 默认关键词搜索
                    matches = self.search_by_keyword(file_path)

                # 对单文件结果按置信度排序并限制数量
                if matches:
                    sorted_matches = sorted(matches, key=lambda x: x['confidence'], reverse=True)
                    self.results.extend(sorted_matches[:self.file_max_results])

            # 发送最终结果
            self.search_finished.emit(self.results)

        except Exception as e:
            self.error_occurred.emit(f"搜索失败: {str(e)}")

    def search_by_keyword(self, file_path):
        """关键词搜索算法（支持中英文）"""
        try:
            matches = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                content_lower = content.lower()
                keyword_lower = self.keyword.lower()

                # 改进的正则表达式，支持中英文单词边界
                # 中文使用unicode汉字范围，英文使用\b单词边界
                if re.search(r'[\u4e00-\u9fa5]', self.keyword):  # 如果包含中文
                    # 中文直接搜索，不使用单词边界
                    pattern = re.escape(keyword_lower)
                else:  # 英文使用单词边界
                    pattern = r'\b{}\b'.format(re.escape(keyword_lower))

                for line_num, line in enumerate(content.split('\n'), 1):
                    line_lower = line.lower()
                    for match in re.finditer(pattern, line_lower):
                        start = max(0, match.start() - 20)
                        end = min(len(line), match.end() + 20)
                        context = line[start:end].replace('\n', ' ')
                        matches.append({
                            'file': os.path.basename(file_path),
                            'path': file_path,
                            'line': line_num,
                            'keyword': self.keyword,
                            'context': f"...{context}...",
                            'confidence': 1.0
                        })
            return matches
        except Exception:
            return []

    def search_by_tfidf(self, file_path):
        """TF-IDF搜索算法（支持中英文）"""
        try:
            matches = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()

            # 改进的中英文分词
            # 中文按字符分，英文按单词分
            words = []
            for word in re.findall(r'[\w\u4e00-\u9fa5]+', content):
                if re.search(r'[\u4e00-\u9fa5]', word):  # 中文
                    words.extend(list(word))  # 中文按字符分
                else:  # 英文
                    words.append(word.lower())

            total_words = len(words)
            if total_words == 0:
                return []

            # 计算词频
            word_counts = defaultdict(int)
            for word in words:
                word_counts[word] += 1

            # 计算TF-IDF分数（简化版）
            keyword_words = []
            if re.search(r'[\u4e00-\u9fa5]', self.keyword):  # 中文关键词
                keyword_words = list(self.keyword.lower())
            else:  # 英文关键词
                keyword_words = [w.lower() for w in re.findall(r'\w+', self.keyword)]

            if not keyword_words:
                return []

            # 计算所有关键词的平均TF-IDF
            scores = []
            for kw in keyword_words:
                tf = word_counts.get(kw, 0) / total_words
                idf = 1.0  # 实际项目中需要计算全局IDF
                scores.append(tf * idf)

            avg_score = sum(scores) / len(scores) if scores else 0

            if avg_score >= self.threshold:
                # 找到关键词出现位置
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    line_lower = line.lower()
                    if all(kw in line_lower for kw in keyword_words):
                        # 找到第一个关键词的位置
                        first_kw_pos = min(line_lower.find(kw) for kw in keyword_words if kw in line_lower)
                        start = max(0, first_kw_pos - 20)
                        end = min(len(line), first_kw_pos + len(self.keyword) + 20)
                        context = line[start:end].replace('\n', ' ')
                        matches.append({
                            'file': os.path.basename(file_path),
                            'path': file_path,
                            'line': line_num,
                            'keyword': self.keyword,
                            'context': f"...{context}...",
                            'confidence': round(avg_score, 2)
                        })
            return matches

        except Exception:
            return []

    def search_by_boolean(self, file_path):
        """布尔模型搜索算法（支持中英文）"""
        try:
            # 获取搜索词（支持中英文混合）
            terms = []
            if re.search(r'[\u4e00-\u9fa5]', self.keyword):  # 包含中文
                terms = list(self.keyword.lower())  # 中文按字符分
            else:  # 英文
                terms = [t.lower() for t in re.findall(r'[\w\u4e00-\u9fa5]+', self.keyword.lower())]

            if not terms:
                return []

            matches = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    line_lower = line.lower()
                    if all(term in line_lower for term in terms):
                        # 找到第一个术语的位置
                        first_term_pos = min(line_lower.find(term) for term in terms if term in line_lower)
                        start = max(0, first_term_pos - 20)
                        end = min(len(line), first_term_pos + len(self.keyword) + 20)
                        context = line[start:end].replace('\n', ' ')
                        matches.append({
                            'file': os.path.basename(file_path),
                            'path': file_path,
                            'line': line_num,
                            'keyword': self.keyword,
                            'context': f"...{context}...",
                            'confidence': 0.9
                        })
            return matches

        except Exception:
            return []

    def search_by_vector(self, file_path):
        """向量空间模型搜索算法（支持中英文）"""
        try:
            matches = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()

            # 改进的中英文分词
            words = []
            for word in re.findall(r'[\w\u4e00-\u9fa5]+', content):
                if re.search(r'[\u4e00-\u9fa5]', word):  # 中文
                    words.extend(list(word))
                else:  # 英文
                    words.append(word.lower())

            # 获取搜索词（支持中英文混合）
            keyword_terms = []
            if re.search(r'[\u4e00-\u9fa5]', self.keyword):  # 包含中文
                keyword_terms = list(self.keyword.lower())
            else:  # 英文
                keyword_terms = [t.lower() for t in re.findall(r'\w+', self.keyword.lower())]

            if not keyword_terms:
                return []

            # 计算词频
            word_counts = defaultdict(int)
            for word in words:
                word_counts[word] += 1

            # 计算搜索词的总出现次数
            keyword_count = sum(word_counts.get(term, 0) for term in keyword_terms)

            if keyword_count > 0:
                # 简单相似度计算
                similarity = keyword_count / max(1, len(words))
                if similarity >= self.threshold:
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        line_lower = line.lower()
                        if all(term in line_lower for term in keyword_terms):
                            first_term_pos = min(line_lower.find(term) for term in keyword_terms if term in line_lower)
                            start = max(0, first_term_pos - 20)
                            end = min(len(line), first_term_pos + len(self.keyword) + 20)
                            context = line[start:end].replace('\n', ' ')
                            matches.append({
                                'file': os.path.basename(file_path),
                                'path': file_path,
                                'line': line_num,
                                'keyword': self.keyword,
                                'context': f"...{context}...",
                                'confidence': round(similarity, 2)
                            })
            return matches

        except Exception:
            return []
    @staticmethod
    def export_to_csv(results, output_path):
        """导出结果到CSV"""
        try:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['file', 'path', 'line', 'keyword', 'context', 'confidence'])
                writer.writeheader()
                writer.writerows(results)
            return True
        except Exception as e:
            raise Exception(f"导出失败: {str(e)}")