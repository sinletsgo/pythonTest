from Crypto.PublicKey import RSA # 비대칭키 알고리즘 RSA
from Crypto.Cipher import AES, PKCS1_OAEP

file_in = open("encrypted_data.bin", "rb")

# 비대칭키 읽어온다.
private_key = RSA.import_key(open("private.pem").read())

enc_msg = file_in.read() #암호환된 데이터 읽어온다

# 비밀키로 복호화한다.
cipher_rsa = PKCS1_OAEP.new(private_key) # 읽어온 private_key로 복호화
dec_msg = cipher_rsa.decrypt(enc_msg) # 불러온 암호화된 데이터를 private_key로로 복호화!

print(dec_msg.decode("utf-8")) #decrypt 되면 dec_msg가 평문이 나온다. 평문 출력!


