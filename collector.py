import requests
import pandas as pd
import time
import execjs
from config import COOKIES, PARAMS


def generate_mars_cid():
    """
    通过执行 JS 文件动态生成 mars_cid
    """
    with open("encryptCid.js", "r", encoding="utf-8") as f:
        js_code = f.read()
    
    ctx = execjs.compile(js_code)
    
    # 生成32位随机字符串
    rand_str = ctx.call("Mar.Random.rand", 32)
    
    # 当前时间戳
    timestamp = str(int(time.time() * 1000))
    
    # 拼接并加密
    raw_cid = f"{timestamp}_{rand_str}"
    mars_cid = ctx.call("Mar.Util.encryptCid", raw_cid)
    
    return mars_cid


def get_product_ids(keyword, max_pages=10, batch_size=120):
    """
    获取商品 ID 列表，支持分页获取
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

        # 动态生成 mars_cid
        mars_cid = generate_mars_cid()

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
            "mars_cid": mars_cid,
            "standby_id": "nature",
            "keyword": keyword,
            "sort": "0",
            "pageOffset": str(page_offset),
            "batchSize": str(batch_size),
            "channelId": "1",
            "gPlatform": "PC",
            "_": str(int(time.time() * 1000))
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

        time.sleep(0.5)

    return product_ids


def get_product_details(product_ids, keyword=""):
    """
    根据商品 ID 列表批量获取商品详情
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

    batch_size = 50
    batches = [product_ids[i:i + batch_size] for i in range(0, len(product_ids), batch_size)]

    for idx, batch in enumerate(batches):
        product_ids_str = ",".join(map(str, batch))

        # 动态生成 mars_cid
        mars_cid = generate_mars_cid()

        params = {
            "app_name": "shop_pc",
            "app_version": "4.0",
            "warehouse": "VIP_CD",
            "province_id": "105101",
            "api_key": PARAMS.get("api_key", ""),
            "user_id": "111693749",
            "mars_cid": mars_cid,
            "wap_consumer": "c",
            "is_default_area": "1",
            "productIds": product_ids_str,
            "scene": "search",
            "standby_id": "nature",
            "_": str(int(time.time() * 1000))
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

        time.sleep(0.5)

    if flattened_data_list:
        df = pd.DataFrame(flattened_data_list)
        filename = f"product_details_{keyword}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"商品详情已保存为 {filename}")
    else:
        print("未获取到任何商品详情数据")


def main():
    keyword = "雪地靴"
    max_pages = 5

    print(f"开始采集关键词为 '{keyword}' 的商品数据...")

    product_ids = get_product_ids(keyword=keyword, max_pages=max_pages)
    print(f"获取到 {len(product_ids)} 个商品 ID")

    if not product_ids:
        print("未获取到商品ID，程序结束")
        return

    get_product_details(product_ids, keyword=keyword)

    print("采集完成！")


if __name__ == "__main__":
    main()
