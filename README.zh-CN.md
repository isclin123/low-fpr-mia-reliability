<p align="right">
  <a href="./README.md"><img alt="English" src="https://img.shields.io/badge/Language-English-blue"></a>
  <a href="./README.zh-CN.md"><img alt="中文" src="https://img.shields.io/badge/%E8%AF%AD%E8%A8%80-%E4%B8%AD%E6%96%87-green"></a>
</p>

# 低误报率成员推断审计的有限样本可靠性：复现包

版本：v1.0.0

日期：2026-06-05

作者：Sicheng Yi

复现包 DOI：https://doi.org/10.5281/zenodo.20552369

预印本 DOI：https://doi.org/10.5281/zenodo.20552862

本仓库支持论文《Finite-Sample Reliability of Low-FPR Membership Inference Audits》。仓库包含项目作者编写的代码、复现命令、轻量级处理后数据/划分数组、score arrays、最终派生表格、图表源输出、附录检查输出，以及用于检查论文中低误报率成员推断审计结果的支撑文档。

## 范围

本仓库对应论文的 arXiv 投稿版本，定位是一个可浏览、可复现的 GitHub 镜像。正式归档版本以 Zenodo 复现包 DOI 为准。本仓库不是原始第三方数据集的再分发。

包含内容：

- `analysis/` 下的分析代码和可复用 score-array 审计工具；
- 依赖文件、smoke examples、配置文件和复现命令；
- `data_processed/` 下的清洗/划分数组和元数据；
- expanded-grid score arrays、metrics、confidence intervals、subsampling 输出和样本量需求摘要，不包含训练模型缓存；
- `figures_tables/` 下的最终主文表格、附录表格、扩展图、Q1 附录图、诊断图和图注；
- Q1 reference-centered score、bounded shadow-model score、tie-rule、split/seed、label-uncertainty、ExtraTrees sanity 和 final CI hardening 输出；
- 用于追踪版本的最终论文 PDF/TeX。

不包含内容：

- 来自 UCI 或 scikit-learn 的原始第三方数据文件；
- `analysis/results/*/models/` 下的大型训练模型缓存，这些文件可由文档中的命令重新生成；
- 临时构建文件、Python 缓存和本地临时文件；
- 打包投稿 zip 文件。GitHub 镜像中省略这些文件，因为正式归档包已经发布在 Zenodo。

## 复现入口

建议从以下文件开始：

- `release/reproducibility_package/README.md`
- `release/reproducibility_package/environment.md`
- `release/reproducibility_package/commands.md`
- `release/reproducibility_package/data_and_outputs_manifest.md`

主命令文件记录了 fast smoke path、expanded tabular run、final confidence-interval hardening、最终表格/图生成、reference-centered compatibility check、bounded shadow-model score-array check、tie-rule sensitivity check、split/seed sensitivity check 和 label-uncertainty check。

## 数据和许可说明

原始数据集是公开第三方数据集，应通过其原始来源获取并引用。本仓库不对这些原始数据集或上游数据内容声明新的许可。仓库中包含的处理后/划分数组仅用于支持复现，并仍受上游数据来源条款约束。

项目作者编写的代码使用 MIT License。项目作者生成的文档、图、表、manifests 和图表源数据，除非单个文件另有说明，预期按 CC BY 4.0 条款复用。详情见 `NOTICE.md`、`LICENSE_MIT.txt` 和 release notes。

## 引用

如果使用本复现包，请引用归档的 Zenodo 记录：

Yi, Sicheng. Finite-Sample Reliability of Low-FPR Membership Inference Audits: Reproducibility Package. Zenodo. https://doi.org/10.5281/zenodo.20552369

关联预印本：

Yi, Sicheng. Finite-Sample Reliability of Low-FPR Membership Inference Audits. Zenodo. https://doi.org/10.5281/zenodo.20552862
