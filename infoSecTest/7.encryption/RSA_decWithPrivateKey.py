from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

file_in = open("encrypted_data.bin", "rb")

# 비대칭키 읽어온다.
private_key = RSA.import_key(open("private.pem").read())

# 공개키로 암호화된 대칭키, 공개키 정보를 읽는다.
enc_session_key, nonce, tag, ciphertext = [ file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

# Decrypt the session key with the private RSA key
# 비밀키로 복호화한다.
cipher_rsa = PKCS1_OAEP.new(private_key)

# 처음에만 비대칭키로 암호화 했고, 서버에서 주고 받을때는 대칭키인 session_key로 복호화 하면서 주고 받는 컨셉.
session_key = cipher_rsa.decrypt(enc_session_key) # enc_session_key로 복호화한 키 session_key

# Decrypt the data with the AES session key

cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce) # nonce
data = cipher_aes.decrypt_and_verify(ciphertext, tag) # ciphertext, tag 넣어서 복호화
print(data.decode("utf-8"))


# 아래는 비대칭키 예시로, 개인키로 복호화하는 과정 code. 이거와 비교하면 쉬워보임.
# 비밀키로 복호화한다.
# cipher_rsa = PKCS1_OAEP.new(private_key) # 읽어온 private_key로 복호화
# dec_msg = cipher_rsa.decrypt(enc_msg)
