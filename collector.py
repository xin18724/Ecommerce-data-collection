import requests
import pandas as pd
import time
from config import COOKIES, PARAMS


def get_product_ids(keyword, max_pages=10, batch_size=120):
    """
    获取商品 ID 列表，支持分页获取
    :param keyword: 搜索关键词
    :param max_pages: 要爬取的页数
    :param batch_size: 每页返回的商品数量
    :return: 商品 ID 列表
    """
    url = "https://mapi-pc.vip.com/vips-mobile/rest/shopping/pc/search/product/rank"
    headers = {
        "pragma": "no-cache",
        "referer": "https://category.vip.com/",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    product_ids = []

    for page in range(max_pages):
        page_offset = page * batch_size

        params = {
            "app_name": "shop_pc",
            "app_version": "4.0",
            "warehouse": "VIP_CD",
            "fdc_area_id": "105101101",
            "client": "pc",
            "mobile_platform": "1",
            "province_id": "105101",
            "api_key": PARAMS.get("api_key", ""),
            "user_id": "111693749",
            "mars_cid": "1736251449066_c8f4870a8ac51d14562510f72d3ee86d",
            "standby_id": "nature",
            "keyword": keyword,
            "sort": "0",
            "pageOffset": str(page_offset),
            "batchSize": str(batch_size),
            "channelId": "1",
            "gPlatform": "PC",
            "_": "1736849594426"
        }

        response = requests.get(url, params=params, headers=headers, cookies=COOKIES)

        if response.status_code != 200:
            print(f"请求失败，状态码：{response.status_code}")
            break

        res = response.json()
        products = res.get("data", {}).get("products", [])

        if not products:
            break

        product_ids.extend([i["pid"] for i in products])
        print(f"已获取第 {page + 1} 页商品数据，共 {len(products)} 个商品")

        # 请求间隔，避免频率过高
        time.sleep(0.5)

    return product_ids


def get_product_details(product_ids, keyword=""):
    """
    根据商品 ID 列表批量获取商品详情
    :param product_ids: 商品 ID 列表
    :param keyword: 搜索关键词，用于生成文件名
    """
    url = "https://mapi-pc.vip.com/vips-mobile/rest/shopping/pc/product/module/list/v2"
    headers = {
        "pragma": "no-cache",
        "referer": "https://category.vip.com/",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    flattened_data_list = []

    # 每次请求最多 50 个商品 ID
    batch_size = 50
    batches = [product_ids[i:i + batch_size] for i in range(0, len(product_ids), batch_size)]

    for idx, batch in enumerate(batches):
        product_ids_str = ",".join(map(str, batch))
        params = {
            "app_name": "shop_pc",
            "app_version": "4.0",
            "warehouse": "VIP_CD",
            "province_id": "105101",
            "api_key": PARAMS.get("api_key", ""),
            "user_id": "111693749",
            "mars_cid": "1736251449066_c8f4870a8ac51d14562510f72d3ee86d",
            "wap_consumer": "c",
            "is_default_area": "1",
            "productIds": product_ids_str,
            "scene": "search",
            "standby_id": "nature",
            "_": "1736848998583"
        }

        response = requests.get(url, params=params, headers=headers, cookies=COOKIES)

        if response.status_code != 200:
            print(f"请求商品详情失败，状态码：{response.status_code}")
            continue

        res = response.json()
        products = res.get("data", {}).get("products", [])

        for data in products:
            flattened_data = {
                "product_id": data.get("productId", ""),
                "title": data.get("title", ""),
                "brand": data.get("brandShowName", ""),
                "category_id": data.get("categoryId", ""),
                "sale_price": data.get("price", {}).get("salePrice", ""),
                "market_price": data.get("price", {}).get("marketPrice", ""),
                "discount": data.get("price", {}).get("saleDiscount", ""),
                "small_image": data.get("smallImage", ""),
                "square_image": data.get("squareImage", ""),
                "status": "在售" if data.get("status") == "0" else "下架"
            }
            flattened_data_list.append(flattened_data)

        print(f"已获取第 {idx + 1}/{len(batches)} 批商品详情，共 {len(products)} 个商品")

        # 请求间隔，避免频率过高
        time.sleep(0.5)

    # 保存为 CSV 文件，文件名包含关键词和时间
    if flattened_data_list:
        df = pd.DataFrame(flattened_data_list)
        filename = f"product_details_{keyword}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"商品详情已保存为 {filename}")
    else:
        print("未获取到任何商品详情数据")


def main():
    """主函数"""
    keyword = "雪地靴"
    max_pages = 5

    print(f"开始采集关键词为 '{keyword}' 的商品数据...")

    # 步骤1：获取商品ID列表
    product_ids = get_product_ids(keyword=keyword, max_pages=max_pages)
    print(f"获取到 {len(product_ids)} 个商品 ID")

    if not product_ids:
        print("未获取到商品ID，程序结束")
        return

    # 步骤2：获取商品详情
    get_product_details(product_ids, keyword=keyword)

    print("采集完成！")


if __name__ == "__main__":
    main()
