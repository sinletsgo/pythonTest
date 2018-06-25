from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

data = "I met aliens in UFO. Here is the map.".encode("utf-8") # 이 data를 암호화 하겠다!
file_out = open("encrypted_data.bin", "wb")

# 공개키 읽어온다( RSA_keyGen에서 생성한 것)
recipient_key = RSA.import_key(open("receiver.pem").read())

# 메세지를 공개키로 암호화
cipher_rsa = PKCS1_OAEP.new(recipient_key) # recipient_key .읽어온 공개키 넣고 암호화
enc_msg = cipher_rsa.encrypt(data) # 암호화된 공개키에 data 넣고 암호화

file_out.write(enc_msg) # 메세지를 암호화된 공개키에 넣은걸 파일에 씀

