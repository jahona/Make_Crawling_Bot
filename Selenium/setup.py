import sys
from cx_Freeze import setup, Executable

setup(
	name="Demo",
	version="1.0",
	description = "테스트 파일",
	author = "kkb",
	executables = [Executable("Main.py")]
)
