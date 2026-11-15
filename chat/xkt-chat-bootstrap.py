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
H4sIAMuP+WoAA+19+3cTR9Lo/qy/ojNJPktBbz8wckQWAgRuEiAx+Xbz2V6fsTSyhWVJaEbYXuNzTBLABoNNEiBg3oFAErDJ
i4eN4Zy9/0nikeSf8i/cquqep0Y2ZJPsvecyu8Ga6e7q6urq6qru6upw5C9/+BONRje2tjL628b/wmP85S+x1vjGtuboxo2x
ZhaNxZqjLX9hrX88an/5S1nV5BKgIrcBApviDfMNDyhKbg04zkax3x3PP+gJR1IDsvbHMsHz9388Hm9+0f9/xhOOpJVirjD6
R3LAb+j/tmj0Rf//GU84oqZK2aKm/oEM8Bv6f+PGF+P/T3nCEVlVlT+0+3/b+G970f9/xmP2P6oBoeFsul/RwvvV37UOoEdb
S0uj/o+3xVraXP3f2tza+hcW/V2xaPD8f97/kdeYs+fZzxOfs5GyMqho5WI5nCoMseq35/WjR/T565WLJyvTH60s3f/18eTq
3P2VJ5dqP5399fGUj73G9NlT1W8Xfn18Ye+ezn0sIhezxFKQs7NzO+T59fHcysOT+sxC9fPblXP3a8e+0Y/fXj1/srp4a+Xh
IsCvLs+zHVve+2XiIwAX8fkz5XxKyxbyzB9gYz7GshnmH87m04XhcG/vyKD2JkB/pyCnlXSAlQDZUr4DcnnnYEmmlcpKhw9y
HJRLbPu7W3a9Ax+l/pKc13LK6D9HM3/tH5KzOWyw1CGybdm7CzOZjTET3t3y9959H7y/uxOSY3ETLKAPH7rgjbEuqfb0/MrD
b6rLp4F+lS8W9MMXVpYmVh5NVi98IgWZ5KQxZFh5eFefW2Zvh2Jxph+5rd/9qnrrdPXKzdrCUX3uSe3ed0DcyvHj/Ev1o0e/
TBzWj0yuPJ3Xj/xQ/WEJXmsLxytn765e/0L/dLq28KRy9Vjl0rXq3Hzt6eXK5OzKwwn98VXA59fH09gJl27q8xdWlk/qd7/W
787+MjGtn7ymX7ytf/YN5KzcvfnLxEnoDMBk9ePb+pGTtR8fQUHoQyhbPb+kL5+BVKknKFpbmTiFbfv8NrZt5eEUAAB8fz59
lQFMFlFGQMssKRFWmZ7iLatMPdEn7+nLn+lTJ802AZf8fPoagwQWSWfl/nxBhTKrE1P6/MeI9g9L1aUrle+f2huuP5nQ5y7X
ni5DBn3ynH5ssXJxAhit9vFy5cRZ4MvakadAc2hg5eojfe4qtEt/dB+yAaGovusM0GaRnCKX8hFWe3CFRbRCMZtS4eXazdr8
986Gfn4fSKHPnovUvjpc+eG2fnQaXnirT/JEpNOjK/C6enHCzMRpBkmVn2Zqtyb187crU5/pjyf0e98BpoAB1FK5eIczCzDO
yuJidenHyvEbgPvqpcvVpZna7M3KxC3OUDCuKg8v7Xpzr37jWBxkaBRUprYWfeZBKAaDzYGwnVYImpgQ8bUnJKFT2Fa28ugE
dIf+9MjqtSVIrpyarsxcY1sY4MBHu8FrAlV9elGfPAqkrV67w8EhdT+dhi+15QXzC7Sa8+bK4wsrj7+A79BdtiJ28l6cQg5c
nONcgnjWvjpanTur35uBT8AZq99+gUPlxgUgkhgkU5OADpAEaFY5cx4HxvQ5/eGkfuMW/K58/w3/WFs4Xbl8rnp3isTRNLCI
yYyAsv7oR5BFxKxG768em67enXOid+Ze5eT8ytIpQBJGEKJnMu/Kw1P2UYfAj9yBHobaK5dm+Zis3j4BGfRjRytnfqzOHgU0
gAshM8hAFIlLi8CRlYUZhGCAXT3/CQern7pSOXtMf3yGM4t77NUOfw5ds7J8dWXpDuK1+tF8df47JrENQt5tYBKy3+RZ/fhV
9t57rPrkBotFW1rbW1o2tQLbzOmzkyvLF2sLD6oXT7CIWizk1UIp4qgKWFV/OF+ZPF279SUKGs75fIZA/p+ZXXkyB92gP7jJ
c6AIWVqszc/TGLPGNJc9tbOf6I+/g0biMIX2P/gOxCSNy2koXrk8C/1hEeLaT9AjhA5g02OKXZjBNQUE7xgbUvvVBOvqCTKc
D+BnNMiGCmklwfLlXC7I+srqaIJl5JyqBFlRyaez+X4jLZURP9k4QTbnHyXn1+R+yJBTAe6IxqcjXjVWmy6kykNKXgunSgog
sj2n4BuWCXRQRpy5oHCAKeFUDtSt3fIQloNPVjrAZS8lqX7Mpykj2puFvAaAcO4a0XhOPs8xBd/GHUjmsvnBbGbUjwXtCGZK
cn89jtvE6w5IJWQFpliihLhF/N1iFHRHuraE/kcO/TMa2tTbHerZ0B051B3xC3l+yOjQQyQ9D/EyhzRFTg0opUOChQ6loCly
SjuULxxUcgGAMKBpRfWNRHcEwP+jW4Xuhm4N9Gw41NU9HMZa/mr86A53D28IRPotBIGESBTsWv5xeCCbU5jfPwRfS0pYGVFS
nA4BgxKcxkNhUA6UEbaZQASINmG5iHzwJoBI+11U2gcwdgP3ELCwmsumFD+WhIo5JKigQ8BHxBCroa4ocJ/cmC0kWTILUcdz
UHsyfumvUgBwC8XYf/0Xs31GWkHKS0loc4DJ4YGSkkG1BNUVrZDA8a0ZEBXgbDdYUT7pKu8sU/9ZdjNhA6yd4MewnFwCXRJR
7O3LyflBqQM+lpQcfskXCkBvpQTfxgW8um6QTQKJrjY6Dhoazin5fm2AZxg3hw9lfJ1RR/Ecv717zV4Vow3hmAMuEmEheNgH
u+ivkEB9Wh7QBEEh9ZU1rZDnXQxfw1nUPSVQRkOkZsMnyUgCs2uLppWyUEQBtihl5VBO7lNylkDlKrcNWB4ot3Pfu6C6EoJN
r6sH+xnJlKSUTRUkdjCrDG8tjCSlKIuyeAv8XwKVOK0NJKV4u8QGlGz/gMZ/U4UD2XRayScl1I6lzU1sg4BblLUBlk5K77aw
1nDblni4jeF/CDXG2uBX80AsGm53JcSjmPtgW3iT7EgIibedm8ItuVBLOMaaw81yuM1Mj4WbQ+HW/4bC/yOxTDaXS0qpcqkE
ffVmAcSMFLGhlsqWUjDcU9DITRJLjdKfUlKKGSVfjmY2trUpUMieNxZ/nsyt62WOAOVNpCTRUeaMVJTzxO7IEensQd6D9NHN
EPRRspKdTFEq5BRkB5CyuUK/A0wdK0A9Bisg9IG0tBm/bX69b7PdiEA16vjXlakTr0f6Nr+uDsm53ObVczg7V344w0A/n3pi
TrjwCpoAV3mgxZT39QgCtbqDM7y95hHBW8TMSdAyf1g9d1fa/L/PQY2UuQ6GC/W+QnpUWi9TaiBbVNfNldEgC45vGYY8KxWG
VerOYk5OKQOFXFqB7n2W1mNFBpi6xm/WZ06vThx+1ublCxqMNa4jgYnUZNfP2L8eMFT/zt0EPRiUQKh95eHx1fOzHKbFYUgj
YCTODAfKSmm0U8kpKa1Q8kthk4gBw2Alaq2Zn9PTLKDJjXIbZLDyqiBht5IEbAw+ozFLNEI5UxbL6fT2g/Djnayq4cTgl7bt
eVfMOtx4l1CHK+c1qg+FvVkWsEiPdpL2h7OjlIP8oNHBbEQFuFZjqkjim1AJHIBguhLz89bRXWm/U14H7OsLNsyRwo75BTIH
1stDFArU629AhnfVfj8O+CBzK3FDNlES5MIDNF3S7LGATc3EV5qKpb6ChnRwVG4oiZ0gYPL9XEcCItJo8EdAD9sQAfASToBc
Kxhy6wCKoYnWNWwoYEtQU4BIbl+hCGVsH3bS9OOYXIc8SbGvUMipdbqsVk8GDTMKlhLqq3MiDgrtXqzG6HOXq3c/x4WohUeG
HlYKF/IpmP0HoaR70Yn0E0VLDfhxLQgGaATIVShpANdIZmxI0QYK6QSTcOkLUgaALZUSWB9jTBK0C+0bLSoSZAGSQVUy1hHZ
rwKCbDxoAkJSJdj/6tyzO6xSF2FnjbEDCVKEPlBhdARAuUxQP7DxgCg4HggDRMDRgf24qUWVXL0o6Q++r83f46sRtXvX4f+S
lTedVeW+nG3NjKrgfzRHl5fsdE81oLt+46Q+eR/IXVu4ZFA8tQ7FqbNHEFUy7cJo1oWH5KKtgSMBWwcIXvKPhC3+LwO1JPYG
k8BWBSkrMSA+n/jwLQB9ORJOcZJ0WHTcX8jm/VJ3XnIo9ulCXnGjCo2opypvLOi2MI3vyw4phbLmX6+UnT6gFAdZrDUahQE4
bte38/LBbL8M4hQsyGyxryCX0gHm8TE8XMpyzRYtykBYG1DyfkQ/SI0wW0WjG78Ylp9nB6eMDkYUeFeAlYzmifkSHsw4+00W
fCDbWODJ/MrTa3ZlFh/T4rDDshkfdUaEmVRnSogUzdOKGLeMogZNOHDA2YQDDVi5+uSGPvOAxK6jsFH/gXXY+jd3pWdtWF8j
DuSYSlbWhvxYB6NBI22caYwWb7IbCI5bomGoniVqy3e4AmTww5CXWetv1GMKZgqwQ4e45oSjWXpDLfftB5UjiSWVfAosuw/e
3/VmYagIbI6GN9hUuND06e3awnUUAAJ96b9Q7DYsBeIDF2DPzdOq1IXufHf+18eTfLz++ngKRIVJqf+EmAp4jdshY9zWzdKa
h+phzS0C10yhxPzYcVmnBOaGNQuxWAckbQZ7H/6GQgHb2MJ8XdkedwMNDYo5czkaJnJIkgeGoNcBi2ay/RaOjkk5RYk4KbMU
rjwlUDqEVBhPimTNk1waWp1TwgEgqgUlYBC6oRTGSRlq4UuBHY0L78fC2PD9yJr7oXjAYlCg23572YbTs7OdYPCC4vAmauJm
Q0kvt5t7gkLPsMPEN3bAhMB185PXVpZnVhaPOvZpHFsDPGH2aO3Wl5hm7nNIPWHgiO2yowUukdnnLTItadXXSDYyWR1EoWHJ
E95ih2JtyBQPmuEcsBeVapNi3AghgwuNCrQw/BJmM2QNLb5oozkFdR1Qfkf5bJJXJEuRfqmO760GC12dVGzc9lm+qt9cppX1
09ALfGMEusC0tH+Z+Kg7r88srCzdBDnCB7roNKMzcJviyix2pmF9GjtxYosjwrcnMJ9zBwK/QNfPfsX7C1fHLcXPzk8WeZXU
4E5FzmkD1kf7CLOvrTWcNzQZmCJVRrg4M7RFPbomlSuoitk3df1SUoYKBxWza7y7hdYJxfJXIw5yA6bV5mxeNUDDuHagkrAz
jWC8xpbriBSw1WwBcm4SOKjqKaMGKPHPl1GCkWFiQ6lkCCuA49/Pv8IsKuVyQxIClAqZDFiJirSO9HJCdZSqWyrlqyPGcqll
5tG4t1njHCRu0TgNblTH/AcQTWC6g3KuzFGGbgEbachvs35fOuAsaea3hCavhHaHNmywf6KRXiyrA2Bw4eyVEFNXkIlZKgGI
GDaVIQFEjgP1ejLVwDZbngINxQcX4iuPL4BCYWoalYtTKANuXACJjfuatAZESpnleoDLRZVL1/h2ryFgKievAzQABUBWj53U
H0/wLb/q3I+VUzexKz4C2XHfuSvoEhoWAW1KXF+5rw/ndDf6plCldLc2+fPEV1IdbTjXJG18YxHHG4ypyYpkr0WNjHxgS14d
Bj3mgG1fpmHngrAAWSHnNXsPe9RumdHmukR9rrWIZ7G1w6IWi2be5jYZUqmUaLpTmFgrD7/TukODVYchRVXlfgXAWTQ0hMJ4
wEtO2ezVl0hWwTCFHwg/wLSBUmGY5ZVhtr1UQuGK+0Z8CSuMFZRVh8ldQoLwsrg69z41DVc/0gqSBeGgabRNQY2dEvrKGQer
mLgVy0NFv4ceDiYWLiD669uiqPbsYmVNUcNkQjv62ODKDNuQRNTCaUKIcpPoCZKshHqGEtS/Nn4ymlqUSxquzQKUMMx7WQ01
e/sShFFFkmcNFwtFvyORf65X0orOZvCGFK2tu7SsyQlra7G+YaIv5GGsW2yRtTrlroNGmBHHdde2Pbu390iNQe53ftJKo0Cn
/VALsSG0R1UQGs7OjKYf5lesmdDaO7Tq3h9Ou1vLaAxBx0Bah0dKEv+11j+782PNwfFXcAnUTX3eA2tKJlc2LwkFtQXqwT7j
eqnxeLUcagq45nlzarc+2+E4uVAMCD5QrAQrk1GpR8Z6UWB1w/MJX+wSq0psGRLMErv4ZtbpoZM4K3VrJv+3zy/r01FMIeS9
YlZfP4vY0r3sJXszbGvrfQrttAs3GXjpTBXIEyTKQe3Y8p6XgJGzJachqFpFXAsJuFjAXmcHnMsIGzbw5QOE1BXtMWXTgbBa
7gPB6c8GWTzA/SKAxw2dTagT8NnEFcWDHXG1w2gUwjZExrhNXaRk0IetUpuTUJnB5fi5K9bjXJ3g/opocV28XV18yhc1QW2r
frUEr5Xb1/THM7g+RN6wlYvf6LML+vHbpo728GHt1mGu4nF9jTythHtMRHhnNVbSzO40+n0to9owbUALrt9kG1RG04VhtNSt
gopdG1fCkIVL8+3AqSUJKfWSElYHshntbWUUa1HCxZKCcLcpGbmcww03s2Yfp/V4AAXFf9rL+cXT6PH0/0+pv+sBgLX9/6Nt
rbEWt/9/a7zthf//n/G4/P+h55/1AEB18SvW/PZWEG3orv+yfct8rFhQsyhTEpnsiJLuKKEak4jHiyMdYDVqhaFEvAV+/zNE
0j4Rj7VsbGlvBrJ1kK9SYiOmcl8l/ruvUAItP1SS09mymmiNvopyrU9ODfaXCuV8OiEcczpS6C2UeDmTyYgiiSj8GAmpAzJI
u0SUxaLFERZvh39K/X2yP9YajMXa4b9oMNzcHuhIlUsqACgWsijysJIMiOaQmv2nkoghIvQ6zDFrBXxRtwgJTGPhWIdYuUpk
cspIh5zL9udDWU0ZUhMphSDuB3YDZSJkaATiM2YPpbMlhSRxAppRHiKtWSvJeUFK+gkz6hALx1pVpsjow2o1zvrKkczIQ9nc
aCKbH1BKWW3c2UGJgcJBpTRmguTAc6BlfOgPQTcFXFSDprPmFi+qtbQHXLCZerA/nE0Vxgxa9OUKqcGOIbnUn82HRP8DLHsx
Wn1rwDVRi2ti2H31bBMTbNPc2mbxTSsVHJJHjO7Z2H5wwM02FqMYvBXj7GZrPMJhrVGz8W3B5niwGZoebwmY/Y2rx417EYmd
yQE07m7n6KAQWuZKSB2FmXkouBW1zXflVCe97oB8QWkvmOQ75Hw/63xTCkrvZsE0UAsZjX0og30gBVXouZAKnZzx4FcxIGJt
8VjMHBMxaItayGXT9d0Ziwfq+iWMq6Vjds4e94W5i9nY2mOwCHoHeljHgKWIiZ57fKhFMM1CfYo2rCDdoFQCPQblslYwkWB9
Y2uM0jYcpYoGwEMIDNEJx4tWExi5tbmY1QYPiNVRwILaaCLcHjf4WCsUE3FXVS3RqAA7YicMjS0waXGny5RKNipZlRHLumSQ
Q8KYFEWCttgx2yRqRutxjOgUYzGiU4fBfaHRBL07e8WA5BgWGzNyxoAIts0YDiM+xtrbXhUkoI6gAWkA3ITwYnXimj45BWVb
vGN4ADqeukRJgBYZGi7JxY5hKBjqKynyYIL+DeEHC48wyIEx7/FrY+qXlWYlpcgGFlx2hHJKRjMwajH7H4HiIu46jCw6HWFw
Gjphk6TyBM7kMQEm2tfW19bcgaZfCBeJSrQWlyjjDg0Sp45p7QTKF9zkGVSUYggY10kcd3UilbykHCO4o18uJtpJQFJfhlC4
i+60M3+41RIirQiy3Q5SuPTZiUeC0M3lvKSbsw22ia5HFDsunnOb5cDobCQJZKRcgsiHbW6z8WuUc3/7WtzPHSfr29mA9dLt
SpvS3GF2Qmumtd01HDZt2mTDoRXHjIvq8XopsE6zBYJiWrejqWSgOa0ib0Ybc4hQAzMUZvbx065kYP41UGx3y22Dji5ymJUw
w0VUCKLGdHJRxkaXdg+6NBMHlBR6I0YTAqUZUYTJzzbbb2rzZpaOQllDzuLlnVKppb4FCdrkHBN4Gt1K8sHK7MEda+qj7jZz
ydra5mrt83CBiUXCWAkaM6eGVgNMmlvpogi6IY81HOuZtkxbig9MmqaNCdo+AUXZRi8u+OuQks7KzG9NGi3t0JMBXFtwq3xc
x8MZOqMRbUjPM+yAWBQ0fdE97W2gvtk6mN7rdTeuqwKDjztqQ6OE1xVrs+mTbSb122yqI/6uK26qtTx/vNnKj7/HfeP/T65y
WPE/1NF8ilobVgd+3zrWif8QA6Pfbf/Hm2Mv7P8/43n5pUhZLUX6svmIkj8IxpE64HuZVS7eqVxcBCMfTBEw8GtPZ2vXpvnx
c7HiOfdQP/JD5eyxlaX7+ux05e5NffIefNePX9PP39Yf3a89vVi9fUKfn6p9eQSP9L+Mi+sAnHmxm31H42W2uvRFbf4GK/eV
81r5r7GWtnBrWzgebwEDt4Xg7NzTuS8ZC8fDzeEW9kHn9vd7kzxz4xqg3AqgPzNbvbFYe/KZfuQm6+zcyfSFo9Wrh/Es9ffX
KhcRV/iy+ulNvl7rUxWNhZRygRWzRZCd2Zzv/T179iWlV/ypNIN/wdbL41lO6ZWoFIiEw7RGWhxOByQf4tgLOcfwRyLkbMW4
5PsA0wj3RIgjDx+3be9E6GP4NxGKHJRLkeHh4chgLA6JPiU1UGBSMslikTjjRBcdMHmPvfLBX1+hOhOvYGmWTEq+ElKAheSD
/2QhEPeholIaUvnPwnBeKfGfKLuLrBvknfQKNo8HBJPgzQlSfP+tUD3DjEhrpKZU1QMJkfE3oyGiXTVqoyP5t9ZhMCAHZrCg
R21GRnvnxqFz7YOHelIFtg4VWKdSAv1uSy57UNmFs/FBOZdsjtrgQh1qOV3g48BZhwsZY7IKN8jwe8qYdeR/y8a2Ovnf2tr8
Qv7/GY+3/Ncv3jaF+crD45wT7avAIDL5ilWabWB5sCBHmD5zcmXpS3jVj9yGrDzAC4a+OCLE6erFCYbcaUwH/NAdCl9bVRSa
4QLxr13+NeBSgoPxQ5bnoVRE0VIRQ2cLY3NWj03rR8/rN5fZmzu37OvdsndX79vbP8ToNV+drdy5xuc1mBiqn1+pTM5Wbl+r
XHqqz55anZjQjy1iYJuGM8AY/q2T0dt3//eOZB0avt1v8Y9EKHJWDqexBHoqZhyCvY1VTy3o1z/mgp3GfjbDuthLLJSBcY7w
JdbTwXCrGLcBcbBrimImbQYCHYxQFIPXX2/avmdHE5DIuZgvJnCqRp/5YvUY7le2ActWLn28en4WA2OceAqdpi9+hhSwEy5p
vW3d0rk9Saf4ExGMjxNOK0pRVZRBrINne3fPtu3vJI3vRA3f3j3v70u2RzfFeJZtW3a982Hv1g+2vbV9X7I1GuVfd+3lCck2
AchweUvG4j5oEzSck0x/8D3vOcabbyb8fPRTBrqKo9eZfu3b2tM5/dQStHcbYNUJWLHKqVt4/GbmXuXsPX1psXrhEzaojPIA
IdVP7iMzHDtZe3AaNKLaJxfgX6pkJKuxqC+Txc55ifdCf0kpstAB1vQPB8XC3RuajN4xu40j+dJLHG3kUiemtadfVL5YqH6N
6GB/XPsWWFg/ingAEKo9hrVTxamBoUKaYQeKahyTCTAUP/y7+BlxEykuyLuSDwdIqMz2frhv557de7fs28mKo9pAId9MO0KR
vnI2l+4d7AsXR80iVOHQIOg9LFTk2XjwDfqZK/SrBk4wP7LQ+wyGRoi8jIwf3oUsjJsBY0Oy0MxH4IrMPjGbY0uFKTCbUhgN
LlFK/K3LxCHxxJSWY2lZGSrkQyUFXZ/diUoebWia3oeZAcmn5oBrgPKuzFk1JKc0mJOtnFZ7WqA9XD42ag0hiYKA2WSEms8W
i6jogJQImTk4u5mc5khDLtv9luQUDaZsN3o2xHOhcNj7YZMvO4SHGbEtPnQ9gr9hudR/sCvW40NHDlz49xcDwk0Oa3fXmS9o
LAu2ccLwG2jK5lO5clphzhYUhoDYVKajyVaAXFiwYtML6xnKW+clnc/6RbvzhKVnNqNNAJ/FuJcjnhtriKdKuhgbg+zm7+eE
z8kL5YebAvy0l1/lKcVSNq/5m4ro5KSkoUQx4Nv7oTnkOUOFNDcncmbmyTYebAUeXP1muvI5n1BS5VIOphO1k4WGWCtDIQ4y
PBbfGI7C/2IJFM9myDPhtt5BMstZtJ0Z8t8xwfw7Rdkhwd0p1uS0FJogSVXSQOvIPyIwe69e+4nrFjCBV87cS7BIk63FbdDi
2sKZ1XPzGPRs5qat3RyBligL/Z1RqLq1G8FCO1mT3Zk2wdyutE2k+4cAtzHJcJqVEl1jPHpDQjiJS2JLCz6scWzn18dXpPGe
cWwtevOyUAtvlWiaPj8Nsx2oOg3Ip8/8sPLwRO3Wp6C+VE/dw5huNNv/MnGyMj21+um85F6kCjtMnj9Gx3z++J/NrbGNL+J/
/hmPs//dk+bvU8c6/j9RMPZc/d8GnfHC/vsznq4P8lmtx7dN4QYWyLSk01xQs0JTY6ZHq29LRlNKybyiDRdKg+Kkts/X1cmZ
pseHcjKpgnKRU3x4sjRpaH++t3CtxHr9G5TP5vu3kc9EoTSatNtTvu35g9lSIU+ByrI5xcOw2j6ipDqhfi1Zp+k4rEeudNIs
Deqs731FpUJyblgG1Ue8diqpZLPvXVALS6PvyiPJ1lj8Xd/uwm5leG8pexAQALmeRB9+H75jAKmhIn/3de3KA4hcrsf3N6CP
kt46mhwq57RsCGW/QaD/dFd7Ps7xb2opv2sd64z/WPPGjXXxf2Mv4v/+Kc/LzLWs4xj9uADwMsMgrpZCxNd5aLkfNwkYqos8
yi8z4ob+gMdVMgqeJUIIuQLXlmxAxEndUmFktLcIgsVbC+2w5cIMvTB+VQSErna2NFXRevnhJ7azoGrslQH4t0GGv4feB7U0
tGsvewUPoGpKr5xOlxpm3lEoDcultJLGX+wVngNK9I70Zowk/NUAAGiOee4OZh4y4HlMArFCJmNPoLOh7o9ogPVq/CAui8Wj
qrO6vDtx3Efdds1jLc7w37xA0WofsdZodAMDdZTh6XKKivoNHj0+tqjPfKnf+KT2dFk/fnXl4Q3Qs8Hc6OvNZHMg/HsLebC7
C/kO+zcNxL5KW+eRAW0oZ09jTa9H0DVpcxP8Qh83tFWSEh33VWFkaRLD+A9JqcFOwBsHkxjlNhaLtfZJm1/nkxVTSynvEvud
BcDeBmJj0DYqt9nA5YVjunH/izk3/hF1rC3/m1s2trj9v1tisRf635/yvMxCr4VYqsAj4Za1TKgdv/gkSTJ5Yh2PcGcw+Om9
pIAxHuVYLCL76OzxlyC03tq+jzH3EoFtEWdMKgxKCdSqghKe4QJzOZcbOjTYJ/H3nJQIh8PoneGMM1+/HPSMxjhAQ4ub4ZIx
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
2zP6Yl3wxfPiefG8eP7Y5/8AMVEGrADWAAA=
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
    cur.setdefault("WECHAT_KF_URL", "")
    cur.setdefault("QQ_GROUP", "1045844951")
    cur.setdefault("SUPPORT_EMAIL", "grantleyzyf@gmail.com")
    lines = ["# xueketupu.com 客服环境变量（600 权限，勿入库）"]
    lines += ["%s=%s" % (k, cur[k]) for k in
              ("CHAT_API_KEY", "CHAT_API_BASE", "CHAT_MODEL", "PORT",
               "CHAT_DAILY_BUDGET", "CHAT_IP_DAILY", "CHAT_MAX_TURNS",
               "WECHAT_KF_URL", "QQ_GROUP", "SUPPORT_EMAIL")]
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
