import base64
import hmac
import os
import hashlib

def getAbsolutePath(fileName):
    dir_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir_path,fileName)
    return path


# md5加密（用户密码）
def encryptMd5(message):
    hl = hashlib.md5()
    hl.update(message.encode(encoding='utf-8'))
    return hl.hexdigest()

# 使用HmacSHA256算法哈希(哈希秘钥为secret)，再对hash值使用Base64加密得到最终的签名值sign
def get_sign_HmacSHA256(message, secret):
    secrets = secret.encode('utf-8')
    messageNew = message.encode('utf-8')
    sign = base64.b64encode(hmac.new(secrets, messageNew, digestmod=hashlib.sha256).digest())
    sign = str(sign, 'utf-8')
    print(sign)
    return sign
