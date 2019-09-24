FROM ubuntu:latest

LABEL maintainer="HeWeiTao <675428202@qq.com>"
ENV TZ=Asia/Shanghai

WORKDIR /root

# add require files
ADD requirements.txt ~/requirements.txt
ADD run_socat.sh ~/run_socat.sh

RUN apt-get update && \
# install develop tools
apt-get install -y \
sudo curl jq openssh-server mysql-client iputils-ping git git-svn socat ssh subversion gnupg net-tools vim zip apt-utils autojump locales zsh wget fonts-powerline tree openssl language-pack-zh-hans \
# python3
python3 python3-all python3-all-dev python3-pip python3-setuptools && \
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
locale-gen zh_CN.UTF-8 && \
pip3 install -r ~/requirements.txt && \
wget --directory-prefix=~ https://cdn.mysql.com/Downloads/Connector-Python/mysql-connector-python-2.1.8.tar.gz && \
pip3 install ~/mysql-connector-python-2.1.8.tar.gz && \
pip3 install mycli && \
# node
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash - && \
apt-get install -y nodejs \
&& apt-get clean \
&& apt-get autoclean \
&& apt-get -y autoremove \
&& rm -rf /root/.npm/cache/* \
&& rm -rf /root/.composer/cache/* \
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# initialize develop environment
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)" "" --unattended
# install zsh plugins
RUN git clone https://github.com/zsh-users/zsh-syntax-highlighting.git && \
echo "source /root/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" >> ~/.zshrc && \
git clone https://github.com/zsh-users/zsh-autosuggestions && \
echo "source /root/zsh-autosuggestions/zsh-autosuggestions.zsh" >> ~/.zshrc && \
cp /usr/share/autojump/autojump.zsh ~ && \
chmod +x ~/autojump.zsh && \
echo "export DISABLE_UNTRACKED_FILES_DIRTY=\"true\"" >> ~/.zshrc && \
echo "git config --global --add oh-my-zsh.hide-dirty 1" >> ~/.zshrc && \
echo "source /root/autojump.zsh" >> ~/.zshrc
