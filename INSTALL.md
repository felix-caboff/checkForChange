# Installation Requirements

This setup is specifically tailored for **Debian 12**. There are some known dependency quirks, but the following commands *should* work as expected.

---

## PyEnv Dependencies

Install system packages required to build Python versions via PyEnv:

```bash
sudo apt install -y \
  build-essential \
  libbz2-dev \
  libncursesw5-dev \
  libreadline-dev \
  libsqlite3-dev \
  libssl-dev \
  libffi-dev \
  liblzma-dev \
  zlib1g-dev \
  tk-dev \
  curl \
  xz-utils \
  wget \
  libdbus-1-dev
```

## Install PyEnv
You can install PyEnv using the official installation script:

`curl -fsSL https://pyenv.run | bash`

Add the following to your ~/.bashrc to initialise PyEnv correctly:

```
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
```

Then reload your shell or run:

`source ~/.bashrc`

## Install Python

Use PyEnv to install the required Python version:

`pyenv install 3.11`

(Make sure you're in the script directory if setting up a local environment.)

## Install PipEnv

Install pipenv using your system package manager:

`sudo apt install pipenv`

## Install Python Libraries

Once in your project directory, install dependencies from requirements.txt using PipEnv:

`pipenv install -r requirements.txt`

## Install Systemd service

```
# EDIT the service file so that the paths reflect where you put it, for example, in /opt
sudo cp checkForChange.service /etc/systemd/system/checkForChange.service
sudo systemctl daemon-reload
sudo systemctl enable checkForChange.service
sudo systemctl start checkForChange.service
```
