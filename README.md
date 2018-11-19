# Make_Crawling_Bot

# Introduce

Crawl documents based on the search terms they are looking for, then crawl them out using the text rank algorithm and document similarity

# Python Version

We use python3.6.2

# Install

- virtualenv


  Since MAC OS has Python2 installed by default throughout the system, pip can be easily installed with the following command.

  ```
  $ sudo easy_install pip
  ```

  If you do not want to install it system-wide with sudo, you can install Python in the user area using HomeBrew.

  ```
  $ brew install python
  ```

  Virtualenv and VirtualenvWrapper can be installed via pip.

  ```
  # Python2
  $ pip install virtualenv virtualenvwrapper

  # Python3
  $ pip3 install virtualenv virtualenvwrapper
  ```

  Virtualenv works by default with the following command.

  ```
  $ virtualenv --python=파이썬버전 가상환경이름
  ```
  
  You can run virtualenv folling this on:
  
  ```
  $ . myenv/bin/activate
  ```
  
- modules

  ```
  $ pip3 install bs4
  $ pip3 install requests

  # article parsing
  pip3 install newspaper3k

  # for text rank algo
  pip3 install konlpy
  pip install -U scikit-learn

  # for GUI
  pip install PyQt5
  ```
  
  
