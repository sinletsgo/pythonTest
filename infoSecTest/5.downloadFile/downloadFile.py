import shutil
import requests
import wget
import PIL
from PIL import Image

url = 'https://cdn.pixabay.com/photo/2018/01/20/14/26/panorama-3094696_960_720.jpg'

# # Method 1
response = requests.get(url, stream=True)
if response.status_code == 200:
    with open('myImage1.jpg', 'wb') as out_file: #wb 파일모드, w 쓰고, b 이진모드, 즉 쓰기 및 바이너리..
        shutil.copyfileobj(response.raw, out_file)

# # Method 2 제일간단
filename = wget.download(url,out='./') #현재 디렉토리에 다운로드하겠다
print(filename)


# 잘안쓰이는 3번째 방법
# # Method 3
r = requests.get('https://cdn.pixabay.com/photo/2018/01/20/14/26/panorama-3094696_960_720.jpg', stream=True)
r.raise_for_status() # 아마 위 200코드. 정상인지 본뒤
r.raw.decode_content = True  # Required to decompress gzip/deflate compressed responses.
with PIL.Image.open(r.raw) as img:
    img.show() #바로 윈도우창으로 이미지를 띄워준다!
r.close()  # Safety when stream=True ensure the connection is released.