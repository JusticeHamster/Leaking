# Low-Rank Modeling and Its Applications In Image Analysis

## Abstract

低秩模型通常指一类通过将有用的变量表示为低秩矩阵来解决问题的方法。低秩模型获得了许多进展，比如

- ```exact low-rank matrix recovery via convex pro-gramming```

- ```matrix completion applied to collaborative filtering```

这篇论文回顾了最近低秩模型的发展，最先进的算法，以及与图像分析相关的应用。
首先给出低秩模型的概念总览以及相关领域的一些挑战。
然后总结```low-rank matrix recovery```的模型和算法并且用数值试验演示了他们的优点和局限性。
之后介绍了一些在图像分析方面低秩模型的应用。
最后得出了一些结论。

## Introduction

### 前提：

- 许多领域数据维度很高，难以分析。比如图片、自然语言文档、用户历史记录、基因组等。

- 但高维度数据往往位于低纬子空间。

### 假设：

$$
rank(D) \ll min(m,n)
$$
其中$D$为$n$个$m$维数据集。

### examples：

```Lambertian reflectance```

```Signal Processing```

### 噪声

现实世界数据由于噪声的存在很难做到真正的低秩，因此对于真实问题使用另一个模型：
$$
D=X+E
$$
X代表了低秩成分，E代表了噪声或测试误差。从带噪声的数据中恢复低秩结构成为了许多问题的关键任务。

常规的寻找低秩近似的方法是作如下优化：
$$
\min_X||D-X||_F^2 \\
s.t.\quad{rank}(X)\leqslant{r}
$$
其中$||Y||_F=\sqrt{\sum_{ij}Y_{ij}^2}$，代表一个矩阵的[Frobenius norm](https://zh.wikipedia.org/wiki/%E7%9F%A9%E9%99%A3%E7%AF%84%E6%95%B8#%E5%BC%97%E7%BD%97%E8%B4%9D%E5%B0%BC%E4%B9%8C%E6%96%AF%E7%AF%84%E6%95%B0)。

根据理论，上面的优化可以由SVD分解：
$$
\mathbf{X}^*=\sum_{i=1}^r\sigma_i\mathbf{u}_i\mathbf{v}_i^T
$$
可以极好地将数据嵌入在一个r维子空间中。

然而虽然分析方案在确定的假设下PCA是数据分析最好的工具之一，但它没法处理真实的复杂应用，举例如下：

- Recovery from a few entries.

- Recovery from gross errors.

所以需要RPCA。

## 最小化秩

### 分析

#### 近似

最小化秩是NP-hard问题，所以需要将其转换为一个凸函数。

用核范数代替秩：
$$
||\mathbf{X}||_*=\sum_{i=1}^r\sigma_i
$$
$\sigma_i$为$\mathbf{X}$的奇异值。

#### 原因：

- 核范数是凸函数

- 核范数被证明是所有秩的近似中最紧的凸函数

### 矩阵补全

#### 近似

以上表达式可以表示为：
$$
\min_\mathbf{X}\ rank(\mathbf{X})\\
s.t.\ \mathcal{P}_\Omega(\mathbf{X})=\mathcal{P}_\Omega(\mathbf{D})
$$
其中$\mathcal{P}_\Omega(\mathbf{X})$是将矩阵投影到所有限制在$\Omega$的非零矩阵空间的操作，即$\mathcal{P}_\Omega(\mathbf{X})$对于$\Omega$空间中的项以及$\Omega$空间外的零与$\mathbf{X}$有相同的值。

#### 再近似

根据上一节的讨论，用核范数代替rank：
$$
\min_\mathbf{X}\ ||\mathbf{X}||_*\\
s.t.\ \mathcal{P}_\Omega(\mathbf{X})=\mathcal{P}_\Omega(\mathbf{D})
$$

#### 再次近似

由于上述约束过强，会导致过拟合，于是一般采用以下更松的形式：
$$
\min_\mathbf{X}\ \frac{1}{2}||\mathcal{P}_\Omega(\mathbf{D})-\mathcal{P}_\Omega(\mathbf{X})||_F^2+\lambda||\mathbf{X}||_*
$$

### RPCA

在轻微的假设下就能讲RPCA问题由下列凸表达式表示，叫做PCP(Principal Component Pursuit)：
$$
\min_{X,E}\ ||\mathbf{X}||_*+\lambda||\mathbf{E}||_1\\
s.t.\ \mathbf{X}+\mathbf{E}=\mathbf{D}
$$
详见RPCA相关论文。

#### 放松

上式考虑到高斯噪声，可以将约束放松为：
$$
||\mathbf{X}+\mathbf{E}-\mathbf{D}||_F\leq\sigma
$$

于是：
$$
\min_{X,E}\ ||\mathbf{X}||_*+\lambda||\mathbf{E}||_1+\frac{\mu}{2}||\mathbf{X}+\mathbf{E}-\mathbf{D}||_F^2
$$

### 优化算法
