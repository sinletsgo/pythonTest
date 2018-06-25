from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import time

# 대칭키 2번째 예시
# 아까랑 똑같은데, 매개체를 file로 주고 받았다는것! file형태로 , 네트웍으로 든 전달할  수 있으니,
# key는 못 담는다, 담으면 누구나 알 수있으니까, 그냥 받았다고 가정함.
# 대칭키는 이렇게 KEY만 알면 푸는거다!

key = get_random_bytes(16) # random byte 생성!
print(key)
cipher = AES.new(key, AES.MODE_EAX)
data = b"This is a test." # FILE을 읽어서 DATA로 실어서 보낼 수도 있고,
ciphertext, tag = cipher.encrypt_and_digest(data)

file_out = open("encrypted.bin", "wb") # write 바이너리 mode로 쓰겠다!
[file_out.write(x) for x in (cipher.nonce, tag, ciphertext)] # cipher.nonce 16byte, tag 16byte

file_out.close()


# 여기서 부터 복호화
time.sleep(1) # 1초 쉬고 읽으라~

file_in = open("encrypted.bin", "rb") # file에 있는걸 읽어와서 복호화!
nonce, tag, ciphertext = (file_in.read(x) for x in (16, 16, -1)) #file 16byte로 읽고,  -1 마지막 index

# print(nonce)
# print(tag)
# print(ciphertext)
# let's assume that the key is somehow available again
cipher = AES.new(key, AES.MODE_EAX, nonce)
data = cipher.decrypt_and_verify(ciphertext, tag) # 풀었을때, This is a test. 나오면 되는것!
print(data)

file_in.close()