import os
import io
import time
from turtle import width
from typing import Container
import requests
import threading
import tkinter as tk
import tkinter.ttk as ttk
import PIL.Image
import PIL.ImageTk
import serial


def play_video(**kwargs):
    canvas = kwargs['c']
    container = kwargs['con']

    r = requests.get('http://192.168.0.112:4747/video', stream=True)
    jpeg = b''
    for chunk in r.iter_content(chunk_size=1024):
        jpeg += chunk
        x = jpeg.split(b'\r\n\r\n')
        if len(x) > 1:
            if not x[0].startswith(b'--'):
                image = io.BytesIO(x[0])
                im = PIL.Image.open(image)
                im = im.rotate(270, expand=True)
                old = canvas.image
                canvas.image = PIL.ImageTk.PhotoImage(im)
                canvas.config(width=im.width, height=im.height)
                canvas.itemconfig(container, image=canvas.image)
            jpeg = x[1]


def write_payload():
    print(teclas_pressionadas)
    if 'i' in teclas_pressionadas:
        payload[2] = 1
    elif 'k' in teclas_pressionadas:
        payload[2] = 255
    else:
        payload[2] = 0
    
    if 'j' in teclas_pressionadas:
        payload[1] = 50
    elif 'l' in teclas_pressionadas:
        payload[1] = 110
    elif 'f' in teclas_pressionadas:
        payload[1] = 30
    elif 'g' in teclas_pressionadas:
        payload[1] = 130
    else:
        payload[1] = 80

    arduino.write(bytearray(payload))


def update_text():
    r = payload[2]
    if r & 0b10000000 != 0:
        r ^= 0b11111111
        r += 1
        r *= -1
    modulo.config(text=f'Módulo: {payload[0]}')
    direcao.config(text=f'Direção: {payload[1]}')
    sentido.config(text=f'Sentido: {r}')


def keyup(e):
    if e.keysym in consideradas and e.keysym in teclas_pressionadas:
        teclas_pressionadas.remove(e.keysym)

    print(e)
    write_payload()
    update_text()


def keydown(e):
    if e.keysym in consideradas and not e.keysym in teclas_pressionadas:
        teclas_pressionadas.append(e.keysym)
    
    if e.keysym == 'space':
        payload[0] = 0
    elif e.keysym == '1':
        payload[0] = 125
    elif e.keysym == '2':
        payload[0] = 150
    elif e.keysym == '3':
        payload[0] = 200
    elif e.keysym == '4':
        payload[0] = 255
    
    print(e)
    write_payload()
    update_text()


def mouse_wheel_up(e):
    if payload[0] < 254:
        payload[0] = payload[0] + 2
    print(e)
    write_payload()
    update_text()


def mouse_wheel_down(e):
    if payload[0] > 1:
        payload[0] = payload[0] - 2
    print(e)
    write_payload()
    update_text()


def focus_out(e):
    print('out')


arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
consideradas = ['i', 'j', 'k', 'l', 'f', 'g']
teclas_pressionadas = []
payload = [0,80,0]


os.system('xset r off')
root = tk.Tk()

f = tk.Frame(master=root,background="black")
f.place(relx=0,rely=0,relwidth=1,relheight=1)
f.columnconfigure(0,weight=1)

modulo = tk.Label(f,text="255",font=("roboto",37),anchor="w",width=100)
sentido = tk.Label(f,text="255",font=("roboto",37),anchor="w",width=100)
direcao = tk.Label(f,text="255",font=("roboto",37),anchor="w",width=100)
modulo.grid(column=0,row=0)
sentido.grid(column=0,row=1)
direcao.grid(column=0,row=2)

b = ttk.Button(f, text="Quit", command=root.destroy)
b.grid(column=2,row=2,sticky="se")

root.bind("<KeyPress>", keydown)
root.bind("<KeyRelease>", keyup)
root.bind("<Button-4>", mouse_wheel_up)
root.bind("<Button-5>", mouse_wheel_down)
root.bind("<FocusOut>", focus_out)

root.mainloop()

os.system('xset r on')


# function set_up_dc(){
#     document.getElementById('feedimg').style.transform = 'rotate(90deg)'
#     document.getElementById('feedimg').style.marginTop = '100px'
# }
# set_up_dc()