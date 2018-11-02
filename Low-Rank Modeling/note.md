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

前提：

- 许多领域数据维度很高，难以分析。比如图片、自然语言文档、用户历史记录、基因组等。

- 但高维度数据往往位于低纬子空间。

于是有假设：
$$
rank(D) \lll min(m,n)
$$
其中$D$为$n$个$m$维数据集。

example: ```Lambertian reflectance```

