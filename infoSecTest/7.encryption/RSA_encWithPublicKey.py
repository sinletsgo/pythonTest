from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP # PKCS1_OAEP 비대칭키 암호화 알고리즘


data = "I met aliens in UFO. Here is the map.".encode("utf-8")
file_out = open("encrypted_data.bin", "wb")

# 이렇게 대칭키, 비대칭키로 암호화하고 복호화 되는 과정을 이해하면
# 어떤 기업 프로젝트 때에, 보완관련해서 어떤 다 자동화 된 부분들이 있는데, 이해 하는데 편한거다.
# 직접 code를 구현할 기회 많지 않음. 컨셉만 이해
# 처음 비대칭키, 대칭키 이해 그림에서 아래 부분을 구현한 예제
# 비대칭키는 암호화, 복호화 시간이 많이 든다.
# http로 접속하는데, 계속 비대칭키 식으로 주고 받으면 탐색이 느리다. 서버도 못버텨줌
# 처음만 비대칭키로 커넥션 맺고, 다음부터는 대칭키로 통신하는 컨셉이다.


# 공개키 읽어온다
recipient_key = RSA.import_key(open("receiver.pem").read())
# 대칭키 AES 에 사용할 16바이트 랜덤 키값 생성
session_key = get_random_bytes(16)

# Encrypt the session key with the public RSA key
# 대칭키를 비대칭키(Public Key)로 암호화
cipher_rsa = PKCS1_OAEP.new(recipient_key)
# enc_session_key 이부분이 달라진거다. 즉 session_key(대칭키)으로 한번 더 암호화 한것!
enc_session_key = cipher_rsa.encrypt(session_key) # enc_session_key 비대칭키.

# 밑에 code인 비대칭키 암호화 와 비교해보기
# cipher_rsa = PKCS1_OAEP.new(recipient_key) # recipient_key .읽어온 공개키 넣고 암호화
# enc_msg = cipher_rsa.encrypt(data) # 암호화된 공개키에 data 넣고 암호화


# Encrypt the data with the AES session key
# data까지 넣어서 암호화 된걸 file에  write 한다
cipher_aes = AES.new(session_key, AES.MODE_EAX)
ciphertext, tag = cipher_aes.encrypt_and_digest(data)
[ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ] #대칭키 풀 때 쓰는 것들 넣어서 file에 넣으면 풀 수 있다

