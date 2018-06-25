from Crypto.PublicKey import RSA

key = RSA.generate(2048) # RSA 기반 키 생성
private_key = key.export_key() # 개인키 즉 비밀키 생성, 이걸로 복호화
file_out = open("private.pem", "wb") # wirte mode 로 file을 열어서
file_out.write(private_key) # open 한 file에 private_key를 write!

public_key = key.publickey().export_key() # 공개키 생성, 이걸로 암호화
file_out = open("receiver.pem", "wb")
file_out.write(public_key)

