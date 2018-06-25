from Crypto.Cipher import AES
# 대칭키 알고리즘 AES, 3DES


key = b'Sixteen byte key' #16btye key 로!

# cipher = 암호
cipher = AES.new(key, AES.MODE_EAX) # 암호화위해 준비된 값, key를 갖고 AES 방식으로 암호화

print(cipher)

nonce = cipher.nonce # key가 맞는지 검증해주는것
print(nonce)

data = b"222" #  이 data 암호화하겠다!
ciphertext, tag = cipher.encrypt_and_digest(data) # aes 대칭키 암호화 된것으로 data 넣고 여기서 제대로 암호화!
# tag는 ciphertext를 검증해주는것

print(ciphertext)
print(tag)


# let's assume that the key is somehow available again
# 여기서 복호화
# Key를 모르면 못 푼다. 여기선 이미 key가 위에 있기에, 풀리는 것
# 그리고 nonce, ciphertext, tag 넣어서 복호화
# 결국은 2가지 key와 ciphertext로 푸는것!

cipher = AES.new(key, AES.MODE_EAX, nonce) # 암호화와 반대로 nonce, key로 암호를 복호화 하고,
data = cipher.decrypt_and_verify(ciphertext, tag) # 또 반대로 ciphertext, tag 넣고 data를 복호화 한다!
print(data) # 복호화된 값 출력


