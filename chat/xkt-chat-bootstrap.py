#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xueketupu.com 站内客服 · 单文件自举安装器

    sudo python3 xkt-chat-bootstrap.py            # 安装/更新（缺 key 时会提示输入）
    sudo python3 xkt-chat-bootstrap.py status     # 看状态
    sudo python3 xkt-chat-bootstrap.py uninstall  # 卸载

做的事：解包 → 建知识库 → 写 /etc/xkt-chat.env → 装 systemd → 配 nginx（含全站注入）→ 自检
不依赖 ssh、不依赖 git、不联网下载。
"""
import base64, getpass, io, json, os, re, shutil, subprocess, sys, tarfile, time, urllib.request

ROOT = "/var/www/k12"
ENVF = "/etc/xkt-chat.env"
UNIT = "/etc/systemd/system/xkt-chat.service"
NGSNIP = "/etc/nginx/snippets/k12-chat.conf"
NGCONF = "/etc/nginx/conf.d/k12.conf"
SVC = "xkt-chat"
SPACEY = (" ", chr(9), chr(13), chr(10))

PAYLOAD_B64 = """
H4sIAFp2+WoAA+19+3cTR9Lo/qy/ojNJPktBbz9wZMQuBAjcJMDG5NvNtb06Y2lkC8uSmBlhe43PMQkPGww2SXg/AgQCScAm
LzA2hnO+7z9JNJL8U+6fcKuqe1562CSbsPc7l9kN1kx3V1dXV1dVV3d1B0N/+sOfcDi8sb2d0d8O/hce8y9/ibRHN3ZEN7ZG
WqMsHIm0hiN/Yu1/PGp/+lNR02UVUJGh9o43o03zjQwqSnYNOO5Gsd8dzz/oCYaSg7L+xzLBr+//aDQaftn/L+IJhlJKIZsf
+yM54Df0f/vG9pf9/yKeYEhLqpmCrv2BDPAb+n/jxpfj/4U8wZCsacof2v2/pf87wq0v+/9FPFb/oxkQGMmkBhQ9uF/7XesA
enS0tTXr/2i0Pdpe0//trW0b/8TCvysWTZ7/z/s/9AZz9zz7afIzNlpUhhS9WCgGk/lhVvnmonHsqDF/s3zlVHnmo9Lyw1+e
TK1eflh6erX647lfnkx72BvMmDtd+WbhlyeX9u7p3sdCciFDLAU5u7u3Q55fnlwuLZ4yZhcqn90tn39YPf61ceLu6sVTlaU7
pcUlgF9ZmWc7tvz158mPAFzI400Xc0k9k88xr4+NexjLpJl3JJNL5UeCicTokP4WQH83L6eUlI+pgKya64JcjXOwONPVotLl
gRwHZZVtf2/LrnfhozSgyjk9q4z9cyz9l4FhOZPFBktdItuWvbswk9UYK+G9LX9P7Pvg/d3dkByJWmABffjQA2+M9UjVZxdL
i19XVs4A/coXFozDl0rLk6XHU5VLRyQ/k9w0hgylxfvG5RX2TiASZcbRu8b9Lyt3zlQ+v11dOGZcflp98C0Qt3ziBP9S+ejx
z5OHjaNTpWfzxtHvK98vw2t14UT53P3VmxeMT2aqC0/L14+Xr96oXJ6vPrtWnporLU4aT64DPr88mcFOuHrbmL9UWjll3P/K
uD/38+SMceqGceWu8enXkLN8//bPk6egMwCT1Y/vGkdPVX94DAWhD6Fs5eKysXIWUqU+v2htefI0tu2zu9i20uI0AAB8fzpz
nQFMFlJGwcpUlRArz0zzlpWnnxpTD4yVT43pU1abgEt+OnODQQILpTLyQC6vQZnVyWlj/mNE+/vlyvLn5e+eORtuPJ00Ll+r
PluBDMbUeeP4UvnKJDBa9eOV8slzwJfVo8+A5tDA8vXHxuXr0C7j8UPIBoSi+m4yQJuFsoqs5kKs+uhzFtLzhUxSg5cbt6vz
37kb+tlDIIUxdz5U/fJw+fu7xrEZeOGtPsUTkU6PP4fX1SuTViZOM0gq/zhbvTNlXLxbnv7UeDJpPPgWMAUMoJbylXucWYBx
SktLleUfyiduAe6rV69Vlmerc7fLk3c4Q8G4Ki9e3fXWXuPW8WgY9CWYTB1txuyjQAQGmwthJ60QNDEh4utMiEOnsK2s9Pgk
dIfx7OjqjWVILp+eKc/eYFsY4MBHu8lrAlVjZsmYOgakrdy4x8EhdT+ZgS/VlQXrC7Sa82bpyaXSkwvwHbrLUcRJ3ivTyIFL
lzmXIJ7VL49VLp8zHszCJ+CM1W8u4FC5dQmIJAbJ9BSgAyQBmpXPXsSBMXPeWJwybt2B3+XvvuYfqwtnytfOV+5PkziaARax
mBFQNh7/ALKImNXs/dXjM5X7l93onX1QPjVfWj4NSMIIQvQs5i0tnnaOOgR+9B70MNRevjrHx2Tl7knIYBw/Vj77Q2XuGKAB
XAiZQQaiSFxeAo4sL8wiBBPs6sUjHKxx+vPyuePGk7OcWWrHXvXwZ9A1pZXrpeV7iNfqR/OV+W+ZxDYIebeBSch+U+eME9fZ
X//KKk9vsUi4rb2zre3NdmCby8bcVGnlSnXhUeXKSRbSCvmclldDrqqAVY3F+fLUmeqdL1DQcM7nGgL5f3au9PQydIPx6DbP
gSJkeak6P09jzB7TXPZUzx0xnnwLjcRhCu1/9C2ISRqXM1C8fG0O+sMmxI0foUcIHcCmzxK7oMF1BQTvOBvWBrQY6+nzM9QH
8DPsZ8P5lBJjuWI262f9RW0sxtJyVlP8rKDkUpncAE9jEwTOUjpK1qvLA36WzGoAbFTnOojXh3Wl8snisJLTg0lVgdq3ZxV8
wzK+LsqI6goK+5gSTGbBxtotD2M5+GSnA1z2Spzqx3y6Mqq/lc/pAAgV1qjOc3LlxhR8m3Ahmc3khjLpMS8WdCKYVuWBehy3
idcdkErICkyxhIq4hby9gvV7Qz1bAv9bDvwzHHgz0Rvo29AbOtQb8gohfsjsxUMkMg/xMod0RU4OKuohwTeHktAUOakfyuUP
KlkfQBjU9YL251hvCMD/o1eDPoa+9PVtONTTOxLEWv5i/ugN9o5s8IUGbASBhEgU7E/+cWQwk1WY1zsMX1UlqIwqSU4Hn0kJ
TuPhIFgEyijbTCB8RJugXMDOfwtApLw1VNoHMHYDyxCwoJbNJBUvloSKOSSooEvAR8QQq+GeMLCc3JwtJFmyClHHc1B70l7p
L5IPcAtE2H/8B3N8RlpByitxaLOPycFBVUmjLYI2ip6P4aDWTYgKsHMtWFE+XlPeXab+s1zLhE2wdoMfx3KyCgYkopjoz8q5
IakLPqpKFr/k8nmgt6LCtwkBr64bZItAoqvNjoOGBrNKbkAf5BkmrOFDGTcx6iie47d3r9WrYrQhHGvAhUIsAA/7YBf9FWKn
X88BmiAopP6irudzvIvhazCDBqcEFmiAbGv4JJlJMNfaoutqBooowBZqRg5k5X4la0tRbmc7gOWAcjv3vYf2assmrSDnGAmU
uJRJ5qXN/+fzT+5tCuHnzbxkiyUX4RvRH1FMZQ5ykPSxFkP6KNnJbizVfFZB/GDYZ/MDLjA2bkS8lk1Qj4keQh9MSZvx2+ZN
/Zudpiwq8xNfladPbgr1b96kDcvZ7ObV86gjyt+fZWAlTj+1xD68gj7iihdaSnk3hRBoC9sgquU94Kx5VGI2deNg63y/ev6+
tPm/z0ONlLkORg3q/fnUmLRepuRgpqCtmyutQxZkOBl4kKn5EfgekVghKyeVwXw2pahx6XlajxWZYOoav9mYPbM6efh5m5fL
64q0mWtqMNRbnFYC+69HDI2Q87fBGgNTBGovLZ5YvTjHYUoWhyGNgJE4MxwoKupYt5JVknpe9UpBi4g+c9pE1FozP6enVUCX
m+U2yWDn1WDIb6Uh2Rx8Wmf2WIVylnCQU6ntB+HHuxlNR0nllbbteU+IQT6FlNCSKOZ0qg+lj1UWsEiNdZMNguJaykJ+sCtA
PFIBrmYtnS2+CR3lAgTyUyiMrWO7Ul63APE5Z7kOzJHCLoEHmX3r5SEK+eoNCiDDe9qAFwe8n9VaFcMOUeLnwgPsLbIvsYDD
7sFX0g1Sf15HOrgqd1ktvi6uioZrFY9imj91yA/7HAlaEirL7ssXoIzjw04lMzDotp+GGzZ3Xz6f1eoMKL2+qTpmlJwmk1v4
+4WJKab9MCOt3P8MPR4Lj81SajCfS4LGGYKStd4N0omKnhz0otMBxmBIVQp5VQe4ZjJjw4o+mE/FmIQ+FkgZBM5TVDBzx5kk
SBfYN1ZQJMgCFIOqZKwjtF8DBNmE3wKElIqx/9W9Z3dQAzGfG8D+GGcHYtyWDqId3WP/FNqVBVikD+2UdTMFkxwbMIpi1JVs
wicqn/AFAStop4sCE5b2V2sYQTIefVedf8CnztUHN+H/kp03ldHk/qzDwUNV2J00KDpJdvTPyj0u9cxuGWxkXFmy8M9asX8/
yJA4flVySbAdPnh/11v5YbByybQDrY3zl0/uVhduAq9vELhJ/4FEbloKZlA4rz8/T5OdS7253hzMX4FZqgtXYXram8OCDuIO
ywUHxUZ9Dq4Q/O0dDdrjrqiBtcX+zLAeAC8x4AiucPENsGSjZh912R2zP5/JeaVeFDYmaTR9LAsogHGXyb2rpKlH5KKeF32g
u0am6mv0ddDXZCDrDSSQCqmK+haqAWtkkFJw2UGSqH5dJxv3bYH+QtfBqRulldnS0jGXq8rlHeEJc8dg7olplqtH6gum8+p2
2cW2B+xOIF3YWB4csDi7v9nwZ7I2BNC6TMY1W+yS6gLMRAOaoXG9FyW6RTGuAUnbo0ZD9eaVMJvJ82SKUtfCCAI7ZIyb6TlF
sqX4K3Vj226wUBQk39HztXLduL1CzoUz0AvcNwRdYJl5MNHrzRmzC6Xl28DznClFp5mdgZ6az+ewM03Tx3RGCi9PiHtoMJ/b
CYNfoOvnvuT9hQ4CW5w4+ckmr5Ic2qnIWX3Q/MhnFWD37ssMK/mi7hZPYIgAAySLCAPkKOsIN+iGZBamxFY/1PWBqgzDRNjq
hsZdQDMkYfg345ZawDTPzuQ0EzQMexcqMSeDCCZrbiKNSj5HzTYgt3vERUHBFW71NUiJqL5YEv0CMeSvgAYVKZKtDYL6oJJz
0FrFBgqBBupyCNqiBlF9UTtwRHU1L7wfCwumBYEL6O9HbbWfw/Hu518PHQITLTssIUApn06DOaJITqgN1JMbqqtU3SSRm+Hm
RNG2NWiMO8w+DhI9Um7L7gDU4D2AaALTHZSzRY4ydAto6mGvw8x65YC7pJXfFpC8EnKGbdjg/ESjulDUBkHto9qICZ3hZ0It
xAARUyubo13kOMCNZ2czqAa22V4YaSoquMAuPbkEis7SgDDNwPF+6xJIZ3Tj0mSDLEt7pQXnJTAX4d5tU5iUT90EaAAKgKwe
P2U8meQezsrlH8qnb2NXfARy4qHbCVojIGwCTngsw6G/2N+PyrQWfUuAUnqtrfLT5JdSHW0418QdfGMTpzEYy8ARyY2s57R8
YEtOG4GpygGHR6pp54KwAFkh53RnDzeo3TbELOO4PtdaxLPZ2mWTidlZY4MNCS4nk6LpbmFi27+/k/XbxPYdVjRNHlA0pwls
CgUwjRrIKYdn7BWSVTBM4QfC9zF9EKb5LKeMsO2qisIVPWZ8rhTECoqay4uoIkF4WZwGvk9N8/r8LKUgWRAOeq62KWhJUkJ/
Me1iFQu3QnG44G1gH6opmql669uiaM7sYgqnaMEU2ANuCWNyZZptiCNqwRQhRLlJ9PhJVkI9wzHqXwc/mU0tyKqOTgCAEgS9
l9HR4uzNSb7aKuI8a7CQL3hdifxzvUFWcDeDN6RgOy1Tsi7HbKdqfcNEX8gjWLdwDra75a6LRpgRx3XPtj27t/dJzUHud3/S
1TGg036ohdgQ2qMpCA21MyP1w7yKrQltr6ld9/5gqra1jMYQdAykdTVIieO/wAPkdvKGenPjrf6J10Ig1Gqpz3tgTclUk62R
hILafPVgn3PSbj6NWg41+Wr0vKXa7c9OOG4uFAOCDxQ7wc5kVtogY70osLvh1wlf7BK7SmwZEswWu/hm1dnAJnFXWmuZ/L+u
X9ano1AhtFhnVV+vRRzpjeZGzmY4HDz9Cq0xiFVBeOlO5mkNLMxB7djy10YCRs6o7kmfZheBSvMq8+LXDH2FP5vYAYdbBL5s
2ODjUgkg9YT7LNl0IKgV+0FwejN+FvXxFSHgcdNmE+YEfLZwRfHgRFzrMhuFsE2RMeEwFykZ7GG71OY4VGZyOX7uifS5fGYS
356Bs6srdytLz/gKA5htlS+X4bV894bxZBb9FrT5p3zla2NuwThx17LRFherdw5zE4/ba7SwLBYGQ2IxurmRZnWn2e9rTaDN
qQ1YwfXe3CFlLJUfwVm5XVBxWuNKELJwab4dOFWVkFKvKEFtMJPW31HGsBYlWFAVhLtNScvFLHp2rZo9nNYTPhQU/+5NXb/i
abj/L6n9rhsA197/F+5o7YjU7v9rj7a+3P/3Ip6a/X/Q88+7AbCy9CVrfWcrjHXcrveqc7FivJDXMjjIYunMqJLqUlGvx6Lh
wmgXTKP0/HAsGoXf/wyQ+ItFI20b2zpbgWxdgIY+GGvvgNRBsgb47/68CmZvQJVTmaIWaw+/ToujcnJoQM0Xc6nYq+H0xo4O
pSuZz+bV2KvpdFoUiYXhx2hAG5Rh+MfCrLMwyqJt8I860C97I+3+SKQT/gv7g61RX1eyqGpQvpDPoAigZRsQVQEt808lFmkF
PFC3BgRikWCkS3huYumsMtolZzMDuUBGV4a1WFIhCPuBu0CZBkyNKD5j9kAqoyokiWKAdXGYrEZdlXOCcvQTNMowC0baNabI
uGXFbov9tYtwTMvDmexYLJMbVNSMPuHuj9hg/qCijlsgOfAsaNkPvQHoCZ+bSJEoUqmzEZXaor4a2AyXnoOZZH7cphX1tEmb
/mw+OdTFPcgB0f2RwqgTDHmj1meazs5GTBMRTNPq4hoqNyyPmr21sfPgYC3T2GxiclakjWpz0ALhsPawRYsOf2vU3wqUiLb5
rCai47R5pyLt01mANphJpZScq78COFFVAtoYKKph/1Y0vt6Tk930ugPy+aW9MEPdIecGWPdbkl96LwOWspZP6+xDGcxlya9B
RwY06PN0DbtiS8RwiHREIxFrRADtmZbPZlL1vRtx9y53EqLzcNzJ6BOeIF/aH197BBZADeP+KmInwufXDhdgraQS6Ff0EQXp
BqWgR8IM1x8sJFj/eE2r6XWEd3sHyJSsogPwAAJDdILRgt0ERtsJxt286oAHxOrKY0F9LBbsjJpsrOcLsWhNVW3hsAA76iQM
DTWY4eFKiyWTHFSqGTU1IsglcCyKIkHbnJi9KWrGydQ40Qk0KtGpy+S+wFiM3t29YkJyDYuNaTltQgRTfxyHER9jnR2vCxJQ
R0QQYxPgmwgvUies6ZNbbnZEu0YGoeOpS5QYGFWBEVUudI1AwUC/qshDMfo3gB9sPIIgBsYbj18HU7+qtCpJRTax4KIjkFXS
uolRm9X/CBR9muswsuh0hMFp6IZNgqohcCaPCzDh/o7+jtYunAkF0GeikmsqVsTFCSROfduBLWs52U2KWuAildapXeO1a0Au
xDpJHFLPBVD/ic5zsnqw3RYZ7Qiy0wlSbJxwkorEXi1P85K1fGwySXgNEtTh0lCx2dtE3I0k8YtsFCNewjZ3OLhTaLXOtXid
b0+pb2cTRkt1Kh1Ka5fVCe3p9s4a5n/zzTcdOLTjCKmherR+zK/TbIGg0OlONJU0NKdd5E3r4y6BaWKGoss5WjqVNChbE8XO
Wilt0rGGHFYlzNyII8ROczrVUMZBl84GdGklDlAVeiNGE+KjFVEEVefQ7W92NGaWrnxRR87i5d0yqK2+BTFa4RsXeJrdStLA
ztyAO9a0PWvb7DBwa2zL5+YCC4uY6QYZtxRBuwkmxaeooghu9hpvOtbTHemOJB+YpJRNdexUN2G2sREX/GVYSWVk5rVVRFsn
9KQPJ9a19h036FAfp3WiDRl1ps0fCYNVL7qnswOMNUcH03u9pUZGBWAWnnDVhhMQXpcw57jJSZJ54n/S3PxFPHb8rzaWSxIB
g9rg71vHOvGfkY0b6+b/0WjHy/n/i3hefSVU1NRQfyYXUnIHYXqkDXpeZeUr98pXlmCSD5MRmOBXn81Vb8zw8DPhAry8aBz9
vnzueGn5oTE3U75/25h6AN+NEzeMi3eNxw+rz65U7p405qerXxzFkL5X0dsMwFkjdnO6+F9lq8sXqvO3WLG/mNOLf4m0dQTb
O4LRaBvMeNsIzs493fvikWA02BpsYx90b38/EeeZm9cA5UqA/uxc5dZS9emnxtHbrLt7JzMWjlWuH8ZYqu9ulK8grvBl9ZPb
3IHp0RSdBZRinhUyBZCnmazn/T179sWl17zJFIN/YbaXw7AO6bWw5AsFg+Q0LIykfJIHcUxAznH8EQu4WzEheT7ANMI9FuDI
w8dt27sR+jj+jQVCB2U1NDIyEhqKRCHRoyQH80yKx1kkFGWc6KIDph6w1z74y2tUZ+w1LM3iccmjIgVYQD74TxYAFRAoKOqw
xn/mR3KKyn+iPC+wXhCh0mvYPH4giARvbpDi+2+F2jDMWFojNalpDZAQGX8zGuK0i2ZtdCX/1jpMBuTATBZsUJuZ0dm5Uehc
5+ChntSArQN51q2oYPNtyWYOKrtQQx+Us/HWsAMu1KEVU3k+Dtx11CBj6sFgkwy/p4xZR/63bWzg/20Pv5T/L+JpLP+NK3ct
YV5aPME50ekFBpHJfVYptoHlYFY5yozZU6XlL+DVOHoXsvIAbwx9PSrE6eqVSYbcaaoDHu6AwtdRFYVmXiL+dcq/JlxKcDB+
eGUeSoUUPRkyzcAgNmf1+Ixx7KJxe4W9tXPLvsSWvbsS72z/EKPXvzxXvneD6zVQDJXPPi9PzZXv3ihffWbMnV6dnDSOL2Fg
e1MNMI5/62T09t3/uSNeh4Zn99v8IxEKl7/SwRSWwK17aZdg72CV0wvGzY+5YKexn0mzHvYKC6RhnCN8ifV1MVw7xXUxHOy6
olhJm4FAB0MU0LhpU8v2PTtagERuZ75Q4FSNMXth9Tgu4HUAy5avfrx6cQ4DY08+g04zlj5FCjgJF7fftm7p3h6ngL5YCOPj
gylFKWiKMoR18Gzv7dm2/d24+Z2o4dm75/198c7wmxGeZduWXe9+mNj6wba3t++Lt4fD/OuuvTwh3iEAmXvA4pGoB9oEDeck
Mx59x3uO8eZbCT8d+4SBreLqdWbc+Kb67LJxehnauw2w6gasWPn0HWPqoTH7oHzugbG8VLl0hA0pYzxAuHLkITLD8VPVR2fA
IqoeuQT/UiWjGZ2FPekMds4rvBcGVKXAAgdYyz9cFAv2bmgxe8fqNo7kK69wtJFL3ZhWn10oX1iofIXoYH/c+AZY2DiGeAAQ
qj2CtVPFycHhfIphB4pqXMoEGIqHXS19StxEhgvyruTBARIosr0f7tu5Z/feLft2ssKYPpjPtdKKUKi/mMmmEkP9wcKYVYQq
HB4Cu4cFCjwbD76ln9n8gGbiBPqRBd5nMDQCtO3G/NG4kI1xK2BsShbSfASuwJyK2RpbGqjATFJhNLhEKfG3LhOHxBOTepal
ZGU4nwuoCobr1CYqOZxXk3ofYSYkj5YFrgHK12TOaAE5qYNOtnPa7WmD9nD52Kw1hCQKAuaQEVouUyigoQNSImDl4OxmcZor
Dbls99uSWzRYst3s2QDPhcJh74ctnswwxphgWzy4Fwf+BmV14GBPpM+DOxvQ9e8t+MS+May9ts5cXmeZHNNi5kJ6SyaXzBZT
CnO3ID8MxKYyXS2OArSnAyu2tiU9R3k7jMX9rF+0N0dYNsxmtgngswjf9oeBSU3x1MgWY+OQ3fr9K+Fz8kL5kRZfcETN6IpX
4ykFNZPTvS0F3PWjpKBEwefZ+6E15DlDBfRaTuTMzJMdPNgOPLj69Uz5M65QkkU1C+pE62aBYdbOUIiDDI9ENwbD8L9IDMWz
deSJ2MfdRTLLXbSTmfLfpWD+laLskODuJGtxzxRaIElTUkDr0D9CoL1Xb/zIbQtQ4OWzD2Is1OJocQe0uLpwdvX8PB56Mnvb
0W6OQFuYBf7O6KiatRvBAjtZi3N3aYzV7i1tIds/ALiNS+YuUinWM87jZmNi17QkFrXgwxoxK788+Vya6JvA1uL2VhZo460S
TTPmZ0DbganThHzG7PelxZPVO5+A+VI5/QDPdCFt//PkqfLM9Oon81Kt/yvomvL8MTbmrz//q7U90vby/K8X8bj7v1Zp/j51
rLP/J9ze3lrT/x0d0baX878X8fR8kMvofZ5tCp9ggUyLu6cLWkZYasza4unZktYVNZ5T9JG8OiROfvB4ero50/R5UE7GNTAu
sornA2CluGn9ed5GX4n9+jcon8kNbKNdE3l1LO6cT3m25w5m1HyOzizJZJUGE6vto0qyG+rX43WWjmv2yI1O0tJgznreVzQq
JGdHZDB9xGu3koy3et4Ds1Ade08ejbdHou95dud3KyN71cxBQADkehw3tXvwHc+SGC7wd0/PrhyAyGb7PH8D+iiprWPx4WJW
zwRQ9psE+nd3dcPHPf4tK+V3rWOd8R9pbdtYd/5f+OX5fy/keZXVuHVcox8dAK8yPMTNNoi4n4fc/bhIwNBc5Kf8MfPcsO8x
fiOtYHANQsjmubXkACLCVNX86FiiAIKlsRXa5ciFGRIwfjUEhHvvHGmaoid4NBDbmdd09tog/Nskw98D74NZGti1l72GEZm6
kpBTKbVp5h15dURWU0oKf7HXeA4okRhNpM0k/NUEAFiOOb4hzNp1z/NYBGL5dNqZQMGStR9xApbQeWQqi0TDmru6XG3ihIe6
7UYDX5y5f/MSnVb3mLWHwxsYmKMMQ6vpVLSvMe72+JIx+4Vx60j12Ypx4npp8RbY2TDd6E+kM1kQ/ol8Dubd+VyX85sOYl+j
5fTQoD6cdaaxlk0h3Jy0uQV+4S43nKvEJYp/1WBk6RLDIPy41GwlYPMmrqCYpiYb58LVhJQCRN28SXgLN5t1/o/akf1in2CN
bvwj6lhb/reCrK89/7UtEnnp/38hz6ss8EaAJfP8JLying504hePJEkWT6yzI9x9GOzMXjLAGD/lUDiRPRSM+wUIrbe372Os
1kXgcOKMS/khKYZWlV/CoCaYLmezw4eG+iX+npViwWAQN3y4z5mtdwc952QcoOGMm6HLGHVY+cfDdcDFWSwu4AdEWb8km1CY
89AXAlidW6lcvuDxlBanVw9/unp+EUBHfMw4dZYHQONBpbcuMbeXm1VxNWMKlzW+WajO4+lLbAPjiyQYZTMzzTRoGeoUnkon
8GIkT3lhloFigz/Gra+Yy5eOQCFTq4+Olv120pnH6YXnlV8G9V5ZemYdz1tZWih/MVn54SYFZ5+qPvgYQ3+unaS+dS4lQBUu
T3aIuVYMzHdaGoAXXA4wv7mwCLmxB7B8hd4N3TpHGP36R2+zoX5mhyTNfo0H1ZrOb941FHE0B4YLCyPqwOSmCxQdOX6W1/yg
mPzoUvMzVKl+Nihrg9lMvx8jehU62MnPimoWPgVV5UBRwZMBxbuCkb6etArjA62VoHALihq2ypqyc9++ve/zUjvlXCqrqH62
z4SLiXyF10OrTOiA1YIFWR8Mio0G3mbvcr+Gf70JVLdKIuHz+TzvbE2QU9+GQse7IGQ/k+g4Y/g71E/HK0g+T/e+Lfu2J7bt
en+dEuS7h/zv7nn7OXKjex8ye8wuo9wKn9hhpLNXcvYoj7CnuOyC1+ex2GaNUpiOxUyPGBdlwRR0m5bMF5SgnM2MFXNJjTxk
ByMAXuXwpRAgxjmxCXxKROAHRpRca7AjUMgWsTXEtnGGPtracpiEJdB8laAXXFzduEgd92N5MMuwuDV81yhq5sFiHVjIeTp1
01JWJiwWiZrltu7ZhpWBFn6DRcLRNg/wEQbYAo8E0bnsJae14C0/P9oI6B2XSHUglB1b3tqHNb+ztUdKy0ldk/o8b+38YPc7
5sfkYDE3hF/f2Wt+GirguwcDKFO4POC1mNHPBJ/5uCc+j0chDSkwADRvyo9rYZqeyA/F94HGADZL4AZ+PFvAHFTBd+EDsBIa
xIGah219L9pOEu1++dxxOgv4fGlpxjj6cWUZ192qJ7/l36sLpzDMqba8B8xNpueHvJpAji8RZPMYbipc/EWdn0+azuRScjbr
VaUefqxqb7B3w6t9G4D6wuef3D9Ul7W32KaEw4He4pvpdLrPzotgN8RZD5TpyfSBdqAf8DfSR1GoGSSiKucGFG8WugtSfRiA
6utzloavzlhP+ApU2rbnLeyUHmxWsoeO2ZP66OwNjM7ELxkdFGmfj+pJYj28c/s823bgGbwTdi8iLE4Y/DRC6z7Afymfvaiy
bUfPSB8U27aDWHPEj4H50AzPbjwBVB4l9BGOj1ZNtvzn20ji4jB9T3EkrLp8oDZ2QxuwW/qHo+1eOt/Gz4biraJKPFsFW0YJ
nJQaRsJiIHFPn4Vqxs+BKrnisKKCuOMo2Ghn0rTylbK/UA+CUZHJFRV7yQi0Bp5jADNaP1LG/G6RowaAnubU0NM11KgriHQ8
4HOXBqRGzAU5Pe1Oa4geFUohgokEV1KJhFcaBlEOQhIEtzcClXt3A+fUdE842I609jb47HNB15DPsIo3mJc37g0WDUapMH+H
1gVR1njDwWg7wYDJwBtMdG+IQY87YEITMQg67G4c70IRxe71AtUzPmfnBjVomhdDd1VNEZLCwfg9nIFxICF9E34+fHjZnthQ
H0gm0I579uLBPFLNoVR0hJj1iQ6ocn6aNI7N0Hvdi7N8TWHrkPbykdny5FXJXvCUXOe386Ozytcf2S/moWbfXistnabjdhYe
rZ6fpwxTZ8off0+pdIA3ffv8NqBVWjxJL9NPzRe7QrFWZR7J5TrvnF7EOWv8HHDjzE38g6tY8OfPqPhpNKJIS4CQN0dkNjOc
0V2jEuSeVuwnmScOhgYgvzw5/OefJw/7e4O/PLkUA7O0q48sBD9zDGCdNuXB+D3AB7CIhz/gFjzYfzbXiDz4x1rRHSHbw1zH
phxgovEfrwA8uzTVaLIbxeKbpVBsI+vqPraJRal2PhyxhGO4mpzHMR7M0IEoDgFkF4q5xv5QBnQeWn5+PA1HJssTs4ImrZMF
KAlodyqUQ5zwN6H1vJIhzYvHQR7VF9HM8xJcKUoWSpkEiLNOoiA1BkE1h4KCxsYxYIIQz6sMT+/9bB7UMG6LsY6Hm8OTCIBl
8X6KqWONEeEQN4NFQ7hQi5C2a+ASRqknMAjYQHwCF2f9fJkVB/vsbeP+3OrxmRostAaNbkht5AFbgiEqdR0tZBrlJIkmZJyi
4MyFDA1UC6ApHZyUaMgvCMOtzQRdENh6Sg2y0IGCRBXrMyBg4j8uYZIUEzVLWDW8cQwkQAFe4N8Jl1xHOgMM6isSD240KCiu
3lxpYNStHj21evNqafF0+fxt49n5xlZbQs+n5DGvGJICJE74cO6Rxh9e6fUPA68PB15PWVLsQDGvy95MIYFzQlE0XaidADlM
V7MWtJ/MaRYWGsnog4xMVcf2Euy/cYkOUpPo4gIJj0KOgd0w4aSTWRdZvpo3XaixAnR1rAFv6/U2fLrQ0Hx38e9oUinobDv9
wWC9OsDou7c+FjUllcjQRiK9h7DvI/tAUAytBJcmh0y8uX3Y6c4ZkLsi0T07+LUNUn8R/b2SE5RZM4AxZ0NrgsgUJAfhbTTA
Wom4EqgRPaIBaJqZNTmtMiJsCg8JQmeARVxpRGpKYYEP2iKQMT8kCRZDqyvfv78pc4nJUAPWygregtLQHmxMvBlDs9d3xl5/
L/Z69xrsSN/spsiNmsJkjdXYmWmxj8kiiYbNwbJaUVUSspbMZOLUC4Q5HjzVeBSLUI2FU/Xjt/vDbjrECE8dBX3Aalaspp7j
HqVpPMLG4cLELcm48CH8d6fFPTxXpvFcWMcxvQ337ODxo3WHmBonPserUsgM/BUnm3rcB5mKk07LV2+Xl+bwBhu64qV87rHx
ZBZvubl1vHxjqvTsRvnwAjbBU7lxr3rniDF1EXD1oKORnGBg0q1evfnz5Bw/qri0dNKYv/bz5Bm6p2eOh/Lg3SqY5wzeeQNa
lWByegBk/oqev4ff431FCz+gOQm2YfXpY+6Yq9yYN6aO83x4ywxyBYYBzX+F27ynHrkO/mGuY38a3sEFlVaWr+JtU0/OrU5e
5+S0CTJ1rjz9rLqwhK1Gxye/jMhxVRVmPX999cqkee0S3j5W/fKw8eSssfCE41RavgA5ERZd0GSHAYHNu3RZxAC1+hiulF1+
xsuYl9ocRi/v4Uu8/6pPjwJQ8XHqVvncffhe/vgo1AqwKt8ugxVe/vYjXrf7biuolN+MZN5HNQ3sZ91AhAi0cQSoudLqV/dK
iyfwwOJbp0I4o5i/RMtzJyR+N1d14Uhp+VHlm2vGp4fFlwdTNkOfv84Zmh+YiYe43HpS/W6mfPITIDZeinX5Gl/YpRumqP3t
WD35R2bn+B0F/JV7U4WLxEzir5R0mTMP+2n6Vhvw4W0gM/5uxTM8oR/ori/ED/fnz980bp8HnLC+DujNh9PG7InVT5+WT98u
n3+I1x5df1RZvojWFg3a6qMF4+kRdPJ++ZF9tRjQ36SbwN1Tz/OecfJJTfA0N+t7xgu4XCDSzLHKHd+V5U/L164gi1y9XT3+
taAnMSOtceBtUuLQUbqfiTAAiDDpmSA/s3BL0KZqc2HCiwep+cka8zPIGd+NJy5yiUqooJyjwxG59E9LPeODPS3kgmnpm2D4
AoYU/OzrzVGKMqrDm0Sm36Bp6flwCiAh7uevA15c9Q0VEnj9EE5pHfD/6xEbH+ppQcMN4EARfEPDjd6m8Y1XyKsYImcdYI41
9PTVmA/MqvfK18bMYzDMgLkQAWG4jmkJVHAgz61JmCS6B9QN+RF9jhTeOZBCP5wpSGTJL5rkdLxZ6z5M4rtkcfporf1wDCZs
Y3kYm0PH2gc6Yn0uA3mYu04Jmo9abZ6G6zj6zkdzDJHVrKbGPnPZyQK54R7+q8+Nna56IcX80OfriUWi4XDfhMuE4HYw8tZQ
f0IWR93xWbbFVwIFYEPgAL5yA+MK5ADnbVAm5vLIJRHYOf9jdW6lfOYCiE7Q03wo4olskmROdQGs3TCMracpbBo9H3yQ8vv9
2Dga9ojDBO4y4OAd1/1dkvrcM1ykrQu2Bd8k26/hUpshzRPtLGYnmNbMHWfL7lmRWYB7QNB7cukjoBpXEbxxXOkB4UAL4z1n
6x9x10zXSWLM86NRe6Ty9ccgWTghuXyySeUa2z2xqINR+Yi2fCm9GvqXJYaH5Zq+XOCiaDRsE50fpuoiLUCZ+GnyS6SrJWDs
YVtHSILQxIzDNa16C47OLmc7vY2XxEwBqOb1fDKftTb9gCzEzKFIMCKJmS8uljnTzc2BkCcs8YOEhVVtylyvpmTTfqThsAzG
+huyOuB0zNB8xiqXgHm4RiUcWfA1SHtu+B4fr7QlmQTgAdwlDsM4sCWLx+3sUTMDGTxwUHrDwYXPWXgnP9oYS7tONv7VgN6j
M5MJEC5p+3H93c/27N23a89uNP+tpqbyCfG1eXtVha52U7zRcFsNJpxSa6FntuNdOg4TEQrXNsfOjqCcqAHWtWjhBBIL0dzI
saLHZXPtDgOsz/xZI5DFHUaOGQvfg2BOzvguBH5mPNZqrmTStTUSbkxg5s4ERguGE80CVMynwWQoyO8I8da4zxuRPtwgTy35
1+4CYiV//SHZXbjPV9UUPS4meM8Jz+pS1Fgo7ukI7NqlgPoerksewdVrMYMkGA3m8A1YjNbdvW3IlE6mQYav5ZqcWBKlwgIT
sSjqbgzZTG5/RU6cb49LpA29C3UYRVptAHV+GYqGc3hluKAJqkQDirjKERL90rhTj63tk2mGiZNrcMSQr7DB6PE4G8wzOi9A
Ni8lqtHO+QEYM0OZXArHiXVvEW6RIZbAlnIiH5B8oH/aw3hdIu6bqUmWKbnTtnHMB+9W6W+x9wZNtPw7x8m/MDD+5VHRcEjU
ddorrlurn5NF2hy9T6ffx5ndNdZeKh839V0DA9cctQxugc+BPc4nNdkM3rYJeTGV7mX91Yx6gDyJqpdb5JE+t11NyzWCXWxs
CiZnJ7MZyEWbewH1Hlce8uZBRrG3J6gNyhGvl7x6TX3Atoj2geAYTWWAGLqXbHIbdH7Iz0YGUZ24fcU2YcVaD1+etps6RPfi
2ctkvlr65ofc9ANLn+ZupeUTxq2v8KodfkAzXUNVvofbwmAWaszP8Bs1hIOEn+Dqvl4aTVQwaOm6P37xhnl8s+Sq0caHWhi3
HLFCE9LFwyYyjdDgMH11zdgQd05dnNOWRlnB7iw9/lyY2u5bPsBEbnyfe1POS/C7ChJoGnuhAn5bcFyiBYgaaYi9IHR/c1Z2
AWzSKu745Pd90fHauMHO3Kdm7l+DPvka3R/mNjvJRA0MDgdedVqlETJguXjXdjz4/OwA/fAzi2VNiLUKB72+yloKAKrjoxmH
KPwQYl7BmQeX/KgYDkw0EmXPT0WTHmk5m8VjyUyq8EkIbeUUV/AIW17TlATF+TyXgRv+zQauqTVoHzwdFx7gzWluXjUAhlEA
pi2P0HL5AEUGrFnq7wGcBGQDW83gAl5y7ZqsCAXyjeB9T2vb5a4kyg+0saIc4mQ2e1xkF3Mue13DKu5UbeJ+Dtpn9NzLByhQ
bMHcCHg6i/cU+JwYOZiLY4Y/neOrBksH69hV1GyzCvv5ojVeJOlnkc6aSYYFB8YJDhLM15OJ0ZatTqe148yo0HhyT0PwT212
l4EgqMivJOEE+lVkQWHBqWIKi3rZ4Jwvj1HIec38yTUfohVgcye2A6rEazSbuM6kSRqWRxN6fkih5dG2aJiG2HAB92cBb+CS
abB1XSD8YIeEPoi3XMD4iPElwYkGEzBVQfvDvdU3KDwVXmtnKl51xkPn8hjuiGMAZ9vYCXFBnPWQEo8YYfFxaUsRJu1q5p9k
caJE3arIqqLSyBAa6Dlh2g1f94KkRjxYx/QDed3eqIJPnf6hdcMaosErrSTCO99VnS/q8bZ2Wj9U69eUcWTh1To4tupT8UHX
Hfq55BHzAiKxJIlLuwM5vGLO3kTcCIBQ5wgnSG3UEG/rhqDGteLTcO+GlYgbW1mcwPa0x/rWQ0Hkty8Qal6vvf2h9mm43m8+
+90TTKqwMTrrL/VbrVyLBDDsaVbr3S+M9cF8JmnNGsYn+nx46wklUVa8HxAGn9thTssGDY1PpBqVa44esKjpzaScjZuLT61M
puwTv8rwEXwEddYj9HsYRY3QdNlDYh7BTaKJBpPHNVSJbTo1KvjcSqWmhKlYnMmNPDdrIYautt9TyTXuEjNEgQgv/BGS8GlD
j4qpJd8tEmPWJhbarB5j1rIGer6BDxIJXI5IJGg8JxIw98glEpLpykafU9pyTzNgptg4hgpMMG52jLdAm1vq3IstQ/0tIks2
Ps69iyDMHcRNi1lYfNy5f2YilJLHcKYbHzf3w9AnvP8GaeLYBNsg/ARMMSsOF0ognsBhO308oAWjXXErLdD13x289vL5lx8R
/+k47Ov3r2Pt+M9Ia7Q9Whv/2fry/McX86wR/+k8AA4jQEuLS7VRoHT4njhQ0DpmjhhKxJV5PHzvEu5H4i5vOvtNo0RbivFN
GtU7R/AIRrys+zw6R/jeKGuxOLR680Ko+vQxD3fksPjd7C5wvFh58ahx6qwHT+NKKaNBjEdnlfvTpcVlvpwq8tK2otLi6dIK
7u+pLvxQvnCaggcXqncO486WK/eMqePG1fO8UrG95I2QAyrh79yTjAvqeKwlbpVZOv3T5BW+3748/bRmF9hPk1d5AKU4CPNS
0/P3ekrLn6Jz6PrjyuV5Y+Vs3zqhi4iYFUToONXN3GhrfsKL5iJc1fwroYZ7PnAGK64dZujZu+Xt7RRiROrHK9mkxIz8aC9n
QJ/7iCvJ5xflzG0/7vLOfX7l0zehM5rDMiHYMK1tWW6gzh1azcFZhW14WZi45WqA4U30335U+e5pdf675sB4SRuS4LxGjcU9
SpPL1TtTzaGJ0g5wCjqT1Bp45bMXjcUpPPtz9os1gImyNjTymuVroVV/vGac+AoGlzE3VVq50hygWdwGaG6fqAHIdz9OnSkt
32sOzSxrQ8vlDyrZWljPrlVXVowHs7iXsSksXhIh9Xk8+7a8zTdX4FQfeN+rSpu8/KSJQ3SQxSHoffF6cMDX84/NfW9sDr7x
502h3shmCUdnsJsdwj+7fAgsWgcNi2zYDIPkb921aT2sV+9Ve9O9B/s2WBvSD2a0DLkz0JWFY8/cz0432PLjBeFr/dZd+IJz
ES1uT5fFGY92ccCQtpHQ9hG8nJbSsCqeGOWpvbkGyUjlYDGnaEm5oHCnGCVb+4TsnSzZHI91GdXt24CdM/As+hT/1m2jks3V
z+2FWIMk3ALewUM9cIKfc07vvZJ5+SP2OF7UKbaDaTr9GgEWyY8E8ee45KvxAri2IEFFHntiU7+piHcPTbe93LmI927EN4bD
froOLCsX4p1hM6S1qPvpytAemGzweJqRQeh1uj/Ucira2Dh2kDnciFhBn4MiuFaC31jArNGJcU/SpKEdx4lb5gQhrVRUEJ3h
PtEgnNSYMROkxnnAJ01xmigAVNNm1LjmjIGoD2VwRjKY0GtiFhqHLFApHlXs5i1VyaLDSc8qVuQLaR9HUFUTvKFk/RLcOpEX
dY4R2s/m58S1Q0k5V7iGLoCqZTfeHHunYAanrGlpHBCbeHV8aIJWGCgUN2a20I6sEasP8JKcEOShbZW4xAiGA7e2wN5wCbuf
J2fW3Tn/8yRtleeGGm5dptMXKsufV+dv8JO7x3lHo0OnxbTOWvwtf27h+/8EyGlckPzlyYwzN9dRjryOXYIzHmdO8iqio9XM
jGdr4HZmF7yUgqQDdskoVsby1RvG0SncPn30e1AlHrTSbtzjn1hNYZjuqymzYIhVVxaa5MPr+EQ+fm60p7rwtHz9OFQG1por
O66QpwCsllByMMBciOEGwvtflud/NKaOGYsfAy1BO8GXWgADWMp0mrXwPAIMBhAYU1ehG9cpRHnsQqvfXFi3DM/TqHtop7Vx
+bIV9QAGnIg/qLfG7O3aOKfAaQXF3RNXXDlpwUSrgagNerqy9AwP4wbj+smkM/6vuoB77EUEgNNEc2yvNytZnZym2FYXU5W/
e+bkBuPppHH5WvXZCiZNPwVYeDwLzAQ+XimfPGfMna4efYbhrmCFG5evS05IxuOHleWLFBhAEQNOG48JW87Z3mMzIZid4EED
l45AluqdL3AO8vQk52LcKH37PFhNVZxZ3RNBAPYcA+ZYpkVnAuXnfFlZzDkI7kq36IsBI2aciR1QOf2U+o9PgHhkCbJeo1AK
HiZhBlTMlH+cBaPTuHiXL8OXpz+FDgJg5emT5StL0KDKZz9Wj5xZ/XgFKEixMR95MJJhdq709DLUUf3hS2P2UWnlU6A9okQb
GCr3P6ucO4NRPEtLxiN+c8Dh6p1jqzfPwKiq3D2JURYUt1ECLM9gJAbGVBxfYnu37WClxyeNW+dwY/P04/Jnj/mZOVgvSpyr
H2MghDkddbKac7zCLNc4eg9Z7ezF8tW5kEg7+0Nl7hj2zc0LPBOKvuUljHOg/f7GrSOY7XuY8h3jRWgLiELikuxWqHP1o/nK
/LeNNwEDpL/+lVWe3mKRcFt7Z1vbm+0RhE62M0xGmWUmU7ASRf7gjTyLV3e9tRdeo+FoRzi6cWNHGxA1EKE4KNrkQSFLiPnV
a5Xl2erc7fLkHb7Dg8ISUDk4glpNzrnEO7W6sMxn2puEMN8sOI9UOc6UgVGOz1IQf2kRScgnynj+eP/+BA8gNm0EbV0jwTmd
b2onaE7FW7f8oe2vNxu09UMd6R5SnCzvxxodu5m0/eZeJpom40/4FjwoZ0ELeWug0KIwxTvze03rnPlu2Bkw/FKZpM7jBjI6
XwcBVd9kBcqiaU8GYxNTUh9G+ZnlKOiWFk/M1KZLGW7w9qZnvg1JWFDCvTCQzfdbFhXYSxglDN+VlBdTgviPd61OfYNMFZtp
JJeto2VSDqbolzWlofcBLaQ1Nr3kRxoYi+sEuK5Nkzpjrn6fG9YqeOM5DEHiCizScAXJAdbkiecMHNeJgA7WcaWKAeitYxGp
yQqpwAehir17jSP3G+ICgi2l2NjQa91K0bCdAV7AklPUhkt+GM9BBuu4xfZUSsMzEOAfsELGqYYJrtXGAdqE1LBRwNamJd2j
1x6hkF7bZzIOBSZCUp+wo4f6KUybH2wU42Y1+bnoTKOYsNutVSLcNuFAhXyqaJc7D1zBFXHeGw3jdCUfl57Ok49qh8eeD3CF
puYwJCxkhyYP9YvQZMjbLDa54UYb1wqW8OOZ7YxTdA//Df2BIWyOeB+a846buELf4QfCNRTCs6Um3tkqPcfqGZ91vlxsevm8
fF4+L5/f9fm/pn7cNwC4AAA=
"""


def sh(cmd, check=False, capture=True, timeout=300):
    r = subprocess.run(cmd, shell=True, capture_output=capture, text=True, timeout=timeout)
    if check and r.returncode != 0:
        print("!! 失败:", cmd)
        print((r.stdout or "") + (r.stderr or ""))
        sys.exit(1)
    return r


def need_root():
    if os.geteuid() != 0:
        sys.exit("需要 root：请用 sudo python3 " + os.path.basename(__file__))


def unpack():
    print("== 1/6 解包 ==")
    raw = base64.b64decode("".join(PAYLOAD_B64.split()))
    os.makedirs(ROOT, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
        names = tf.getnames()
        tf.extractall(ROOT)
    for rel in ("chat/server.py", "chat/build_kb.py", "assets/chat-widget.js",
                "assets/chat-widget.css", "deploy/chat/chat.conf", "deploy/chat/xkt-chat.service"):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            sys.exit("解包缺文件: " + p)
    os.chmod(os.path.join(ROOT, "scripts/deploy-chat.sh"), 0o755)
    print("   已就位 %d 个条目" % len(names))


def env_file():
    print("== 2/6 环境变量 ==")
    cur = {}
    if os.path.exists(ENVF):
        for ln in open(ENVF, encoding="utf-8"):
            if "=" in ln and not ln.strip().startswith("#"):
                k, v = ln.strip().split("=", 1)
                cur[k] = v
    if not cur.get("CHAT_API_KEY"):
        print("   需要一个 DeepSeek API key（platform.deepseek.com → API keys）")
        k = getpass.getpass("   CHAT_API_KEY (输入不回显，直接回车则跳过): ").strip()
        if k:
            cur["CHAT_API_KEY"] = k
    cur.setdefault("CHAT_API_BASE", "https://api.deepseek.com")
    cur.setdefault("CHAT_MODEL", "deepseek-chat")
    cur.setdefault("PORT", "8091")
    cur.setdefault("CHAT_DAILY_BUDGET", "500")
    cur.setdefault("CHAT_IP_DAILY", "6")
    cur.setdefault("CHAT_MAX_TURNS", "12")
    lines = ["# xueketupu.com 客服环境变量（600 权限，勿入库）"]
    lines += ["%s=%s" % (k, cur[k]) for k in
              ("CHAT_API_KEY", "CHAT_API_BASE", "CHAT_MODEL", "PORT",
               "CHAT_DAILY_BUDGET", "CHAT_IP_DAILY", "CHAT_MAX_TURNS")]
    with open(ENVF, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(ENVF, 0o600)
    print("   写入 %s（key %s）" % (ENVF, "已配置" if cur.get("CHAT_API_KEY") else "为空→服务将以检索模式运行"))


def build_kb():
    print("== 3/6 知识库 ==")
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    r = subprocess.run(["python3", os.path.join(ROOT, "chat/build_kb.py"), ROOT],
                       capture_output=True, text=True, env=env, timeout=600)
    print("   " + (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr).strip() else "   （无输出）")
    for d in ("chat/state", "chat/logs"):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    sh("chown -R www-data:www-data %s/chat/state %s/chat/logs" % (ROOT, ROOT))


def systemd():
    print("== 4/6 systemd ==")
    shutil.copy(os.path.join(ROOT, "deploy/chat/xkt-chat.service"), UNIT)
    sh("systemctl daemon-reload", check=True)
    sh("systemctl enable %s >/dev/null 2>&1" % SVC)
    sh("systemctl restart %s" % SVC)
    time.sleep(1.2)
    st = sh("systemctl is-active %s" % SVC).stdout.strip()
    print("   状态: " + st)
    if st != "active":
        print(sh("journalctl -u %s -n 20 --no-pager" % SVC).stdout)


def _blocks(s):
    out, i, n = [], 0, len(s)
    while i < n:
        k = s.find("server", i)
        if k < 0:
            break
        j = k + 6
        while j < n and s[j] in SPACEY:
            j += 1
        if j < n and s[j] == "{":
            depth, j = 1, j + 1
            while j < n and depth:
                if s[j] == "{":
                    depth += 1
                elif s[j] == "}":
                    depth -= 1
                j += 1
            out.append((k, j))
            i = j
        else:
            i = k + 6
    return out


def _has443(blk):
    for line in blk.splitlines():
        t = line.strip()
        if t.startswith("listen") and "443" in t:
            return True
    return False


def _sname(blk):
    for line in blk.splitlines():
        t = line.strip()
        if t.startswith("server_name"):
            v = t[len("server_name"):].strip().rstrip(";").strip()
            return v or "(empty)"
    return "(none)"


def _anchor(blk):
    pos = 0
    for line in blk.splitlines(True):
        pos += len(line)
        if line.strip().startswith("server_name"):
            return pos
    pos = 0
    for line in blk.splitlines(True):
        pos += len(line)
        if line.strip().startswith("listen"):
            return pos
    return blk.find("{") + 1


def _patch(s, inc):
    parts, last, log = [], 0, []
    for idx, (a, b) in enumerate(_blocks(s), 1):
        parts.append(s[last:a])
        blk = s[a:b]
        is443 = _has443(blk)
        nm = _sname(blk)
        has = inc in blk
        if is443 and not has:
            p = _anchor(blk)
            blk = blk[:p] + "    " + inc + chr(10) + blk[p:]
            log.append((idx, nm, "INSERTED", True))
        elif (not is443) and has:
            blk = blk.replace("    " + inc, "").replace(inc, "")
            log.append((idx, nm, "REMOVED", False))
        else:
            log.append((idx, nm, "already" if has else "skip", is443))
        parts.append(blk)
        last = b
    parts.append(s[last:])
    return "".join(parts), log


def nginx():
    print("== 5/6 nginx ==")
    os.makedirs(os.path.dirname(NGSNIP), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "deploy/chat/chat.conf"), NGSNIP)
    inc = "include snippets/k12-chat.conf;"
    files = []
    for d in ("/etc/nginx/conf.d", "/etc/nginx/sites-enabled"):
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                p = os.path.realpath(os.path.join(d, f))
                if os.path.isfile(p) and p not in files:
                    files.append(p)
    hit = 0
    for p in files:
        try:
            s = open(p, encoding="utf-8").read()
        except Exception:
            continue
        if "server" not in s:
            continue
        new, log = _patch(s, inc)
        if new != s:
            open(p, "w", encoding="utf-8").write(new)
        for idx, nm, act, is443 in log:
            if act == "INSERTED" and is443:
                hit += 1
            print("   [srv] %s block%d 443=%s name=%s %s" % (p, idx, "yes" if is443 else "no", nm, act))
    if not hit:
        print("   !! no 443 block patched; current listens:")
        print(sh("grep -rn listen /etc/nginx/conf.d /etc/nginx/sites-enabled 2>/dev/null | head -20").stdout)
    t = sh("nginx -t")
    print("   " + (t.stderr or t.stdout).strip().splitlines()[-1])
    if t.returncode != 0:
        sys.exit("nginx config test failed, not reloading")
    sh("systemctl reload nginx")
    print("   reload done")
    r = sh("curl -s -o /dev/null -w '%{http_code}' -H 'Host: xueketupu.com' http://127.0.0.1/api/chat/health")
    print("   local nginx probe /api/chat/health : " + r.stdout.strip())
    r = sh("nginx -T 2>/dev/null | grep -n 'k12-chat' | head -8")
    print("   nginx -T hits:" + chr(10) + (r.stdout or "   (none)"))


def verify():
    print("== 6/6 自检 ==")
    def get(url, timeout=8):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return r.status, r.read(4000)
        except Exception as e:
            return 0, str(e).encode()

    st, body = get("http://127.0.0.1:8091/api/chat/health")
    print("   本机 8091 : %s %s" % (st, body[:120].decode("utf-8", "ignore")))
    st, body = get("https://xueketupu.com/api/chat/health")
    print("   域名 /api : %s %s" % (st, body[:120].decode("utf-8", "ignore")))
    st, body = get("https://xueketupu.com/")
    print("   首页注入 chat-widget.js : %s" % ("是" if b"chat-widget.js" in body else "否"))
    st, body = get("https://xueketupu.com/assets/chat-widget.css")
    print("   挂件样式 : %s %d bytes" % (st, len(body)))
    print("\n完成。打开 https://xueketupu.com/ 看右下角「客服」按钮。")
    print("日志: /var/www/k12/chat/logs/   限额: %s" % ENVF)


def status():
    print(sh("systemctl status %s --no-pager -n 8" % SVC).stdout)
    sp = os.path.join(ROOT, "chat/state", time.strftime("%Y-%m-%d") + ".json")
    if os.path.exists(sp):
        print("今日用量:", open(sp).read()[:200])
    lp = os.path.join(ROOT, "chat/logs", time.strftime("%Y-%m-%d") + ".jsonl")
    if os.path.exists(lp):
        n = sum(1 for _ in open(lp, encoding="utf-8"))
        print("今日日志行数:", n)


def uninstall():
    sh("systemctl disable --now %s" % SVC)
    for p in (UNIT, NGSNIP):
        if os.path.exists(p):
            os.remove(p)
    s = open(NGCONF, encoding="utf-8").read() if os.path.exists(NGCONF) else ""
    s = re.sub(r"\n\s*include snippets/k12-chat\.conf;", "", s)
    open(NGCONF, "w", encoding="utf-8").write(s)
    sh("systemctl daemon-reload && nginx -t && systemctl reload nginx")
    print("已卸载服务与 nginx 注入（/etc/xkt-chat.env 与 chat/ 目录保留）")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "install"
    if cmd == "status":
        need_root(); status()
    elif cmd == "uninstall":
        need_root(); uninstall()
    else:
        need_root()
        unpack(); env_file(); build_kb(); systemd(); nginx(); verify()
