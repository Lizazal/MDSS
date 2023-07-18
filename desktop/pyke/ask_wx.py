r'''
    A "match" here is one of:
        - an instance of qa_helpers.regexp
            - msg (for error message)
            - prompt (without the [])
            - match(str) returns converted value (None if no match)
        - an instance of qa_helpers.qmap
            - test (a match)
            - value (value to use)
        - an instance of slice (step must be None)
        - a tuple of matches (implied "or")
        - some other python value (which stands for itself)

    A "review" here is a tuple of (match, review_string)

    "Alternatives" here is a tuple of (tag, label_string)
'''

import sys
if __name__ != "__main__" \
   and ('__main__' not in sys.modules
        or 'doctest' not in sys.modules['__main__'].__file__):
    # So we don't screw up doctest runs on boxes that don't have wxPython
    # installed...
    import wx
import itertools
from pyke import qa_helpers

def review_ans(dlg, ans, review=None):
    if review:

        def matches2(ans, test):
            try:
                qa_helpers.match(ans, test)
                return True
            except ValueError:
                return False

        def matches(ans, test):
            if isinstance(ans, (tuple, list)):
                return any(map(lambda elem: matches2(elem, test),
                                          ans))
            return matches2(ans, test)
        msg = '\n\n'.join(review_str for review_test, review_str in review
                                       if matches(ans, review_test))
        if msg:
            dlg2 = wx.MessageDialog(dlg, msg, 'Answer Information',
                                    wx.OK | wx.ICON_INFORMATION)
            dlg2.ShowModal()
            dlg2.Destroy()

def get_answer(question, title, conv_fn=None, test=None, review=None):
    dlg = wx.TextEntryDialog(None, question, title, '',
                             wx.CENTRE | wx.RESIZE_BORDER | wx.OK)
    while True:
        status = dlg.ShowModal()
        if status != wx.ID_OK:
            raise AssertionError("dlg.ShowModal failed with %d" % status)
        ans = dlg.GetValue()
        try:
            if conv_fn: ans = conv_fn(ans)
            if test: ans = qa_helpers.match(ans, test)
            break
        except ValueError as e:
            err = wx.MessageDialog(dlg,
                                   "Answer should be %s\nGot %s" %
                                       (e.message, repr(ans)),
                                   "Error Notification",
                                   wx.OK | wx.ICON_ERROR)
            err.ShowModal()
            err.Destroy()
            dlg.SetValue("")
    review_ans(dlg, ans, review)
    dlg.Destroy()
    return ans
def ask_yn(question, review=None):
    dlg = wx.MessageDialog(None, question, 'Ответьте на вопрос:',
                           wx.YES_NO | wx.ICON_QUESTION)
    status = dlg.ShowModal()
    if status not in (wx.ID_YES, wx.ID_NO):
        raise AssertionError("dlg.ShowModal failed with %d" % status)
    ans = status == wx.ID_YES
    global answers
    answers+=question
    if status==wx.ID_YES:
        answers+=" - ответ 'Да'\n\n"
    else:
        answers +=" - ответ 'Нет'\n\n"
    review_ans(dlg, ans, review)
    dlg.Destroy()
    return ans

def ask_select_1(question, alternatives, review=None):
    dlg = wx.SingleChoiceDialog(None, question, 'Ответьте на вопрос:',
                                [msg for tag, msg in alternatives],wx.RESIZE_BORDER |
                                wx.OK | wx.CENTRE)
    status = dlg.ShowModal()
    if status != wx.ID_OK:
        raise AssertionError("dlg.ShowModal failed with %d" % status)
    selection = dlg.GetSelection()
    #print 'Got selection: %s' % str(selection)
    ans = alternatives[selection][0]
    global answers
    answers+=question
    answers=answers+" - ответ '"+alternatives[selection][1]+"'\n\n"
    review_ans(dlg, ans, review)
    dlg.Destroy()
    return ans