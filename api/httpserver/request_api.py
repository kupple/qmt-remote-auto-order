from flask import Flask, request, jsonify
import threading
import sys
from api.global_params import G

class APIService:
    def __init__(self,trade_controller):
        self.app = Flask(__name__)
        self.server = None
        self.thread = None
        self.trade_controller = trade_controller
        self._register_routes()
        self._is_running = False  # 新增：服务状态标志
      
        # 捕获werkzeug的输出
        import logging
        class FlaskLogHandler(logging.Handler):
            def emit(self, record):
                # 获取日志消息
                log_message = self.format(record)
                # 过滤掉时间戳
                log_message = log_message.split('] ')[1] if '] ' in log_message else log_message
                # 发送到G.logger
                G.logger.info("api调用： " + log_message, extra={"showMessage": True})
        
        # 获取werkzeug logger
        werkzeug_logger = logging.getLogger('werkzeug')
        # 添加handler
        handler = FlaskLogHandler()
        handler.setLevel(logging.INFO)
        werkzeug_logger.addHandler(handler)

    def _get_task_by_identifier(self, task_id=None, strategy_code=None):
        if task_id not in (None, ""):
            try:
                task_id = int(task_id)
            except (TypeError, ValueError):
                return None, "task_id must be an integer", 400

            task = G.orm.get_task_detail({"id": task_id})
            if not task or task.get("delete_time"):
                return None, "task not found", 404
            return task, None, None

        if isinstance(strategy_code, str):
            strategy_code = strategy_code.strip()

        if not strategy_code:
            return None, "task_id or strategy_code is required", 400

        task_list = G.orm.get_task_list({"strategy_code": strategy_code})
        if not task_list:
            return None, "task not found", 404
        return task_list[0], None, None

    def _register_routes(self):

        # 示例路由：获取持仓
        @self.app.route('/api/shippings', methods=['GET'])
        def shippings():
            res = G.orm.get_shippings_on_api()
            return jsonify({
                            'code':200,
                            'data': res,
                            })

        # 示例路由：获取资源
        @self.app.route('/api/positions', methods=['GET'])
        def positions():
            # Required parameters
            strategy_code = request.args.get('strategy_code')
            if not strategy_code:                
                return jsonify({'error': 'strategy_code is required'}), 400

            res = G.orm.get_positions_on_api(strategy_code)
            return jsonify({
                            'code':200,
                            'data': res,
                            })
        # 示例路由：获取资源
        @self.app.route('/api/account_fund', methods=['GET'])
        def account_fund():
            # Required parameters

            res = self.trade_controller.get_account_info() 
            return jsonify({
                            'code':200,
                            'data': res,
                            })

        # 示例路由：创建资源
        @self.app.route('/api/order', methods=['POST'])
        def order():
            data = request.get_json()
            print(data)
            strategy_code = data.get('strategy_code')
            stock_code = data.get('stock_code')
            volume = data.get('volume')
            price = data.get('price')
            order_type = data.get('order_type',1)
            is_buy = data.get('is_buy',1)
            if not strategy_code:                
                return jsonify({'error': 'strategy_code is required'}), 400
            if not stock_code:                
                return jsonify({'error': 'stock_code is required'}), 400
            if not volume:                
                return jsonify({'error': 'volume is required'}), 400
            if not price:                
                return jsonify({'error': 'price is required'}), 400
            if not order_type:                
                return jsonify({'error': 'order_type is required'}), 400
            if not is_buy:                
                return jsonify({'error': 'is_buy is required'}), 400
            
            ok,message = self.trade_controller.manage_api_trader(data)
            if not ok:
                return jsonify({
                    'code':400,
                    'data': message,
                }), 400
            return jsonify({
                'code':200,
                'data': "下单成功",
            })

        # 调整单个任务比例
        @self.app.route('/api/task/position_ratio', methods=['POST', 'PUT'])
        def update_task_position_ratio():
            data = request.get_json(silent=True) or {}
            task_id = data.get('task_id')
            strategy_code = data.get('strategy_code')
            position_ratio = data.get('position_ratio')

            if position_ratio in (None, ''):
                return jsonify({'error': 'position_ratio is required'}), 400

            try:
                position_ratio = float(position_ratio)
            except (TypeError, ValueError):
                return jsonify({'error': 'position_ratio must be a number'}), 400

            if position_ratio < 0:
                return jsonify({'error': 'position_ratio must be greater than or equal to 0'}), 400

            task, error_message, status_code = self._get_task_by_identifier(task_id, strategy_code)
            if error_message:
                return jsonify({'error': error_message}), status_code

            if task.get('order_count_type') != 1:
                return jsonify({'error': 'only order_count_type=1 tasks support position_ratio adjustment'}), 400

            ok = G.orm.update_task(task['id'], position_ratio=position_ratio)
            if not ok:
                return jsonify({'error': 'update task failed'}), 500

            return jsonify({
                'code': 200,
                'data': {
                    'task_id': task['id'],
                    'strategy_code': task.get('strategy_code'),
                    'position_ratio': position_ratio,
                },
            })

        # 示例路由：获取特定资源
        @self.app.route('/api/today_trades', methods=['GET'])
        def today_trades():
            
            return jsonify({"TodayTrades": "TodayTrades"})

        # 示例路由：更新资源
        @self.app.route('/api/items/<item_id>', methods=['PUT'])
        def update_item(item_id):
            data = request.get_json()
            return jsonify({"item_id": item_id, "name": data.get('name')})

        # 示例路由：删除资源
        @self.app.route('/api/total_account_information', methods=['GET'])
        def total_account_information():
            return jsonify({"TotalAccountInformation": "TotalAccountInformation"})

    def start(self, host='localhost', port=5000):
        """启动 API 服务（非阻塞）"""
        if self._is_running:
            print("Server is already running")
            return

        def shutdown_server():
            # Try Werkzeug shutdown first
            func = request.environ.get('werkzeug.server.shutdown')
            if func is not None:
                func()
                return 'Server shutting down...'
            
            # For production servers, we'll terminate the thread
            self._is_running = False
            if self.server is not None:
                self.server.shutdown()
            return 'Server shutting down...'



        # 创建 Flask development server
        from werkzeug.serving import make_server
        self.server = make_server(host, port, self.app, threaded=True)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        self._is_running = True  # 更新状态
        print(f"Server started on {host}:{port}")

    def stop(self):
        """停止 API 服务"""
        if not self._is_running:
            print("Server is not running")
            return

        try:
            # 关闭服务器
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            # 等待线程结束
            if self.thread:
                self.thread.join(timeout=2.0)
                
        except Exception as e:
            print(f"Error stopping server: {e}")
        finally:
            self._is_running = False  # 更新状态
            self.server = None
            self.thread = None
            print("Server stopped")

    def is_running(self):
        """检查服务是否正在运行"""
        return self._is_running and self.thread.is_alive()
