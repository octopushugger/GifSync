import tkinter as tk
from TkinterDnD2 import *
from PIL import Image as PILImage, ImageTk, ImageSequence
import time
import os
exec(compile(source=open('TransparencyFix.py').read(), filename='TransparencyFix.py', mode='exec'))

current_box = ""

def purge_other_box():
    global current_box
    if TextBox[0].get() == "" and TextBox[1].get() != "":
        current_box = 1
    elif TextBox[0].get() != "" and TextBox[1].get() == "":
        current_box = 0
    elif TextBox[0].get() != "" and TextBox[1].get() != "" and current_box != "":
        TextBox[current_box].delete(0,20)
        current_box = not current_box

def show_text(event):
    if event.data.endswith(".gif"):
        global openfilepath
        openfilepath = event.data
        global im
        im = PILImage.open(openfilepath)
        # count frames in gif
        global frameCnt
        while 1:
            try:
                while 1:
                    im.seek(im.tell()+1)
                    frameCnt = im.tell()
            except EOFError:
                break # end of sequence
        im.seek(0)
        global loopgif
        window.after_cancel(loopgif)
        loopgif = window.after(0, update)

def update():
    global im
    global image_on_label
    test = ImageTk.PhotoImage(im)
    image_on_label.configure(image=test)
    image_on_label.image = test
    if im.tell() == frameCnt:
        im.seek(0)
    else:
        im.seek(im.tell()+1)
    global loopgif
    global current_box
    if current_box==0 and TextBox[0].get() != "":
        loopgif = window.after(TextBox[0].get(), update)
    elif current_box==1 and TextBox[1].get() != "":
        loopgif = window.after(int(round(1000/(frameCnt+1)*60/int(TextBox[1].get()))), update)
    else:
        loopgif = window.after(im.info["duration"], update)

def test_val(inStr,acttyp):
    if acttyp == '1':
        if inStr == '.':
            return True
        if not inStr.isdigit():
            return False
    global im
    im.seek(0)
    global loopgif
    window.after_cancel(loopgif)
    loopgif = window.after(0, update)
    purge = window.after(17, purge_other_box)
    return True

def restartbuttonpressed():
    global loopgif
    window.after_cancel(loopgif)
    im.seek(0)
    loopgif = window.after(0, update)

def savebuttonpressed():
    global im
    # gifs with lower than 20ms frametime default to 100ms i think, either way it's slow as balls so better to just move up to 20ms if it's less
    frametime = 20
    # frametime textbox
    if TextBox[0].get() != "":
        if TextBox[0].get() > 20:
            frametime = TextBox[0].get()
        filename = openfilepath.replace(".gif","")+"_GifSync_Frametime"+str(frametime)+"ms.gif"

        # commented out because save_transparent_gif() appears to work fine for non-transparent gifs
        # if has_transparency(im):
        save_transparent_gif(ImageSequence.Iterator(im),int(frametime),filename)
        # else:
        #     im.save(filename, save_all=True, duration=int(TextBox[0].get()), disposal=2)

    # bpm textbox
    elif TextBox[1].get() != "":
        BPM = int(TextBox[1].get())
        if round(1000/(frameCnt+1)*60/int(TextBox[1].get())) > 20:
            frametime = round(1000/(frameCnt+1)*60/int(TextBox[1].get()))
        else:
            BPM = int(round(1000/(frameCnt+1)*60/20))
        filename = openfilepath.replace(".gif","")+"_GifSync_"+str(BPM)+"BPM.gif"
        save_transparent_gif(ImageSequence.Iterator(im),int(frametime),filename)

def has_transparency(img):
    if img.info.get("transparency", None) is not None:
        return True
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                return True
    elif img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True

    return False

# create window
window = TkinterDnD.Tk()
window.title('GifSync')
window.resizable(0,0)
window.config(bg='#36393f')
# drag n drop functions
window.drop_target_register(DND_FILES)
window.dnd_bind('<<Drop>>', show_text)

# create labels and input boxes
TextBox = []

tk.Label(window, text='Frame-time in ms:').grid(row=1,column=1,sticky="ne")
# TextBox[0] = tk.Entry(window,validate='key')
# TextBox[0].grid(row=1, column=2, sticky="nw")
# TextBox[0]['validatecommand'] = (TextBox[0].register(test_val),'%S','%d')

tk.Label(window, text='or BPM:').grid(row=2,column=1,sticky="ne")
# TextBox[1] = tk.Entry(window,validate='key')
# TextBox[1].grid(row=2, column=2, sticky="nw")
# TextBox[1]['validatecommand'] = (TextBox[0].register(test_val),'%S','%d')


tk.Label(window, text='Note: Min frametime 20ms\nBPM will be recalculated accordingly').grid(row=3,columnspan=4,sticky="n")

TextBox = []
for EntryNumber in range(0,2):
    TextBox.append(tk.Entry(window,validate='key'))
    TextBox[EntryNumber].grid(row=EntryNumber+1, column=2, sticky="nw")
    TextBox[EntryNumber]['validatecommand'] = (TextBox[EntryNumber].register(test_val),'%S','%d')

# create buttons
button = tk.Button(window, text='Restart Gif', width=25, command=restartbuttonpressed).grid(row=13, columnspan=4, sticky="n")
button = tk.Button(window, text='Save', width=25, command=savebuttonpressed).grid(row=14, columnspan=4, sticky="n")

#load image
openfilepath = "Default.gif"
im = PILImage.open(openfilepath)

# count frames in gif
frameCnt = 1
while 1:
    try:
        while 1:
            im.seek(im.tell()+1)
            # do something to im
            frameCnt = im.tell()
    except EOFError:
        break # end of sequence

im.seek(0)

# create image object - needs to be done after loading image
test = ImageTk.PhotoImage(im)
image_on_label = tk.Label(window,bg='#36393f',image=test)
image_on_label.grid(row=16, columnspan=4, sticky="n")


# start gif playback
loopgif = window.after(0, update)

# start running window
window.mainloop()