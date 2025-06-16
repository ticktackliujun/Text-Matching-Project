import os
from PyQt5.QtCore import QThread, pyqtSignal
import csv
import time
import matplotlib

matplotlib.use('Qt5Agg')  # 确保使用Qt后端
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = ["SimHei"]
plt.rcParams['axes.unicode_minus'] = False


## 评估工作线程
# evaluation_worker.py
from PyQt5.QtCore import QThread, pyqtSignal
import csv
import time

class EvaluationWorker(QThread):
    """评估工作线程，处理耗时的指标计算"""
    progress_updated = pyqtSignal(int, str)  # 进度值, 状态信息
    metrics_calculated = pyqtSignal(dict)  # 计算好的指标
    error_occurred = pyqtSignal(str)  # 错误信息

    def __init__(self, ground_truth_path, predicted_path, threshold):
        super().__init__()
        self.ground_truth_path = ground_truth_path
        self.predicted_path = predicted_path
        self.threshold = threshold
        self.cancel_flag = False

    def run(self):
        try:
            if not self.ground_truth_path or not self.predicted_path:
                self.error_occurred.emit("请选择真实样本集和预测样本集文件")
                return

            # 1. 加载真实样本数据
            self.progress_updated.emit(20, "加载真实样本数据...")
            ground_truth = self.load_csv_data(self.ground_truth_path)
            if not ground_truth:
                self.error_occurred.emit("真实样本数据加载失败")
                return

            # 2. 加载预测样本数据
            self.progress_updated.emit(40, "加载预测样本数据...")
            predicted = self.load_csv_data(self.predicted_path)
            if not predicted:
                self.error_occurred.emit("预测样本数据加载失败")
                return

            # 3. 计算评估指标
            self.progress_updated.emit(80, "计算评估指标...")
            metrics = self.calculate_metrics(ground_truth, predicted, self.threshold)

            # 4. 发送结果信号
            self.metrics_calculated.emit(metrics)
            self.progress_updated.emit(100, "评估完成")

        except Exception as e:
            self.error_occurred.emit(f"评估过程出错: {str(e)}")

    def load_csv_data(self, file_path):
        """从CSV文件加载数据"""
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 确保所有字段都存在
                    row.setdefault("file", "")
                    row.setdefault("path", "")
                    row.setdefault("line", "")
                    row.setdefault("keyword", "")
                    row.setdefault("context", "")
                    row.setdefault("confidence", "0")
                    data.append(row)
            return data
        except Exception as e:
            raise Exception(f"加载CSV数据失败: {str(e)}")

    def calculate_metrics(self, ground_truth, predicted_results, threshold):
        """计算评估指标，根据文件名、行号和关键词匹配"""
        if not ground_truth or not predicted_results:
            return {
                "precision": 0,
                "recall": 0,
                "f1": 0,
                "avg_time": 0,
                "error_rate": 0,
                "detail": []
            }

        # 构建真实样本集的索引 (file, line, keyword) 作为唯一标识
        truth_index = {}
        for item in ground_truth:
            key = (item.get("file", ""), item.get("line", ""), item.get("keyword", ""))
            truth_index[key] = item

        total_relevant = len(truth_index)  # 总相关文档数
        total_retrieved = 0  # 总检索结果数
        total_correct = 0  # 总正确结果数
        total_time = 0  # 总响应时间
        false_positives = 0  # 误检数（假阳性）

        detail_results = []

        # 处理预测结果
        for query_id, query_data in enumerate(predicted_results):
            # 获取当前查询的所有预测结果
            predictions = [query_data]  # 假设每行是一个预测结果
            time_ms = 0  # 如果没有时间信息，默认为0

            correct_in_query = 0
            retrieved_in_query = 0

            for pred in predictions:
                # 检查置信度是否达到阈值
                if float(pred.get("confidence", 0)) >= threshold:
                    retrieved_in_query += 1

                    # 检查是否为真实样本（使用file, line, keyword匹配）
                    key = (pred.get("file", ""), pred.get("line", ""), pred.get("keyword", ""))

                    if key in truth_index:
                        correct_in_query += 1

            false_positives_in_query = max(0, retrieved_in_query - correct_in_query)

            total_retrieved += retrieved_in_query
            total_correct += correct_in_query
            total_time += time_ms
            false_positives += false_positives_in_query

            # 详细结果
            detail_results.append({
                "query_id": query_id,
                "keyword": query_data.get("keyword", ""),
                "relevant": total_relevant,  # 对于整个查询集来说
                "retrieved": retrieved_in_query,
                "correct": correct_in_query,
                "time_ms": time_ms
            })

        # 计算各项指标
        precision = total_correct / total_retrieved if total_retrieved > 0 else 0
        recall = total_correct / total_relevant if total_relevant > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        avg_time = total_time / len(predicted_results) if predicted_results else 0
        error_rate = false_positives / total_retrieved if total_retrieved > 0 else 0

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "avg_time": avg_time,
            "error_rate": error_rate,
            "detail": detail_results
        }

    def cancel(self):
        """取消评估"""
        self.cancel_flag = True