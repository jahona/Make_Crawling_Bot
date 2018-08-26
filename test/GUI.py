from PyQt4.QtGui import *
import MyWindow
import sys
import pickle

class XWindow(QMainWindow, MyWindow.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        # 초기 샘플데이타
        self.initData()

        # 검색 버튼 이벤트 핸들링
        self.btnSearch.clicked.connect(self.search)

        # 메인윈도우 보이기
        self.show()

    def search(self):
        keyword = self.lineEdit.text()
        resultData = self.sampleData[keyword]
        self.tableWidget.setRowCount(len(resultData))
        row = 0
        for item in resultData:
            self.tableWidget.setItem(row, 0, QTableWidgetItem(keyword))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(item))
            row += 1

    def initData(self):
        self.sampleData = {
            'Python': ['Fluent Python', 'Python Programming', 'Learning Python'],
            'go' : 'The Go Programming Language',
            'C#' : ['Inside C#', 'C# In Depth'],
            'C' : 'The C Programming Language'
        }

    def saveData(self):
        with open("test.data","wb") as f:
            pickle.dump(self.sampleData, f)
        QMessageBox.information(self, "저장", "데이타 저장됨")

    def openData(self):
        with open("test.data","rb") as f:
            self.sampleData = pickle.load(f)
        QMessageBox.information(self, "오픈", "데이타 로딩됨")

app = QApplication(sys.argv)
xwin = XWindow()
app.exec_()
