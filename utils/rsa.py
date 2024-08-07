import os.path
import random
import time
from math import gcd

import cv2
import numpy as np
from PIL import Image
import sympy


def image_to_rgb(path):
    with Image.open(path) as img:
        a = np.array(img.convert("RGB"))
        return a
def inspect_color(img_array):
    return (np.int64(np.array(img_array[:,:,0])),
            np.int64(np.array(img_array[:,:,1])),
            np.int64(np.array(img_array[:,:,2])))

def save(img, path):
    pill_img = Image.fromarray(img.astype(np.uint8), mode="RGB")
    pill_img.save(path)
    return

def generatePrime():
    p = random.randrange(128,1024)
    while (not(sympy.isprime(p))):
        p = random.randrange(128, 1024)

    q = random.randrange(128, 1024)
    while (p == q or not(sympy.isprime(q))):
        q = random.randrange(128, 1024)
    return p, q

def mod(m,k,n):
    if(k==1):
        return m % n
    elif (k % 2) == 1:
        m1 = mod(m**2 %n,k//2, n)
        return (m1*m%n)
    else:
        return mod(m**2%n, k//2, n)

def encryption(m,e,n):
    m_chip = np.copy(m)
    m_key = np.empty_like(m)
    for i in range(len(m)):
        for j in range(len(m[0])):
            m_chip[i][j] = mod(m_chip[i][j], e, n)
            m_key[i][j] = m_chip[i][j] // 256
            m_chip[i][j] %= 256
    return m_chip, m_key

def decryption(m_chip, m_key, d, n):
    m_plain = np.copy(m_chip)
    for i in range(len(m_chip)):
        for j in range(len(m_chip[0])):
            m_plain[i][j] = mod(m_plain[i][j]+256*m_key[i][j], d, n)
    return m_plain

def RSA(path, enc_path, dec_path):
    img = image_to_rgb(path)
    r, g, b = inspect_color(img)
    p, q = generatePrime()

    n = p*q
    m = (p-1)*(q-1)
    e = random.randrange(1, m)
    while (gcd(e,m)!=1):
        e = random.randrange(1, m)
    k = 1
    while ((1+m*k) % e != 0):
        k += 1
    d = int((1+m*k)/e)

    print('hit1')

    r, Mkey_r = encryption(r,e,n)
    g, Mkey_g = encryption(g,e,n)
    b, Mkey_b = encryption(b,e,n)

    img_chip = np.dstack([r,g,b])

    print('hit2')
    save(img_chip, enc_path)

    img = image_to_rgb(enc_path)
    r, g, b = inspect_color(img)

    print('hit3')
    r = decryption(r, Mkey_r, d, n)
    g = decryption(g, Mkey_g, d, n)
    b = decryption(b, Mkey_b, d, n)

    img_plain = np.dstack([r,g,b])

    print('hit4')
    save(img_plain, dec_path)

    return 'sukses'

# secure = RSA(path,enc_path,dec_path)
