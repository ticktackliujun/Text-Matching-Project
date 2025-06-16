from PyQt5.QtCore import QThread, pyqtSignal, QElapsedTimer
import os
import re
from collections import defaultdict
import csv
import math
from collections import defaultdict, Counter  # 添加Counter

class SearchWorker(QThread):
    """后台搜索工作线程"""
    search_progress = pyqtSignal(int, str)  # 进度百分比, 当前文件
    search_finished = pyqtSignal(list, int)  # 修改为接受两个参数: 结果列表和耗时
    error_occurred = pyqtSignal(str)  # 错误信息

    def __init__(self, file_list_path, keyword, algorithm="keyword", threshold=0.5, file_max_results=10):
        super().__init__()
        self.file_list_path = file_list_path
        self.keyword = keyword.lower()
        self.algorithm = algorithm
        self.threshold = threshold
        self.file_max_results = file_max_results  # 单文件最大结果数
        self.results = []
        self.timer = QElapsedTimer()

    def run(self):
        self.timer.start()
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

            # 修正缩进位置 - 应该在try块的末尾
            elapsed_time = self.timer.elapsed()
            self.search_finished.emit(self.results, elapsed_time)

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
        """改进的TF-IDF搜索算法（支持中英文）"""
        try:
            matches=[]
            # 读取文档内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()

            # 改进的分词（使用简单的正则，实际应用可替换为更复杂的分词器）
            words = []
            # 英文按单词分，中文按连续字符分
            for match in re.finditer(r'([\u4e00-\u9fa5]+|[a-zA-Z]+)', content):
                word = match.group(0)
                if re.search(r'[\u4e00-\u9fa5]', word):  # 中文
                    # 简单的N-gram分词（这里用bigram）
                    if len(word) > 1:
                        words.extend([word[i:i + 2] for i in range(len(word) - 1)])
                    else:
                        words.append(word)
                else:  # 英文
                    words.append(word.lower())

            total_words = len(words)
            if total_words == 0:
                return []

            # 计算词频
            word_counts = defaultdict(int)
            for word in words:
                word_counts[word] += 1

            # 分词搜索关键词
            keyword_tokens = []
            for match in re.finditer(r'([\u4e00-\u9fa5]+|[a-zA-Z]+)', self.keyword.lower()):
                token = match.group(0)
                if re.search(r'[\u4e00-\u9fa5]', token):
                    if len(token) > 1:
                        keyword_tokens.extend([token[i:i + 2] for i in range(len(token) - 1)])
                    else:
                        keyword_tokens.append(token)
                else:
                    keyword_tokens.append(token.lower())

            if not keyword_tokens:
                return []

            # 计算TF-IDF分数（使用简化的IDF）
            # 在实际应用中，IDF应该基于整个语料库计算
            # 这里使用一个简化的IDF：log(总文档数/包含该词的文档数)
            # 由于单文档搜索，使用log(1 + 总词数/词出现次数)作为近似
            scores = []
            for token in keyword_tokens:
                tf = word_counts.get(token, 0) / total_words
                # 简化的IDF计算
                idf = math.log(1 + total_words / max(1, word_counts.get(token, 0)))
                scores.append(tf * idf)

            # 计算向量相似度（余弦相似度）
            query_vector = [1.0] * len(keyword_tokens)  # 查询向量（全1）
            doc_vector = scores
            dot_product = sum(a * b for a, b in zip(query_vector, doc_vector))
            query_norm = math.sqrt(len(keyword_tokens))
            doc_norm = math.sqrt(sum(v ** 2 for v in doc_vector))
            similarity = dot_product / (query_norm * doc_norm) if (query_norm * doc_norm) > 0 else 0

            if similarity >= self.threshold:
                # 找到关键词出现位置
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    line_lower = line.lower()
                    if any(token in line_lower for token in keyword_tokens):
                        # 找到第一个匹配的token位置
                        pos = min(line_lower.find(token) for token in keyword_tokens if token in line_lower)
                        start = max(0, pos - 20)
                        end = min(len(line), pos + 20)
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

        except Exception as e:
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
        """改进的向量空间模型搜索算法（支持中英文）"""
        try:
            matches = []
            # 读取文档内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()

            # 分词（与TF-IDF使用相同的分词策略）
            words = []
            for match in re.finditer(r'([\u4e00-\u9fa5]+|[a-zA-Z]+)', content):
                word = match.group(0)
                if re.search(r'[\u4e00-\u9fa5]', word):
                    if len(word) > 1:
                        words.extend([word[i:i + 2] for i in range(len(word) - 1)])
                    else:
                        words.append(word)
                else:
                    words.append(word.lower())

            # 分词搜索关键词
            keyword_tokens = []
            for match in re.finditer(r'([\u4e00-\u9fa5]+|[a-zA-Z]+)', self.keyword.lower()):
                token = match.group(0)
                if re.search(r'[\u4e00-\u9fa5]', token):
                    if len(token) > 1:
                        keyword_tokens.extend([token[i:i + 2] for i in range(len(token) - 1)])
                    else:
                        keyword_tokens.append(token)
                else:
                    keyword_tokens.append(token.lower())

            if not keyword_tokens:
                return []

            # 构建文档向量和查询向量
            vocabulary = list(set(words + keyword_tokens))
            term_to_idx = {term: i for i, term in enumerate(vocabulary)}

            # 文档向量（使用TF-IDF权重）
            doc_vector = [0.0] * len(vocabulary)
            for term, count in Counter(words).items():
                if term in term_to_idx:
                    tf = count / len(words)
                    idf = math.log(1 + len(words) / max(1, count))  # 简化IDF
                    doc_vector[term_to_idx[term]] = tf * idf

            # 查询向量（关键词权重设为1，其他为0）
            query_vector = [0.0] * len(vocabulary)
            for term in keyword_tokens:
                if term in term_to_idx:
                    query_vector[term_to_idx[term]] = 1.0

            # 计算余弦相似度
            dot_product = sum(a * b for a, b in zip(query_vector, doc_vector))
            query_norm = math.sqrt(sum(v ** 2 for v in query_vector))
            doc_norm = math.sqrt(sum(v ** 2 for v in doc_vector))
            similarity = dot_product / (query_norm * doc_norm) if (query_norm * doc_norm) > 0 else 0

            if similarity >= self.threshold:
                # 找到关键词出现位置
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    line_lower = line.lower()
                    if any(token in line_lower for token in keyword_tokens):
                        pos = min(line_lower.find(token) for token in keyword_tokens if token in line_lower)
                        start = max(0, pos - 20)
                        end = min(len(line), pos + 20)
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

        except Exception as e:
            return []
    @staticmethod
    def export_to_csv(results, output_path, algorithm, keyword, elapsed_time):
        """导出结果到CSV，耗时信息写入每条记录"""
        try:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                # 定义CSV列名
                fieldnames = ['file', 'path', 'line', 'keyword', 'context', 'confidence', 'algorithm', 'time_ms']
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                writer.writeheader()

                # 为每条记录添加算法和耗时信息
                for result in results:
                    # 创建新的字典，避免修改原始结果
                    row = {
                        'file': result.get('file', ''),
                        'path': result.get('path', ''),
                        'line': result.get('line', ''),
                        'keyword': result.get('keyword', ''),
                        'context': result.get('context', ''),
                        'confidence': result.get('confidence', 0),
                        'algorithm': algorithm,
                        'time_ms': elapsed_time
                    }
                    writer.writerow(row)
            return True
        except Exception as e:
            raise Exception(f"导出失败: {str(e)}")