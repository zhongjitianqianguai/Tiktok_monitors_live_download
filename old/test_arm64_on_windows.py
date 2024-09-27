import fake_useragent

# 首先实例化fake_useragent对象
ua = fake_useragent.UserAgent()
# 打印请求头
print(ua.random)