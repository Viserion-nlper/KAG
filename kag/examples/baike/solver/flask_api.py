from flask import Flask, request, jsonify
import logging
import time  # 导入time模块
from kag.common.conf import KAG_CONFIG, init_env
from kag.common.registry import import_modules_from_path
from kag.solver.logic.solver_pipeline import SolverPipeline

# 初始化 Flask 应用
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

class MedicineDemo:
    """
    init for kag client
    """
    def qa(self, query):
        resp = SolverPipeline.from_config(KAG_CONFIG.all_config["kag_solver_pipeline"])
        answer, trace_log = resp.run(query)
        return answer, trace_log

# 在应用启动前进行一次性初始化
@app.before_first_request
def initialize_app():
    # 修改为你的配置文件路径
    init_env("/Users/czq/code/KAG/KAG/kag/examples/baike/kag_config.yaml")
    import_modules_from_path("/Users/czq/code/KAG/KAG/kag/examples/baike/solver")
    import_modules_from_path("./prompt")

@app.route('/qa', methods=['POST'])
def handle_qa():
    start_time = time.time()  # 记录请求开始时间
    try:
        # 获取请求中的 query 参数
        query = request.json.get('query')
        if not query:
            return jsonify({"error": "Missing query parameter"}), 400

        demo = MedicineDemo()
        answer, trace_log = demo.qa(query)

        # 计算耗时
        time_used = time.time() - start_time
        
        return jsonify({
            "query": query,
            "answer": answer,
            "trace_log": trace_log,
            "time_used": round(time_used, 4)  # 保留4位小数
        })

    except Exception as e:
        # 异常时也计算耗时
        time_used = time.time() - start_time
        logging.exception("Error processing request")
        return jsonify({
            "error": str(e),
            "time_used": round(time_used, 4)  # 保留4位小数
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
