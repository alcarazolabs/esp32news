import certifi

user = "root"
password = "123456789"
host = "192.168.18.27"
database = "esp32news"

# Certificados rutas para la conexión ssl a planetScale
"""
ssl_cer_path_linux = "/etc/ssl/certs/ca-certificates.crt"
ssl_cer_path_windows = "C:\\Users\\freddydev\\anaconda3\\envs\\freddydev\\lib\\site-packages\\certifi\\cacert.pem"
"""
ssl_cer_path = certifi.where()

DATABASE_CONNECTION_URI = 'mysql+pymysql://'+user+':'+password+'@'+host+'/'+database+'?ssl_ca='+ssl_cer_path

print(DATABASE_CONNECTION_URI)