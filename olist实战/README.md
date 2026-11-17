# Olist 巴西电商数据分析实战

基于 Kaggle 公开的 [Olist Brazilian E-commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)（10 万订单、9 张关联表）的完整数据分析项目：**数据处理 → 客户分析 → 经营诊断 → 预测建模**，共 14 个 Jupyter Notebook，另附一份自包含 HTML 总结报告。

## 数据获取

数据文件不入库（合计约 200MB），请按以下方式还原：

1. 下载 [Kaggle 数据集](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)（或解压仓库外的 `archive.zip`）
2. 将 9 个 CSV 放入 `源数据/` 目录
3. 运行 [数据处理.ipynb](数据处理.ipynb)，生成 `data/` 下 8 张清洗后表（所有后续 notebook 的输入）

## 目录结构

```
├── 数据处理.ipynb              # 清洗 9 张源表 → data/*_clean.csv
├── RFM.ipynb                   # 客户价值分层（4 类客群）
├── 复购留存.ipynb              # 复购率/间隔/30天唤醒漏斗
├── 销售趋势.ipynb              # 月度订单量与销售额
├── 品类与价格带.ipynb          # 品类 TOP10、价格带、帕累托
├── 支付方式偏好.ipynb          # 信用卡/分期行为
├── 交付时效与准时率.ipynb      # 履约水平诊断
├── 评分分布与差评归因.ipynb    # 差评根因（物流）
├── 运费与地理关系.ipynb        # 同/跨州运费、供需地理错配
├── 商品关联与交叉销售.ipynb    # 购物篮深度、品类共现
├── 客户生命周期价值（LTV）.ipynb # 洛伦兹曲线、价值集中度
├── 流失预测.ipynb              # 首单特征能否预测流失
├── 配送延迟与评分预测.ipynb    # 差评预警模型
├── 销量需求预测.ipynb          # 月度订单量基线预测
├── olist-report/olist-report.html  # HTML 总结报告（自包含，可直接打开）
└── data/                       # 清洗后数据（运行数据处理后生成）
```

## 运行环境

- Python 3.12
- 依赖：`pip install pandas matplotlib scikit-learn jupyter nbconvert nbclient`

## 核心结论速览

| 主题 | 关键发现 |
|---|---|
| 客户结构 | 93,358 名客户，复购率仅 3.0%，一次性交易型平台；RFM 四类客群中发展客户占 60% |
| 复购留存 | 复购间隔中位 28 天，51% 的复购发生在首购后 30 天内；错过窗口全年仅补回 1.39% |
| 销售趋势 | 2017→2018 月订单量近翻倍（3,619→6,598）后进入 6,000±500 平台期 |
| 品类价格 | 健康美容/手表礼品/床品餐桌为销售额前三；<50 价位走量、100–200 价位贡献最大金额 |
| 支付 | 信用卡占 75.9% 订单，51.5% 订单使用分期（巴西 BNPL 文化） |
| 履约与评分 | 平均送达 12.1 天、准时率 93.2%；迟到订单差评率 61% vs 准时 9%——差评主因是物流 |
| 运费地理 | 跨州运费 3 倍于同州；卖家集中东南部，北方运费高企抑制需求 |
| 交叉销售 | 仅 3.3% 订单含多件商品，购物篮深度是最大 GMV 杠杆 |
| 建模 | 流失不可从首单特征预测（AUC 0.54）；差评可用迟到天数预警（AUC 0.67）；销量预测移动平均最优（MAE 386） |

完整分析与运营建议见 [olist-report/olist-report.html](olist-report/olist-report.html)。
