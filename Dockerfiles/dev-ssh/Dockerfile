FROM ubuntu:latest

LABEL maintainer="HeWeiTao <675428202@qq.com>"
ENV USER heweitao
ENV TZ=Asia/Shanghai

# add require files
ADD requirements.txt /home/requirements.txt
ADD run_socat.sh /home/run_socat.sh

RUN apt-get update && \
# install develop tools
apt-get install -y \
sudo curl jq openssh-server mysql-client iputils-ping git git-svn socat ssh subversion gnupg net-tools vim zip apt-utils autojump locales zsh wget fonts-powerline tree openssl language-pack-zh-hans \
# python3
python3 python3-all python3-all-dev python3-pip python3-setuptools && \
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
locale-gen zh_CN.UTF-8 && \
pip3 install -r /home/requirements.txt && \
wget --directory-prefix=/home https://cdn.mysql.com/Downloads/Connector-Python/mysql-connector-python-2.1.8.tar.gz && \
pip3 install /home/mysql-connector-python-2.1.8.tar.gz && \
pip3 install mycli && \
# node
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash - && \
apt-get install -y nodejs && \
# initialize user
adduser --quiet --disabled-password --shell /bin/zsh --home /home/${USER} --gecos "User" ${USER} && \
echo "${USER}:123456" | chpasswd &&  usermod -aG sudo ${USER} \
&& apt-get clean \
&& apt-get autoclean \
&& apt-get -y autoremove \
&& rm -rf /root/.npm/cache/* \
&& rm -rf /root/.composer/cache/* \
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# initialize develop environment
USER ${USER}
WORKDIR /home/${USER}
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)" "" --unattended
# install zsh plugins
RUN git clone https://github.com/zsh-users/zsh-syntax-highlighting.git && \
echo "source /home/${USER}/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" >> /home/${USER}/.zshrc && \
git clone https://github.com/zsh-users/zsh-autosuggestions && \
echo "source /home/${USER}/zsh-autosuggestions/zsh-autosuggestions.zsh" >> /home/${USER}/.zshrc && \
cp /usr/share/autojump/autojump.zsh ~ && \
chmod +x ~/autojump.zsh && \
echo "export DISABLE_UNTRACKED_FILES_DIRTY=\"true\"" >> /home/${USER}/.zshrc && \
echo "git config --global --add oh-my-zsh.hide-dirty 1" >> /home/${USER}/.zshrc && \
echo "source /home/${USER}/autojump.zsh" >> /home/${USER}/.zshrc && \
mkdir /home/${USER}/.ssh && \
touch /home/${USER}/.ssh/authorized_keys

# open sshd
USER root
RUN echo "root:123456" | chpasswd
RUN mkdir /var/run/sshd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
