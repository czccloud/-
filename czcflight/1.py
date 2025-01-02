from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

# 数据库连接配置
host = "localhost"
user = "root"
password = "fg839661164"
dbname = "test"

app = Flask(__name__)
CORS(app)

# 连接数据库
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=dbname
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error: {e}")
        return None

# 执行 SQL 查询
def execute_query(conn, query, params=None):
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
    except Error as e:
        print(f"Query failed: {e}")

# 获取查询结果
def fetch_query_results(conn, query, params=None):
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"Query failed: {e}")
        return None

# 用户注册
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username = data['username']
    password = data['password']
    email = data['email']

    conn = connect_to_database()
    if conn:
        query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s);"
        execute_query(conn, query, (username, password, email))
        return jsonify({"message": "用户注册成功"}), 201
    return jsonify({"message": "数据库连接失败"}), 500

# 用户登录
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    username = data['username']
    password = data['password']

    conn = connect_to_database()
    if conn:
        query = "SELECT user_id FROM users WHERE username = %s AND password = %s;"
        results = fetch_query_results(conn, query, (username, password))
        if results:
            return jsonify({"message": "登录成功", "user_id": results[0][0]}), 200
        else:
            return jsonify({"message": "用户名或密码错误"}), 401
    return jsonify({"message": "数据库连接失败"}), 500

# 管理员登录
@app.route('/admin/login', methods=['POST'])
def login_admin():
    data = request.json
    username = data['username']
    password = data['password']

    conn = connect_to_database()
    if conn:
        query = "SELECT user_id FROM users WHERE username = %s AND password = %s AND is_admin = TRUE;"
        results = fetch_query_results(conn, query, (username, password))
        if results:
            return jsonify({"message": "管理员登录成功", "admin_id": results[0][0]}), 200
        else:
            return jsonify({"message": "用户名或密码错误或不是管理员"}), 401
    return jsonify({"message": "数据库连接失败"}), 500

# 查看所有航班
@app.route('/flights', methods=['GET'])
def view_flights():
    conn = connect_to_database()
    if conn:
        query = "SELECT * FROM flights;"
        results = fetch_query_results(conn, query)
        flights = [{"flight_id": row[0], "origin": row[1], "destination": row[2], "departure_time": row[3], "price": row[4]} for row in results]
        return jsonify({"flights": flights}), 200
    return jsonify({"message": "数据库连接失败"}), 500

# 搜索航班
@app.route('/search_flights', methods=['GET'])
def search_flights():
    keyword = request.args.get('keyword', '').strip()  # 获取搜索关键字
    conn = connect_to_database()
    if conn:
        try:
            query = "SELECT * FROM flights WHERE origin LIKE %s OR destination LIKE %s;"
            cursor = conn.cursor()
            cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
            results = cursor.fetchall()
            flights = [{"flight_id": row[0], "origin": row[1], "destination": row[2], "departure_time": row[3], "price": row[4]} for row in results]
            return jsonify({"flights": flights}), 200
        except Error as e:
            print(f"Error searching flights: {e}")
            return jsonify({"message": "数据库查询失败"}), 500
        finally:
            conn.close()
    else:
        return jsonify({"message": "数据库连接失败"}), 500

# 预订航班
@app.route('/book_flight', methods=['POST'])
def book_flight():
    data = request.json
    user_id = data['user_id']
    flight_id = data['flight_id']
    quantity = data['quantity']

    conn = connect_to_database()
    if conn:
        query = "INSERT INTO bookings (user_id, flight_id, quantity) VALUES (%s, %s, %s);"
        execute_query(conn, query, (user_id, flight_id, quantity))
        return jsonify({"message": "航班预订成功"}), 200
    return jsonify({"message": "数据库连接失败"}), 500

# 查看我的订单
@app.route('/my_bookings', methods=['GET'])
def get_my_bookings():
    user_id = request.args.get('user_id')  # 从查询参数中获取用户ID

    conn = connect_to_database()
    if conn:
        try:
            query = """
            SELECT bookings.booking_id, flights.origin, flights.destination, flights.departure_time, flights.price, bookings.quantity
            FROM bookings
            INNER JOIN flights ON bookings.flight_id = flights.flight_id
            WHERE bookings.user_id = %s;
            """
            results = fetch_query_results(conn, query, (user_id,))
            bookings = [{"booking_id": row[0], "origin": row[1], "destination": row[2], "departure_time": row[3], "price": row[4], "quantity": row[5]} for row in results]
            return jsonify({"bookings": bookings}), 200
        except Error as e:
            print(f"Error fetching bookings: {e}")
            return jsonify({"message": "无法获取订单信息"}), 500
    return jsonify({"message": "数据库连接失败"}), 500

# 创建订单
@app.route('/create_booking', methods=['POST'])
def create_booking():
    data = request.json
    user_id = data['user_id']

    conn = connect_to_database()
    if conn:
        try:
            query_flights = """
            SELECT bookings.flight_id, bookings.quantity, flights.price
            FROM bookings
            INNER JOIN flights ON bookings.flight_id = flights.flight_id
            WHERE bookings.user_id = %s;
            """
            bookings = fetch_query_results(conn, query_flights, (user_id,))

            if not bookings:
                return jsonify({"message": "没有预订的航班"}), 400

            total_amount = sum(row[1] * row[2] for row in bookings)

            query_order = "INSERT INTO orders (user_id, total_amount, status, order_date) VALUES (%s, %s, 'Pending', NOW());"
            execute_query(conn, query_order, (user_id, total_amount))

            query_order_id = "SELECT LAST_INSERT_ID();"
            order_id = fetch_query_results(conn, query_order_id)[0][0]

            for flight_id, quantity, price in bookings:
                query_order_item = "INSERT INTO order_items (order_id, flight_id, quantity, price) VALUES (%s, %s, %s, %s);"
                execute_query(conn, query_order_item, (order_id, flight_id, quantity, price))

            query_clear_bookings = "DELETE FROM bookings WHERE user_id = %s;"
            execute_query(conn, query_clear_bookings, (user_id,))

            return jsonify({"message": "订单已创建", "order_id": order_id, "total_amount": total_amount}), 201
        except Error as e:
            print(f"Error creating booking: {e}")
            return jsonify({"message": "订单创建失败"}), 500
    return jsonify({"message": "数据库连接失败"}), 500

# 支付订单
@app.route('/pay_booking', methods=['POST'])
# 支付订单
@app.route('/pay_booking', methods=['POST'])
def pay_booking():
    data = request.json
    booking_id = data.get('booking_id')

    if not booking_id:
        return jsonify({"message": "订单号不能为空"}), 400

    conn = connect_to_database()
    if conn:
        try:
            # 检查订单是否存在且状态为待支付（Pending）
            query_booking = "SELECT * FROM orders WHERE order_id = %s AND status = 'Pending';"
            result = fetch_query_results(conn, query_booking, (booking_id,))
            if not result:
                return jsonify({"message": "订单不存在或已支付"}), 400

            # 获取该订单包含的所有航班项
            query_order_items = "SELECT flight_id, quantity FROM order_items WHERE order_id = %s;"
            order_items = fetch_query_results(conn, query_order_items, (booking_id,))

            if not order_items:
                return jsonify({"message": "订单中没有航班项"}), 400

            # 尝试更新每个航班项的库存
            for flight_id, quantity in order_items:
                query_update_stock = "UPDATE flights SET seats = seats - %s WHERE flight_id = %s AND seats >= %s;"
                execute_query(conn, query_update_stock, (quantity, flight_id, quantity))

            # 检查是否有库存不足的情况
            query_check_stock = """
            SELECT COUNT(*) FROM flights f
            INNER JOIN order_items oi ON f.flight_id = oi.flight_id
            WHERE oi.order_id = %s AND f.seats < 0;
            """
            stock_issue = fetch_query_results(conn, query_check_stock, (booking_id,))
            if stock_issue[0][0] > 0:
                return jsonify({"message": "库存不足，无法支付订单"}), 400

            # 如果一切正常，则将订单状态更新为已支付（Paid）
            query_pay = "UPDATE orders SET status = 'Paid', order_date = NOW() WHERE order_id = %s;"
            execute_query(conn, query_pay, (booking_id,))

            return jsonify({"message": "订单支付成功"}), 200
        except Error as e:
            print(f"Error during payment: {e}")
            return jsonify({"message": "订单支付失败"}), 500
    return jsonify({"message": "数据库连接失败"}), 500

# 添加航班
@app.route('/add_flight', methods=['POST'])
def add_flight():
    data = request.json
    origin = data.get('origin')
    destination = data.get('destination')
    departure_time = data.get('departure_time')
    price = data.get('price')

    # 检查数据完整性
    if not all([origin, destination, departure_time, price]):
        return jsonify({"message": "缺少必要的航班信息"}), 400

    conn = connect_to_database()
    if conn:
        try:
            query = "INSERT INTO flights (origin, destination, departure_time, price, seats) VALUES (%s, %s, %s, %s, %s)"
            cursor = conn.cursor()
            cursor.execute(query, (origin, destination, departure_time, price, 100))  # 假设初始座位数为100
            conn.commit()
            return jsonify({"message": "航班添加成功"}), 201
        except Error as e:
            print(f"Error adding flight: {e}")
            return jsonify({"message": "数据库操作失败"}), 500
        finally:
            conn.close()
    else:
        return jsonify({"message": "数据库连接失败"}), 500

# 修改航班信息
@app.route('/update_flight', methods=['POST'])
def update_flight():
    data = request.json
    flight_id = data.get('flight_id')
    origin = data.get('origin')
    destination = data.get('destination')
    departure_time = data.get('departure_time')
    price = data.get('price')
    admin_id = data.get('admin_id')

    if not all([flight_id, origin, destination, departure_time, price, admin_id]):
        return jsonify({"message": "输入数据不完整"}), 400

    conn = connect_to_database()
    if conn:
        try:
            query_admin_check = "SELECT is_admin FROM users WHERE user_id = %s;"
            result = fetch_query_results(conn, query_admin_check, (admin_id,))
            if not result or not result[0][0]:
                return jsonify({"message": "没有权限操作"}), 403

            query_update_flight = """
            UPDATE flights
            SET origin = %s, destination = %s, departure_time = %s, price = %s
            WHERE flight_id = %s;
            """
            execute_query(conn, query_update_flight, (origin, destination, departure_time, price, flight_id))
            return jsonify({"message": "航班信息更新成功"}), 200
        except Error as e:
            print(f"Flight update failed: {e}")
            return jsonify({"message": "航班信息更新失败"}), 500
        finally:
            conn.close()
    return jsonify({"message": "数据库连接失败"}), 500

# 启动 Flask 应用
if __name__ == '__main__':
    app.run(debug=True)
