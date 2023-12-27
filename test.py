#! /usr/bin/env python
import wx
import wx.media
import wx.lib.mixins.inspection

import vlc

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyUI(None)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True
    
    def setScore(self, role, score):
        wx.CallAfter(self.frame.updateScore, role, score)

    def endGame(self, isLeftWin):
        wx.CallAfter(self.frame.game_ending, isLeftWin)

# class MyPanel(wx.Panel):
class MyUI(wx.Frame):
    STATUS = {"start": 0, "end": 1}
    ROLE = {"left": "defender", "right": "terrorist"}

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Test", pos=(-1, -1), size=(500, 500))

        self.full = False
        self.right_score = 0
        self.left_score = 0
        self.vlcinstance = vlc.Instance()
        self.player = self.vlcinstance.media_player_new()


        # self.mp = wx.media.MediaCtrl(self, size=wx.Size(512,384), szBackend=wx.media.MEDIABACKEND_DIRECTSHOW)
        # self.mp.Load("./defend1.mp4")
        # self.mp.Bind(wx.media.EVT_MEDIA_LOADED,self.OnPlay)   
        self.main_screen_panel = wx.Panel(self, -1)

        score_font = wx.Font(120, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD)
        button_font = wx.Font(40, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD)

        self.pnlVideo = wx.Panel(self.main_screen_panel, style=wx.ID_ANY)
        
        self.left_score_text = wx.StaticText(self.main_screen_panel, label="0", size=(-1, -1))
        self.right_score_text = wx.StaticText(self.main_screen_panel, label="0", size=(-1, -1))
        self.left_score_text.SetFont(score_font)
        self.right_score_text.SetFont(score_font)
        white = (255, 255, 255)
        black = (0, 0, 0)
        self.left_score_text.SetForegroundColour(white)
        self.right_score_text.SetForegroundColour(white)

        self._do_layout()


        # self.button = wx.Button(self, label="START")
        # self.button.SetFont(button_font)

        # self.Bind(wx.EVT_BUTTON, self.OnClick, self.button)
        # self.media_control.Bind(wx.media.EVT_MEDIA_LOADED, self.afterLoad)
        # self.media_control.Bind(wx.media.EVT_MEDIA_FINISHED, self.init_game)

        self.pnlVideo.SetBackgroundColour(wx.WHITE)
        self.player.set_xwindow(self.pnlVideo.GetHandle())

        self.init_game()
        self.playMedia("./videos/defend2.mp4")

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
    
    def _do_layout(self):
        # self.toggleFullScreen()
        self.SetBackgroundColour('black')
        # self.p = wx.Panel(self, -1)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.AddSpacer(80)
        main_sizer.Add(top_sizer, 0, wx.EXPAND , border=10)
        main_sizer.Add(bottom_sizer, 0, wx.EXPAND, border=10)

        # sizer_2.Add(self.left_score_text, 0, flag=wx.ALIGN_TOP, border=2)
        # sizer_2.Add(self.right_score_text, 0, flag=wx.ALIGN_BOTTOM, border=2)
        top_sizer.AddStretchSpacer(1)
        top_sizer.Add(self.left_score_text, 0, wx.Center | wx.ALL, 10)
        top_sizer.AddStretchSpacer(2)
        top_sizer.Add(self.right_score_text, 0, wx.Center | wx.ALL, 10)
        top_sizer.AddStretchSpacer(1)

        bottom_sizer.Add(self.pnlVideo, 1, wx.EXPAND, 0)

        self.main_screen_panel.SetSizer(main_sizer)
        self.Centre()
        self.Layout()
        

    def updateUI(self):
        self.right_score_text.SetLabel(str(self.right_score))
        self.left_score_text.SetLabel(str(self.left_score))
    
    def init_game(self, e=None):
        self.pnlVideo.Hide()
        self.updateUI()

    # winner is defend or terror
    # if game is over => True
    # yet over => False
    def updateScore(self, winner, score):
        if MyUI.ROLE["left"] == winner:
            self.left_score = score
        elif MyUI.ROLE["right"] == winner:
            self.right_score = score
        
        self.updateUI()
    
    def game_ending(self, isLeftWin):

        if isLeftWin:
            to_play_video = f"./videos/defend2.mp4"
        elif not isLeftWin:
            to_play_video = f"./videos/terror2.mp4"

        self.playMedia(to_play_video)

    def playMedia(self, filepath):

        self.media = self.vlcinstance.media_new(filepath)
        self.player.set_media(self.media)

        if self.player.get_media():
            self.pnlVideo.Show()
            self.player.play()
            print("Media Playing")

        else:
            print("Media Load Failed")

        # self.media_control.Play()
    
    def OnTimer(self, event):
        """Update the position slider"""

        if self.player.get_state() != vlc.State.Playing:
            self.pnlVideo.Hide()
        else:
            self.pnlVideo.Show()

    def toggleFullScreen(self):
        self.full = not self.full
        self.ShowFullScreen(self.full, wx.FULLSCREEN_ALL)
    
    def quit(self, event):
        # self.Destroy()
        pass

if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()