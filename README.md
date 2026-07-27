# Ecommerce-data-collection
# 唯品会商品数据采集工具（例）

> 基于唯品会PC端搜索API的商品数据采集脚本

## 技术栈

- Python 3.x
- Requests
- Pandas

## 功能说明

1. 根据关键词搜索商品，获取商品ID列表（支持分页）
2. 根据商品ID批量获取商品详情（价格、品牌、图片等）
3. 自动清洗数据并导出为CSV文件

## 运行方式

1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 复制 `config.example.py` 为 `config.py`，填入配置信息
4. 运行：`python collector.py`

## 输出示例

CSV文件包含以下字段：商品ID、标题、品牌、分类、销售价、市场价、折扣、图片链接、状态

## 注意事项

- 仅供个人学习研究使用
- 请勿高频请求，代码已内置请求间隔控制（如有）
- 本项目不包含采集到的数据文件

## 项目状态

Demo版本，可扩展为多关键词批量采集
