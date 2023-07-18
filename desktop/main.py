# driver.py

import sys
import wx
from pyke import knowledge_engine, krb_traceback
from pyke import ask_wx

app = []
app = wx.App(None)
engine = knowledge_engine.engine(__file__)
engine.ask_module = ask_wx


# def ca_test_questions():
#     while True:
#         engine.reset()
#         ask_wx.answers=""
#         try:
#             abox = wx.MessageDialog(None,
#                                    "Начать работу",
#                                    "Начало работы", wx.OK)
#             abox.ShowModal()
#             engine.activate('ca_rules_questions')
#             vals, plans = engine.prove_1_goal(
#                 'ca_rules_questions.what_therapy($therapy)')
#             dlg = wx.MessageDialog(None,
#                                    "Выбирайте терапию: %s" % (vals['therapy']),
#                                    "Результат", wx.OK | wx.HELP)
#             dlg.SetHelpLabel("Показать путь решения")
#             status = dlg.ShowModal()
#             if status==wx.ID_HELP:
#                 name = wx.MessageDialog(None,
#                                    "Пройденные шаги:\n\n%s\n\nРезультат: %s" % (ask_wx.answers,(vals['therapy'])),
#                                    "Результат", wx.OK)
#                 name.ShowModal()
#             control = ask_wx.ask_yn("Начать с начала?")
#             if not control:
#                 exit()
#         except Exception as ex:
#             print(ex)
#             # krb_traceback.print_exc()
#             dlg = wx.MessageDialog(None, "Решения нет. Попробуйте заново:",
#                                    "Результат", wx.OK)
#             dlg.ShowModal()
class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(600, 200))

        abox = wx.Button(self, wx.ID_ANY, label="Начать работу")
        self.Bind(wx.EVT_BUTTON, self.ca_test_questions, abox)
    def ca_test_questions(self, event):
        while True:
            engine.reset()
            ask_wx.answers = ""
            try:
                engine.activate('ca_rules_questions')
                vals, plans = engine.prove_1_goal(
                    'ca_rules_questions.what_therapy($therapy)')
                dlg = wx.MessageDialog(None,
                                    "Выбирайте терапию: %s" % (vals['therapy']),
                                    "Результат", wx.OK | wx.HELP)
                dlg.SetHelpLabel("Показать путь решения")
                status = dlg.ShowModal()
                if status == wx.ID_HELP:
                    name = wx.MessageDialog(None,
                                            "Пройденные шаги:\n\n%s\n\nРезультат: %s" % (ask_wx.answers, (vals['therapy'])),
                                            "Результат", wx.OK)
                    name.ShowModal()
                control = ask_wx.ask_yn("Начать сначала?")
                if not control:
                    exit()
            except Exception as ex:
                print(ex)
                dlg = wx.MessageDialog(None, "Решения нет. Попробуйте заново:",
                                    "Результат", wx.OK | wx.CANCEL)
                status = dlg.ShowModal()
                if status == wx.ID_CANCEL:
                    exit()

frame=MyFrame(None, 'Фибрилляция предсердий')
frame.Show()
app.MainLoop()

# ca_test_questions()
