#-*- coding: UTF-8 -*-
import random
import wx
import urllib2
import urllib
import re

ChinaStockIndexList = [
    "000001", # sh000001
    "399001", # sz399001
    "000300", # sh000300
    "399005", # sz399005
    "399006", # sz399006
    "000003", # sh000003
]

########################################################################
class NotePage(wx.Panel):
    def __init__(self, parent, stock_code,imgType):
        wx.Panel.__init__(self, parent)
        self.size = self.GetMaxWidth()
        self.PicShow=wx.StaticBitmap(self, -1, wx.NullBitmap, wx.DefaultPosition,wx.DefaultSize, 0 )
        self.DrawLines(stock_code,imgType)

    def DrawLines(self,stock_code,imgType):
        code = stock_code.split(" ")
        stockId = code[0]
        exchange = "sz" if (int(stockId) // 100000 == 3) else "sh"
        img_path = "http://image.sinajs.cn/newchart/%s/n/%s%s.gif" % (imgType, exchange, stockId)
        img_load = urllib2.urlopen(img_path)
        localFile = open('desktop.gif', 'wb')
        localFile.write(img_load.read())
        localFile.close()

        img = wx.Image('desktop.gif',wx.BITMAP_TYPE_ANY)
        self.PicShow.SetBitmap(wx.BitmapFromImage(img))

########################################################################
class DemoFrame(wx.Frame):
    def __init__(self,parent):
        """Constructor"""
        self.imgtype = ['min', 'daily', 'weekly', 'monthly']

        wx.Frame.__init__(self, None, wx.ID_ANY,"Chinese Stock Market",size=(700,450))

        self.m_menubar = wx.MenuBar( 0 )
        self.m_menu1 = wx.Menu()
        self.m_menubar.Append( self.m_menu1, u"File" )
        
        self.m_menu2 = wx.Menu()
        self.m_menubar.Append( self.m_menu2, u"Check" )
        
        self.m_menu3 = wx.Menu()
        self.m_menubar.Append( self.m_menu3, u"Help" )
        
        self.SetMenuBar( self.m_menubar )
        
        panel = wx.Panel(self)
        self.tab_num = 3

        self.notebook = wx.Notebook(panel)
        self.stock_code = "000001 "
        self.tabOne = NotePage(self.notebook,self.stock_code,"min")
        self.notebook.AddPage(self.tabOne, "minutely")
        self.tabTwo = NotePage(self.notebook,self.stock_code,"daily")
        self.notebook.AddPage(self.tabTwo, "daily")
        self.tabThree = NotePage(self.notebook,self.stock_code,"weekly")
        self.notebook.AddPage(self.tabThree, "weekly")
        self.tabFour = NotePage(self.notebook,self.stock_code,"monthly")
        self.notebook.AddPage(self.tabFour, "monthly")

        #zone_list = ['000001', '000300']
        file_object = open('./stock.history')
        stocklist=[]
        try:
            zone_list = file_object.readlines( )
            for line in zone_list:
                stocklist.append(line.strip())
        finally:
            file_object.close()

        self.stock_zones = wx.ListBox(panel, 26, wx.DefaultPosition,wx.Size(120,400), stocklist, wx.LB_SINGLE)
        self.stock_zones.SetSelection(0)

        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_button_check = wx.Button( self, wx.ID_ANY, u"Load stock", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button_add = wx.Button( self, wx.ID_ANY, u"Add Stock", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button_update_file = wx.Button( self, wx.ID_ANY, u"Update file", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrl_stock_code = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )

        bSizer1.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
        bSizer1.Add(self.stock_zones, 0, wx.ALL|wx.EXPAND|wx.SHAPED, 1)
        panel.SetSizer(bSizer1)

        bSizer2 = wx.BoxSizer( wx.VERTICAL )

        bSizer2_1 = wx.BoxSizer( wx.HORIZONTAL )
        self.getChinaStockIndexInfo("000001 ")
        self.m_text_stockEnd = wx.StaticText( self, wx.ID_ANY, u"Current Price: " + self.stockEnd + u"   ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_text_stockZD = wx.StaticText( self, wx.ID_ANY, u"Div & Yield: " + self.stockZD + u"("+self.stockFD+u"%)"+ u"   ", wx.DefaultPosition, wx.DefaultSize, 0 )
        label = wx.StaticText( self, wx.ID_ANY, u"Enter the stock: ", wx.DefaultPosition, wx.DefaultSize, 0 )

        bSizer2_1.Add( self.m_text_stockEnd,1,wx.CENTER,5)
        bSizer2_1.Add( self.m_text_stockZD,1,wx.CENTER,5)

        bSizer2_2 = wx.BoxSizer( wx.HORIZONTAL )
        bSizer2_2.Add( label,1,wx.CENTER,1)
        bSizer2_2.Add( self.m_textCtrl_stock_code,1,wx.CENTER,1)
        bSizer2_2.Add( self.m_button_check,1,wx.CENTER,1)
        bSizer2_2.Add( self.m_button_add,1,wx.CENTER,1)
        bSizer2_2.Add( self.m_button_update_file,1,wx.CENTER,1)

        bSizer2.Add( bSizer2_1)
        bSizer2.Add( bSizer2_2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add( bSizer2)

        self.m_button_check.Bind(wx.EVT_BUTTON, self.OnCheckStock)
        self.m_button_add.Bind(wx.EVT_BUTTON, self.OnAddStock)
        self.stock_zones.Bind(wx.EVT_LISTBOX,self.OnSelectItem)
        self.m_button_update_file.Bind(wx.EVT_BUTTON,self.OnUpdateFile)

        self.SetSizer( sizer )
        self.Layout()

        self.Show()

    #----------------------------------------------------------------------
    def getChinaStockIndexInfo(self,stockCode):
        try:
            exchange = "sz" if (int(stockCode) // 100000 == 3) else "sh"
            dataUrl = "http://hq.sinajs.cn/list=s_" + exchange + stockCode
            stdout = urllib.urlopen(dataUrl)
            stdoutInfo = stdout.read().decode('gb2312')
            tempData = re.search('''(")(.+)(")''', stdoutInfo).group(2)
            stockInfo = tempData.split(",")
            #stockCode = stockCode,
            self.stockName   = stockInfo[0]
            self.stockEnd    = stockInfo[1]
            self.stockZD     = stockInfo[2]
            self.stockLastEnd= str(float(self.stockEnd) - float(self.stockZD))
            self.stockFD     = stockInfo[3]
            self.stockZS     = stockInfo[4]
            self.stockZS_W   = str(int(self.stockZS) / 100)
            self.stockJE     = stockInfo[5]
            self.stockJE_Y   = str(int(self.stockJE) / 10000)

        except Exception as e:
            print(">>>>>> Exception: " + str(e))
        finally:
            None

    def getChinaStockIndividualInfo(self,stockCode):
        try:
            exchange = "sh" if (int(stockCode) // 100000 == 6) else "sz"
            dataUrl = "http://hq.sinajs.cn/list=" + exchange + stockCode
            stdout = urllib.urlopen(dataUrl)
            stdoutInfo = stdout.read().decode('gb2312')
            tempData = re.search('''(")(.+)(")''', stdoutInfo).group(2)
            stockInfo = tempData.split(",")
            #stockCode = stockCode,
            self.stockName   = stockInfo[0]
            self.stockStart  = stockInfo[1]
            self.stockLastEnd= stockInfo[2]
            self.stockCur    = stockInfo[3]
            self.stockMax    = stockInfo[4]
            self.stockMin    = stockInfo[5]
            self.stockUp     = round(float(self.stockCur) - float(self.stockLastEnd), 2)
            self.stockRange  = round(float(self.stockUp) / float(self.stockLastEnd), 4) * 100
            self.stockVolume = round(float(stockInfo[8]) / (100 * 10000), 2)
            self.stockMoney  = round(float(stockInfo[9]) / (100000000), 2)
            self.stockTime   = stockInfo[31]

        except Exception as e:
            print(">>>>>> Exception: " + str(e))
        finally:
            None
    #----------------------------------------------------------------------

    def OnCheckStock(self, event):
        """"""
        self.stock_code = self.m_textCtrl_stock_code.GetValue()
        if self.stock_code in ChinaStockIndexList:
            self.getChinaStockIndexInfo(self.stock_code)
            self.m_text_stockEnd.SetLabel(u"Current Price: " + self.stockEnd + u"   ")
            self.m_text_stockZD.SetLabel(u"Div & Yield: " + self.stockZD + u"("+self.stockFD+u"%)"+ u"   ")
        else:
            self.getChinaStockIndividualInfo(self.stock_code)
            self.m_text_stockEnd.SetLabel(u"Current Price: " + self.stockStart + u"   ")
            self.m_text_stockZD.SetLabel(u"Div & Yield: " + self.stockZD + u"("+self.stockFD+u"%)"+ u"   " )

        self.tabOne.DrawLines(self.stock_code,"min")
        self.tabTwo.DrawLines(self.stock_code,"daily")
        self.tabThree.DrawLines(self.stock_code,"weekly")
        self.tabFour.DrawLines(self.stock_code,"monthly")

    def OnAddStock(self, event):
        self.stock_zones.Append(self.stock_code.strip() + " " +self.stockName)

    def OnSelectItem(self,event):
        sel = self.stock_zones.GetSelection()
        code = self.stock_zones.GetString(sel).split(" ")
        self.stock_code = code[0].decode("utf-8").encode("ascii")
        if self.stock_code in ChinaStockIndexList:
            self.getChinaStockIndexInfo(self.stock_code)
            self.m_text_stockEnd.SetLabel(u"Current Price: " + self.stockEnd + u"   ")
            self.m_text_stockZD.SetLabel(u"Div & Yield: " + self.stockZD + u"("+self.stockFD+u"%)"+ u"   ")
        else:
            self.getChinaStockIndividualInfo(self.stock_code)
            self.m_text_stockEnd.SetLabel(u"Current Price: " + self.stockStart + u"   ")
            self.m_text_stockZD.SetLabel(u"Div & Yield: %.2f(%.2f%s)" %(self.stockUp,self.stockRange,"%"))

        self.tabOne.DrawLines(self.stock_code,"min")
        self.tabTwo.DrawLines(self.stock_code,"daily")
        self.tabThree.DrawLines(self.stock_code,"weekly")
        self.tabFour.DrawLines(self.stock_code,"monthly")

    def OnUpdateFile(self,event):
        file_object = open('./stock.history','w')
        #stocklist=[]
        count = self.stock_zones.GetCount()
        for i in range(0,count):
            line = self.stock_zones.GetString(i) + "\n"
            file_object.write(line.encode("utf-8"))
        file_object.close()

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = DemoFrame(None)
    app.MainLoop()
