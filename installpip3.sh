# pip3 설치
sudo apt-get update
sudo apt-get install -y python3-pip

# 버전 확인
pip3 --version

# pip3 대신 pip 라고 입력하기 위한 명령어
# 아래 명령어를 입력하면 pip 라고 쳐도 pip3를 작동시킬 수 있습니다.
sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
