数据库课设——简单的实现航班订票管理系统

# the first step

   创建数据库，3306端口，host=local，用户名密码自己记住后面有用\n
   
   CREATE TABLE users (
   
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    
    username VARCHAR(255) NOT NULL UNIQUE,
    
    password VARCHAR(255) NOT NULL,
    
    email VARCHAR(255) NOT NULL UNIQUE,
    
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE flights (
    
    flight_id INT AUTO_INCREMENT PRIMARY KEY,
    
    origin VARCHAR(255) NOT NULL,
    
    destination VARCHAR(255) NOT NULL,
    
    departure_time DATETIME NOT NULL,
    
    price DECIMAL(10, 2) NOT NULL,
    
    seats INT NOT NULL
);

CREATE TABLE bookings (
    
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    
    user_id INT NOT NULL,
   
    flight_id INT NOT NULL,
    
    quantity INT NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
   
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
);

CREATE TABLE orders (
    
    order_id INT AUTO_INCREMENT PRIMARY KEY,
   
    user_id INT NOT NULL,
    
    total_amount DECIMAL(10, 2) NOT NULL,
   
    status VARCHAR(255) NOT NULL,
    
    order_date DATETIME NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE order_items (
   
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    
    order_id INT NOT NULL,
    
    flight_id INT NOT NULL,
   
    quantity INT NOT NULL,
   
    price DECIMAL(10, 2) NOT NULL,
   
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
);



   

# the second step
   
   打开1.py
   
   运行python 1.py
   
   如果有没安装的包，根据系统提示自行pip安装，注意安装对应版本

   需要注意的是，1.py中以下代码的内容都要改成自己的内容

   # 数据库连接配置

host = "localhost"

user = "root"

password = "839661164"（本人qq号）

dbname = "test"

app = Flask(__name__)

CORS(app

# the third step

运行3.html，你会得到自己的管理系统

ps：

123.jpg用来更换网页背景，要跟html文件放在同一文件夹下，并且在html文件中做出相应的修改
