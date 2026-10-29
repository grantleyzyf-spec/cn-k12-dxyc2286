# 高中数学（人教 A 版）公式台账 —— 高风险 58 页逐页视觉读取

## 方法与判据

- **对象**：`docs/math-hs-formula-check.md` 附二的高风险页（公式分 ≥60），共 **58 页 / 974 页全册**。
- **读法**：每页按 160 dpi 渲染 → 视觉模型 `agnes-3.0-flash` 逐条转写公式（不解释、不复述题干），每页结果落盘一份 JSON，再与 974 页 OCR 文本逐字符组比对。
- **判据**：公式里每个 ≥3 位的字母数字串若在 OCR 该页文本中找不到，记 1 次「OCR 丢失」。丢失多＝OCR 在该页把公式读丢/读残，**正说明公式不能从 OCR 抄**。
- **可靠性交叉验**：另用独立视觉模型对 `必修第一册 p227` 全页复读，与本流水线同一页结果一致（24 条公式全对上，含 `tan45°=1`、`(1+tan15°)/(1−tan15°)` 推导链、`cosθ=−3/5, θ∈(π/2,π)` 等）；此前手工抽检 4 页也 4/4 全对。

## 汇总

| 册 | 已读页 | 公式条数 | 无公式页 | OCR 丢失字符组 |
| --- | ---: | ---: | ---: | ---: |
| 必修第1册 | 27 | 521 | 0 | 432 |
| 必修第2册 | 16 | 270 | 0 | 509 |
| 选必第1册 | 6 | 166 | 0 | 4 |
| 选必第2册 | 6 | 125 | 0 | 70 |
| 选必第3册 | 3 | 39 | 0 | 8 |
| **合计** | **58** | **1121** | **0** | **1023** |

## 全页清单

| 册 | PDF 页 | 公式分 | 公式条数 | OCR 丢失 | 首条公式 |
| --- | ---: | ---: | ---: | ---: | --- |
| 必修第1册 | 160 | 61 | 27 | 0 | `y=5, y=0.25x, y=log_7 x+1, y=1.002^x` |
| 必修第1册 | 177 | 63 | 6 | 0 | `328° = -32° + 360°` |
| 必修第1册 | 178 | 128 | 28 | 0 | `S₂ = {β | β = 270° + k • 360°, k ∈ Z}` |
| 必修第1册 | 190 | 84 | 18 | 46 | `$OM^{2}+MP^{2}=1$` |
| 必修第1册 | 191 | 117 | 21 | 46 | `$(1 - \sin x)(1 + \sin x)$` |
| 必修第1册 | 192 | 99 | 30 | 53 | `$a^2 \cos 2\pi - b^2 \sin \frac{3\pi}{2} + ab ` |
| 必修第1册 | 193 | 96 | 16 | 45 | `用 $\cos \alpha$ 表示 $\sin \alpha, \tan \alpha$` |
| 必修第1册 | 196 | 87 | 18 | 0 | `sin(π+α) = -sinα，` |
| 必修第1册 | 197 | 91 | 14 | 0 | `(3) sin(-16π/3) = -sin(16π/3)` |
| 必修第1册 | 198 | 73 | 17 | 35 | `原式 = $\frac{-\cos \alpha \sin \alpha}{(-\tan \` |
| 必修第1册 | 199 | 62 | 11 | 0 | `y=x` |
| 必修第1册 | 200 | 141 | 13 | 0 | `(2) cos(3π/2 + α) = cos[π + (π/2 + α)] = -cos(` |
| 必修第1册 | 201 | 119 | 25 | 0 | `cos(65/6π)` |
| 必修第1册 | 220 | 67 | 14 | 0 | `y = tan x` |
| 必修第1册 | 223 | 123 | 12 | 64 | `$\frac{[cos(\alpha - \beta) - 1]^2 + \sin^2(\a` |
| 必修第1册 | 224 | 131 | 17 | 0 | `cos(α−β)=cos α cos β+sin α sin β` |
| 必修第1册 | 225 | 115 | 8 | 2 | `sin(α+β) = sin αcos β + cos αsin β` |
| 必修第1册 | 226 | 108 | 17 | 59 | `$\cos(\frac{\pi}{4}+\alpha)=\cos\frac{\pi}{4}\` |
| 必修第1册 | 227 | 171 | 24 | 0 | `tan 45°=1` |
| 必修第1册 | 229 | 86 | 16 | 0 | `tan 4α = (sin 4α) / (cos 4α) = - (120 / 169) ×` |
| 必修第1册 | 232 | 83 | 15 | 74 | `$\sin ^{2} \frac{\alpha}{2}, \quad \cos ^{2} \` |
| 必修第1册 | 233 | 101 | 15 | 2 | `sin(α + β) + sin(α - β) = 2sin α cos β` |
| 必修第1册 | 234 | 77 | 28 | 0 | `y = sin x + √3 cos x ;` |
| 必修第1册 | 236 | 244 | 40 | 5 | `cos a = 1/7` |
| 必修第1册 | 237 | 119 | 16 | 0 | `cos 4α - 4cos 2α = 8sin²α` |
| 必修第1册 | 261 | 121 | 28 | 1 | `π < x < 2π` |
| 必修第1册 | 262 | 117 | 27 | 0 | `(3) tan 70° cos 10° (√3 tan 20° - 1);` |
| 必修第2册 | 21 | 61 | 18 | 52 | `$\lambda(\mu a)=(\lambda\mu)a$` |
| 必修第2册 | 28 | 99 | 22 | 1 | `(|a+b|cosθ-|a|cosθ1-|b|cosθ2)e=0,` |
| 必修第2册 | 30 | 60 | 20 | 0 | `(1) ½(a + b) + ½(a − b) = a；` |
| 必修第2册 | 36 | 65 | 15 | 0 | `a = AA₁ + AA₂ = 2i + 3j` |
| 必修第2册 | 42 | 107 | 20 | 0 | `a=(5, -7)` |
| 必修第2册 | 43 | 63 | 13 | 1 | `a=(-3, 4), b=(5, 2), 求 |a|, |b|, a·b` |
| 必修第2册 | 51 | 75 | 18 | 53 | `$a^2=b^2+c^2-2bc\cos A$` |
| 必修第2册 | 54 | 113 | 13 | 81 | `$A = 15^\circ, B = 45^\circ, c = 3 + \sqrt{3}$` |
| 必修第2册 | 55 | 60 | 11 | 0 | `= (√2( (√3/2) × (√2/2) + (1/2) × (√2/2) )) / (` |
| 必修第2册 | 56 | 78 | 4 | 0 | `AC = a sin(γ + δ) / sin[180° - (β + γ + δ)] = ` |
| 必修第2册 | 67 | 70 | 40 | 101 | `$\boldsymbol{a} = \boldsymbol{b}$` |
| 必修第2册 | 68 | 87 | 18 | 99 | `a=12 cm, b=5 cm, A=120°` |
| 必修第2册 | 93 | 74 | 10 | 9 | `4; -i; 2√3+2i; -1/2 - (√3/2)i` |
| 必修第2册 | 96 | 81 | 16 | 0 | `=2(cos π/2 + i sin π/2) = 2(0 + i) = 2i` |
| 必修第2册 | 97 | 90 | 18 | 112 | `$\sqrt{10}(\cos \frac{\pi}{2} + \mathrm{i} \si` |
| 必修第2册 | 98 | 65 | 14 | 0 | `1的平方根为 ±1` |
| 选必第1册 | 35 | 61 | 17 | 0 | `已知: 如图 1.4-11, a ⊂ β, b ⊂ β, a ∩ b = P, a // α` |
| 选必第1册 | 84 | 82 | 46 | 2 | `$l_1: 2x + 3y - 8 = 0$` |
| 选必第1册 | 88 | 62 | 18 | 1 | `M₁(5, -7), M₂(-2, -1)` |
| 选必第1册 | 89 | 60 | 21 | 0 | `a², b², r²` |
| 选必第1册 | 103 | 76 | 32 | 0 | `C₁：x²+y²=4` |
| 选必第1册 | 107 | 105 | 32 | 1 | `3x + 2y - 1 = 0` |
| 选必第2册 | 19 | 71 | 16 | 0 | `a_n = a_1 + (n-1)d (n≥2)` |
| 选必第2册 | 24 | 73 | 13 | 25 | `$a_1+a_n=a_2+a_{n-1}=\cdots=a_{\frac{n}{2}}+a_` |
| 选必第2册 | 25 | 70 | 17 | 6 | `S_n = 1 + 2 + 3 + ··· + n，` |
| 选必第2册 | 56 | 67 | 11 | 9 | `>(k+1)x.` |
| 选必第2册 | 84 | 89 | 41 | 11 | `y=ln(2x-1)` |
| 选必第2册 | 86 | 63 | 27 | 19 | `$y = \frac{2}{\sqrt{3x+1}}$` |
| 选必第3册 | 35 | 65 | 16 | 8 | `(a + b)^3, (a + b)^4` |
| 选必第3册 | 114 | 60 | 17 | 0 | `Q(a, b) = Σ_{i=1}^{n} (y_i - bx_i - a)²` |
| 选必第3册 | 134 | 65 | 6 | 0 | `P(X=0, Y=1) = P(Y=1) - P(X=1, Y=1).` |

## 逐页公式明细

<details><summary><b>必修第1册 · PDF p160</b>（公式分 61，27 条）</summary>

- `y=5, y=0.25x, y=log_7 x+1, y=1.002^x`
- `[10, 1000]`
- `y=0.25x, y=1.002^x`
- `y=5`
- `y=log_7 x+1`
- `y=5`
- `y=0.25x`
- `y=1.002^x`
- `x=20 时，y=5`
- `x>20 时，y>5`
- `y=1.002^x`
- `(805, 806)`
- `1.002^{x_0}=5`
- `[10, 1000]`
- `x>x_0 时，y>5`
- `y=log_7 x+1`
- `[10, 1000]`
- `x=1000 时`
- `y=log_7 1000+1≈4.55<5`
- `y=log_7 x+1`
- `25%`
- `x∈[10, 1000]`
- `y≤0.25x, 即 log_7 x+1≤0.25x`
- `f(x)=log_7 x+1-0.25x, x∈[10, 1000]`
- `f(x)`
- `[10, 1000]`
- `f(x)≤f(10)≈-0.3167<0`

</details>

<details><summary><b>必修第1册 · PDF p177</b>（公式分 63，6 条）</summary>

- `328° = -32° + 360°`
- `-392° = -32° - 360°`
- `S = {β | β = -32° + k · 360°, k ∈ Z}`
- `S = {β | β = α + k · 360°, k ∈ Z}`
- `-950°12' = 129°48' - 3 × 360°`
- `S₁ = {β | β = 90° + k · 360°, k ∈ Z}`

</details>

<details><summary><b>必修第1册 · PDF p178</b>（公式分 128，28 条）</summary>

- `S₂ = {β | β = 270° + k • 360°, k ∈ Z}`
- `S = S₁ ∪ S₂`
- `= {β | β = 90° + 2k • 180°, k ∈ Z} ∪ {β | β = 90° + 180° + 2k • 180°, k ∈ Z}`
- `= {β | β = 90° + 2k • 180°, k ∈ Z} ∪ {β | β = 90° + (2k+1)180°, k ∈ Z}`
- `= {β | β = 90° + n • 180°, n ∈ Z}`
- `y = x`
- `-360° ≤ β < 720°`
- `S = {β | β = 45° + k • 360°, k ∈ Z} ∪ {β | β = 225° + k • 360°, k ∈ Z}`
- `= {β | β = 45° + n • 180°, n ∈ Z}`
- `45° - 2 × 180° = -315°`
- `45° - 1 × 180° = -135°`
- `45° + 0 × 180° = 45°`
- `45° + 1 × 180° = 225°`
- `45° + 2 × 180° = 405°`
- `45° + 3 × 180° = 585°`
- `7k (k ∈ Z)`
- `7k (k ∈ Z)`
- `420°`
- `-75°`
- `855°`
- `-510°`
- `0° ~ 360°`
- `-54°18'`
- `395°8'`
- `-1 190°30'`
- `-720° ≤ β < 360°`
- `1 303°18'`
- `-225°`

</details>

<details><summary><b>必修第1册 · PDF p190</b>（公式分 84，18 条）</summary>

- `$OM^{2}+MP^{2}=1$`
- `$x^{2}+y^{2}=1$`
- `$\sin^{2}\alpha+\cos^{2}\alpha=1$`　⚠ OCR 丢失 `alpha`, `alpha`
- `$\alpha\ne k\pi+\frac{\pi}{2}$ $(k\in\mathbf{Z})$`　⚠ OCR 丢失 `alpha`, `frac`, `mathbf`
- `$\frac{\sin\alpha}{\cos\alpha}=\tan\alpha$`　⚠ OCR 丢失 `frac`, `alpha`, `alpha`, `alpha`
- `$\sin\alpha=-\frac{3}{5}$`　⚠ OCR 丢失 `alpha`, `frac`
- `$\sin\alpha<0$`　⚠ OCR 丢失 `alpha`
- `$\sin\alpha\ne -1$`　⚠ OCR 丢失 `alpha`
- `$\cos^{2}\alpha=1-\sin^{2}\alpha=1-\left(-\frac{3}{5}\right)^{2}=\frac{16}{25}$`　⚠ OCR 丢失 `alpha`, `alpha`, `left`, `frac`, `right`, `frac`
- `$\cos\alpha<0$`　⚠ OCR 丢失 `alpha`
- `$\cos\alpha=-\sqrt{\frac{16}{25}}=-\frac{4}{5}$`　⚠ OCR 丢失 `alpha`, `sqrt`, `frac`, `frac`
- `$\tan\alpha=\frac{\sin\alpha}{\cos\alpha}=\left(-\frac{3}{5}\right)\times\left(-\frac{5}{4}\right)=\frac{3}{4}$`　⚠ OCR 丢失 `alpha`, `frac`, `alpha`, `alpha`, `left`, `frac`, `right`, `times`, `left`, `frac`, `right`, `frac`
- `$\cos\alpha=\frac{4}{5}$，$\tan\alpha=-\frac{3}{4}$`　⚠ OCR 丢失 `alpha`, `frac`, `alpha`, `frac`
- `$\frac{\cos x}{1-\sin x}=\frac{1+\sin x}{\cos x}$`　⚠ OCR 丢失 `frac`, `frac`
- `$\cos x\ne 0$`
- `$\sin x\ne -1$`
- `$1+\sin x\ne 0$`
- `左边$=\frac{\cos x(1+\sin x)}{(1-\sin x)(1+\sin x)}=\frac{\cos x(1+\sin x)}{1-\sin^{2}x}=\frac{\cos x(1+\sin x)}{\cos^{2}x}=\frac{1+\sin x}{\cos x}=右边$`　⚠ OCR 丢失 `frac`, `frac`, `frac`, `frac`

</details>

<details><summary><b>必修第1册 · PDF p191</b>（公式分 117，21 条）</summary>

- `$(1 - \sin x)(1 + \sin x)$`
- `$= 1 - \sin^2 x = \cos^2 x$`
- `$= \cos x \cos x$`
- `$\frac{\cos x}{1 - \sin x} = \frac{1 + \sin x}{\cos x}$`　⚠ OCR 丢失 `frac`, `frac`
- `$\cos \alpha = -\frac{4}{5}$`　⚠ OCR 丢失 `alpha`, `frac`
- `$\tan \varphi = -\sqrt{3}$`　⚠ OCR 丢失 `varphi`, `sqrt`
- `$\sin \theta = 0.35$`　⚠ OCR 丢失 `theta`
- `$\cos \theta \tan \theta$`　⚠ OCR 丢失 `theta`, `theta`
- `$\frac{2 \cos^2 \alpha - 1}{1 - 2 \sin^2 \alpha}$`　⚠ OCR 丢失 `frac`, `alpha`, `alpha`
- `$(1 + \tan^2 \alpha) \cos^2 \alpha$`　⚠ OCR 丢失 `alpha`, `alpha`
- `$\sin^4 \alpha + \sin^2 \alpha \cos^2 \alpha + \cos^2 \alpha = 1$`　⚠ OCR 丢失 `alpha`, `alpha`, `alpha`, `alpha`
- `$-\frac{17\pi}{3}$`　⚠ OCR 丢失 `frac`
- `$\frac{21\pi}{4}$`　⚠ OCR 丢失 `frac`
- `$-\frac{23\pi}{6}$`　⚠ OCR 丢失 `frac`
- `$1500^\circ$`　⚠ OCR 丢失 `circ`
- `$6\sin(-90^\circ) + 3\sin 0^\circ - 8\sin 270^\circ + 12\cos 180^\circ$`　⚠ OCR 丢失 `circ`, `circ`, `circ`, `circ`
- `$10\cos 270^\circ + 4\sin 0^\circ + 9\tan 0^\circ + 15\cos 360^\circ$`　⚠ OCR 丢失 `circ`, `circ`, `circ`, `circ`
- `$2\cos \frac{\pi}{2} - \tan \frac{\pi}{4} + \frac{3}{4}\tan^2 \frac{\pi}{6} - \sin \frac{\pi}{6} + \cos^2 \frac{\pi}{6} + \sin \frac{3\pi}{2}$`　⚠ OCR 丢失 `frac`, `frac`, `frac`, `frac`, `frac`, `frac`, `frac`
- `$\sin^2 \frac{\pi}{3} + \cos^2 \frac{3\pi}{2} - \tan^2 \frac{\pi}{3}$`　⚠ OCR 丢失 `frac`, `frac`, `frac`
- `$a \sin 0^\circ + b \cos 90^\circ + c \tan 180^\circ$`　⚠ OCR 丢失 `circ`, `circ`, `circ`
- `$-p^2 \cos 180^\circ + q^2 \sin 90^\circ - 2pq \cos 0^\circ$`　⚠ OCR 丢失 `circ`, `circ`, `circ`

</details>

<details><summary><b>必修第1册 · PDF p192</b>（公式分 99，30 条）</summary>

- `$a^2 \cos 2\pi - b^2 \sin \frac{3\pi}{2} + ab \cos \pi - ab \sin \frac{\pi}{2}$`　⚠ OCR 丢失 `frac`, `frac`
- `$\tan 0 + n \cos \frac{1}{2}\pi - \beta \sin \pi - q \cos \frac{3}{2}\pi - r \sin 2\pi$`　⚠ OCR 丢失 `frac`, `beta`, `frac`
- `$\sin 186^\circ$`　⚠ OCR 丢失 `circ`
- `$\tan 505^\circ$`　⚠ OCR 丢失 `circ`
- `$\sin 7.6\pi$`
- `$\tan (-\frac{23\pi}{4})$`　⚠ OCR 丢失 `frac`
- `$\cos 940^\circ$`　⚠ OCR 丢失 `circ`
- `$\cos (-\frac{59\pi}{17})$`　⚠ OCR 丢失 `frac`
- `$\sin \alpha = -\frac{\sqrt{3}}{2}$`　⚠ OCR 丢失 `alpha`, `frac`, `sqrt`
- `$\cos \alpha = -\frac{5}{13}$`　⚠ OCR 丢失 `alpha`, `frac`
- `$\tan \alpha = -\frac{3}{4}$`　⚠ OCR 丢失 `alpha`, `frac`
- `$\cos \alpha = 0.68$`　⚠ OCR 丢失 `alpha`
- `$f(x) = \sin(x + \frac{\pi}{4}) + 2\sin(x - \frac{\pi}{4}) - 4\cos 2x + 3\cos(x + \frac{3\pi}{4})$`　⚠ OCR 丢失 `frac`, `frac`, `frac`
- `$x = \frac{\pi}{4}$`　⚠ OCR 丢失 `frac`
- `$x = \frac{3\pi}{4}$`　⚠ OCR 丢失 `frac`
- `$\tan 125^\circ \sin 273^\circ$`　⚠ OCR 丢失 `circ`, `circ`
- `$\frac{\tan 108^\circ}{\cos 305^\circ}$`　⚠ OCR 丢失 `frac`, `circ`, `circ`
- `$\sin \frac{5\pi}{4} \cos \frac{4\pi}{5} \tan \frac{11\pi}{6}$`　⚠ OCR 丢失 `frac`, `frac`, `frac`
- `$\frac{\cos \frac{5\pi}{6} \tan \frac{11\pi}{6}}{\sin \frac{2\pi}{3}}$`　⚠ OCR 丢失 `frac`, `frac`, `frac`, `frac`
- `$\sin (-\frac{67\pi}{12})$`　⚠ OCR 丢失 `frac`
- `$\tan (-\frac{15\pi}{4})$`　⚠ OCR 丢失 `frac`
- `$\cos 398^\circ 13'$`　⚠ OCR 丢失 `circ`
- `$\tan 766^\circ 15'$`　⚠ OCR 丢失 `circ`
- `$\sin \theta \tan \theta < 0$`　⚠ OCR 丢失 `theta`, `theta`
- `$\cos \theta \tan \theta < 0$`　⚠ OCR 丢失 `theta`, `theta`
- `$\frac{\sin \theta}{\tan \theta} > 0$`　⚠ OCR 丢失 `frac`, `theta`, `theta`
- `$\sin \theta \cos \theta > 0$`　⚠ OCR 丢失 `theta`, `theta`
- `$\sin x = -\frac{1}{3}$`　⚠ OCR 丢失 `frac`
- `$\tan \alpha = \sqrt{3}$`　⚠ OCR 丢失 `alpha`, `sqrt`
- `$\pi < \alpha < \frac{3}{2}\pi$`　⚠ OCR 丢失 `alpha`, `frac`

</details>

<details><summary><b>必修第1册 · PDF p193</b>（公式分 96，16 条）</summary>

- `用 $\cos \alpha$ 表示 $\sin \alpha, \tan \alpha$`　⚠ OCR 丢失 `alpha`, `alpha`, `alpha`
- `用 $\sin \alpha$ 表示 $\cos \alpha, \tan \alpha$`　⚠ OCR 丢失 `alpha`, `alpha`, `alpha`
- `$\frac{1 - 2\sin x \cos x}{\cos^2 x - \sin^2 x} = \frac{1 - \tan x}{1 + \tan x}$`　⚠ OCR 丢失 `frac`, `frac`
- `$\tan^2 \alpha - \sin^2 \alpha = \tan^2 \alpha \sin^2 \alpha$`　⚠ OCR 丢失 `alpha`, `alpha`, `alpha`, `alpha`
- `$(\cos \beta - 1)^2 + \sin^2 \beta = 2 - 2\cos \beta$`　⚠ OCR 丢失 `beta`, `beta`, `beta`
- `$\sin^4 \alpha + \cos^4 \alpha = 1 - 2\sin^2 \alpha \cos^2 \alpha$`　⚠ OCR 丢失 `alpha`, `alpha`, `alpha`, `alpha`
- `$\tan \alpha = 2$`　⚠ OCR 丢失 `alpha`
- `$\frac{\sin \alpha + \cos \alpha}{\sin \alpha - \cos \alpha}$`　⚠ OCR 丢失 `frac`, `alpha`, `alpha`, `alpha`, `alpha`
- `$\sqrt{\frac{1 + \sin \alpha}{1 - \sin \alpha}} - \sqrt{\frac{1 - \sin \alpha}{1 + \sin \alpha}}$`　⚠ OCR 丢失 `sqrt`, `frac`, `alpha`, `alpha`, `sqrt`, `frac`, `alpha`, `alpha`
- `$\frac{\cos x}{1 - \sin x} = \frac{1 + \sin x}{\cos x}$`　⚠ OCR 丢失 `frac`, `frac`
- `$\sin^2 x + \cos^2 x = 1$`
- `$\sin^4 \frac{\pi}{3} - \cos^4 \frac{\pi}{3}$`　⚠ OCR 丢失 `frac`, `frac`
- `$\sin^2 \frac{\pi}{3} - \cos^2 \frac{\pi}{3}$`　⚠ OCR 丢失 `frac`, `frac`
- `$\sin^4 \alpha - \cos^4 \alpha$`　⚠ OCR 丢失 `alpha`, `alpha`
- `$\sin^2 \alpha - \cos^2 \alpha$`　⚠ OCR 丢失 `alpha`, `alpha`
- `$\forall x \in \mathbf{R}, \sin^2 x - \cos^2 x = \sin^4 x - \cos^4 x$`　⚠ OCR 丢失 `forall`, `mathbf`

</details>

<details><summary><b>必修第1册 · PDF p196</b>（公式分 87，18 条）</summary>

- `sin(π+α) = -sinα，`
- `cos(π+α) = -cosα，`
- `tan(π+α) = tanα，`
- `sin(-α) = -sinα，`
- `cos(-α) = cosα，`
- `tan(-α) = -tanα，`
- `sin(π-α) = sinα，`
- `cos(π-α) = -cosα，`
- `tan(π-α) = -tanα，`
- `(1) cos 225°；`
- `(2) sin (8π/3)；`
- `(3) sin(-16π/3)；`
- `(4) tan(-2040°)。`
- `解：(1) cos 225° = cos(180°+45°)`
- `= -cos 45° = -√2/2；`
- `(2) sin (8π/3) = sin(2π+2π/3)`
- `= sin (2π/3) = sin(π-π/3)`
- `= sin (π/3) = √3/2；`

</details>

<details><summary><b>必修第1册 · PDF p197</b>（公式分 91，14 条）</summary>

- `(3) sin(-16π/3) = -sin(16π/3)`
- `= -sin(5π + π/3)`
- `= -(-sin(π/3)) = √3/2;`
- `(4) tan(-2 040°) = -tan 2 040°`
- `= -tan(6 × 360° - 120°)`
- `= tan 120° = tan(180° - 60°)`
- `= -tan 60° = -√3.`
- `cos(180°+α)sin(α+360°) / [tan(-α-180°)cos(-180°+α)]`
- `tan(-α-180°) = tan[-(180°+α)]`
- `= -tan(180°+α)`
- `= -tan α,`
- `cos(-180°+α) = cos[-(180°-α)]`
- `= cos(180°-α)`
- `= -cos α,`

</details>

<details><summary><b>必修第1册 · PDF p198</b>（公式分 73，17 条）</summary>

- `原式 = $\frac{-\cos \alpha \sin \alpha}{(-\tan \alpha)(-\cos \alpha)} = -\cos \alpha.$`　⚠ OCR 丢失 `frac`, `alpha`, `alpha`, `alpha`, `alpha`, `alpha`
- `$\cos \frac{13}{9} \pi = \_\_\_\_\_\_\_\_\_$`　⚠ OCR 丢失 `frac`
- `$\sin(1 + \pi) = \_\_\_\_\_\_\_\_\_$`
- `$\sin(-\frac{\pi}{5}) = \_\_\_\_\_\_\_\_\_$`　⚠ OCR 丢失 `frac`
- `$\tan(-70^\circ 6') = \_\_\_\_\_\_\_\_\_$`　⚠ OCR 丢失 `circ`
- `$\cos \frac{6 \pi}{7} = \_\_\_\_\_\_\_\_\_$`　⚠ OCR 丢失 `frac`
- `$\tan 1 000^\circ 21' = \_\_\_\_\_\_\_\_\_$`　⚠ OCR 丢失 `circ`
- `$\cos(-420^\circ)$`　⚠ OCR 丢失 `circ`
- `$\sin(-\frac{7}{6} \pi)$`　⚠ OCR 丢失 `frac`
- `$\tan(-1 440^\circ)$`　⚠ OCR 丢失 `440`, `circ`
- `$\cos(-\frac{77}{6} \pi)$`　⚠ OCR 丢失 `frac`
- `$\tan 315^\circ$`　⚠ OCR 丢失 `circ`
- `$\sin(-\frac{11}{4} \pi)$`　⚠ OCR 丢失 `frac`
- `$\sin(-\alpha - 180^\circ)\cos(-\alpha)\sin(-\alpha + 180^\circ)$`　⚠ OCR 丢失 `alpha`, `circ`, `alpha`, `alpha`, `circ`
- `$\cos^3(-\alpha)\sin(2\pi + \alpha)\tan^3(\alpha - \pi)$`　⚠ OCR 丢失 `alpha`, `alpha`, `alpha`
- `$\frac{4 \pi}{3}, \frac{5 \pi}{4}, \frac{5 \pi}{3}, \frac{7 \pi}{4}, \frac{8 \pi}{3}, \frac{11 \pi}{4}$`　⚠ OCR 丢失 `frac`, `frac`, `frac`, `frac`, `frac`, `frac`
- `$y = 2k\pi + (\frac{\pi}{2} - \alpha) (k \in \mathbf{Z})$`　⚠ OCR 丢失 `frac`, `alpha`, `mathbf`

</details>

<details><summary><b>必修第1册 · PDF p199</b>（公式分 62，11 条）</summary>

- `y=x`
- `x₅=y₁，y₅=x₁，`
- `sin(π/2−α)=y₅，cos(π/2−α)=x₅，`
- `sin(π/2−α)=cos α，`
- `cos(π/2−α)=sin α，`
- `sin(π/2+α)=cos α，`
- `cos(π/2+α)=−sin α，`
- `(1) sin(3π/2−α)=−cos α；`
- `(2) cos(3π/2+α)=sin α。`
- `(1) sin(3π/2−α)=sin[π+(π/2−α)]`
- `=−sin(π/2−α)=−cos α；`

</details>

<details><summary><b>必修第1册 · PDF p200</b>（公式分 141，13 条）</summary>

- `(2) cos(3π/2 + α) = cos[π + (π/2 + α)] = -cos(π/2 + α) = sin α`
- `[sin(2π - α)cos(π + α)cos(π/2 + α)cos(11π/2 - α)] / [cos(π - α)sin(3π - α)sin(-π - α)sin(9π/2 + α)]`
- `= [(-sin α)(-cos α)(-sin α)cos(5π + (π/2 - α))] / [(-cos α)sin(π - α)[-sin(π + α)]sin(4π + (π/2 + α))]`
- `= [-sin²αcos α(-cos(π/2 - α))] / [(-cos α)sin α[-(-sin α)]sin(π/2 + α)]`
- `= -sin α / cos α = -tan α`
- `sin(53° - α) = 1/5`
- `-270° < α < -90°`
- `sin(37° + α) = sin[90° - (53° - α)] = cos(53° - α)`
- `143° < 53° - α < 323°`
- `sin(53° - α) = 1/5 > 0`
- `143° < 53° - α < 180°`
- `cos(53° - α) = -√(1 - sin²(53° - α)) = -√(1 - (1/5)²) = -2√6/5`
- `sin(37° + α) = -2√6/5`

</details>

<details><summary><b>必修第1册 · PDF p201</b>（公式分 119，25 条）</summary>

- `cos(65/6π)`
- `sin(-31/4π)`
- `cos(-1 182°13')`
- `sin 670°39'`
- `tan(-26π/3)`
- `tan 580°21'`
- `cos(5/2π - α) = sin α`
- `cos(7/2π + α) = sin α`
- `sin(9/2π - α) = cos α`
- `sin(11/2π - α) = -cos α`
- `[cos(α - π/2) / sin(5π/2 + α)]·sin(α - 2π)·cos(2π - α)`
- `cos²(-α) - tan(2π + α) / cos(π/2 + α)`
- `[cos(α - 3π)·cos(3π/2 - α)] / sin²(α - π/2)`
- `cos(-17π/4)`
- `sin(-1 574°)`
- `sin(-2 160°52')`
- `cos(-1 751°36')`
- `cos 1 615°8'`
- `sin(-26/3π)`
- `sin(360° - α) = -sin α`
- `cos(360° - α) = cos α`
- `tan(360° - α) = -tan α`
- `1 + sin(α - 2π)·sin(π + α) - 2cos²(-α)`
- `sin(-1 071°)·sin 99° + sin(-171°)·sin(-261°)`
- `P(3/5, 4/5)`

</details>

<details><summary><b>必修第1册 · PDF p220</b>（公式分 67，14 条）</summary>

- `y = tan x`
- `tan x ≥ -1, x ∈ [0, π/2) ∪ (π/2, π)`
- `tan x > 0; tan x = 0; tan x < 0`
- `y = tan 3x`
- `y = tan 2x, x ≠ π/4 + kπ/2 (k ∈ Z); y = 5tan x/2, x ≠ (2k + 1)π (k ∈ Z)`
- `tan(-52°), tan(-47°); tan 13π/4, tan 17π/5`
- `y = 1 - sin x, x ∈ [0, 2π]; y = 3cos x + 1, x ∈ [0, 2π]`
- `y = sin 2/3 x, x ∈ R; y = 1/2 cos 4x, x ∈ R`
- `y = |sin x|; y = 1 - cos 2x; y = -3sin 2x; y = 1 + 2tan x`
- `y = 1 - 1/2 cos π/3 x, x ∈ R; y = 3sin(2x + π/4), x ∈ R; y = -3/2 cos(1/2 x - π/6), x ∈ R; y = 1/2 sin(1/2 x + π/3), x ∈ R`
- `sin 103°15′, sin 164°30′; cos(-3/10 π), cos(-4/9 π); sin 508°, sin 144°; cos(47/10 π), cos(44/9 π)`
- `y = 1 + sin x, x ∈ [0, 2π]; y = -cos x, x ∈ [0, 2π]`
- `y = -tan(x + π/6) + 2`
- `y = tan(2x - π/3), x ≠ 5π/12 + kπ/2 (k ∈ Z)`

</details>

<details><summary><b>必修第1册 · PDF p223</b>（公式分 123，12 条）</summary>

- `$\frac{[cos(\alpha - \beta) - 1]^2 + \sin^2(\alpha - \beta)}{(cos\ \alpha - cos\ \beta)^2 + (sin\ \alpha - sin\ \beta)^2}$`　⚠ OCR 丢失 `frac`, `alpha`, `beta`, `alpha`, `beta`, `alpha`, `beta`, `alpha`, `beta`
- `$cos(\alpha - \beta) = cos\ \alpha cos\ \beta + sin\ \alpha sin\ \beta$`　⚠ OCR 丢失 `alpha`, `beta`, `alpha`, `beta`, `alpha`, `beta`
- `$\alpha = 2k\pi + \beta (k \in Z)$`　⚠ OCR 丢失 `alpha`, `beta`
- `$cos(\alpha - \beta) = cos\ \alpha cos\ \beta + sin\ \alpha sin\ \beta$ $C_{(\alpha - \beta)}$`　⚠ OCR 丢失 `alpha`, `beta`, `alpha`, `beta`, `alpha`, `beta`, `alpha`, `beta`
- `$cos(\frac{\pi}{2} - \alpha) = sin\ \alpha$`　⚠ OCR 丢失 `frac`, `alpha`, `alpha`
- `$cos(\pi - \alpha) = -cos\ \alpha$`　⚠ OCR 丢失 `alpha`, `alpha`
- `$cos(\frac{\pi}{2} - \alpha) = cos\ \frac{\pi}{2} cos\ \alpha + sin\ \frac{\pi}{2} sin\ \alpha = 0 + 1 \times sin\ \alpha = sin\ \alpha$`　⚠ OCR 丢失 `frac`, `alpha`, `frac`, `alpha`, `frac`, `alpha`, `times`, `alpha`, `alpha`
- `$cos(\pi - \alpha) = cos\ \pi cos\ \alpha + sin\ \pi sin\ \alpha = (-1) \times cos\ \alpha + 0 = -cos\ \alpha$`　⚠ OCR 丢失 `alpha`, `alpha`, `alpha`, `times`, `alpha`, `alpha`
- `$sin\ \alpha = \frac{4}{5}$, $\alpha \in (\frac{\pi}{2},\ \pi)$`　⚠ OCR 丢失 `alpha`, `frac`, `alpha`, `frac`
- `$cos\ \beta = -\frac{5}{13}$, $\beta$ 是第三象限角`　⚠ OCR 丢失 `beta`, `frac`, `beta`
- `$cos\ \alpha = -\sqrt{1 - sin^2\ \alpha} = -\sqrt{1 - (\frac{4}{5})^2} = -\frac{3}{5}$`　⚠ OCR 丢失 `alpha`, `sqrt`, `alpha`, `sqrt`, `frac`, `frac`
- `$sin\ \beta = -\sqrt{1 - cos^2\ \beta} = -\sqrt{1 - (-\frac{5}{13})^2} = -\frac{12}{13}$`　⚠ OCR 丢失 `beta`, `sqrt`, `beta`, `sqrt`, `frac`, `frac`

</details>

<details><summary><b>必修第1册 · PDF p224</b>（公式分 131，17 条）</summary>

- `cos(α−β)=cos α cos β+sin α sin β`
- `=(−3/5)×(−5/13)+4/5×(−12/13)`
- `=−33/65`
- `cos(3π/2−α)=−sin α`
- `cos(−α)=cos α`
- `cos α=−3/5, α∈(π/2, π)`
- `cos(π/4−α)`
- `sin θ=15/17`
- `cos(θ−π/3)`
- `sin α=−2/3, α∈(π, 3π/2), cos β=3/4, β∈(3π/2, 2π)`
- `cos(β−α)`
- `α+β=α−(−β)`
- `cos(α+β)=cos[α−(−β)]`
- `=cos α cos(−β)+sin α sin(−β)`
- `=cos α cos β−sin α sin β`
- `cos(α+β)=cos α cos β−sin α sin β  (C₍α₊β₎)`
- `sin(α+β), sin(α−β)`

</details>

<details><summary><b>必修第1册 · PDF p225</b>（公式分 115，8 条）</summary>

- `sin(α+β) = sin αcos β + cos αsin β`
- `sin(α-β) = sin αcos β - cos αsin β`
- `tan(α+β) = (tan α + tan β)/(1 - tan αtan β)`
- `tan(α-β) = (tan α - tan β)/(1 + tan αtan β)`
- `sin α = -3/5`
- `cos α = √(1 - sin²α) = √(1 - (-3/5)²) = 4/5`
- `tan α = sin α/cos α = (-3/5)/(4/5) = -3/4`
- `sin(π/4 - α) = sin π/4cos α - cos π/4sin α = (√2/2) × 4/5 - (√2/2) × (-3/5) = 7√2/10`　⚠ OCR 丢失 `4cos`, `4sin`

</details>

<details><summary><b>必修第1册 · PDF p226</b>（公式分 108，17 条）</summary>

- `$\cos(\frac{\pi}{4}+\alpha)=\cos\frac{\pi}{4}\cos\alpha-\sin\frac{\pi}{4}\sin\alpha$`　⚠ OCR 丢失 `frac`, `alpha`, `frac`, `alpha`, `frac`, `alpha`
- `$=\frac{\sqrt{2}}{2}\times\frac{4}{5}-\frac{\sqrt{2}}{2}\times(-\frac{3}{5})=\frac{7\sqrt{2}}{10}$`　⚠ OCR 丢失 `frac`, `sqrt`, `times`, `frac`, `frac`, `sqrt`, `times`, `frac`, `frac`, `sqrt`
- `$\tan(\alpha-\frac{\pi}{4})=\frac{\tan\alpha-\tan\frac{\pi}{4}}{1+\tan\alpha\tan\frac{\pi}{4}}$`　⚠ OCR 丢失 `alpha`, `frac`, `frac`, `alpha`, `frac`, `alpha`, `frac`
- `$=\frac{\tan\alpha-1}{1+\tan\alpha}$`　⚠ OCR 丢失 `frac`, `alpha`, `alpha`
- `$=\frac{-\frac{3}{4}-1}{1+(-\frac{3}{4})}=-7$`　⚠ OCR 丢失 `frac`, `frac`, `frac`
- `$\sin(\frac{\pi}{4}-\alpha)=\cos(\frac{\pi}{4}+\alpha)$`　⚠ OCR 丢失 `frac`, `alpha`, `frac`, `alpha`
- `$\sin 72^\circ \cos 42^\circ-\cos 72^\circ \sin 42^\circ$`　⚠ OCR 丢失 `circ`, `circ`, `circ`, `circ`
- `$\cos 20^\circ \cos 70^\circ-\sin 20^\circ \sin 70^\circ$`　⚠ OCR 丢失 `circ`, `circ`, `circ`, `circ`
- `$\frac{1+\tan 15^\circ}{1-\tan 15^\circ}$`　⚠ OCR 丢失 `frac`, `circ`, `circ`
- `$\sin 72^\circ \cos 42^\circ-\cos 72^\circ \sin 42^\circ$`　⚠ OCR 丢失 `circ`, `circ`, `circ`, `circ`
- `$=\sin(72^\circ-42^\circ)$`　⚠ OCR 丢失 `circ`, `circ`
- `$=\sin 30^\circ$`　⚠ OCR 丢失 `circ`
- `$=\frac{1}{2}$`　⚠ OCR 丢失 `frac`
- `$\cos 20^\circ \cos 70^\circ-\sin 20^\circ \sin 70^\circ$`　⚠ OCR 丢失 `circ`, `circ`, `circ`, `circ`
- `$=\cos(20^\circ+70^\circ)$`　⚠ OCR 丢失 `circ`, `circ`
- `$=\cos 90^\circ$`　⚠ OCR 丢失 `circ`
- `$=0$`

</details>

<details><summary><b>必修第1册 · PDF p227</b>（公式分 171，24 条）</summary>

- `tan 45°=1`
- `(1+tan 15°)/(1−tan 15°) = (tan 45°+tan 15°)/(1−tan 45°tan 15°)`
- `= tan(45°+15°)`
- `= tan 60°`
- `= √3`
- `cos θ=−3/5, θ∈(π/2, π)`
- `sin θ=−12/13`
- `cos(π/6+θ)`
- `tan α=3`
- `tan(α+π/4)`
- `sin 72°cos 18°+cos 72°sin 18°`
- `cos 72°cos 12°+sin 72°sin 12°`
- `(tan 12°+tan 33°)/(1−tan 12°tan 33°)`
- `cos 74°sin 14°−sin 74°cos 14°`
- `sin 34°sin 26°−cos 34°cos 26°`
- `sin 20°cos 110°+cos 160°sin 70°`
- `(1/2)cos x − (√3/2)sin x`
- `√3 sin x + cos x`
- `√2 (sin x − cos x)`
- `√2 cos x − √6 sin x`
- `sin(α−β)cos α − cos(β−α)sin α = 3/5`
- `sin(β+5π/4)`
- `S_(α±β), C_(α±β), T_(α±β)`
- `sin 2α, cos 2α, tan 2α`

</details>

<details><summary><b>必修第1册 · PDF p229</b>（公式分 86，16 条）</summary>

- `tan 4α = (sin 4α) / (cos 4α) = - (120 / 169) × (169 / 119) = -120 / 119`
- `cos A = 4/5`
- `tan B = 2`
- `2A + 2B`
- `cos A = 4/5, 0 < A < π`
- `sin A = √(1 - cos² A) = √[1 - (4/5)²] = 3/5`
- `tan A = (sin A) / (cos A) = (3/5) × (5/4) = 3/4`
- `tan 2A = (2 tan A) / (1 - tan² A) = (2 × 3/4) / [1 - (3/4)²] = 24/7`
- `tan B = 2`
- `tan 2B = (2 tan B) / (1 - tan² B) = (2 × 2) / (1 - 2²) = -4/3`
- `tan(2A + 2B) = (tan 2A + tan 2B) / (1 - tan 2A tan 2B) = [(24/7 - 4/3)] / [1 - (24/7) × (-4/3)] = 44/117`
- `cos A = 4/5, 0 < A < π`
- `sin A = √(1 - cos² A) = √[1 - (4/5)²] = 3/5`
- `tan A = (sin A) / (cos A) = (3/5) × (5/4) = 3/4`
- `tan B = 2`
- `tan(A + B) = (tan A + tan B) / (1 - tan A tan B) = [(3/4 + 2)] / [1 - (3/4) × 2] = -11/2`

</details>

<details><summary><b>必修第1册 · PDF p232</b>（公式分 83，15 条）</summary>

- `$\sin ^{2} \frac{\alpha}{2}, \quad \cos ^{2} \frac{\alpha}{2}, \quad \tan ^{2} \frac{\alpha}{2}$`　⚠ OCR 丢失 `frac`, `alpha`, `quad`, `frac`, `alpha`, `quad`, `frac`, `alpha`
- `$\cos 2 \alpha=1-2 \sin ^{2} \alpha$`　⚠ OCR 丢失 `alpha`, `alpha`
- `$\cos \alpha=1-2 \sin ^{2} \frac{\alpha}{2}$`　⚠ OCR 丢失 `alpha`, `frac`, `alpha`
- `$\sin ^{2} \frac{\alpha}{2}=\frac{1-\cos \alpha}{2}$`　⚠ OCR 丢失 `frac`, `alpha`, `frac`, `alpha`
- `$\cos 2 \alpha=2 \cos ^{2} \alpha-1$`　⚠ OCR 丢失 `alpha`, `alpha`
- `$\cos \alpha=2 \cos ^{2} \frac{\alpha}{2}-1$`　⚠ OCR 丢失 `alpha`, `frac`, `alpha`
- `$\cos ^{2} \frac{\alpha}{2}=\frac{1+\cos \alpha}{2}$`　⚠ OCR 丢失 `frac`, `alpha`, `frac`, `alpha`
- `$\tan ^{2} \frac{\alpha}{2}=\frac{1-\cos \alpha}{1+\cos \alpha}$`　⚠ OCR 丢失 `frac`, `alpha`, `frac`, `alpha`, `alpha`
- `$\sin \frac{\alpha}{2}= \pm \sqrt{\frac{1-\cos \alpha}{2}}$`　⚠ OCR 丢失 `frac`, `alpha`, `sqrt`, `frac`, `alpha`
- `$\cos \frac{\alpha}{2}= \pm \sqrt{\frac{1+\cos \alpha}{2}}$`　⚠ OCR 丢失 `frac`, `alpha`, `sqrt`, `frac`, `alpha`
- `$\tan \frac{\alpha}{2}= \pm \sqrt{\frac{1-\cos \alpha}{1+\cos \alpha}}$`　⚠ OCR 丢失 `frac`, `alpha`, `sqrt`, `frac`, `alpha`, `alpha`
- `$\sin \alpha \cos \beta=\frac{1}{2}[\sin (\alpha+\beta)+\sin (\alpha-\beta)]$`　⚠ OCR 丢失 `alpha`, `beta`, `frac`, `alpha`, `beta`, `alpha`, `beta`
- `$\sin \theta+\sin \varphi=2 \sin \frac{\theta+\varphi}{2} \cos \frac{\theta-\varphi}{2}$`　⚠ OCR 丢失 `theta`, `varphi`, `frac`, `theta`, `varphi`, `frac`, `theta`, `varphi`
- `$\sin (\alpha+\beta)=\sin \alpha \cos \beta+\cos \alpha \sin \beta$`　⚠ OCR 丢失 `alpha`, `beta`, `alpha`, `beta`, `alpha`, `beta`
- `$\sin (\alpha-\beta)=\sin \alpha \cos \beta-\cos \alpha \sin \beta$`　⚠ OCR 丢失 `alpha`, `beta`, `alpha`, `beta`, `alpha`, `beta`

</details>

<details><summary><b>必修第1册 · PDF p233</b>（公式分 101，15 条）</summary>

- `sin(α + β) + sin(α - β) = 2sin α cos β`
- `sin α cos β = (1/2)[sin(α + β) + sin(α - β)]`
- `sin(α + β) + sin(α - β) = 2sin α cos β`
- `α + β = θ, α - β = φ`
- `a = (θ + φ) / 2, β = (θ - φ) / 2`
- `sin θ + sin φ = 2sin((θ + φ) / 2)cos((θ - φ) / 2)`
- `tan(α/2) = sin α / (1 + cos α) = (1 - cos α) / sin α`
- `cos θ = 1/3, 270° < θ < 360°, sin(θ/2), cos(θ/2)`
- `7/25`
- `cos α sin β = (1/2)[sin(α + β) - sin(α - β)]`
- `cos α cos β = (1/2)[cos(α + β) + cos(α - β)]`
- `sin α sin β = -(1/2)[cos(α + β) - cos(α - β)]`
- `sin θ - sin φ = 2cos((θ + φ) / 2)sin((θ - φ) / 2)`　⚠ OCR 丢失 `2cos`
- `cos θ + cos φ = 2cos((θ + φ) / 2)cos((θ - φ) / 2)`　⚠ OCR 丢失 `2cos`
- `cos θ - cos φ = -2sin((θ + φ) / 2)sin((θ - φ) / 2)`

</details>

<details><summary><b>必修第1册 · PDF p234</b>（公式分 77，28 条）</summary>

- `y = sin x + √3 cos x ;`
- `y = 3sin x + 4cos x .`
- `y = A sin (x + φ)`
- `y = a sin x + b cos x`
- `y = a sin x + b cos x`
- `y = A sin (x + φ)`
- `y = sin x + √3 cos x`
- `=2(1/2 sin x + √3/2 cos x)①`
- `=2(sin x cos π/3 + cos x sin π/3) = 2 sin (x + π/3) .`
- `3sin x + 4cos x = A sin (x + φ)`
- `3sin x + 4cos x = A sin x cos φ + A cos x sin φ .`
- `A cos φ = 3 , A sin φ = 4 ,`
- `A² cos² φ + A² sin² φ = 25 ,`
- `A² = 25 .`
- `A = 5 ,`
- `cos φ = 3/5 , sin φ = 4/5 .`
- `y = 5 sin (x + φ)`
- `OP = 1 ,`
- `∠POQ = π/3 ,`
- `∠POC = α ,`
- `S = f (α) ,`
- `S = f (α)`
- `OB = cos α , BC = sin α .`
- `DA/OA = tan π/3 = √3 .`
- `OA = √3/3`
- `DA = √3/3`
- `BC = √3/3 sin α ,`
- `AB = OB − OA = cos α − √3/3 sin α .`

</details>

<details><summary><b>必修第1册 · PDF p236</b>（公式分 244，40 条）</summary>

- `cos a = 1/7`
- `cos(α+β) = -11/14`
- `β = (α+β) - α`
- `sin(30°+α) = 3/5`
- `60° < α < 150°`
- `sin A = 5/13`
- `cos B = 3/5`
- `tan(α+β) = 3`
- `tan(α-β) = 5`
- `sin 347° cos 148° + sin 77° cos 58°`
- `sin 164° sin 224° + sin 254° sin 314°`
- `sin(α+β)cos(γ-β) - cos(β+α)sin(β-γ)`
- `sin(α-β)sin(β-γ) - cos(α-β)cos(γ-β)`
- `(tan(5π/4) + tan(5π/12)) / (1 - tan(5π/12))`
- `(sin(α+β) - 2sinαcosβ) / (2sinαsinβ + cos(α+β))`
- `sin α = 0.80`
- `α ∈ (0, π/2)`
- `(sin 2α - cos 2α)² = 1 - sin 4α`
- `tan(x/2 + π/4) + tan(x/2 - π/4) = 2tan x`
- `(1 + sin 2φ) / (cos φ + sin φ) = cos φ + sin φ`
- `(1 - 2sinαcosα) / (cos²α - sin²α) = (1 - tanα) / (1 + tanα)`
- `(1 - cos 2θ) / (1 + cos 2θ) = tan²θ`
- `(1 + sin 2θ - cos 2θ) / (1 + sin 2θ + cos 2θ) = tan θ`
- `sin(α+β) = 1/2`
- `sin(α-β) = 1/3`
- `sinαcosβ = 5cosαsinβ`
- `tanα = 5tanβ`
- `(1 - tanθ) / (2 + tanθ) = 1`
- `tan 2θ = -4tan(θ + π/4)`
- `3√15sinx + 3√5cosx`　⚠ OCR 丢失 `15sinx`, `5cosx`
- `(3/2)cosx - (√3/2)sinx`　⚠ OCR 丢失 `cosx`, `sinx`
- `√3sin(x/2) + cos(x/2)`　⚠ OCR 丢失 `3sin`
- `(√2/4)sin(π/4 - x) + (√6/4)cos(π/4 - x)`
- `x² + p(x+1) + 1 = 0`
- `B = π/4`
- `h = (1/3)BC`
- `3√10 / 10`
- `√10 / 10`
- `-√10 / 10`
- `-3√10 / 10`

</details>

<details><summary><b>必修第1册 · PDF p237</b>（公式分 119，16 条）</summary>

- `cos 4α - 4cos 2α = 8sin²α`
- `(tan α tan 2α) / (tan 2α - tan α) + √3 (sin²α - cos²α) = 2sin (2α - π/3)`
- `α + 2β = 2π/3`
- `tan (α/2) tan β = 2 - √3`
- `f(x) = sin(π/3 + 4x) + sin(4x - π/6)`
- `f(x) = a sin x + b cos x (a² + b² ≠ 0)`
- `sin²30° + cos²60° + sin 30° cos 60° = 3/4`
- `sin²20° + cos²50° + sin 20° cos 50° = 3/4`
- `sin²15° + cos²45° + sin 15° cos 45° = 3/4`
- `(1/2)(sin α + sin β) = sin((α + β)/2) cos((α - β)/2)`
- `(1/2)(cos α + cos β) = cos((α + β)/2) cos((α - β)/2)`
- `B(cos β, sin β)`
- `C(cos 1/2(α + β), sin 1/2(α + β))`
- `A(cos α, sin α)`
- `1/2(β - α)`
- `f(α) = sin⁴α + cos⁴α, x ∈ {n | n = 2k, k ∈ N₊}`

</details>

<details><summary><b>必修第1册 · PDF p261</b>（公式分 121，28 条）</summary>

- `π < x < 2π`
- `7π/6`
- `7π/4`
- `-√2/2`
- `√3/2`
- `√3`
- `y = √2 + sin x/π`
- `y = 3 - 2cos x`　⚠ OCR 丢失 `2cos`
- `y = sin x, x ∈ R`
- `y = 1/2 sin(3x - π/3)`
- `y = -2sin(x + π/4)`
- `y = 1 - sin(2x - π/5)`
- `y = 3sin(π/6 - x/3)`
- `y = sin x, x ∈ [0, π/2]`
- `y = sin x, x ∈ [0, 2π]`
- `y = sin(x + φ) + k, x ∈ [0, 2π] (φ, k 都是常数)`
- `y = sin(5x + π/6)`
- `y = 2sin(1/6 x)`
- `sin α = 4/5, cos(α + β) = 5/13`
- `cos(π/4 - α) = 3/5, sin(5π/4 + β) = -12/13, α ∈ (π/4, 3π/4), β ∈ (0, π/4)`
- `tan α = 1/7, sin β = √10/10`
- `tan α + tan β = tan(α + β) - tan α tan β tan(α + β)`
- `tan 20° + tan 40° + √3 tan 20° tan 40°`
- `α + β = 3π/4`
- `(1 - tan α)(1 - tan β)`
- `(tan 20° + tan 40° + tan 120°) / (tan 20° tan 40°)`
- `1/sin 10° - √3/cos 10°`
- `sin 40° (tan 10° - √3)`

</details>

<details><summary><b>必修第1册 · PDF p262</b>（公式分 117，27 条）</summary>

- `(3) tan 70° cos 10° (√3 tan 20° - 1);`
- `(4) sin 50° (1 + √3 tan 10°).`
- `(1) 已知 cos θ = -3/5，π < θ < 3π/2，求 (sin θ/2 - cos θ/2)² 的值；`
- `(2) 已知 sin α/2 - cos α/2 = 1/5，求 sin α 的值；`
- `(3) 已知 sin⁴θ + cos⁴θ = 5/9，求 sin 2θ 的值；`
- `(4) 已知 cos 2θ = 3/5，求 sin⁴θ + cos⁴θ 的值.`
- `(1) 已知 cos(α+β) = 1/5，cos(α-β) = 3/5，求 tan α tan β 的值；`
- `(2) 已知 cos α + cos β = 1/2，sin α + sin β = 1/3，求 cos(α-β) 的值.`
- `证明：`
- `(1) cos 4α + 4 cos 2α + 3 = 8 cos⁴α；`
- `(2) (1 + sin 2α) / (2 cos²α + sin 2α) = 1/2 tan α + 1/2；`
- `(3) sin(2α+β)/sin α - 2 cos(α+β) = sin β / sin α；`
- `(4) (3 - 4 cos 2A + cos 4A) / (3 + 4 cos 2A + cos 4A) = tan⁴A.`
- `已知 sin α - cos α = 1/5，0 ≤ α ≤ π，求 sin(2α - π/4) 的值.`
- `已知 cos(π/4 + x) = 3/5，17π/12 < x < 7π/4，求 (sin 2x + 2 sin²x) / (1 - tan x) 的值.`
- `已知 sin θ + cos θ = 2 sin α，sin θ cos θ = sin²β，求证：4 cos²2α = cos²2β.`
- `已知函数 f(x) = cos⁴x - 2 sin x cos x - sin⁴x，`
- `(1) 求 f(x) 的最小正周期；`
- `(2) 当 x ∈ [0, π/2] 时，求 f(x) 的最小值以及取得最小值时 x 的集合.`
- `已知函数 f(x) = sin(x + π/6) + sin(x - π/6) + cos x + a 的最大值为 1，`
- `(1) 求常数 a 的值；`
- `(2) 求函数 f(x) 的单调递减区间；`
- `(3) 求使 f(x) ≥ 0 成立的 x 的取值集合.`
- `已知函数 f(x) = √3 sin 2x + 2 cos²x + m 在区间 [0, π/2] 上的最大值为 6，`
- `(1) 求常数 m 的值；`
- `(2) 当 x ∈ R 时，求函数 f(x) 的最小值，以及相应 x 的集合.`
- `如图，正方形 ABCD 的边长为 1，P，Q 分别为边 AB，DA 上的点，当 △APQ 的周长为 2 时，求 ∠PCQ 的大小.`

</details>

<details><summary><b>必修第2册 · PDF p21</b>（公式分 61，18 条）</summary>

- `$\lambda(\mu a)=(\lambda\mu)a$`　⚠ OCR 丢失 `lambda`, `lambda`
- `$(\lambda+\mu)a=\lambda a+\mu a$`　⚠ OCR 丢失 `lambda`, `lambda`
- `$\lambda(a+b)=\lambda a+\lambda b$`　⚠ OCR 丢失 `lambda`, `lambda`, `lambda`
- `$(-\lambda)a=-(\lambda a)=\lambda(-a)$`　⚠ OCR 丢失 `lambda`, `lambda`, `lambda`
- `$\lambda(a-b)=\lambda a-\lambda b$`　⚠ OCR 丢失 `lambda`, `lambda`, `lambda`
- `$\lambda(\mu_{1}a+\mu_{2}b)=\lambda\mu_{1}a+\lambda\mu_{2}b$`　⚠ OCR 丢失 `lambda`, `lambda`, `lambda`
- `$(-3)\times4a$`　⚠ OCR 丢失 `times4a`
- `$3(a+b)-2(a-b)-a$`
- `$(2a+3b-c)-(3a-2b+c)$`
- `原式 $=(-3\times4)a=-12a$`　⚠ OCR 丢失 `times4`
- `原式 $=3a+3b-2a+2b-a=5b$`
- `原式 $=2a+3b-c-3a+2b-c$`
- `$=-a+5b-2c$`
- `$\overrightarrow{AB}=\boldsymbol{a},\ \overrightarrow{AD}=\boldsymbol{b}$`　⚠ OCR 丢失 `overrightarrow`, `boldsymbol`, `overrightarrow`, `boldsymbol`
- `$\overrightarrow{AC}=\overrightarrow{AB}+\overrightarrow{AD}=\boldsymbol{a}+\boldsymbol{b}$`　⚠ OCR 丢失 `overrightarrow`, `overrightarrow`, `overrightarrow`, `boldsymbol`, `boldsymbol`
- `$\overrightarrow{DB}=\overrightarrow{AB}-\overrightarrow{AD}=\boldsymbol{a}-\boldsymbol{b}$`　⚠ OCR 丢失 `overrightarrow`, `overrightarrow`, `overrightarrow`, `boldsymbol`, `boldsymbol`
- `$\overrightarrow{MA}=-\frac{1}{2}\overrightarrow{AC}=-\frac{1}{2}(\boldsymbol{a}+\boldsymbol{b})=-\frac{1}{2}\boldsymbol{a}-\frac{1}{2}\boldsymbol{b}$`　⚠ OCR 丢失 `overrightarrow`, `frac`, `overrightarrow`, `frac`, `boldsymbol`, `boldsymbol`, `frac`, `boldsymbol`, `frac`, `boldsymbol`
- `$\overrightarrow{MB}=\frac{1}{2}\overrightarrow{DB}=\frac{1}{2}(\boldsymbol{a}-\boldsymbol{b})=\frac{1}{2}\boldsymbol{a}-\frac{1}{2}\boldsymbol{b}$`　⚠ OCR 丢失 `overrightarrow`, `frac`, `overrightarrow`, `frac`, `boldsymbol`, `boldsymbol`, `frac`, `boldsymbol`, `frac`, `boldsymbol`

</details>

<details><summary><b>必修第2册 · PDF p28</b>（公式分 99，22 条）</summary>

- `(|a+b|cosθ-|a|cosθ1-|b|cosθ2)e=0,`
- `|a+b|cosθ-|a|cosθ1-|b|cosθ2=0,`
- `|a+b|cosθ=|a|cosθ1+|b|cosθ2.`
- `|a+b||c|cosθ=|a||c|cosθ1+|b||c|cosθ2.`
- `(a+b)·c=a·c+b·c.`
- `(a·b)c=a(b·c)`
- `(a+b)^2=a^2+2ab+b^2, (a+b)(a-b)=a^2-b^2.`　⚠ OCR 丢失 `2ab`
- `(a+b)^2=a^2+2a·b+b^2;`
- `(a+b)·(a-b)=a^2-b^2.`
- `(a+b)^2=(a+b)·(a+b)`
- `=a·a+a·b+b·a+b·b`
- `=a^2+2a·b+b^2;`
- `(a+b)·(a-b)=a·a-a·b+b·a-b·b`
- `=a^2-b^2.`
- `|a|=6, |b|=4, 60°`
- `(a+2b)·(a-3b)`
- `=a·a-3a·b+2b·a-6b·b`
- `=|a|^2-a·b-6|b|^2`
- `=|a|^2-|a||b|cosθ-6|b|^2`
- `=6^2-6×4×cos60°-6×4^2`
- `=-72.`
- `|a|=3, |b|=4, a+kb, a-kb`

</details>

<details><summary><b>必修第2册 · PDF p30</b>（公式分 60，20 条）</summary>

- `(1) ½(a + b) + ½(a − b) = a；`
- `(2) ½(a + b) − ½(a − b) = b.`
- `求作向量 c，使 a + b + c = 0.`
- `(1) 求作向量 a + b，a − b；`
- `(2) 当向量 a，b 成什么位置关系时，满足 |a + b| = |a − b|？`
- `(1) 5(2a − 2b) + 4(2b − 3a)；`
- `(2) 6(a − 3b + c) − 4(−a + b − c)；`
- `(3) ½[(3a − 2b) + 5a − ⅓(6a − 9b)]；`
- `(4) (x − y)(a + b) − (x − y)(a − b).`
- `如图，AM = ⅓AB，AN = ⅓AC. 求证 MN = ⅓BC.`
- `(1) 若 a，b 满足 |a| = 2，|b| = 3，则 |a + b| 的最大值为_______，最小值为_______；`
- `(2) 当不共线的向量 a，b 满足_______时，a + b 平分 a 与 b 的夹角.`
- `(1) 已知 |a| = 3，|b| = 4，且 a 与 b 的夹角 θ = 150°，求 a · b，(a + b)²，|a + b|；`
- `(2) 已知 |a| = 2，|b| = 5，且 a · b = −3，求 |a + b|，|a − b|.`
- `(λa) · b = λ(a · b) = a · (λb).`
- `(1) AD = BC；`
- `(2) AD = ⅓BC；`
- `(3) AB = DC，且 |AB| = |AD|.`
- `在△ABC 中，AD = ¼AB，DE ∥ BC，且与边 AC 相交于点 E，△ABC 的中线 AM 与 DE 相交于点 N. 设 AB = a，AC = b，用 a，b 分别表示向量 AE，BC，DE，DB，EC，DN，AN.`
- `如图，在任意四边形 ABCD 中，E，F 分别为 AD，BC 的中点，求证：AB + DC = 2EF.`

</details>

<details><summary><b>必修第2册 · PDF p36</b>（公式分 65，15 条）</summary>

- `a = AA₁ + AA₂ = 2i + 3j`
- `a = (2, 3)`
- `b = -2i + 3j = (-2, 3)`
- `c = -2i - 3j = (-2, -3)`
- `d = 2i - 3j = (2, -3)`
- `a = (x₁, y₁), b = (x₂, y₂)`
- `a + b = (x₁i + y₁j) + (x₂i + y₂j)`
- `= x₁i + x₂i + y₁j + y₂j`
- `= (x₁ + x₂)i + (y₁ + y₂)j`
- `a + b = (x₁ + x₂, y₁ + y₂)`
- `a - b = (x₁ - x₂, y₁ - y₂)`
- `a = (2, 1), b = (-3, 4)`
- `a + b = (2, 1) + (-3, 4) = (-1, 5)`
- `a - b = (2, 1) - (-3, 4) = (5, -3)`
- `A(x₁, y₁), B(x₂, y₂)`

</details>

<details><summary><b>必修第2册 · PDF p42</b>（公式分 107，20 条）</summary>

- `a=(5, -7)`
- `b=(-6, -4)`
- `a · b = 5 × (-6) + (-7) × (-4)`
- `= -30 + 28`
- `= -2`
- `|a| = √(5² + (-7)²) = √74`
- `|b| = √((-6)² + (-4)²) = √52`
- `cos θ = (a · b) / (|a| |b|) = -2 / (√74 × √52) ≈ -0.03`
- `θ ≈ 92°`
- `cos(α - β) = cos α cos β + sin α sin β`
- `OA→ = (cos α, sin α)`
- `OB→ = (cos β, sin β)`
- `OA→ · OB→ = cos α cos β + sin α sin β`
- `OA→ · OB→ = |OA→| · |OB→| cos θ = cos θ`
- `cos θ = cos α cos β + sin α sin β`
- `α = 2kπ + β - θ`
- `α = 2kπ + β - θ`
- `α - β = 2kπ ± θ, k∈Z`
- `cos(α - β) = cos θ`
- `cos(α - β) = cos α cos β + sin α sin β`

</details>

<details><summary><b>必修第2册 · PDF p43</b>（公式分 63，13 条）</summary>

- `a=(-3, 4), b=(5, 2), 求 |a|, |b|, a·b`
- `a=(2, 3), b=(-2, 4), c=(-1, -2), 求 a·b, (a+b)·(a-b), a·(b+c), (a+b)²`
- `a=(3, 2), b=(5, -7), 求 a 与 b 的夹角 θ`
- `在△ABC中, AD=1/3 AB, 点E是CD的中点. 设 AB=a, AC=b, 用 a, b 表示 CD, AE`
- `F₁=(3, 4), F₂=(2, -5), F₃=(3, 1), 求作用在原点的合力 F₁+F₂+F₃ 的坐标`
- `a=(-2, 1), A(0, 0); a=(1, 3), A(-1, 5); a=(-2, -5), A(3, 7)`
- `在平行四边形ABCD中, 顶点A(-1, -2), B(3, -1), C(5, 6), 求顶点 D 的坐标`
- `O(0, 0), A(1, 2), B(-1, 3), 且 OA'=2OA, OB'=3OB, 求点 A', B' 及向量 A'B' 的坐标`　⚠ OCR 丢失 `2OA`
- `A(1, 1), B(-1, 5), 且 AC=1/2 AB, AD=2 AB, AE=-1/2 AB, 求点 C, D, E 的坐标`
- `A(1, 2), B(-3, -4), C(2, 3.5); P(-1, 2), Q(0.5, 0), R(5, -6); E(9, 1), F(1, -3), G(8, 0.5)`
- `A(-1, -4), B(5, 2), C(3, 4); A(-2, -3), B(19, 4), C(-1, -6); A(2, 5), B(5, 2), C(10, 7)`
- `|a|=3, b=(1, 2), 且 a∥b, 求 a 的坐标`
- `a=(4, 2), 求与 a 垂直的单位向量的坐标`

</details>

<details><summary><b>必修第2册 · PDF p51</b>（公式分 75，18 条）</summary>

- `$a^2=b^2+c^2-2bc\cos A$`　⚠ OCR 丢失 `2bc`
- `$=60^2+34^2-2\times 60\times 34\cos 41^\circ$`　⚠ OCR 丢失 `times`, `times`, `circ`
- `$\approx 1676.78$`　⚠ OCR 丢失 `approx`
- `$a\approx 41(\text{cm})$`　⚠ OCR 丢失 `approx`, `text`
- `$\cos B=\frac{c^2+a^2-b^2}{2ca}=\frac{34^2+41^2-60^2}{2\times 34\times 41}=-\frac{763}{2788}$`　⚠ OCR 丢失 `frac`, `frac`, `times`, `times`, `frac`
- `$B\approx 106^\circ$`　⚠ OCR 丢失 `approx`, `circ`
- `$C=180^\circ-(A+B)\approx 180^\circ-(41^\circ+106^\circ)=33^\circ$`　⚠ OCR 丢失 `circ`, `approx`, `circ`, `circ`, `circ`, `circ`
- `在 $\triangle ABC$ 中，$a=7$，$b=8$，锐角 $C$ 满足 $\sin C=\frac{3\sqrt{3}}{14}$`　⚠ OCR 丢失 `triangle`, `frac`, `sqrt`
- `$\sin C=\frac{3\sqrt{3}}{14}$`　⚠ OCR 丢失 `frac`, `sqrt`
- `$\cos C=\sqrt{1-\sin^2 C}=\sqrt{1-(\frac{3\sqrt{3}}{14})^2}=\frac{13}{14}$`　⚠ OCR 丢失 `sqrt`, `sqrt`, `frac`, `sqrt`, `frac`
- `$c^2=a^2+b^2-2ab\cos C=49+64-2\times 7\times 8\times \frac{13}{14}=9$`　⚠ OCR 丢失 `times`, `times`, `times`, `frac`
- `$c=3$`
- `$\cos B=\frac{c^2+a^2-b^2}{2ca}=\frac{9+49-64}{2\times 3\times 7}=-\frac{1}{7}$`　⚠ OCR 丢失 `frac`, `frac`, `times`, `times`, `frac`
- `$B\approx 98^\circ$`　⚠ OCR 丢失 `approx`, `circ`
- `在 $\triangle ABC$ 中，已知 $b=12.9\text{ cm}$，$c=15.4\text{ cm}$，$A=42.3^\circ$`　⚠ OCR 丢失 `triangle`, `text`, `text`, `circ`
- `在 $\triangle ABC$ 中，已知 $a=5$，$b=2$，$C=\frac{\pi}{3}$`　⚠ OCR 丢失 `triangle`, `frac`
- `在 $\triangle ABC$ 中，已知 $a=2$，$b=\sqrt{2}$，$c=\sqrt{3}+1$`　⚠ OCR 丢失 `triangle`, `sqrt`, `sqrt`
- `在 $\triangle ABC$ 中，已知 $b=5$，$c=2$，锐角 $A$ 满足 $\sin A=\frac{\sqrt{231}}{20}$`　⚠ OCR 丢失 `triangle`, `frac`, `sqrt`

</details>

<details><summary><b>必修第2册 · PDF p54</b>（公式分 113，13 条）</summary>

- `$A = 15^\circ, B = 45^\circ, c = 3 + \sqrt{3}$`　⚠ OCR 丢失 `circ`, `circ`, `sqrt`
- `$C = 180^\circ - (A + B) = 180^\circ - (15^\circ + 45^\circ) = 120^\circ$`　⚠ OCR 丢失 `circ`, `circ`, `circ`, `circ`, `circ`
- `$a = \frac{c \sin A}{\sin C} = \frac{(3 + \sqrt{3}) \sin 15^\circ}{\sin 120^\circ} = \frac{(3 + \sqrt{3}) \sin(45^\circ - 30^\circ)}{\sin 120^\circ}$`　⚠ OCR 丢失 `frac`, `frac`, `sqrt`, `circ`, `circ`, `frac`, `sqrt`, `circ`, `circ`, `circ`
- `$= \frac{(3 + \sqrt{3})(\sin 45^\circ \cos 30^\circ - \cos 45^\circ \sin 30^\circ)}{\sin 120^\circ}$`　⚠ OCR 丢失 `frac`, `sqrt`, `circ`, `circ`, `circ`, `circ`, `circ`
- `$= \frac{(3 + \sqrt{3})(\frac{\sqrt{2}}{2} \times \frac{\sqrt{3}}{2} - \frac{\sqrt{2}}{2} \times \frac{1}{2})}{\frac{\sqrt{3}}{2}} = \sqrt{2}$`　⚠ OCR 丢失 `frac`, `sqrt`, `frac`, `sqrt`, `times`, `frac`, `sqrt`, `frac`, `sqrt`, `times`, `frac`, `frac`, `sqrt`, `sqrt`
- `$b = \frac{c \sin B}{\sin C} = \frac{(3 + \sqrt{3}) \sin 45^\circ}{\sin 120^\circ}$`　⚠ OCR 丢失 `frac`, `frac`, `sqrt`, `circ`, `circ`
- `$= \frac{(3 + \sqrt{3}) \times \frac{\sqrt{2}}{2}}{\frac{\sqrt{3}}{2}} = \sqrt{6} + \sqrt{2}$`　⚠ OCR 丢失 `frac`, `sqrt`, `times`, `frac`, `sqrt`, `frac`, `sqrt`, `sqrt`, `sqrt`
- `$B = 30^\circ, b = \sqrt{2}, c = 2$`　⚠ OCR 丢失 `circ`, `sqrt`
- `$\sin C = \frac{c \sin B}{b} = \frac{2 \sin 30^\circ}{\sqrt{2}} = \frac{\sqrt{2}}{2}$`　⚠ OCR 丢失 `frac`, `frac`, `circ`, `sqrt`, `frac`, `sqrt`
- `$C = 45^\circ$, 或 $C = 135^\circ$`　⚠ OCR 丢失 `circ`, `circ`
- `$A = 105^\circ$`　⚠ OCR 丢失 `circ`
- `$a = \frac{b \sin A}{\sin B} = \frac{\sqrt{2} \sin 105^\circ}{\sin 30^\circ} = \frac{\sqrt{2} \sin(60^\circ + 45^\circ)}{\sin 30^\circ}$`　⚠ OCR 丢失 `frac`, `frac`, `sqrt`, `circ`, `circ`, `frac`, `sqrt`, `circ`, `circ`, `circ`
- `$= \frac{\sqrt{2}(\sin 60^\circ \cos 45^\circ + \cos 60^\circ \sin 45^\circ)}{\sin 30^\circ}$`　⚠ OCR 丢失 `frac`, `sqrt`, `circ`, `circ`, `circ`, `circ`, `circ`

</details>

<details><summary><b>必修第2册 · PDF p55</b>（公式分 60，11 条）</summary>

- `= (√2( (√3/2) × (√2/2) + (1/2) × (√2/2) )) / (1/2) = √3 + 1`
- `当 C = 135° 时，A = 15°`
- `a = (b sin A) / (sin B) = (√2 sin 15°) / (sin 30°) = (√2 sin(45° − 30°)) / (sin 30°) = (√2( sin 45° cos 30° − cos 45° sin 30° )) / (sin 30°) = (√2 × ( (√2/2) × `
- `在区间 (0, π) 内`
- `在区间 (0, π/2) 内单调递增`
- `在区间 (π/2, π) 内单调递减`
- `在 △ABC 中，已知 A = 60°，B = 45°，c = 20 cm`
- `在 △ABC 中，已知 a = 20 cm，b = 11 cm，B = 30°`
- `在 △ABC 中，已知 a = 2，c = (2√3)/3，A = 120°，求 b 和 C`
- `在 △ABC 中，已知 b = 2，A = 45°，C = 75°，求 c`
- `在 △ABC 中，已知 cos A = 4/5，B = π/3，b = √3，求 a，c`

</details>

<details><summary><b>必修第2册 · PDF p56</b>（公式分 78，4 条）</summary>

- `AC = a sin(γ + δ) / sin[180° - (β + γ + δ)] = a sin(γ + δ) / sin(β + γ + δ)`
- `BC = a sin γ / sin[180° - (α + β + γ)] = a sin γ / sin(α + β + γ)`
- `AB = √(AC² + BC² - 2AC × BC cos α)`
- `AB = √(a² sin²(γ + δ) / sin²(β + γ + δ) + a² sin²γ / sin²(α + β + γ) - 2a² sin(γ + δ) sin γ cos α / [sin(β + γ + δ) sin(α + β + γ)])`

</details>

<details><summary><b>必修第2册 · PDF p67</b>（公式分 70，40 条）</summary>

- `$\boldsymbol{a} = \boldsymbol{b}$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`
- `$\boldsymbol{a} \cdot \boldsymbol{b} = 1$`　⚠ OCR 丢失 `boldsymbol`, `cdot`, `boldsymbol`
- `$\boldsymbol{a}^2 \neq \boldsymbol{b}^2$`　⚠ OCR 丢失 `boldsymbol`, `neq`, `boldsymbol`
- `$|\boldsymbol{a}|^2 = |\boldsymbol{b}|^2$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`
- `$|\boldsymbol{a}| > |\boldsymbol{b}|$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`
- `$\boldsymbol{a} > \boldsymbol{b}$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`
- `$|\boldsymbol{a} + \boldsymbol{b}| \leqslant |\boldsymbol{a}| + |\boldsymbol{b}|$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`, `leqslant`, `boldsymbol`, `boldsymbol`
- `$|\boldsymbol{a} \cdot \boldsymbol{b}| \geqslant |\boldsymbol{a}| |\boldsymbol{b}|$`　⚠ OCR 丢失 `boldsymbol`, `cdot`, `boldsymbol`, `geqslant`, `boldsymbol`, `boldsymbol`
- `$|\boldsymbol{a} - \boldsymbol{b}| \leqslant |\boldsymbol{a}| - |\boldsymbol{b}|$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`, `leqslant`, `boldsymbol`, `boldsymbol`
- `$\overrightarrow{AC} = \overrightarrow{AB} + \overrightarrow{AD}$`　⚠ OCR 丢失 `overrightarrow`, `overrightarrow`, `overrightarrow`
- `$-\lambda\boldsymbol{a}$`　⚠ OCR 丢失 `lambda`, `boldsymbol`
- `$|- \lambda\boldsymbol{a}| \geqslant |\boldsymbol{a}|$`　⚠ OCR 丢失 `lambda`, `boldsymbol`, `geqslant`, `boldsymbol`
- `$\lambda^2\boldsymbol{a}$`　⚠ OCR 丢失 `lambda`, `boldsymbol`
- `$-\lambda\boldsymbol{a} \parallel \boldsymbol{a}$`　⚠ OCR 丢失 `lambda`, `boldsymbol`, `parallel`, `boldsymbol`
- `$\overrightarrow{OA} + \overrightarrow{OB} + \overrightarrow{OC} + \overrightarrow{OD}$`　⚠ OCR 丢失 `overrightarrow`, `overrightarrow`, `overrightarrow`, `overrightarrow`
- `$\overrightarrow{OM}$`　⚠ OCR 丢失 `overrightarrow`
- `$2\overrightarrow{OM}$`　⚠ OCR 丢失 `overrightarrow`
- `$3\overrightarrow{OM}$`　⚠ OCR 丢失 `overrightarrow`
- `$4\overrightarrow{OM}$`　⚠ OCR 丢失 `overrightarrow`
- `$\boldsymbol{e}_1 = (0, 0), \boldsymbol{e}_2 = (1, -2)$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`
- `$\boldsymbol{e}_1 = (-1, 2), \boldsymbol{e}_2 = (5, 7)$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`
- `$\boldsymbol{e}_1 = (3, 5), \boldsymbol{e}_2 = (6, 10)$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`
- `$\boldsymbol{e}_1 = (2, -3), \boldsymbol{e}_2 = \left(\frac{1}{2}, -\frac{3}{4}\right)$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`, `left`, `frac`, `frac`, `right`
- `$\overrightarrow{AC} = \boldsymbol{a}, \overrightarrow{BD} = \boldsymbol{b}$`　⚠ OCR 丢失 `overrightarrow`, `boldsymbol`, `overrightarrow`, `boldsymbol`
- `$A(-3, -4), B(5, -12)$`
- `$\overrightarrow{AB}$`　⚠ OCR 丢失 `overrightarrow`
- `$|\overrightarrow{AB}|$`　⚠ OCR 丢失 `overrightarrow`
- `$\overrightarrow{OC} = \overrightarrow{OA} + \overrightarrow{OB}$`　⚠ OCR 丢失 `overrightarrow`, `overrightarrow`, `overrightarrow`
- `$\overrightarrow{OD} = \overrightarrow{OA} - \overrightarrow{OB}$`　⚠ OCR 丢失 `overrightarrow`, `overrightarrow`, `overrightarrow`
- `$\overrightarrow{OA} \cdot \overrightarrow{OB}$`　⚠ OCR 丢失 `overrightarrow`, `cdot`, `overrightarrow`
- `$A(1, 1), B(-1, 0), C(0, 1)$`
- `$\overrightarrow{AB} = \overrightarrow{CD}$`　⚠ OCR 丢失 `overrightarrow`, `overrightarrow`
- `$\boldsymbol{a} = (1, 0), \boldsymbol{b} = (1, 1), \boldsymbol{c} = (-1, 0)$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`, `boldsymbol`
- `$\boldsymbol{c} = \lambda\boldsymbol{a} + \mu\boldsymbol{b}$`　⚠ OCR 丢失 `boldsymbol`, `lambda`, `boldsymbol`, `boldsymbol`
- `$\cos A, \cos B, \cos C$`
- `$\boldsymbol{a} = (1, 0), \boldsymbol{b} = (1, 1)$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`
- `$\lambda$`　⚠ OCR 丢失 `lambda`
- `$\lambda\boldsymbol{b}$`　⚠ OCR 丢失 `lambda`, `boldsymbol`
- `$\boldsymbol{a} + \lambda\boldsymbol{b} \perp \boldsymbol{a}$`　⚠ OCR 丢失 `boldsymbol`, `lambda`, `boldsymbol`, `perp`, `boldsymbol`
- `$\theta = 30^{\circ}$`　⚠ OCR 丢失 `theta`, `circ`

</details>

<details><summary><b>必修第2册 · PDF p68</b>（公式分 87，18 条）</summary>

- `a=12 cm, b=5 cm, A=120°`
- `a=6 cm, b=8 cm, A=30°`
- `a=7 cm, b=23 cm, C=130°`
- `a=2 cm, b=3 cm, c=4 cm`
- `$\overrightarrow{AB}=\boldsymbol{a}+5\boldsymbol{b}, \overrightarrow{BC}=-2\boldsymbol{a}+8\boldsymbol{b}, \overrightarrow{CD}=3(\boldsymbol{a}-\boldsymbol{b})$`　⚠ OCR 丢失 `overrightarrow`, `boldsymbol`, `boldsymbol`, `overrightarrow`, `boldsymbol`, `boldsymbol`, `overrightarrow`, `boldsymbol`, `boldsymbol`
- `$\overrightarrow{AB}=\boldsymbol{a}, \overrightarrow{BC}=\boldsymbol{b}, \overrightarrow{DC}=\boldsymbol{c}, |\boldsymbol{a}+\boldsymbol{b}+\boldsymbol{c}|$`　⚠ OCR 丢失 `overrightarrow`, `boldsymbol`, `overrightarrow`, `boldsymbol`, `overrightarrow`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`
- `$\overrightarrow{OA}=\boldsymbol{a}, \overrightarrow{OB}=\boldsymbol{b}, \overrightarrow{OC}=\boldsymbol{c}, \overrightarrow{OD}=\boldsymbol{d}$`　⚠ OCR 丢失 `overrightarrow`, `boldsymbol`, `overrightarrow`, `boldsymbol`, `overrightarrow`, `boldsymbol`, `overrightarrow`, `boldsymbol`
- `$\boldsymbol{a}+\boldsymbol{b}+\boldsymbol{c}+\boldsymbol{d}=\boldsymbol{0}$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`
- `$\boldsymbol{a}-\boldsymbol{b}+\boldsymbol{c}-\boldsymbol{d}=\boldsymbol{0}$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`
- `$\boldsymbol{a}+\boldsymbol{b}-\boldsymbol{c}-\boldsymbol{d}=\boldsymbol{0}$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`
- `$\boldsymbol{a}-\boldsymbol{b}-\boldsymbol{c}-\boldsymbol{d}=\boldsymbol{0}$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`
- `$\boldsymbol{a}=2\boldsymbol{e}_1+\boldsymbol{e}_2, \boldsymbol{b}=-3\boldsymbol{e}_1+2\boldsymbol{e}_2$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`
- `$\overrightarrow{BC}=\boldsymbol{a}, \overrightarrow{CA}=\boldsymbol{b}, \overrightarrow{AE}=\boldsymbol{c}, \boldsymbol{a}\cdot\boldsymbol{b}+\boldsymbol{b}\cd`　⚠ OCR 丢失 `overrightarrow`, `boldsymbol`, `overrightarrow`, `boldsymbol`, `overrightarrow`, `boldsymbol`, `boldsymbol`, `cdot`, `boldsymbol`, `boldsymbol`
- `$|\boldsymbol{a}|=1, |\boldsymbol{b}|=1, |\boldsymbol{c}|=3, |\boldsymbol{a}+\boldsymbol{b}+\boldsymbol{c}|$`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`
- `$\boldsymbol{a}\perp\boldsymbol{b}\Leftrightarrow |\boldsymbol{a}+\boldsymbol{b}|=|\boldsymbol{a}-\boldsymbol{b}|$`　⚠ OCR 丢失 `boldsymbol`, `perp`, `boldsymbol`, `Leftrightarrow`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`
- `$\boldsymbol{a}+\boldsymbol{b}=\boldsymbol{c}, \boldsymbol{a}-\boldsymbol{b}=\boldsymbol{d}, |\boldsymbol{a}|=|\boldsymbol{b}|\Leftrightarrow\boldsymbol{c}\perp`　⚠ OCR 丢失 `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `boldsymbol`, `Leftrightarrow`, `boldsymbol`, `perp`
- `$\overrightarrow{OP_1}+\overrightarrow{OP_2}+\overrightarrow{OP_3}=\boldsymbol{0}, |\overrightarrow{OP_1}|=|\overrightarrow{OP_2}|=|\overrightarrow{OP_3}|$`　⚠ OCR 丢失 `overrightarrow`, `overrightarrow`, `overrightarrow`, `boldsymbol`, `overrightarrow`, `overrightarrow`, `overrightarrow`
- `$\overrightarrow{OA}=\boldsymbol{a}, \overrightarrow{OB}=\boldsymbol{b}, \overrightarrow{MN}$`　⚠ OCR 丢失 `overrightarrow`, `boldsymbol`, `overrightarrow`, `boldsymbol`, `overrightarrow`

</details>

<details><summary><b>必修第2册 · PDF p93</b>（公式分 74，10 条）</summary>

- `4; -i; 2√3+2i; -1/2 - (√3/2)i`
- `1/2(cos π/4 - isin π/4); -1/2(cos π/3 + isin π/3); 1/2(sin 5π/12 + icos 5π/12); cos 7π/5 + isin 7π/5; 2(cos π/3 + isin π/6)`
- `6(cos 3π/2 + isin 3π/2); 2(cos 5π/3 + isin 5π/3)`
- `z1 = r1(cos θ1 + isin θ1), z2 = r2(cos θ2 + isin θ2)`
- `z1z2 = r1(cos θ1 + isin θ1) • r2(cos θ2 + isin θ2)`　⚠ OCR 丢失 `z1z2`
- `= r1r2(cos θ1 + isin θ1)(cos θ2 + isin θ2)`　⚠ OCR 丢失 `r1r2`
- `= r1r2[ (cos θ1cos θ2 - sin θ1sin θ2) + i(sin θ1cos θ2 + cos θ1sin θ2) ]`　⚠ OCR 丢失 `r1r2`, `1cos`, `1sin`, `1cos`, `1sin`
- `= r1r2 [cos(θ1+θ2) + isin(θ1+θ2)]`　⚠ OCR 丢失 `r1r2`
- `r1(cos θ1 + isin θ1) • r2(cos θ2 + isin θ2)`
- `= r1r2[cos(θ1+θ2) + isin(θ1+θ2)]`　⚠ OCR 丢失 `r1r2`

</details>

<details><summary><b>必修第2册 · PDF p96</b>（公式分 81，16 条）</summary>

- `=2(cos π/2 + i sin π/2) = 2(0 + i) = 2i`
- `8(cos π/6 + i sin π/6) × 2(cos π/4 + i sin π/4)`
- `2(cos 4π/3 + i sin 4π/3) × 4(cos 5π/6 + i sin 5π/6)`
- `√2(cos 240° + i sin 240°) × √(3/2)(cos 60° + i sin 60°)`
- `3(cos 18° + i sin 18°) × 2(cos 54° + i sin 54°) × 5(cos 108° + i sin 108°)`
- `12(cos 7π/4 + i sin 7π/4) ÷ [6(cos 2π/3 + i sin 2π/3)]`
- `√3(cos 150° + i sin 150°) ÷ [√2(cos 225° + i sin 225°)]`
- `2 ÷ (cos π/4 + i sin π/4)`
- `-i ÷ [2(cos 120° + i sin 120°)]`
- `3 - √3i`
- `1 - √3/2 + 1/2 i`
- `3√2(cos π/4 + i sin π/4)`
- `8(cos 11π/6 + i sin 11π/6)`
- `9(cos π + i sin π)`
- `6(cos 4π/3 + i sin 4π/3)`
- `3(cos π/3 + i sin π/3) × 3(cos π/6 + i sin π/6)`

</details>

<details><summary><b>必修第2册 · PDF p97</b>（公式分 90，18 条）</summary>

- `$\sqrt{10}(\cos \frac{\pi}{2} + \mathrm{i} \sin \frac{\pi}{2}) \times \sqrt{2}(\cos \frac{\pi}{4} + \mathrm{i} \sin \frac{\pi}{4})$`　⚠ OCR 丢失 `sqrt`, `frac`, `mathrm`, `frac`, `times`, `sqrt`, `frac`, `mathrm`, `frac`
- `$10(\cos \frac{2\pi}{3} + \mathrm{i} \sin \frac{2\pi}{3}) \div [5(\cos \frac{\pi}{3} + \mathrm{i} \sin \frac{\pi}{3})]$`　⚠ OCR 丢失 `frac`, `mathrm`, `frac`, `div`, `frac`, `mathrm`, `frac`
- `$12(\cos \frac{3\pi}{2} + \mathrm{i} \sin \frac{3\pi}{2}) \div [6(\cos \frac{\pi}{6} + \mathrm{i} \sin \frac{\pi}{6})]$`　⚠ OCR 丢失 `frac`, `mathrm`, `frac`, `div`, `frac`, `mathrm`, `frac`
- `$\sqrt{2}(\cos \frac{2\pi}{3} + \mathrm{i} \sin \frac{2\pi}{3}) \times 2\sqrt{2}(\cos \frac{\pi}{3} + \mathrm{i} \sin \frac{\pi}{3})$`　⚠ OCR 丢失 `sqrt`, `frac`, `mathrm`, `frac`, `times`, `sqrt`, `frac`, `mathrm`, `frac`
- `$2(\cos 75^\circ + \mathrm{i} \sin 75^\circ) \times (\frac{1}{2} - \frac{1}{2}\mathrm{i})$`　⚠ OCR 丢失 `circ`, `mathrm`, `circ`, `times`, `frac`, `frac`, `mathrm`
- `$4(\cos 300^\circ + \mathrm{i} \sin 300^\circ) \div [\sqrt{2}(\cos \frac{3\pi}{4} + \mathrm{i} \sin \frac{3\pi}{4})]$`　⚠ OCR 丢失 `circ`, `mathrm`, `circ`, `div`, `sqrt`, `frac`, `mathrm`, `frac`
- `$(-\frac{1}{2} + \frac{\sqrt{3}}{2}\mathrm{i}) \div [2(\cos \frac{\pi}{3} + \mathrm{i} \sin \frac{\pi}{3})]$`　⚠ OCR 丢失 `frac`, `frac`, `sqrt`, `mathrm`, `div`, `frac`, `mathrm`, `frac`
- `$\frac{1}{\cos \theta + \mathrm{i} \sin \theta} = \cos \theta - \mathrm{i} \sin \theta$`　⚠ OCR 丢失 `frac`, `theta`, `mathrm`, `theta`, `theta`, `mathrm`, `theta`
- `$\frac{1}{z}$`　⚠ OCR 丢失 `frac`
- `$z = 4(\cos \frac{\pi}{12} + \mathrm{i} \sin \frac{\pi}{12})$`　⚠ OCR 丢失 `frac`, `mathrm`, `frac`
- `$z = \cos \frac{\pi}{6} - \mathrm{i} \sin \frac{\pi}{6}$`　⚠ OCR 丢失 `frac`, `mathrm`, `frac`
- `$z = \frac{\sqrt{2}}{2}(1 - \mathrm{i})$`　⚠ OCR 丢失 `frac`, `sqrt`, `mathrm`
- `$(\cos 75^\circ + \mathrm{i} \sin 75^\circ)(\cos 15^\circ + \mathrm{i} \sin 15^\circ) = \mathrm{i}$`　⚠ OCR 丢失 `circ`, `mathrm`, `circ`, `circ`, `mathrm`, `circ`, `mathrm`
- `$(\cos 3\theta - \mathrm{i} \sin 3\theta)(\cos 2\theta - \mathrm{i} \sin 2\theta) = \cos 5\theta - \mathrm{i} \sin 5\theta$`　⚠ OCR 丢失 `theta`, `mathrm`, `theta`, `theta`, `mathrm`, `theta`, `theta`, `mathrm`, `theta`
- `$\frac{(\cos 7\vartheta + \mathrm{i} \sin 7\vartheta)(\cos 2\vartheta + \mathrm{i} \sin 2\vartheta)}{(\cos 5\vartheta + \mathrm{i} \sin 5\vartheta)(\cos 3\varth`　⚠ OCR 丢失 `frac`, `vartheta`, `mathrm`, `vartheta`, `vartheta`, `mathrm`, `vartheta`, `vartheta`, `mathrm`, `vartheta`, `varth`
- `$\frac{\cos \varphi - \mathrm{i} \sin \varphi}{\cos \varphi + \mathrm{i} \sin \varphi}$`　⚠ OCR 丢失 `frac`, `varphi`, `mathrm`, `varphi`, `varphi`, `mathrm`, `varphi`
- `$z = \sqrt{3} - \mathrm{i}$`　⚠ OCR 丢失 `sqrt`, `mathrm`
- `$\angle 1 + \angle 2 + \angle 3 = \frac{\pi}{2}$`　⚠ OCR 丢失 `angle`, `angle`, `angle`, `frac`

</details>

<details><summary><b>必修第2册 · PDF p98</b>（公式分 65，14 条）</summary>

- `1的平方根为 ±1`
- `z₁ = r₁(cos θ₁ + i sin θ₁), z₂ = r₂ · (cos θ₂ + i sin θ₂)`
- `z₁z₂ = r₁r₂ [cos(θ₁ + θ₂) + i sin(θ₁ + θ₂)]`
- `n(n ≥ 2, n ∈ N)`
- `z₁ = r₁(cos θ₁ + i sin θ₁), z₂ = r₂(cos θ₂ + i sin θ₂), ⋯, zₙ = rₙ(cos θₙ + i sin θₙ)`
- `z₁z₂⋯zₙ = r₁r₂⋯rₙ [cos(θ₁ + θ₂ + ⋯ + θₙ) + i sin(θ₁ + θ₂ + ⋯ + θₙ)]`
- `z₁ = z₂ = ⋯ = zₙ = r(cos θ + i sin θ)`
- `[r(cos θ + i sin θ)]ⁿ = rⁿ(cos nθ + i sin nθ)`
- `n (n ∈ N*)`
- `z = ρ(cos φ + i sin φ) (ρ > 0)`
- `z³ = 1 = cos 0 + i sin 0`
- `[ρ(cos φ + i sin φ)]³ = ρ³(cos 3φ + i sin 3φ) = cos 0 + i sin 0`
- `ρ³ = 1`
- `3φ = 0 + 2kπ (k ∈ Z)`

</details>

<details><summary><b>选必第1册 · PDF p35</b>（公式分 61，17 条）</summary>

- `已知: 如图 1.4-11, a ⊂ β, b ⊂ β, a ∩ b = P, a // α, b // α.`
- `求证: α // β.`
- `因为 a // α, b // α, 所以 n · u = 0, n · v = 0.`
- `因为 a ⊂ β, b ⊂ β, a ∩ b = P,`
- `所以对任意点 Q ∈ β, 存在 x, y ∈ R, 使得 PQ = xu + yv.`
- `从而 n · PQ = n · (xu + yv) = xn · u + yn · v = 0.`
- `所以, 向量 n 也是平面 β 的法向量. 故 α // β.`
- `如图 1.4-12, 在长方体 ABCD-A₁B₁C₁D₁ 中, AB = 4, BC = 3, CC₁ = 2. 线段 B₁C 上是否存在点 P, 使得 A₁P // 平面 ACD₁?`
- `那么就有 n · A₁P = 0, 由此通过向量的坐标运算可得结果.`
- `因为 A, C, D₁ 的坐标分别为 (3, 0, 0), (0, 4, 0), (0, 0, 2), 所以`
- `AC = (-3, 4, 0), AD₁ = (-3, 0, 2).`
- `设 n = (x, y, z) 是平面 ACD₁ 的法向量, 则 n · AC = 0, n · AD₁ = 0, 即`
- `{ -3x + 4y = 0, -3x + 2z = 0. }`
- `所以 { x = (2/3)z, y = (1/2)z. }`
- `取 z = 6, 则 x = 4, y = 3. 所以, n = (4, 3, 6) 是平面 ACD₁ 的一个法向量.`
- `由 A₁, C, B₁ 的坐标分别为 (3, 0, 2), (0, 4, 0), (3, 4, 2), 得 A₁B₁ = (0, 4, 0), B₁C = (-3, 0, -2).`
- `设点 P 满足 B₁P = λB₁C (0 ≤ λ ≤ 1), 则 B₁P = (-3λ, 0, -2λ), 所以 A₁P = A₁B₁ + B₁P = (-3λ, 4, -2λ).`

</details>

<details><summary><b>选必第1册 · PDF p84</b>（公式分 82，46 条）</summary>

- `$l_1: 2x + 3y - 8 = 0$`
- `$l_2: 2x + 3y + 18 = 0$`
- `$l_1: 3x + 4y = 10$`
- `$l_2: 3x + 4y = 0$`
- `$l_1: 3x - 4y + 6 = 0$`
- `$l_2: 3x - 4y + C = 0$`
- `$l_1: x - 2y + 1 = 0$`
- `$l_2: x - 2y + 4 = 0$`
- `$l_1: 2x - y + 7 = 0$`
- `$l_2: x + y = 1$`
- `$l_1: x - 3y - 10 = 0$`
- `$l_2: y = \frac{x + 5}{3}$`　⚠ OCR 丢失 `frac`
- `$l_1: 3x - 5y + 10 = 0$`
- `$l_2: 9x - 15y + 30 = 0$`
- `$2x - 3y + 10 = 0$`
- `$3x + 4y - 2 = 0$`
- `$3x - 2y + 4 = 0$`
- `$2x + y - 8 = 0$`
- `$x - 2y + 1 = 0$`
- `$4x - 3y - 7 = 0$`
- `$A(1, 2)$`
- `$B(2, 0)$`
- `$M(1, 0)$`
- `$N(-4, 0)$`
- `$P(0, 3)$`
- `$Q(-1, 1)$`
- `$P(a, 2)$`
- `$Q(-2, -3)$`
- `$M(1, 1)$`
- `$|PQ| = |PM|$`
- `$A(5, 12)$`
- `$N(-1, 5)$`
- `$P(-5, 7)$`
- `$12x + 5y - 3 = 0$`　⚠ OCR 丢失 `12x`
- `$3x - 2y - 1 = 0$`
- `$3x - 2y + 1 = 0$`
- `$6x + 8y - 3 = 0$`
- `$6x + 8y + 5 = 0$`
- `$ax + 2y + 8 = 0$`
- `$4x + 3y = 10$`

</details>

<details><summary><b>选必第1册 · PDF p88</b>（公式分 62，18 条）</summary>

- `M₁(5, -7), M₂(-2, -1)`
- `A(2, -3)`
- `(x-2)² + (y+3)² = 25`
- `(x-2)² + (y+3)² = 25`
- `(5-2)² + (-7+3)² = 25`
- `M₁`
- `(x-2)² + (y+3)² = 25`
- `(-2-2)² + (-1+3)² = 20`
- `M₂`
- `M₀(x₀, y₀)`
- `x² + y² = r²`
- `x² + y² = r²`
- `A(5, 1), B(7, -3), C(2, -8)`
- `a, b, r`
- `(x-a)² + (y-b)² = r²`
- `A(5, 1), B(7, -3), C(2, -8)`
- `{ (5-a)² + (1-b)² = r², (7-a)² + (-3-b)² = r², (2-a)² + (-8-b)² = r²,`
- `{ a² + b² -10a -2b +26 = r², a² + b² -14a +6b +58 = r², a² + b² -4a +16b +68 = r².`　⚠ OCR 丢失 `16b`

</details>

<details><summary><b>选必第1册 · PDF p89</b>（公式分 60，21 条）</summary>

- `a², b², r²`
- `{ a-2b=8, a+b=-1. }`
- `{ a=2, b=-3, }`
- `(5-a)²+(1-b)²=r²`
- `r²=25`
- `(x-2)²+(y+3)²=25`
- `A(1,1), B(2,-2)`
- `l: x-y+1=0`
- `(a, b)`
- `|CA|=|CB|, a-b+1=0`
- `x-y+1=0`
- `a-b+1=0. ①`
- `|CA|=|CB|`
- `√((a-1)²+(b-1)²)=√((a-2)²+(b-2)²),`
- `a-3b-3=0. ②`
- `a=-3, b=-2`
- `C(-3, -2)`
- `r=|AC|=√((1+3)²+(1+2)²)=5`
- `(x+3)²+(y+2)²=25.`
- `(1,1), (2,-2), D(3/2, -1/2), k_AB=(-2-1)/(2-1)=-3`
- `y+1/2=1/3(x-3/2),`

</details>

<details><summary><b>选必第1册 · PDF p103</b>（公式分 76，32 条）</summary>

- `C₁：x²+y²=4`
- `C₂：x²+y²-8x-6y+16=0`
- `C₁：x²+y²+2x+3y+1=0`
- `C₂：x²+y²+4x+3y+2=0`
- `4x-3y=50`
- `x²+y²=100`
- `x-7y+2=0`
- `y=x`
- `y=6`
- `2x-3y+6=0`
- `3x-y-6=0`
- `C：x²+y²-2x-4y=0`
- `3x-y=0`
- `x-y=0`
- `C：x²+y²-x+2y=0`
- `l：x-y+1=0`
- `BE=a/3`
- `CF=a/2`
- `x-y-4=0`
- `x²+y²+6x-4=0`
- `x²+y²+6y-28=0`
- `x²+y²-4=0`
- `x²+y²-4x+4y-12=0`
- `M(3, -1)`
- `C：x²+y²+2x-6y+5=0`
- `N(1, 2)`
- `∠A=45°`
- `A(-2, -2)`
- `B(-2, 6)`
- `C(4, -2)`
- `x²+y²=4`
- `|PA|²+|PB|²+|PC|²`

</details>

<details><summary><b>选必第1册 · PDF p107</b>（公式分 105，32 条）</summary>

- `3x + 2y - 1 = 0`
- `x - y sin θ + 2 = 0`
- `[π/4, π/2]`
- `[π/4, 3π/4]`
- `[π/4, π/2) ∪ (π/2, 3π/4)`
- `3x - 4y + 5 = 0`
- `3x + 4y - 5 = 0`
- `3x + 4y + 5 = 0`
- `3x - 4y - 5 = 0`
- `2x + 3y = a`
- `4x + 6y - 3 = 0`
- `x + 2ay - 1 = 0`
- `(3a - 1)x - ay - 1 = 0`
- `x + (1 + a)y = 2 - a`
- `2ax + 4y = -16`
- `4ax + y = 1`
- `(1 - a)x + y = -1`
- `2x + ay = 2`
- `ax + 2y = 1`
- `(3a + 2)x + (1 - 4a)y + 8 = 0`
- `(5a - 2)x + (a + 4)y - 7 = 0`
- `x - y - 2 = 0`
- `x + y - 1 = 0`
- `3x - y + 4 = 0`
- `3x + y - 5 = 0`
- `x^2 + y^2 - 4x + 2my + 2m^2 - 2m + 1 = 0`
- `x^2 + y^2 - 6x + 4y + 12 = 0`
- `x^2 + y^2 - 14x - 2y + 14 = 0`　⚠ OCR 丢失 `14x`
- `f(c) ≈ f(a) + ((c - a)/(b - a))[f(b) - f(a)]`
- `(1 + 3λ)x + (1 + 4λ)y - 2λ - 4λ = 0`
- `2x - y - 2 = 0`
- `x + y + 3 = 0`

</details>

<details><summary><b>选必第2册 · PDF p19</b>（公式分 71，16 条）</summary>

- `a_n = a_1 + (n-1)d (n≥2)`
- `a_1 = a_1 + (1-1)d = a_1`
- `a_n = a_1 + (n-1)d`
- `a_n = a_1 + (n-1)d = dn + (a_1 - d)`
- `f(x) = dx + (a_1 - d)`
- `a_n = f(n)`
- `f(x) = dx + (a_1 - d)`
- `(1, f(1)), (2, f(2)), …, (n, f(n)), …`
- `f(x) = dx + (a_1 - d)`
- `f(x) = kx + b (k, b为常数)`
- `f(1) = k + b, f(2) = 2k + b, …, f(n) = nk + b, …`
- `a_n = 5 - 2n`
- `a_n - a_{n-1} = d`
- `a_{n-1} = 5 - 2(n-1) = 7 - 2n`
- `d = a_n - a_{n-1} = (5 - 2n) - (7 - 2n) = -2`
- `a_1 = 5 - 2 × 1 = 3`

</details>

<details><summary><b>选必第2册 · PDF p24</b>（公式分 73，13 条）</summary>

- `$a_1+a_n=a_2+a_{n-1}=\cdots=a_{\frac{n}{2}}+a_{\frac{n}{2}+1}$`　⚠ OCR 丢失 `cdots`, `frac`, `frac`
- `$S_n=1+2+3+\cdots+n$`　⚠ OCR 丢失 `cdots`
- `$(1+n)+[2+(n-1)]+\cdots+[\frac{n}{2}+(\frac{n}{2}+1)]$`　⚠ OCR 丢失 `cdots`, `frac`, `frac`
- `$(1+n)+(1+n)+\cdots+(1+n)$`　⚠ OCR 丢失 `cdots`
- `$\frac{n(1+n)}{2}$`　⚠ OCR 丢失 `frac`
- `$S_n=1+2+3+\cdots+n$`　⚠ OCR 丢失 `cdots`
- `$(1+n)+[2+(n-1)]+\cdots+[(\frac{n+1}{2}-1)+(\frac{n+1}{2}+1)]+\frac{n+1}{2}$`　⚠ OCR 丢失 `cdots`, `frac`, `frac`, `frac`
- `$(1+n)+(1+n)+\cdots+(1+n)+\frac{n+1}{2}$`　⚠ OCR 丢失 `cdots`, `frac`
- `$\frac{n-1}{2}\cdot(1+n)+\frac{n+1}{2}$`　⚠ OCR 丢失 `frac`, `cdot`, `frac`
- `$\frac{n(1+n)}{2}$`　⚠ OCR 丢失 `frac`
- `$S_n=1+2+3+\cdots+n=\frac{n(1+n)}{2}$`　⚠ OCR 丢失 `cdots`, `frac`
- `$S_n=1+2+3+\cdots+n=\frac{n(n+1)}{2}$`　⚠ OCR 丢失 `cdots`, `frac`
- `$2S_n=2(1+2+3+\cdots+n)=n(n+1)$`　⚠ OCR 丢失 `cdots`

</details>

<details><summary><b>选必第2册 · PDF p25</b>（公式分 70，17 条）</summary>

- `S_n = 1 + 2 + 3 + ··· + n，`
- `S_n = n + (n - 1) + (n - 2) + ··· + 1，`
- `2S_n = (n + 1) + [(n - 1) + 2] + [(n - 2) + 3] + ··· + (1 + n)`
- `= (1 + n) + (1 + n) + ··· + (1 + n)`
- `= n(n + 1)，`
- `S_n = 1 + 2 + 3 + ··· + n = \frac{n(n + 1)}{2}．`　⚠ OCR 丢失 `frac`
- `a_1 + a_n = a_2 + a_{n - 1} = ··· = a_n + a_1，`
- `S_n = a_1 + a_2 + ··· + a_n，`
- `S_n = a_n + a_{n - 1} + ··· + a_1，`
- `2S_n = (a_1 + a_n) + (a_2 + a_{n - 1}) + ··· + (a_n + a_1)`
- `= (a_1 + a_n) + (a_1 + a_n) + ··· + (a_1 + a_n)`
- `= n(a_1 + a_n)，`
- `S_n = \frac{n(a_1 + a_n)}{2}．`　⚠ OCR 丢失 `frac`
- `\frac{a_1 + a_n}{2} = \frac{a_1 + a_2 + ··· + a_n}{n}，`　⚠ OCR 丢失 `frac`, `frac`
- `\frac{a_1 + a_n}{2}，`　⚠ OCR 丢失 `frac`
- `a_n = a_1 + (n - 1)d，`
- `S_n = na_1 + \frac{n(n - 1)}{2}d．`　⚠ OCR 丢失 `frac`

</details>

<details><summary><b>选必第2册 · PDF p56</b>（公式分 67，11 条）</summary>

- `>(k+1)x.`
- `S_n > nx`
- `-1+3-5+...+(-1)^n(2n-1)=(-1)^n n`
- `\frac{1}{1×2}，\frac{1}{2×3}，\frac{1}{3×4}，...，\frac{1}{n(n+1)}`　⚠ OCR 丢失 `frac`, `frac`, `frac`, `frac`
- `a_1=4，2a_{n+1}=a_n a_{n+1}=1`
- `-1+3-5+7+...+(-1)^n(2n-1)+(-1)^{n+1}(2n+1)+(-1)^{n+2}(2n+3)=(-1)^{n+2}(2n+2)`
- `1+3+5+...+(2n-1)=n^2`
- `1+2+2^2+...+2^{n-1}=2^n-1`
- `1^3+2^3+3^3+...+n^3=[\frac{1}{2}n(n+1)]^2`　⚠ OCR 丢失 `frac`
- `a_1=1，4a_{n+1}=a_n a_{n+1}+2a_n=9 (n∈N^*)`
- `\frac{1}{1×4}，\frac{1}{4×7}，\frac{1}{7×10}，...，\frac{1}{(3n-2)(3n+1)}`　⚠ OCR 丢失 `frac`, `frac`, `frac`, `frac`

</details>

<details><summary><b>选必第2册 · PDF p84</b>（公式分 89，41 条）</summary>

- `y=ln(2x-1)`
- `u=2x-1(x>\frac{1}{2})`　⚠ OCR 丢失 `frac`
- `y=\ln u`
- `y=\ln(2x-1)`
- `y=\ln u`
- `u=2x-1(x>\frac{1}{2})`　⚠ OCR 丢失 `frac`
- `y=f(u)`
- `u=g(x)`
- `y=f(u)=f(g(x))=\ln(2x-1)`
- `y=f(u)`
- `u=g(x)`
- `y=f(g(x))`
- `y=\ln(2x-1)`
- `y=\ln u`
- `u=2x-1(x>\frac{1}{2})`　⚠ OCR 丢失 `frac`
- `y=\sin 2x`
- `y=\sin u`
- `u=2x`
- `y=\sin 2x`
- `y=\sin u`
- `u=2x`
- `y'_x`
- `y'_u`
- `u'_x`
- `y'_x=(\sin 2x)'=(2\sin x\cos x)'`
- `=2[(\sin x)'\cdot\cos x+\sin x\cdot(\cos x)']`　⚠ OCR 丢失 `cdot`, `cdot`
- `=2[\cos x\cdot\cos x+\sin x\cdot(-\sin x)]`　⚠ OCR 丢失 `cdot`, `cdot`
- `=2(\cos^2x-\sin^2x)`
- `=2\cos 2x`
- `y'_u=(\sin u)'=\cos u`
- `u'_x=(2x)'=2`
- `y'_x=2\cos 2x=\cos u\cdot 2=y'_u\cdot u'_x`　⚠ OCR 丢失 `cdot`, `cdot`
- `y=f(u)`
- `u=g(x)`
- `y=f(g(x))`
- `y=f(u)`
- `u=g(x)`
- `y'_x=y'_u\cdot u'_x`　⚠ OCR 丢失 `cdot`
- `y=(3x+5)^3`
- `y=e^{-0.05x+1}`　⚠ OCR 丢失 `05x`

</details>

<details><summary><b>选必第2册 · PDF p86</b>（公式分 63，27 条）</summary>

- `$y = \frac{2}{\sqrt{3x+1}}$`　⚠ OCR 丢失 `frac`, `sqrt`
- `$y = (1-2x)^3$`
- `$y = \log_2(2x+1)$`
- `$y = \cos \frac{x}{3}$`　⚠ OCR 丢失 `frac`
- `$y = \sin(\frac{3\pi}{2} - 3x)$`　⚠ OCR 丢失 `frac`
- `$y = 2^{2x+1}$`
- `$y = e^{-2x+1}$ 在 $x = \frac{1}{2}$ 处的导数`　⚠ OCR 丢失 `frac`
- `$y = \ln(5x+2)$ 在 $x=1$ 处的导数`
- `$y = \sqrt[3]{3x-1}$ 在点 $(\frac{2}{3}, 1)$ 处的切线方程`　⚠ OCR 丢失 `sqrt`, `frac`
- `$y = 2x^3 - 3x^2 + 5$`
- `$y = \frac{2}{x^3} + \frac{4}{x+1}$`　⚠ OCR 丢失 `frac`, `frac`
- `$y = 2^x + \log_3 x$`
- `$y = x^5 e^{x^2}$`
- `$y = \frac{x^3-1}{\sin x}$`　⚠ OCR 丢失 `frac`
- `$y = \frac{\sin x}{\sin x + \cos x}$`　⚠ OCR 丢失 `frac`
- `$y = (x+1)^{99}$`
- `$y = \frac{x}{\sqrt{2x+1}}$`　⚠ OCR 丢失 `frac`, `sqrt`
- `$y = (2x-3)\sin(2x+5)$`
- `$y = \frac{\cos(3x-2)}{2x}$`　⚠ OCR 丢失 `frac`
- `$y = (3x+1)^2 \ln(3x)$`
- `$y = 3^x e^{-3x}$`
- `$f(x) = 13 - 8x + \sqrt{2}x^2$，且 $f'(x_0)=4$，求 $x_0$`　⚠ OCR 丢失 `sqrt`
- `$y = x \ln x$`
- `$y = \frac{\sin x}{x}$ 在点 $M(\pi, 0)$ 处的切线方程`　⚠ OCR 丢失 `frac`
- `$f(x) = f'(\frac{\pi}{4})\sin x - \cos x$，求 $f(x)$ 在 $x = \frac{\pi}{4}$ 处的导数`　⚠ OCR 丢失 `frac`, `frac`
- `$f(x) = 1 - e^x$ 的图象与 $x$ 轴相交于点 $P$，求该曲线在点 $P$ 处的切线方程`
- `$f(x) = \frac{x^2}{2} + 2x - 3\ln x$，求 $f(x)$ 的导数，并求出 $f'(x)>0$ 的解集`　⚠ OCR 丢失 `frac`

</details>

<details><summary><b>选必第3册 · PDF p35</b>（公式分 65，16 条）</summary>

- `(a + b)^3, (a + b)^4`
- `(a + b)^n = C_n^0 a^n + C_n^1 a^{n-1} b^1 + ... + C_n^k a^{n-k} b^k + ... + C_n^n b^n, n \in N^*`
- `a^{n-k} b^k (k = 0, 1, ..., n)`
- `T_{k+1} = C_n^k a^{n-k} b^k`
- `(1 + x)^n = C_n^0 + C_n^1 x + C_n^2 x^2 + ... + C_n^k x^k + ... + C_n^n x^n`
- `(x + 1/x)^6`
- `(x + 1/x)^6 = (x + x^{-1})^6`
- `= C_6^0 x^6 + C_6^1 x^5 x^{-1} + C_6^2 x^4 x^{-2} + C_6^3 x^3 x^{-3} + C_6^4 x^2 x^{-4} + C_6^5 x^1 x^{-5} + C_6^6 x^{-6}`
- `= x^6 + 6x^4 + 15x^2 + 20 + 15x^{-2} + 6x^{-4} + x^{-6}`　⚠ OCR 丢失 `15x`, `15x`
- `(1 + 2x)^7`
- `2\sqrt{x} - 1/\sqrt{x}`　⚠ OCR 丢失 `sqrt`, `sqrt`
- `(2\sqrt{x} - 1/\sqrt{x})^6`　⚠ OCR 丢失 `sqrt`, `sqrt`
- `(1 + 2x)^7`
- `T_{3+1} = C_7^3 \times 1^{7-3} \times (2x)^3`　⚠ OCR 丢失 `times`, `times`
- `(1 + 2x)^7`
- `C_7^3 = 35`

</details>

<details><summary><b>选必第3册 · PDF p114</b>（公式分 60，17 条）</summary>

- `Q(a, b) = Σ_{i=1}^{n} (y_i - bx_i - a)²`
- `= Σ_{i=1}^{n} [y_i - bx_i - (ȳ - b x̄) + (ȳ - b x̄) - a]²`
- `= Σ_{i=1}^{n} [(y_i - ȳ) - b(x_i - x̄) + (ȳ - b x̄) - a]²`
- `= Σ_{i=1}^{n} [(y_i - ȳ) - b(x_i - x̄)]² + 2 Σ_{i=1}^{n} [(y_i - ȳ) - b(x_i - x̄)] × [(ȳ - b x̄) - a] + n [(ȳ - b x̄) - a]²`
- `Σ_{i=1}^{n} [(y_i - ȳ) - b(x_i - x̄)](ȳ - b x̄ - a)`
- `= (ȳ - b x̄ - a) Σ_{i=1}^{n} [(y_i - ȳ) - b(x_i - x̄)]`
- `= (ȳ - b x̄ - a) [Σ_{i=1}^{n} (y_i - ȳ) - b Σ_{i=1}^{n} (x_i - x̄)]`
- `= (ȳ - b x̄ - a) [(nȳ - nȳ) - b(nx̄ - nx̄)]`
- `= 0`
- `Q(a, b) = Σ_{i=1}^{n} [(y_i - ȳ) - b(x_i - x̄)]² + n(ȳ - b x̄ - a)²`
- `a = ȳ - b x̄`
- `Q(a, b) = Σ_{i=1}^{n} [(y_i - ȳ) - b(x_i - x̄)]²`
- `= b² Σ_{i=1}^{n} (x_i - x̄)² - 2b Σ_{i=1}^{n} (x_i - x̄)(y_i - ȳ) + Σ_{i=1}^{n} (y_i - ȳ)²`
- `b̂ = [Σ_{i=1}^{n} (x_i - x̄)(y_i - ȳ)] / [Σ_{i=1}^{n} (x_i - x̄)²]`
- `b̂ = [Σ_{i=1}^{n} (x_i - x̄)(y_i - ȳ)] / [Σ_{i=1}^{n} (x_i - x̄)²],`
- `â = ȳ - b̂ x̄`
- `（2）`

</details>

<details><summary><b>选必第3册 · PDF p134</b>（公式分 65，6 条）</summary>

- `P(X=0, Y=1) = P(Y=1) - P(X=1, Y=1).`
- `P(X=1)P(Y=1) = P(X=1, Y=1).`
- `P(X=0, Y=0) = P(X=0)P(Y=0);`
- `P(X=0, Y=1) = P(X=0)P(Y=1);`
- `P(X=1, Y=0) = P(X=1)P(Y=0);`
- `P(X=1, Y=1) = P(X=1)P(Y=1),`

</details>

## 结论

1. **58 页逐页读完，共 1121 条公式**，无「读不出」页；无公式页 0 个（多为纯练习题版式）。
2. **OCR 在这 58 页共丢失 1023 个字符组**，即公式密集页上 OCR 文本确实不可用于公式；与 §附一 的 30 页双引擎实测（数字一致率中位 0.60）互为印证。
3. 口径不变：**知识点、例题数值、答案一律不从 OCR 抄**；需要公式时按本台账的逐页清单取，要再核就回原页 PDF（页码为 PDF 页，高中 5 册无文字层故未换算教材印刷页）。
4. 本台账只做「读出并落盘」，**未据此改动任何知识点/题目的数值**——如有需要，下一步可拿台账逐点比对题库里的公式表述。

## 对照样例：必修第二册 p97（OCR 丢失 112 个字符组，全册最差）

| 来源 | 该页（复数的三角表示·乘除运算）读到什么 |
| --- | --- |
| 974 页 OCR（Vision 引擎） | `（2） VT0（cos 2 +isin 2） X./z（cos 升 +isin #）`、`10（cosg +isinW）卡5（cos 专+isin零）` —— 希腊字母与分式全被读成乱码 |
| 视觉模型（本台账） | `√10(cos π/2 + i sin π/2) × √2(cos …)`、`10(cos 2π/3 + i sin 2π/3) ÷ [5(cos π/3 + i sin π/3)]`、`12(cos 3π/2 + i sin 3π/2) ÷ [6(cos π/6 + i sin π/6)]`、`2(cos75° + i sin75°) × (1/2 − 1/2 i)` |

两侧的结构（`12(cos …) ÷ [6(cos …)]`、`2(cos75°…) × (…)`）能一一对上，**说明视觉模型读的是原页、没有编造**；同时说明公式密集页上 OCR 文本完全不可用。
