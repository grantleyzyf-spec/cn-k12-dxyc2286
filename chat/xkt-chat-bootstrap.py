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
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
dm5s0EfHGDaO5BtvcLSRS+2YVl9eKl+aq3yN6OB43PoWWFg7jngAEGo9gq1Tw8m+gXyK4QCKZmyLCTAUD7ta+IK4iRQX5F3J
gxMkUGL7Ptm/a++efVv372KFYbUvn2ukE6FQTymTTXX39wQLw0YVanCgH/QeFijwYjz4ln5m872KjhOsjyzwEYOpESDXGv2H
eyUT40bAWJcstPIRuAKzLszG3FJgCcwkZUaTS9QSf2sKcUj8ZVLNslRCHsjnAkUZw3WcL+UcWtG0vA8yHZJHyQLXAOUdhTNK
IJFUYU02S5r9aYL+cPlYrzeEJAoCZpERSi5TKKCiA1IiYJTg7GZwmu0dctme9yS7aDBkuz6yAV4KhcO+Txo8mQGMI8G+eNDf
Bv4GE8XeQx2RLg96L+DWv7fgE75h2LqzzVxeZZkcU2L6YXlDJpfMllIys/cgPwDEpjptDZYK5LeBDRuuR+uob4aq2K+1q3bm
CEvXYnqfAD6LcNc+DD6qi6dCuhgbgeLG71eEz8kL9QcbfMHBYkaVvQp/Uyhmcqq3oYCePXIKahR8nn2fGFOeM1RAdXIiZ2b+
2sKDzcCDK99Mls/xBSVZKmZhOVHaWWCANTMU4iDDI9FNwTD8LxJD8WykPBG+2m0ks+xVW5ku/20LzL9SlR0W3J1kDXZLoQFe
KXIKaB36ewhW75VbP3LdAhbw8vlHMRZqsPS4BXpcnTu/cnEWk55M3bX0myPQFGaB/2aUqmb1TrDALtZg9SCNMaf/aAPp/gHA
bUTSPUWlWMcIj5uNCc9oSRxqwYNV4lJ+eX5DGu0axd6iCysLNPFeia5ps5Ow2oGqU4d82tTj5flT1Xufg/pSOfMIc7rQav/z
2Ony5MTK57OSc7craDN5fh8d89XzfzU2R5pf5//6Iy77+DsXzd+mjTX8f8LNzU7/n5aWaPNr+++PuDo+zmXULs92mRtYINPi
dnNByQhNjRlunJ6taVUuxnOyOpgv9ovMDx5PRztnmi4Pysm4AspFVvZ8DKwU17U/z3u4V2Le/g3qZ3K928lrIl8cjlvtKc+O
3KFMMZ+jnCWZrOxiWO0YkpPt0L4ar9F0bNYjVzpplQZ11vORrFClRHYwAaqPuG2Xk/FGz4egFhaHP0wMxZsj0Q89e/J75MF9
xcwhQADkehwd1z14j7kkBgr83tOxOwcgstkuz9+APnJq23B8oJRVMwGU/TqB/t1D7XrZ57+hpfymbawx/yONTZtq8v9FXuf/
+0OuDcyxrWOb/bgBsIFhEjdTIeL7PLTdj4cEDNVFnuWP6XnDHmOMRlrGABqEkM1zbckCRISiFvNDw90FECzuWmibpRQW6Ib5
qyAg9L2zvFNktZtH/LBdeUVlb/bBv3UK/HfgI1BLA7v3sTcx6lKVuxOpVLFu4Z354mCimJJT+Iu9yUtAje6h7rT+Cn/VAQCa
Y447hBme9byMQSCWT6etLygg0vkQDbBulUefskg0rNibyzlfjnpo2G657MXp/ptXKFvdM9YcDm9koI4yDJ+mrGjfYGztiQVt
6kvtztHqyyXt5M3l+TugZ4O50dOdzmRB+Hfnc2B353Nt1mcqiH2FDs9DfepA1vqONWwOoXPSlgb4hV5uaKvEJYpxVWBmqRLD
QPu4VO8kYMtmvkAxpZh0L4WnCSkZiLpls9gt3KK3+R/ndf2fcwUda+Pv0cbq8r+xsamlxSH/myKR1/rfH3JtYIG3AyyZ55nw
Smo60IpPPJIkGTyxhke4PRns5D5SwBjPcig2kT0UcPslCK33duxnzLlFYNnEGZHy/VIMtSq/hIFLYC5nswOH+3skfp+VYsFg
EN077Hlma7eD1mmMAzS0uBluGeMaVv7xSA1wkW/FBvygqOuXEjoUZk3sQgCr00uVmUsez/L8xMqRL1YuzgPoiI9pp8/zIGdM
VHrnCrPvcrMqnmaM47HGt3PVWcy+xDYyfkiCkTSTE0yBnuGawt9SBl6M1inPTTFY2OCPdudrZttLR6BQqNFHqWW/G7OWse7C
88ZnYHmvLLw00vNWFubKX45VfrhNAdinq48+w/Ce66dobK1HCdCEbSc7xGwnBvo9HQ3ADR4H6M9sWITs2ANYfkJvh27kEcZ9
/WN3WX8PM8OOpr7BRLX65jcfGooqmgbFhYURdWByfQsUN3L8LK/4YWHy45aan+GS6md9CaUvm+nxY9SuTImd/KxUzMKjYFE+
WJIxM6C4lzGa15MuwvxAbSUotgVFC9sSirxr//59H/FauxK5VFYu+tl+HS6+5Ce8Hjplwg1YJVhIqH1B4WjgrXef6FHwr7cb
l1u5u9vn83ne39ZNm/omFErhgpD9TKJ0xvC3v4dSKEg+T/v+rft3dG/f/dEaNWjvHsp/sPe9dZTG7X0o7NGHjErL3LDDaGav
ZB1RHkVPsdcFr89jsM0qtfA9VtN3xLgoC6Zg2JRkviAHE9nMcCmXVGiH7FAEwBc5fCkEiHFOrAOfXiLwg4NyrjHYEihkS9gb
Yts4wz1aZz18hTVQfZVgFGxc7V6lhvuxPqhlWN2YvqtU1ctgtRasZM1OXbeWUQirRaJ6vW17t2NjjVH2NouEo00e4CMMogUe
CeLmspc2rQVv+Xn6IqB3XKKlA6Hs3Prufmz5/W0dUjqRVBWpy/Puro/3vK8/TPaVcv349P19+qP+At57MEgyhccDXoMZ/Uzw
mY/vxOcx3VG/DBNA8ab8eBamqN35/vh+WDGAzbrRgR/zB+iTKvgBPABWQoU44LjYtg+jzSTRHpYvnKBcwBeXFya1Y59VFvHc
rXrqO/68Oncaw5yc9T2gbjI13+9VBHL8iCCbx5BSscVfUnl+0nQml0pks96i1MHTqnYGOzdu6NoI1Bd7/skD/TVFO0tNcjgc
6Cy9k06nu8yyCHZjnHVAnY5MF6wO9AP+Rroo0jSDRCwmcr2yNwvDBW99GGTq67LWhqfWeE54ClTavvddHJQO7Fayg9LsSV2U
XwMjMPFJRoWFtMtH7SSxHT64XZ7tOzEH76g5igiLEwYfDdK5D/Bfymceqmzf2THYBdW27yTWHPRj8D10w7MHM4Amhgh9hOOj
U5Ot//M9JHFpgJ6nOBJGWz5YNvZAH3BYegaizV7KYeNn/fFG0STmT8Ge0QtOSgWjXTFYuKPLQDXj50DlXGlALoK44yiYaGfS
dPKVMp/QCIJSkcmVZPPICFYNzFUAFq0fKaM/N8jhAKCmOTXUtIMaNRWRjgd99tqA1KB+IKem7e9c0aNKKUSwu5svUt3dXmkA
RDkISRDc3gg07t0DnOMYnnCwGWntdXnss0FXkM+wibeZl3fubRYNRqkyv4feBVHWeMPBaDPB2NQMt2J4QwxG3AITuoiBzmF7
5/gQikh1rxeonvFZBzeoQNe8GJ5bVGQhKSyM38EZGCcS0rfbz6cPr9sR6+8CyQSr4959mHxHciSeojRhxiNKQmV9NKYdn6T7
mhtrfUdlI0l7+ehUeeyaZB54Srb87Tw9VvnmU/NGT1z23fXlhTOUUmfu6crFWSowfrb82WN6Swm86dmNu4DW8vwpupl4od+Y
DYqzKj3tli3fOd2IXGo8D7h29jb+wVMs+PNnXPhpNqJI6wYhr8/IbGYgo9pmJcg9pdRDMk8khgYgvzw/8uefx474O4O/PL8S
A7W0rYs0BD+zTGCVnPJg/h7kE1jEvB+0Cx4cP5NrRBn8Y5zoDpLuoZ9jUwlQ0fiPNwCeWZta1NmN4u31Wii2kXVVH9vMotQ6
n45YwzJddc7jGPdlKOmJRQCZlWK2ud+fgTUPNT8/ZrxJkOaJRWElrZEFKAnIOxXqIU74m9Bar2RI8+pxkEe1VRQ9J4LtjZyF
WjoB4qyVKEidQVD1oaCgMXEM6CDEtYFh9t5zs7AMo1uMkQJuGrMNAMvi9ynGj7sjwiFuAY2GcKEeIW1XwSWMUk9gEDCB+AQu
1vb5MStO9qm72sPplROTDiwUl067Uht5wJRgiErNQAuZRiVJogkZJ8touZCigcsCrJQWTup25ReEYV/NBF0Q2FqLGhShpIFE
FeMxIKDjPyLhKykmWpawabjjGEiAAtzAv6M2uY50Bhg0ViQe7GhQ3FutuuKi1K0cO71y+9ry/Jnyxbvay4vuWlu3mk8lhr1i
SgqQaPCh7ZHGH17prU8Cbw0E3koZUuxgKa8mvJlCN9qEftYzjDvX3ZlCfCfmGRGw0gWnRWTRZfVmUaHS7S6sNJhR+xjprhZ/
ExzQEYmyp0n0JQMJcyPHQJEYtRJOb4tUYcWbLjjUArU47MLsaq1Sny646vM2hh5KygWV7aA/GKtXAxhJYjwsKXIK6IOMqXYQ
9l2kMBgkDNuXdijEu9uFXGA1iewNifHayb/jIPWUcANYsoLSWwYwhglF8x+EojFuqwLNFCTLUJiIgUITsb2gbnWILqH2prdt
VdyI1CnMFYT7BQa5pUGpLs0FPqiuQMF8vyS4EBWzfM+Buuwm7CUXZssKboPa0B/sTLwez7O3dsXe+jD2VvsqDErPzK4k3LrC
EgpzqKJp4epkkETB7mBdpVSUuxNKMpMRMwoxx/xT7hNdRHPMna6d4u2ftFMuI0w+CksGcxxqja/jU0sTmMnGssuJXst4NiK2
+M6IT/VcncD0sJZsva5uPZiFtCaXqXbyBn5NhTTFV0hw6rHnMxUJT8vX7pYXpvEjN/QVmPKFZ9rzKfwQzp0T5Vvjyy9vlY/M
YRc8lVsPqveOauOXAVcP7kXSPhlofSvXbv88Ns0zFi8vnNJmr/88dpY+5TPNo33w8ytY5ix+FgcWXoLJ6QGQ+S1uDj55jJ80
mvsBNU5QH6svnvG9u8qtWW38BC+HH6JBrsBIodmv0RN8/Kkt/w+zZf9x/UwXNFpZvIYfpHp+YWXsJienSZDxC+WJl9W5Bew1
7o3y7xVZvmaFRS/eXLk6pn+ZCT9QVv3qiPb8vDb3nOO0vHgJSiIs+oaTGSkEavHCjAgTavQxPEybecnr6N+9OYIbwUeu8PGr
vjgGQMXD8TvlCw/hefmzY9AqwKp8twiKevm7T3nb9s9fQaP840n6J6smgP2MjxQhAk0cAequtPL1g+X5k5i3+M7pEBods1fo
BO+kxD/fVZ07urz4tPLtde2LI+LJo3GToS/e5AzN82Zinpc7z6vfT5ZPfQ7Exu9mzVznZ7/0ESrqfzM2T1soU9P8Mwb8lm+4
il0U/RW/pVcznHnYTxN3moAP7wKZ8XcjpvKEcaDPgSF+6MI/e1u7exFwwvZaYDSfTGhTJ1e+eFE+c7d88Ql+Genm08riZVTI
aNJWn85pL47iPvBXn5pfHwP663QTuHtqed4zQttWo/ydnfU9IwU8URDv9LnK98Yri1+Ur19FFrl2t3riG0FPYkY6BsEPTonc
o/QJJ8IAIIJdNEpb0WLngvyu9bMLL+ZT85PC5mdQMr4HEy9yiUqooJyjHIlc+qeljpG+jgbapWnoGmV4A7oW/OzqzNEbeUiF
O4m0wz5dGfShlSAh7hdvAl586esvdOMXitDqtcD/51M20t/RgLodwIEqeIe6Hd1N4B1vkDfRT/t5gDm20NHlUCiY0e7Vb7TJ
Z6C7AXMhAkK3HVa6cYEDeW7YaZIYHlhuaKvRZ3nDBwfe0A/rGySy5Bddsu7NGUdDTOKOtGhhGsdDHINRU58ewO5QdvtAS6zL
pkMP8N1VguajXutJcS0Z8HykhoiiejMOjc2mSgvkBjr4ry47dmrRC2/0B12+jlgkGg53jdpUCK4qI2/193QnRMY7bogbfCVQ
ADYEDuCHOzCvQA5w3obFRD9BuSJiP2d/rE4vlc9eAtEJ6zSfipiYTZJ0axjAmh3DYHuyctO4OcInKf8EIBtB3R9xGEVHBA7e
8kXAK1KX3QhG2tpgG/B1sr0Kl5oMqSe2M5idYBrGPeqOdsNJr8A3SXCD5cqnQDW+RPDO8UUPCAerMH4Kbe1Md/XWOknMeZ4h
tUMq33wGkoUTkssnk1S2ud0Ri1oYlc9oY7ulU8EtaIlhzlx9uxe4KBoNm0TnOVVtpAUooz+NfYV0NQSMOW1rCEkQ6qhxeOxV
q8FRCnO2y+t+aqYLwGJezSfzWcMvCGQhFg5FghFJGMd4nmZ9r/sPQpmwxPMJC61al7leRc6m/UjDgQQo628nir3WvRuycIx6
3WCqK1TDUgRvg+SWw92AvNLWZBKAB9CRHKZxYGsWM/LsLWZ6M5h3UHrbwoXrrLyLZzjG2rYEx68M6ENKnUyA8NTbj0f0frZ3
3/7de/eg+m90NZXvFk/r97co09ffZG803OTAhFNqNfT0fnxAWTERobCzO2ZxBGVFDbB2ooUmJVYi28hy6Mdls9MJAdvTfzoE
svjMkcVi4W4KunHGHRV46nhsVT/spK/XSOi7wHTnBUZniqP1Ylj0y8UYCvJPhXgdO+xupA+7lHGSf/UhIFby1+bKbkNX4KIi
q3Fh4K0TnjGkuGKhuKdM2M7TgtoRrnk9iAfcwoIkGC42vAuL0dG8twmZ0so0yPBOrsmJU1OqLDAR56b2zpDOZN/ByIk093iK
6rq7UINRpNEEULNTQwFzln0aLmiCRaIBBWXlCIkeacS6jq2+S1MPEyvX4Iyh7USX2eOxdpgXtH4jWf82kWN1zvfCnOnP5FI4
T4zPF6EXDbEE9pQT+aDkg/WnOYxfVETXGsfrBL1uNXUc/cJPrPQ0mO5Dow3/znnyL0yMf3lWuE6JmkF7w/Zh63WySJNl9CkJ
fpyZQ2O4W/m4qm+bGHgsqWTQSz4H+jg3arIZ/CAnlMW39OnWV2bUg7S3WPRyjTzSZder+WfEOLuY2BR0zk5mM1CK/H8B9Q5b
GdrNg4LC/Seo9CUiXi/t6tXdJjZFtA8Ex1AqA8RQvaSTW0AruI2WwO8yAjRaiQynZ0Q4Fotwjwx8hnqMZYu9388G+3AlqrsT
rUO3jJM4XeIH4iawfvoSn3kw53MOV77fPhxgOJApuLx4UrvzNX7Ah6d9po9blR+gIxrou/zzHPqnOmwfsaYNg0nUjOnTgnyf
Xk8HLdnaMjGh/saNPV6xpHIcuNqNHm+ITR08OHT7nHDaJtYubozTJ4vws90TLxAu/5D4pTn6VBYlnz4itFrXNVx6S4Gu4z8T
bykSewts3w5+HgICDX7SYQj/iSchwpFCt2lQV9e3PWuoj6g5Pl5SnvlBe/ktoOb+Ifu686mbf4ihGxV+L8Dmn0mOS3Ty4pDx
yAxCo6k/QW0ALWam1cTk/eIfM6Pc4ehZqDvo6Y57wCDf4KaO7l8o6aiBGmXBq2atdEMG9DHv6tspPj87SD/8+pyvv4ziXra8
2rIGzXEZhRMYfojFS0Z7iq9nuNwdHHUT0Ounok6PdCKbxexrOlW4aUU+rOL7QsJCURS5mwKc1qW2h3+12q6vhRQAQLnQA7w7
9ZVGF2AY/qBbKAgtlw9QSMSqtf47gKZNNrBNj6rgNVdvyQjNoB0f/JjV6taG7RWVB9oY4R1xMgY8NrILS9I8rTGqWxds8fER
crBa96EIyjRzuXEDns7iRxh8VowszMUxw5/W+eXA0sI6ZhMO/7Kwn5/W41cy/SzS6jCdDDgwT3CSYLmOTIx81VqtOpy1oEzz
yW5c4R9ncZvaI6jIv7fCCfRKZEFhwamiC4ta2WDdBRimWHuHVWiz8ujoW3dBt0CVeIt6F9cwBaWBxFC3mu+X6Ri4KRqmKTZQ
QMc04A08Gg42rgmEZ7ToVvvwEx4wP2L8oHPUxawsyqhV2X2cg2L/xWu45OJ33HjMYB7jPHEO4B4CDkJcEGctpMQlZlh8RNpa
Uvvyxcw/SI9GibpNThTlIs0MsQKtE6bZ8TW//uTGgzVM35tXTQ8dvGrWHzoNdRANbul8FO65O3m+pMabmulUtFirfuDMwu8G
4dyqfYsXbkji7l1iUP+6kjhoxQPr3hx+P8/0nnYDIJZzhBOkPiqIt/H5I/dW8XJ1WjFeokcvixPYjuZY11ooiPLm15Hqt2v6
fTgvV78G/TpgN5upQXd01nZpMHq5Gglg2pOt7j0gTJC+fCZp2EIjo10+/KQLvaKi+PFDmHz2YwA6DHHVhJFqVK8+esCi+h4t
lXTvLl5OmUzFR19J8RF8BG3WIvRbKEVuaNr0IWHOcJVo1MUkXmUpMVUnt4rrXlQcNfSFxfrabT9qNcRwA/G3XOTch0SPzSDC
i10WSdg0MKLCYOY+MDFmWJnkpR9jxmEN7ucDH3R3o3XT3U3zubsbbI9cd7ekb9DjTlra2HRnwEyxEYyRGGVc7RhpgD431Gya
NvT3NIgi2fgI3zMFYW4hblqYhPERq5/QaCiVGEb7PT6i+/3QI/y4D9LE4v3rEnfjtdviiCdw2C4fj+TBMF/0IQa6/ruj9n67
S8R/WpJ9/fZtrB7/GWmMNked8Z+Nr/M//jHXKvGf1gRwGAEK1rozCpSS74mEgkaaOWIoEVfm8XDHJHQ24vvZlPtNoZfmZOYe
GNV7RzEFI36Q+yLuEXDHJ+MkOLRy+1Ko+uIZD3fksPj3123geLXy/DHt9HkPZuNKyUNBjEdnlYcTy/OL/KxUlCWfoeX5M8tL
6LxTnfuhfOkMBQ/OVe8dQbeVqw+08RPatYu8UeE78nbIApXwt/ok42k5prVEP5iFMz+NXeX+9uWJFw4Xr5/GrvEASpEI80rd
/Hsdy4tf4B7JzWeVmVlt6XzXGqGLiJgRRGjJ6qY72uqP8GNyES5x/5VQw70fW4MVVw8z9Ozb+t4OCjEiKeyVTFJiQZ7ayxrQ
Z09xJfn8op7u02Ovb3XiK5+5DYNRH5YOwYRp+FzZgVrdr+qDMyqb8LJgv+QcwPBr8999Wvn+RXX2+/rAeE0TkuA8t86iA9LY
YvXeeH1oorYFnIx7KkUHvPL5y9r8OOb+nPpyFWCirgmNNo/yTmjVH69rJ7+GyaVNjy8vXa0PUK9uAtR9IxwAuWvj+NnlxQf1
oel1TWi5/CE564T18np1aUl7NIWOinVh8ZoIqcvj2b/1Pe45gRYv8L63KG328kwThymRxWEYfXF7qNfX8fctXW9vCb79582h
zsgWCWdnsJ0dxj+7fQgsWgMNq2zcApPkb+3Odx2sU+0sdqY7D3VtNBzSD2WUDFn1uKODc0/3Z6ev1PL0gvC01i8XnqBKrsRN
q1HkeDSrA4bkI0K+IfgBWnqHTfGXUf62M+fyGqkcLOVkJZkoyHxviF4bTkCmm0o2x2NdhlTzi79WQzSLW2t/azdRyeZqTVwh
1uAVeny3GK7e2ZzVyvVK+gceccTxY5zC10tR6dcgsEh+MIg/RySfwxi2+RdBQx5Tv6/1GOLDQ1anl++x4Vc24pvCYT99Diyb
KMRbw3pIa0n102dBO0Dn5vE0g30w6vSNUGNvzcTG4h5m2U3DBrosFMHTAnzGAnqLVow7kjoNzThO9IcThDTe4gLRGu4SHULd
Xo+ZoGWcB3ySpl9nAcBlWo8aV6whD7WRC9bABR26I0TBPUKBavGoYjtvFeUs7ruoWdmIfKHVxxJUVQdvqFl7ILZGoEXN/gAd
7Pg5cc1QUs4VtqkLoJzsxrtjugFm0HJLSyOA2OiGkf5R2minUNyY3kMzskZswsNNclSQh3wm8cAPFAeubYG+YRN2P49NrukW
//MY+cFzRQ39kin7QmXxRnX2Fs/cPcIHGvc1GnTtrMHf8OcG7twnQE6Mg2L1y/NJa2m+RlnKWlwAJz3WkrS5hvuNemHMrYG+
yjZ4KRlJB+ySkY2C5Wu3tGPj6Bt97DEsJR7U0m494I+YozJYvcWUXjHEqktzdcrh5/hEOZ432lOde1G+eQIaA23NVhyPv1MA
VumWczDBbIihd+DDr8qzP2rjx7X5z4CWsDrBEyeAXqyl7x018DICDEYHaOPXYBjXqERlzEor315asw4v4zY85EatzcwYIQ2g
wIngglptzPTFRpsCzQqKuyeuuHrKgIlaA1Eb1unKwktMxg3K9fMxa/xfdQ4d6IV7v1VFs/jO642sjE1QbKuNqcrfv7Ryg/Zi
TJu5Xn25hK8mXgAsTM/Cj39PXdCmz1SPvcRwV9DCtZmbkhWS9uxJZfEyef1TOIBVx2NCl7P29/hkCKwTTDRw5SgUqd77Em2Q
F6c4F6MX9N2LoDVV0bJ6IDz8TRsDbCxdo9OB8jxfRhHdBkGXc4O+GA2iB5GYAZUTL2j8uAHEw0aQ9dziJHgMhB4tMVn+cQqU
Tu3yfX4mXZ74AgYIgJUnTpWvLkCHKud+rB49u/LZElCQAl8+9WCYwtT08osZaKP6w1fa1NPlpS+A9ogSuRNUHp6rXDiLzgML
C9pT/uWAI9V7x1dun4VZVbl/CkMoKChjGbA8i2EWGDBxYoHt276TLT87pd25gF7LE8/K557xnDnYLkqca59hlINujlpZzTpf
wcrVjj1AVjt/uXxtOiTenf+hMn0cx+b2JV4IRd/iAgYxkDO/ducoFnsMJt9xXoWcNGQSl6S3Qpsrn85WZr9z9/AFSH/9K6u8
uMMi4abm1qamd5ojCJ10ZzBGmaEmUyQShfXgF3nmr+1+dx/cRsPRlnB006aWJiBqIGK6X1A8EmJ+7Xplcao6fbc8do97XVDM
AS4OlqBWnXOu8EGtzi1yS3uzEOZbBOfRUo6WMjDKiSkK4l+eRxJyQxnzj/cc6OYBxLqOoKypJFjN+bp6gmJdeGtOAZQDtWqD
snZkI32HFI3lA9iixVVJOaA7KpGZjD/hWfBQIgurkNcBhc5GKd6Zf9e0Zk/bDjsDil8qk1R5UEBG5ccBsNTXOYgxaNqRwcDD
lNSFIXx6PXIyoTME/W3dHX07eNOjmTsFCQ1KbC/0ZvM9hkaVJpcljD6WU158E8R/vKsN6tukqphMI9l0HSWTsjBFT0KRXXcf
UENaxfcjP+iiLK4Rz7o6TWqUuVonNmxV8MY6FEHiCqziepBiAavzxDoDx1UioIV1bG/FBPTWsIhU56BQ4INQhWOee+S+Ky4g
2FKyiQ3d1hyYDJgF4AY0ObnoevKFjlKksI4YbE+1FMyBAP+AFjJCLYzyVW0EoI1Krp0CttY16Q7VmUIhvfqeyQhUGA1JXUKP
7u+hqGye2CjG1Wra56KcRjGhtxuHJeg9YEGF9lRRL7cmXMGDYT4arkG4ko9LT2vmI+f02PsxHlQ4kiFhJTPuuL9HxB1D2XqB
x67+JraDHLGPp/czTqE7/DeMB8anWYJ5yOYd0XGFscMHhGsohLmlRt/fJq3jEIlbnf8Pnbn8J11G/s9sWkWXhX/D+U+4MVxz
/tMUfZ3/+Q+5Vs3/afAEnf+UT9/mXplgCqFj7Mx1belzDHT98RR+QYrM+5kFbfaKHgs/wUWm7VTDCtT12sAAnns66NWhuUpx
Dg7siuX5kx5P+cux8o27aKouPlleOIV2DgU1omr89QKaEotPqi9voNGEPrYX4YmhGPNOgZUHCn7l6g1t9rpphOnBj0c81Scn
K+cnednq7W951DRFfZ8zAtVFYDCPiQf777Ml7eQMqtKmHRNi3NaCH9zYwScU3s3jukXwcs0hkCN3pd0dyeMRuRS96zsRklwH
wZE/UegLCBndJYU7EQYW6EqsaNRwGsNXHs+7cGs9BeJ7Urb0Vmt8JsWPGV5h9sJq2mE79qEYWVC5emjPrEPipASmRaCcnFLX
qHE6gG7e+iD/82nl3I3KxNd0TnNsghtfaN3Z03lZGjaOVuyN1oVPp5tfESYA7dhnywuT6LN+4Rl+8LEmtdgrNcSPEXkGAX7Q
9LX2cBr3ehYmoU9gv1af3gAupK/sTRr5KKxkdjRpnmg5STp+Fgxpbfx4+fq0lZac/f8pUiCYucbKJ09CM3ybDt7h1so1sO2v
RIc2NsYjEVuzjqaG4k0IZwh4hX7wUFpM6tHk1vLK2Fj5wQuRCgGZCI93T+McOzbOtzMoPcEExuteHRdfeKM6qyHBw3ahHHVp
8pj+iwAa0Gz4kM2P21hkqZsZ2sSLpZv8EMtCbncX/vrDTcKESw97T/lGyvML1Rdn9+3bjzkbSLKAYFm7j9aiUvncXHnyiBUe
72KXx7Nr60fbu3fu/Wjb7u08Grm2KBLIEGnmnbixbuJQWzRL+Z6QdvoxYCPpxw4Jpd9rcaB8Rz84cQvLtDjcWiL79Th8M3L+
4GiX0/d1Vb9Xm8+r7ueKCKzDIdV0cF2vM6oa1lPzkEXAHyaSSdM4X7e7qfjr9DntKWHexx6LzcXPnNB0cJ5E4FkkPx+MuBqL
yb5a+7DWbxNbxKyjfU4Q8MJcOnqEb7uLWyH3fcXSr+77WttdCwKv5g3LT0fX6+qKpXFzB/++sR6H11XdWvFyuLYaR69u1/qd
W/Fa1cFV9Ee4t9bdotIvYFbd5D7QAcW77Aem4rgUShlj5rcyPAvAHHA5deR2qFSZmS3fPBGDocd5KdJ5oAcyfqLVyEqI2y7c
0of5UCxlKcMdKR6r7B9SMFQKD7FJ7LySV6zAbufW3R8w9lYg0qQwkdbnznfVH+7GmIgI40jpbrCtYWdWFOqFLdGY6/DAcEiO
gDcJuwhdcMWr/f3d+3S89AsDse58DTVXbl9DRWd2kodgVWdvwfKO2NrT/LkiUijme7J8/9Qe9omaJWCDaSdbnSjxKjqTSHpi
rQXQxEPVlycqNx5KtiNYGJMtLBpeCwxp8OytYCStsC3RMBE8pdrDVyiJCzKECFzFBRGzJtYm1B3QE+rW0NS19crzBX6yQmnD
nvGYngGz8T073uMxlPoxCFcET/PVk5bBizdBiaNfZCCIArCsi1+gBuu/Jo9p099K9q6l7V0T6zt1DlCxrNqOriK/5xTKPe1N
24dbd0bYwgIRl41AdYjX7cB0zWH0ZAiwaJMvlumqKSvWi0Ru2EteH1iXJineAG3qyJTaQaa0m5TLChTrH8Ag4JROu0tC9xgC
e5cR740sYuM4vd3YOiany9R/q5mY0D7pUyoMXhvT86KIFpwx3wIav/np+GPqHSJrJDQitxuJSRhd3BK2OH7U5hwFwVgP3X1b
29vXRLdeu+8YcktA68zxFFgg51JsZewKzGKwW+E3F38EFmOYkYJ6gmYwO/F7xt4IEpxIS7Zn+PW+4Ovr9fX6en39vtf/BQvj
oy8AzAAA
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
                "assets/chat-widget.css", "deploy/chat/chat.conf", "deploy/chat/xkt-chat.service",
                "chat/selftest.py"):
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
